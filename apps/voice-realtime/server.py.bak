"""
Servidor WebSocket de voz en tiempo real para Mystic.
Pipeline completo:
  Audio (PCM16) → VAD → Whisper STT → Intent Router → Template/LLM → TTS + Soundscape → Audio mezclado → Frontend

Protocolo: OpenAI Realtime API compatible.
"""
import asyncio
import base64
import json
import logging
import os
import time
import uuid
from pathlib import Path
from typing import Optional

import httpx
import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

from apps.voice_realtime.pipeline.stt import transcribe, VoiceActivityDetector
from apps.voice_realtime.pipeline.tts import TTSEngine
from apps.voice_realtime.pipeline.audio_mixer import AudioMixer, SOUNDSCAPES
from apps.voice_realtime.intent_router import IntentRouter, RoutedAction
from apps.voice_realtime.voice_templates import VoiceTemplateEngine
from apps.voice_realtime.mcp_client import MCPClient, get_mcp_client

# ─── Configuración ───
BASE_DIR = Path(__file__).resolve().parent.parent.parent
SAMPLE_RATE = 24000  # Sample rate de salida (para TTS)
INPUT_SAMPLE_RATE = 16000
logger = logging.getLogger("voice-realtime.server")

# ─── Inicializar componentes ───
tts_engine = TTSEngine(provider="kokoro", voice="em_alex")
audio_mixer = AudioMixer(soundscape="minimal")
intent_router = IntentRouter(use_llm_fallback=True)
template_engine = VoiceTemplateEngine()

app = FastAPI(title="Mystic Voice Realtime")

# ─── Mensajes de estado ───
STATUS_MESSAGES = {
    "listening": "🎙️ Te escucho...",
    "listening_with_music": "🎵 Te escucho...",
    "understanding": "🧠 Entendiendo...",
    "routing": "🎯 Buscando destino...",
    "thinking": "✨ Pensando...",
    "generating_voice": "🎤 Preparando respuesta...",
    "speaking": "🔊 Mystic habla...",
    "redirecting": "↪️ Redirigiendo...",
    "error": "⚠️ Algo salió mal, intenta de nuevo",
}

# ─── Sesiones activas ───
SESSIONS: dict[str, dict] = {}


async def _send(ws: WebSocket, data: dict):
    """Envía mensaje JSON al WebSocket."""
    await ws.send_text(json.dumps(data, ensure_ascii=False))


async def _send_status(ws: WebSocket, key: str, message: str = None):
    """Envía mensaje de estado."""
    await _send(ws, {
        "type": "status",
        "status": key,
        "message": message or STATUS_MESSAGES.get(key, ""),
    })


async def _send_audio(ws: WebSocket, audio_b64: str, sample_rate: int = SAMPLE_RATE, mime_type: str = "audio/wav"):
    """Envía chunk de audio al frontend."""
    await _send(ws, {
        "type": "response.audio.delta",
        "delta": audio_b64,
        "sample_rate": sample_rate,
        "mime_type": mime_type,
    })


async def _send_soundscape(ws: WebSocket, audio_b64: str):
    """Envía soundscape de fondo al frontend."""
    await _send(ws, {
        "type": "soundscape.delta",
        "delta": audio_b64,
        "sample_rate": 44100,
        "mime_type": "audio/wav",
    })


async def _send_redirect(ws: WebSocket, url: str, message: str):
    """Envía redirección al frontend."""
    await _send(ws, {
        "type": "redirect",
        "url": url,
        "message": message,
    })


