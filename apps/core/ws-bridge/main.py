"""WebSocket Bridge — Redis pub/sub → WebSocket + Chat + Audio.

Subscribes to Redis channels and forwards events to connected WebSocket clients.
Also handles chat messages with LLM + optional TTS audio responses.
"""

import asyncio
import base64
import json
import logging
import os
import subprocess
import time
import uuid
from pathlib import Path

import httpx
import redis.asyncio as aioredis
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("ws-bridge")

app = FastAPI(title="SDC WebSocket Bridge — Chat + Audio", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

REPO = Path(__file__).resolve().parent.parent.parent.parent
AUDIO_DIR = REPO / "state" / "media"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

# ─── Config ───
REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
MCP_URL = os.getenv("MCP_URL", "http://127.0.0.1:8180")
LLM_MODEL = os.getenv("LLM_MODEL", "deepseek/deepseek-v4-flash")
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY", "")
TTS_ENABLED = os.getenv("TTS_ENABLED", "true").lower() == "true"

CHANNELS = [
    "agent:content:done", "agent:content:failed",
    "agent:sales:new-order", "agent:support:ticket",
    "system:pipeline:start", "system:pipeline:end",
    "system:alert", "system:service:health",
]

connections: set[WebSocket] = set()
conversations: dict[str, list[dict]] = {}  # session_id → history


# ═══════════════════════════════════════════════
#  TTS — Text-to-Speech con Kokoro/edge-tts
# ═══════════════════════════════════════════════

async def text_to_speech(text: str) -> str | None:
    """Generate audio from text, returns base64 MP3 or None."""
    try:
        output_path = str(AUDIO_DIR / f"tts-{uuid.uuid4().hex[:8]}.wav")
        cmd = [
            "edge-tts", "--voice", "es-MX-DaliaNeural",
            "--rate", "-8%", "--pitch", "+5Hz", "--volume", "+15%",
            "--text", text[:1500],
            "--write-media", output_path,
        ]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if r.returncode == 0 and Path(output_path).stat().st_size > 1000:
            with open(output_path, "rb") as f:
                audio_b64 = base64.b64encode(f.read()).decode()
            Path(output_path).unlink(missing_ok=True)
            return audio_b64
        # Fallback: try kokoro if available
        fallback = subprocess.run(
            ["python3", "-c", f"""
import sys; sys.path.insert(0, '{REPO}')
from apps.core.voice.tts import speak
r = speak('''{text[:500].replace(chr(39), chr(39)*2)}''')
if r['status'] == 'ok': print(r['output'])
            """],
            capture_output=True, text=True, timeout=30,
        )
        if fallback.returncode == 0 and fallback.stdout.strip():
            out = fallback.stdout.strip()
            with open(out, "rb") as f:
                audio_b64 = base64.b64encode(f.read()).decode()
            Path(out).unlink(missing_ok=True)
            return audio_b64
    except Exception as e:
        log.warning(f"TTS failed: {e}")
    return None


# ═══════════════════════════════════════════════
#  LLM — Chat completion
# ═══════════════════════════════════════════════

async def ask_llm(messages: list[dict]) -> str:
    """Send messages to LLM and get response text."""
    # Try OpenRouter first
    if OPENROUTER_KEY:
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {OPENROUTER_KEY}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": LLM_MODEL,
                        "messages": messages,
                        "temperature": 0.3,
                        "max_tokens": 1024,
                    },
                )
                if resp.status_code == 200:
                    return resp.json()["choices"][0]["message"]["content"]
        except Exception as e:
            log.warning(f"OpenRouter failed: {e}")

    # Fallback: local Ollama
    try:
        prompt = "\n".join(m["content"] for m in messages[-5:])
        r = subprocess.run(
            ["ollama", "run", "tinyllama:1.1b", prompt],
            capture_output=True, text=True, timeout=60,
        )
        return r.stdout.strip() or r.stderr.strip() or "Sin respuesta"
    except Exception as e:
        return f"Error: {e}"


# ═══════════════════════════════════════════════
#  Chat Handler
# ═══════════════════════════════════════════════

