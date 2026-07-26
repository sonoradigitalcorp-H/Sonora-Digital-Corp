import asyncio
import base64
import json
import os
import subprocess
import tempfile
import uuid
import logging
from datetime import datetime, timezone
from pathlib import Path

import httpx
import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

from clients.aztrotech.realtime_voice.pipeline.stt import transcribe
from clients.aztrotech.voice.tts import TTS

BASE = Path(__file__).resolve().parent.parent.parent.parent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("aztrotech-realtime")

app = FastAPI(title="AztroTech Mystic Chat")

_tts = TTS(engine="edge")

STATUS_MESSAGES = {
    "listening": "🎙️ Escuchando...",
    "thinking": "🧠 Analizando tu consulta...",
    "consulting": "🔍 Resolviendo...",
    "generating_response": "✨ Generando respuesta...",
    "preparing_audio": "🎧 Preparando audio...",
    "working": "⚙️ Trabajando...",
    "almost_done": "⏳ Casi listo...",
}

PERSONA_FILE = BASE / "clients" / "aztrotech" / "ai" / "persona.md"
OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY", "")
LLM_MODEL = "nvidia/nemotron-3-nano-30b-a3b:free"
SAMPLE_RATE = 16000

SESSIONS: dict[str, dict] = {}


async def _send(ws: WebSocket, data: dict):
    await ws.send_text(json.dumps(data, ensure_ascii=False))


async def _send_status(ws: WebSocket, key: str, message: str = None):
    await _send(ws, {
        "type": "status",
        "status": key,
        "message": message or STATUS_MESSAGES.get(key, ""),
    })


def load_persona() -> str:
    if PERSONA_FILE.exists():
        with open(PERSONA_FILE) as f:
            return f.read()
    return "Eres Mystic, asistente de AztroTech. Responde en español, directa y profesional."


PERSONA = load_persona()


async def ask_llm(messages: list[dict]) -> str | None:
    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json",
    }
    payload = {"model": LLM_MODEL, "messages": messages, "max_tokens": 300, "temperature": 0.7}
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
            if r.status_code == 200:
                return r.json()["choices"][0]["message"]["content"]
            logger.warning(f"LLM {r.status_code}: {r.text[:100]}")
    except Exception as e:
        logger.error(f"LLM error: {e}")
    return None


async def handle_user_message(ws: WebSocket, session: dict, text: str):
    if not text:
        return
    if "history" not in session:
        session["history"] = [
            {"role": "system", "content": PERSONA + "\n\nEres Mystic, asesora de AztroTech. Respondes en español, máximo 3 oraciones, directa y cálida."},
        ]

    session["history"].append({"role": "user", "content": text})
    session["history"] = session["history"][-10:]

    await _send_status(ws, "thinking")
    await asyncio.sleep(0.5)

    await _send_status(ws, "consulting")
    reply = await ask_llm(session["history"])
    if not reply:
        reply = "Disculpa, no pude procesar tu mensaje. ¿Puedes repetirlo?"

    session["history"].append({"role": "assistant", "content": reply})

    await _send(ws, {
        "type": "conversation.item.created",
        "item": {
            "id": str(uuid.uuid4()),
            "type": "message",
            "role": "user",
            "content": [{"type": "text", "text": text}],
        },
    })

    await _send(ws, {
        "type": "response.output_text.delta",
        "delta": reply,
    })

    await _send_status(ws, "preparing_audio")
    audio_bytes = await _tts.synthesize(reply)
    if audio_bytes:
        audio_b64 = base64.b64encode(audio_bytes).decode()
        await _send(ws, {
            "type": "response.output_audio.delta",
            "delta": audio_b64,
            "sample_rate": 24000,
            "mime_type": "audio/mpeg",
        })
        await _send(ws, {
            "type": "response.output_audio.done",
        })
    else:
        await _send_status(ws, "almost_done")

    await _send(ws, {"type": "response.done"})


async def session_handler(ws: WebSocket, session_id: str):
    audio_buffer = bytearray()
    session = SESSIONS.get(session_id, {})
    SESSIONS[session_id] = session

    await _send(ws, {
        "type": "session.created",
        "session": {"id": session_id, "version": "1.0", "features": ["text", "audio"]},
    })
    await _send_status(ws, "listening")

    try:
        while True:
            raw = await asyncio.wait_for(ws.receive_text(), timeout=300)
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                continue

            msg_type = msg.get("type")

            if msg_type == "input_text":
                text = msg.get("text", "").strip()
                if text:
                    logger.info(f"[{session_id}] text: {text[:60]}")
                    await handle_user_message(ws, session, text)

            elif msg_type == "input_audio_buffer.append":
                try:
                    audio_buffer.extend(base64.b64decode(msg["audio"]))
                except Exception:
                    pass

            elif msg_type == "input_audio_buffer.commit":
                if len(audio_buffer) < 320:
                    continue
                await _send_status(ws, "listening")
                await _send(ws, {"type": "input_audio_buffer.speech_stopped"})
                logger.info(f"[{session_id}] audio {len(audio_buffer)} bytes")
                result = await transcribe(bytes(audio_buffer), language="es")
                text = result.get("text", "").strip()
                audio_buffer.clear()
                if text:
                    logger.info(f"[{session_id}] → {text[:80]}")
                    await handle_user_message(ws, session, text)

            elif msg_type == "ping":
                await _send(ws, {"type": "pong"})

    except WebSocketDisconnect:
        logger.info(f"[{session_id}] disconnected")
    except asyncio.TimeoutError:
        logger.info(f"[{session_id}] timeout")
    finally:
        SESSIONS.pop(session_id, None)


@app.websocket("/v1/chat")
async def chat_ws(ws: WebSocket):
    await ws.accept()
    session_id = str(uuid.uuid4())[:8]
    logger.info(f"[{session_id}] connected")
    try:
        await session_handler(ws, session_id)
    except Exception as e:
        logger.error(f"[{session_id}] error: {e}")
        try:
            await ws.close()
        except Exception:
            pass


@app.get("/", response_class=HTMLResponse)
@app.get("/chat", response_class=HTMLResponse)
async def index():
    return HTMLResponse(FRONTEND_HTML)


LANDING_FILE = Path(__file__).parent / "frontend" / "landing.html"
FRONTEND_HTML = LANDING_FILE.read_text(encoding="utf-8") if LANDING_FILE.exists() else "<h1>AztroTech Voice</h1><p>Landing page not found</p>"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8902, log_level="info")