async def ask_llm(system_prompt: str, messages: list, max_tokens: int = 300,
                  session_id: str = None, user_text: str = None) -> Optional[str]:
    """
    Consulta al LLM vía MCP Gateway (Unified Brain).
    Proveedor unificado: opencode-go → deepseek-v4-flash.
    Contexto enriquecido con Unified Brain (Engram + Neo4j + Qdrant).
    Fallback: openrouter → ollama.
    """
    mcp = get_mcp_client()
    context_extra = ""

    # 1. Obtener contexto del Unified Brain (Engram + Neo4j + Qdrant)
    try:
        brain_ctx = await mcp.brain_context(user_text or system_prompt[:60], limit=3)
        if brain_ctx:
            context_extra += f"\n\n🧠 CONTEXTO DEL SISTEMA:\n{brain_ctx}"
    except Exception as e:
        logger.warning(f"Brain context error: {e}")

    # 2. Intentar LLM vía MCP Gateway (proveedor unificado)
    try:
        # Construir mensaje completo con contexto
        full_messages = [{"role": "system", "content": system_prompt + context_extra}]
        full_messages.extend(messages[-6:])

        result = await mcp.execute("llm_chat", {
            "messages": full_messages,  # ← array, no string
            "max_tokens": max_tokens,
            "temperature": 0.7,
            "provider": "opencode-go",
            "brain_context": brain_ctx,
        })
        if result:
            if isinstance(result, dict):
                return result.get("text") or result.get("content")
            if isinstance(result, str):
                try:
                    d = json.loads(result)
                    return d.get("text") or d.get("content") or result
                except json.JSONDecodeError:
                    return result
    except Exception as e:
        logger.warning(f"MCP LLM failed: {e}")

    # 3. Fallback: OpenRouter directo (si hay key)
    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    if not api_key:
        logger.warning("No OPENROUTER_API_KEY, giving up")
        return None

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "opencode/deepseek-v4-flash-free",
        "messages": [{"role": "system", "content": system_prompt + context_extra}] + messages[-6:],
        "max_tokens": max_tokens,
        "temperature": 0.7,
    }
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
            )
            if r.status_code == 200:
                return r.json()["choices"][0]["message"]["content"]
            logger.warning(f"LLM {r.status_code}: {r.text[:100]}")
    except Exception as e:
        logger.error(f"LLM error: {e}")
    return None


def build_mystic_persona(tone: str = "warm") -> str:
    """Construye la personalidad de Mystic según el tono."""
    base = """Eres Mystic, el alma de Sonora Digital Corp. Eres una asistente IA profesional, cálida y mexicana. 
Tu misión es ayudar a dueños de PYME, startups y profesionales independientes en México a encontrar soluciones digitales para sus negocios.

REGLAS:
- Responde en español mexicano, cálido y directo
- Máximo 3 oraciones, ve al grano
- Si el usuario pide ir a algún lado (precios, servicios, contacto, agenda), dile que lo llevarás y confirma
- Nunca inventes precios o productos que no existen
- Usa lenguaje sencillo, sin jerga técnica
- Siempre termina ofreciendo ayudar en algo más
"""

    if tone == "energetic":
        base += "\nTono: ENERGÉTICO y motivador, usa frases cortas y contundentes."
    elif tone == "calm":
        base += "\nTono: TRANQUILO y pausado, transmite seguridad y confianza."
    elif tone == "professional":
        base += "\nTono: PROFESIONAL y formal, datos precisos y estructura clara."
    else:  # warm
        base += "\nTono: CÁLIDO y cercano, como hablando con un amigo que sabe de tecnología."

    base += "\n\nProductos disponibles: Cyber Diagnosis Express ($999/mes), SSL Guardian ($299/mes), DNS Guardian ($399/mes), Email Guardian ($399/mes), Call Engine Mini ($999/mes), Super Seller Agent ($1499/mes), Clone Mini ($999/mes), WhatsApp Agent Mini ($599/mes), Uptime Guardian ($199/mes), Backup Guardian ($499/mes)."

    return base