async def handle_chat(ws: WebSocket, cmd: dict):
    """Handle chat message: LLM → optional TTS → response."""
    text = cmd.get("text", "").strip()
    session_id = cmd.get("session_id", "default")

    if not text:
        await ws.send_json({"type": "error", "error": "Texto vacío"})
        return

    # Track conversation
    if session_id not in conversations:
        conversations[session_id] = [
            {"role": "system", "content": "Eres Mystic, la asistente de Sonora Digital Corp. Responde en español mexicano, natural y cálido. Eres una asistente ejecutiva con personalidad."}
        ]

    conversations[session_id].append({"role": "user", "content": text})

    # Get LLM response
    response = await ask_llm(conversations[session_id])
    conversations[session_id].append({"role": "assistant", "content": response})

    # Keep history manageable
    if len(conversations[session_id]) > 20:
        conversations[session_id] = conversations[session_id][:1] + conversations[session_id][-10:]

    # Determine if audio is requested (by flag or always from voice widget)
    want_audio = cmd.get("audio", True)

    result = {
        "type": "chat_response",
        "text": text,
        "response": response,
        "session_id": session_id,
    }

    # Generate audio if TTS enabled
    if want_audio and TTS_ENABLED:
        audio_b64 = await text_to_speech(response)
        if audio_b64:
            result["type"] = "audio_response"
            result["audio"] = audio_b64

    await ws.send_json(result)


# ═══════════════════════════════════════════════
#  Redis Listener (events)
# ═══════════════════════════════════════════════

@app.on_event("startup")
async def startup():
    if REDIS_PASSWORD:
        asyncio.create_task(redis_listener())


async def redis_listener():
    while True:
        try:
            r = await aioredis.from_url(
                f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}",
                decode_responses=True,
            )
            pubsub = r.pubsub()
            await pubsub.subscribe(*CHANNELS)
            async for msg in pubsub.listen():
                if msg["type"] == "message":
                    dead = set()
                    for ws in connections:
                        try:
                            await ws.send_json({
                                "channel": msg["channel"],
                                "data": json.loads(msg["data"]),
                            })
                        except Exception:
                            dead.add(ws)
                    connections -= dead
        except Exception as e:
            log.warning(f"Redis error: {e}")
            await asyncio.sleep(5)


# ═══════════════════════════════════════════════
#  WebSocket Endpoint
# ═══════════════════════════════════════════════

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    connections.add(ws)
    await ws.send_json({"type": "connected", "status": "Mystic chat + audio listo"})

    try:
        while True:
            msg = await ws.receive_text()
            try:
                cmd = json.loads(msg)
                msg_type = cmd.get("type", "")

                if msg_type == "chat":
                    await handle_chat(ws, cmd)

                elif msg_type == "mcp":
                    async with httpx.AsyncClient() as client:
                        resp = await client.post(
                            f"{MCP_URL}/mcp/execute",
                            json={"tool": cmd["tool"], "args": cmd.get("args", {})},
                            timeout=30,
                        )
                        await ws.send_json({"type": "mcp_result", "result": resp.json()})

                elif msg_type == "hasura":
                    async with httpx.AsyncClient() as client:
                        resp = await client.post(
                            HASURA_URL,
                            json={"query": cmd["query"]},
                            headers={"x-hasura-admin-secret": HASURA_SECRET},
                            timeout=15,
                        )
                        await ws.send_json({"type": "hasura_result", "data": resp.json()})

                elif msg_type == "ping":
                    await ws.send_json({"type": "pong"})

                else:
                    await ws.send_json({"type": "error", "error": f"Tipo desconocido: {msg_type}"})

            except json.JSONDecodeError:
                await ws.send_json({"type": "error", "error": "JSON inválido"})
            except Exception as e:
                await ws.send_json({"type": "error", "error": str(e)[:200]})

    except WebSocketDisconnect:
        connections.discard(ws)
    except Exception:
        connections.discard(ws)


# ═══════════════════════════════════════════════
#  Audio file serving
# ═══════════════════════════════════════════════

@app.get("/audio/{filename}")
async def get_audio(filename: str):
    path = AUDIO_DIR / filename
    if path.exists():
        return FileResponse(path, media_type="audio/ogg")
    return {"error": "not found"}


# ═══════════════════════════════════════════════
#  Entry point
# ═══════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("WS_BRIDGE_PORT", "8181"))
    log.info(f"Starting WS Bridge on port {port}")
    uvicorn.run(app, host="127.0.0.1", port=port)
