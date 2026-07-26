import asyncio
import base64
import json
import os
import subprocess
import sys
import tempfile
import uuid
import logging
from datetime import datetime, timezone
from pathlib import Path

import httpx
import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

from tenants.aztrotech.skills.realtime_voice.pipeline.stt import transcribe
from tenants.aztrotech.skills.realtime_voice.pipeline.vad import VADDetector, FRAME_MS
from tenants.aztrotech.skills.voice.tts import TTS

BASE = Path(__file__).resolve().parent.parent.parent.parent
POLICIES_YAML = BASE / "aztrotech" / "policies.yaml"

# Policy Engine
sys.path.insert(0, str(BASE.parent))  # core/ está en raíz
from core.policy import PolicyEngine

_policy = None
def get_policy() -> PolicyEngine:
    global _policy
    if _policy is None:
        if POLICIES_YAML.exists():
            _policy = PolicyEngine.from_yaml(str(POLICIES_YAML))
            logger.info(f"Policy Engine loaded from {POLICIES_YAML.name}")
        else:
            _policy = PolicyEngine()
            logger.warning("No policies.yaml found, using defaults")
    return _policy

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

PERSONA_FILE = BASE / "aztrotech" / "prompt.md"
OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY", "")
TENANT_ID = "aztrotech"
LLM_MODEL = "nvidia/nemotron-3-nano-30b-a3b:free"

# Costos estimados por acción (USD)
COST_LLM_CALL = 0.0001     # Nemotron free tier ~0
COST_TTS_CALL = 0.002      # Qwen3-TTS local + GPU
COST_STT_CALL = 0.0        # Whisper local, gratis

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

    # Marcar como respondiendo (para barge-in)
    session["responding"] = True
    session["cancel_event"] = asyncio.Event()

    policy = get_policy()

    # === POLICY GATE: LLM ===
    llm_decision = await policy.validate(TENANT_ID, "llm", cost=COST_LLM_CALL, context={"model": LLM_MODEL})
    if not llm_decision.allowed:
        await _send(ws, {
            "type": "response.output_text.delta",
            "delta": f"⛔ {llm_decision.reason}",
        })
        await _send(ws, {"type": "response.done"})
        session["responding"] = False
        logger.warning(f"Policy blocked LLM: {llm_decision.reason}")
        return

    # Verificar cancelación antes de LLM
    if session["cancel_event"].is_set():
        session["responding"] = False
        return

    await _send_status(ws, "consulting")
    reply = await ask_llm(session["history"])

    # Verificar cancelación después de LLM
    if session["cancel_event"].is_set():
        session["responding"] = False
        return

    if not reply:
        reply = "Disculpa, no pude procesar tu mensaje. ¿Puedes repetirlo?"
    else:
        policy.record(TENANT_ID, "llm", COST_LLM_CALL, LLM_MODEL)

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

    # === POLICY GATE: TTS ===
    tts_decision = await policy.validate(TENANT_ID, "tts", cost=COST_TTS_CALL, context={"model": "Qwen/Qwen3-TTS-12Hz-0.6B-Base"})
    if not tts_decision.allowed:
        await _send(ws, {"type": "response.done"})
        session["responding"] = False
        logger.warning(f"Policy blocked TTS: {tts_decision.reason}")
        return

    # Verificar cancelación antes de TTS
    if session["cancel_event"].is_set():
        session["responding"] = False
        return

    await _send_status(ws, "preparing_audio")
    audio_bytes = await _tts.synthesize(reply)

    # Verificar cancelación después de TTS
    if session["cancel_event"].is_set():
        session["responding"] = False
        return

    if audio_bytes:
        policy.record(TENANT_ID, "tts", COST_TTS_CALL, "qwen3-tts")
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
    session["responding"] = False


async def session_handler(ws: WebSocket, session_id: str):
    audio_buffer = bytearray()
    session = SESSIONS.get(session_id, {"responding": False, "cancel_event": None})
    SESSIONS[session_id] = session
    session["responding"] = False
    session["cancel_event"] = None

    # VAD para barge-in
    vad = VADDetector(
        threshold=0.5,
        on_speech_start=lambda: asyncio.ensure_future(_handle_barge_in(ws, session)),
    )

    await _send(ws, {
        "type": "session.created",
        "session": {"id": session_id, "version": "1.0", "features": ["text", "audio", "barge_in"]},
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
                    # Barge-in: si está respondiendo, cancelar
                    if session.get("responding"):
                        await _cancel_response(ws, session)
                    await handle_user_message(ws, session, text)

            elif msg_type == "input_audio_buffer.append":
                try:
                    chunk = base64.b64decode(msg["audio"])
                    audio_buffer.extend(chunk)
                    # VAD en cada chunk (~32ms) para detección en tiempo real
                    vad.process_chunk(bytes(chunk))
                except Exception:
                    pass

            elif msg_type == "input_audio_buffer.commit":
                if len(audio_buffer) < 320:
                    continue

                # Barge-in: si está respondiendo, cancelar
                if session.get("responding"):
                    await _cancel_response(ws, session)

                vad.reset()
                await _send_status(ws, "listening")
                await _send(ws, {"type": "input_audio_buffer.speech_stopped"})
                logger.info(f"[{session_id}] audio {len(audio_buffer)} bytes ({len(audio_buffer)/32000:.1f}s)")

                result = await transcribe(bytes(audio_buffer), language="es")
                text = result.get("text", "").strip()
                audio_buffer.clear()

                if text:
                    logger.info(f"[{session_id}] → {text[:80]}")
                    await handle_user_message(ws, session, text)

            elif msg_type == "cancel_response":
                await _cancel_response(ws, session)

            elif msg_type == "ping":
                await _send(ws, {"type": "pong"})

    except WebSocketDisconnect:
        logger.info(f"[{session_id}] disconnected")
    except asyncio.TimeoutError:
        logger.info(f"[{session_id}] timeout")
    finally:
        session["responding"] = False
        SESSIONS.pop(session_id, None)


async def _cancel_response(ws: WebSocket, session: dict):
    """Cancela la respuesta en curso (barge-in)."""
    if session.get("cancel_event"):
        session["cancel_event"].set()
    session["responding"] = False
    await _send(ws, {"type": "response.cancelled"})
    await _send(ws, {"type": "input_audio_buffer.speech_started"})
    await _send_status(ws, "listening")
    logger.info("⛔ Respuesta cancelada por barge-in")


async def _handle_barge_in(ws: WebSocket, session: dict):
    """Callback de VAD: cuando el usuario empieza a hablar mientras el asistente responde."""
    if session.get("responding"):
        logger.info("🗣️ Barge-in detectado durante respuesta")
        await _cancel_response(ws, session)


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


@app.get("/budget")
async def budget_report():
    """Reporte de presupuesto del día para el tenant."""
    policy = get_policy()
    report = policy.report(TENANT_ID)
    return report


LANDING_FILE = Path(__file__).parent / "frontend" / "landing.html"
FRONTEND_HTML = LANDING_FILE.read_text(encoding="utf-8") if LANDING_FILE.exists() else "<h1>AztroTech Voice</h1><p>Landing page not found</p>"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8902, log_level="info")