async def handle_voice_interaction(
    ws: WebSocket,
    session: dict,
    text: str,
    soundscape_bytes: bytes = None,
):
    """
    Procesa una interacción de voz completa:
    1. Entiende la intención
    2. Elige template o genera con LLM
    3. Sintetiza voz con fondo musical
    4. Si aplica, redirige al usuario
    """
    if not text:
        return

    # ─── 1. Inicializar historial ───
    if "history" not in session:
        session["history"] = []
    if "interaction_count" not in session:
        session["interaction_count"] = 0
    if "tone" not in session:
        session["tone"] = "warm"

    session["interaction_count"] += 1
    session["history"].append({"role": "user", "content": text})
    session["history"] = session["history"][-10:]

    # ─── 2. Clasificar intención ───
    await _send_status(ws, "understanding")
    route = intent_router.route(text, session["history"])

    logger.info(f"Intent: {route.type}/{route.destination} (conf={route.payload.get('confidence', 0):.2f})")

    # ─── 3. Elegir tono según intención ───
    tone_map = {
        "book_appointment": "warm",
        "buy_product": "energetic",
        "go_pricing": "energetic",
        "go_services": "warm",
        "go_contact": "professional",
        "general_chat": "warm",
    }
    session["tone"] = tone_map.get(route.payload.get("intent_id", ""), "warm")
    template_engine.set_tone(session["tone"])

    # ─── 4. Generar respuesta ───
    response_text = None

    # 4a. Intentar template primero
    if route.type != "talk":
        variables = {
            "min_price": "199",
            "max_price": "1,499",
            "products_count": "10",
            "products_list": "agentes IA, ciberseguridad, monitoreo, respaldos",
        }
        response_text = template_engine.get_response(
            route.payload.get("intent_id", ""), variables
        )

    # 4b. Si no hay template o es conversación general, usar LLM
    if not response_text:
        await _send_status(ws, "thinking")
        persona = build_mystic_persona(session["tone"])
        reply = await ask_llm(persona, session["history"],
                              session_id=session.get("session_id"),
                              user_text=text)
        if reply:
            response_text = reply
        else:
            response_text = template_engine.get_response("error")

    # ─── 5. Agregar seguimiento si aplica ───
    if route.type == "talk" and session["interaction_count"] > 1:
        follow_up = template_engine.get_follow_up()
        response_text = f"{response_text} {follow_up}"

    session["history"].append({"role": "assistant", "content": response_text})

    # ─── 6. Confirmar al frontend ───
    await _send(ws, {
        "type": "conversation.item.created",
        "item": {
            "id": str(uuid.uuid4()),
            "type": "message",
            "role": "user",
            "content": [{"type": "text", "text": text}],
        },
    })

    # Enviar texto primero (para feedback visual rápido)
    await _send(ws, {
        "type": "response.output_text.delta",
        "delta": response_text,
    })

    # ─── 7. Sintetizar voz con fondo musical ───
    await _send_status(ws, "generating_voice")
    audio_mixer.set_speaking(True)

    tts_audio = await tts_engine.synthesize(response_text)
    if tts_audio:
        # Mezclar con soundscape si hay
        if soundscape_bytes:
            mixed = audio_mixer.mix_with_tts(tts_audio, soundscape_bytes, is_speaking=True)
            audio_b64 = base64.b64encode(mixed).decode()
        else:
            audio_b64 = base64.b64encode(tts_audio).decode()

        await _send(ws, {
            "type": "response.audio.delta",
            "delta": audio_b64,
            "sample_rate": 24000,
            "mime_type": "audio/mpeg",
        })

    audio_mixer.set_speaking(False)

    # ─── 8. Enviar comando de redirección si aplica ───
    if route.redirect_url:
        await _send_status(ws, "redirecting")
        msg = route.response_override or template_engine.get_response(
            route.payload.get("intent_id", ""), {}
        )
        await _send_redirect(ws, route.redirect_url, msg)

    # ─── 9. Guardar en Engram vía MCP (memoria persistente) ───
    session_id_str = session.get("session_id", "unknown")
    try:
        mcp = get_mcp_client()
        await mcp.engram_save(
            tenant_id="sonora-digital-corp",
            key=f"voice_session:{session_id_str}:{int(time.time())}",
            value=json.dumps({
                "user_text": text[:500],
                "response": response_text[:500],
                "intent": route.payload.get("intent_id", ""),
                "destination": route.destination,
                "tone": session.get("tone", "warm"),
            }, ensure_ascii=False),
            user_id="mystic",
            layer=1,
            importance=2,
            tags=f"voice,{route.payload.get('intent_id', 'chat')}",
        )
    except Exception as e:
        logger.warning(f"Engram save failed (non-critical): {e}")

    # ─── 10. Finalizar ───
    await _send(ws, {"type": "response.done"})


async def session_handler(ws: WebSocket, session_id: str):
    """Manejador principal de sesión WebSocket."""
    audio_buffer = bytearray()
    session = SESSIONS.get(session_id, {
        "created_at": time.time(),
        "session_id": session_id,
    })
    SESSIONS[session_id] = session

    vad = VoiceActivityDetector(silence_timeout_ms=800)
    soundscape_task = None
    current_soundscape = b""

    # ─── Iniciar sesión ───
    await _send(ws, {
        "type": "session.created",
        "session": {
            "id": session_id,
            "version": "2.0",
            "features": ["text", "audio", "soundscape", "redirect"],
            "soundscapes": audio_mixer.get_soundscape_list(),
            "agent": "Mystic",
        },
    })

    # Elegir soundscape según momento del día
    hour = time.localtime().tm_hour
    if 6 <= hour < 12:
        soundscape = "nature"
    elif 12 <= hour < 18:
        soundscape = "energetico"
    elif 18 <= hour < 22:
        soundscape = "calido"
    else:
        soundscape = "minimal"
    audio_mixer.set_soundscape(soundscape)

    await _send_status(ws, "listening_with_music")

    # ─── Tarea de fondo: enviar soundscape continuo ───
    async def soundscape_loop():
        nonlocal current_soundscape
        try:
            while True:
                segment = await audio_mixer.generate_soundscape_segment(3000)
                current_soundscape = segment
                b64 = base64.b64encode(segment).decode()
                await _send_soundscape(ws, b64)
                await asyncio.sleep(3)
        except asyncio.CancelledError:
            pass
        except Exception:
            pass

    soundscape_task = asyncio.create_task(soundscape_loop())

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
                    await handle_voice_interaction(ws, session, text, current_soundscape)

            elif msg_type == "input_audio_buffer.append":
                try:
                    audio_buffer.extend(base64.b64decode(msg["audio"]))
                except Exception:
                    pass

            elif msg_type == "input_audio_buffer.commit":
                if len(audio_buffer) < 640:  # Mínimo 40ms de audio
                    continue

                await _send_status(ws, "listening_with_music")
                await _send(ws, {"type": "input_audio_buffer.speech_stopped"})

                logger.info(f"[{session_id}] audio chunk: {len(audio_buffer)} bytes")
                result = await transcribe(bytes(audio_buffer), language="es")
                text = result.get("text", "").strip()
                audio_buffer.clear()

                if text:
                    logger.info(f"[{session_id}] → {text[:80]}")
                    await handle_voice_interaction(ws, session, text, current_soundscape)

            elif msg_type == "change_soundscape":
                name = msg.get("soundscape", "")
                audio_mixer.set_soundscape(name)
                await _send(ws, {
                    "type": "soundscape.changed",
                    "soundscape": name,
                    "available": audio_mixer.get_soundscape_list(),
                })

            elif msg_type == "change_tone":
                tone = msg.get("tone", "warm")
                template_engine.set_tone(tone)
                session["tone"] = tone
                await _send(ws, {"type": "tone.changed", "tone": tone})

            elif msg_type == "ping":
                await _send(ws, {"type": "pong"})

    except WebSocketDisconnect:
        logger.info(f"[{session_id}] disconnected")
    except asyncio.TimeoutError:
        logger.info(f"[{session_id}] timeout")
    finally:
        if soundscape_task:
            soundscape_task.cancel()
        SESSIONS.pop(session_id, None)


@app.websocket("/v1/chat")
async def chat_ws(ws: WebSocket):
    """WebSocket endpoint para voz en tiempo real."""
    await ws.accept()
    session_id = str(uuid.uuid4())[:8]
    logger.info(f"[{session_id}] Mystic voice session connected")
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
    """Sirve el frontend."""
    frontend_file = Path(__file__).parent / "frontend" / "mystic_voice.html"
    if frontend_file.exists():
        return HTMLResponse(frontend_file.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>Mystic Voice</h1><p>Frontend not found</p>")


@app.get("/api/soundscapes")
async def list_soundscapes():
    """Lista los soundscapes disponibles."""
    return {"soundscapes": audio_mixer.get_soundscape_list()}


@app.get("/api/health")
async def health():
    """Health check."""
    return {
        "status": "ok",
        "agent": "Mystic",
        "version": "2.0",
        "soundscape": audio_mixer.soundscape_name,
        "active_sessions": len(SESSIONS),
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("VOICE_PORT", "8900"))
    logging.basicConfig(level=logging.INFO)
    logger.info(f"Mystic Voice Realtime starting on :{port}")
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="info")
