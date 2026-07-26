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
from apps.voice_realtime.pipeline.wakeword import WakeWordDetector
from apps.voice_realtime.pipeline.monitor import SystemMonitor
from apps.voice_realtime.pipeline.session_db import SessionDB
from apps.voice_realtime.actions.browser import BrowserActions
from apps.voice_realtime.actions.code_executor import CodeExecutor
from apps.voice_realtime.actions.pdf_generator import PDFGenerator
from apps.voice_realtime.pipeline.tts import TTSEngine
from apps.voice_realtime.pipeline.audio_mixer import AudioMixer, SOUNDSCAPES
from apps.voice_realtime.intent_router import IntentRouter, RoutedAction
from apps.voice_realtime.voice_templates import VoiceTemplateEngine
from apps.voice_realtime.pipeline.engram_bridge import EngramBridge, get_engram_bridge
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
wakeword = WakeWordDetector(threshold=0.5)
browser = BrowserActions()
code_executor = CodeExecutor()
pdf_generator = PDFGenerator()
system_monitor = SystemMonitor()
session_db = SessionDB()
engram_bridge = get_engram_bridge()

app = FastAPI(title="Mystic Voice Realtime")

# ─── Mensajes de estado ───
STATUS_MESSAGES = {
    "wakeword": "🔮 Di \"Hey Jarvis\" para activarme",
    "wakeword_detected": "🎯 ¡Te escucho!",
    "listening": "🎙️ Te escucho...",
    "listening_with_music": "🎵 Te escucho...",
    "understanding": "🧠 Entendiendo...",
    "routing": "🎯 Buscando destino...",
    "thinking": "✨ Pensando...",
    "browsing": "🌐 Navegando...",
    "reading": "📖 Leyendo resultados...",
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


async def _send_browser_view(ws: WebSocket, view_url: str | None, label: str = "page"):
    """Envía una captura de pantalla del navegador al frontend."""
    if view_url:
        await _send(ws, {
            "type": "browser.view",
            "url": view_url,
            "label": label,
            "timestamp": time.time(),
        })

async def _send_redirect(ws: WebSocket, url: str, message: str):
    """Envía redirección al frontend."""
    await _send(ws, {
        "type": "redirect",
        "url": url,
        "message": message,
    })


async def ask_llm(system_prompt: str, messages: list, max_tokens: int = 300,
                  session_id: str = None, user_text: str = None,
                  memory_context: str = "") -> Optional[str]:
    full_messages = [{"role": "system", "content": system_prompt}]
    if memory_context:
        full_messages.append({"role": "system", "content": memory_context})
    full_messages.extend(messages[-6:])

    # 1. OpenRouter (tu key con credito)
    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    if api_key:
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                r = await client.post("https://openrouter.ai/api/v1/chat/completions",
                    headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                    json={"model": "openai/gpt-4o-mini", "messages": full_messages, "max_tokens": max_tokens, "temperature": 0.7})
                if r.status_code == 200:
                    return r.json()["choices"][0]["message"]["content"]
                logger.warning(f"OpenRouter {r.status_code}: {r.text[:80]}")
        except Exception as e:
            logger.warning(f"OpenRouter error: {e}")

    # 2. OpenCode API (tu suscripción, fallback)
    api_key2 = os.environ.get("OPENCODE_API_KEY", "")
    if api_key2:
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                r = await client.post("https://api.opencode.ai/v1/chat/completions", 
                    headers={"Authorization": f"Bearer {api_key2}", "Content-Type": "application/json"},
                    json={"model": "gpt-4o-mini", "messages": full_messages, "max_tokens": max_tokens, "temperature": 0.7})
                if r.status_code == 200 and r.text not in ("Not Found", ""):
                    try: return r.json().get("choices", [{}])[0].get("message", {}).get("content", "")
                    except: pass
        except Exception as e:
            logger.warning(f"OpenCode error: {e}")

    # 3. Ollama local (ultimo recurso, lento)
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post("http://127.0.0.1:11434/api/chat", json={
                "model": "qwen3:4b", "messages": full_messages, "stream": False,
                "options": {"temperature": 0.7, "num_predict": max_tokens}})
            if r.status_code == 200:
                reply = r.json().get("message", {}).get("content", "")
                if reply: return reply
    except Exception as e:
        logger.warning(f"Ollama error: {e}")

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
    session["_last_interaction_start"] = time.time()
    session["history"].append({"role": "user", "content": text})
    session["history"] = session["history"][-10:]

    # ─── 2. Clasificar intención ───
    await _send_status(ws, "understanding")
    route = intent_router.route(text, session["history"])

    logger.info(f"Intent: {route.type}/{route.destination} (conf={route.payload.get('confidence', 0):.2f})")
    
    # ─── 2b. Browser actions: navegación web por voz ───
    if route.type == "browse" and route.destination:
        await _send_status(ws, "browsing")
        result = await browser.navigate_and_read(route.destination)
        if result["status"] == "ok":
            await _send_status(ws, "reading")
            route.payload["response_text"] = f"He navegado a {result['title']}.\n\n{result['text'][:600]}"
            view = await browser.capture_view("navigate")
            await _send_browser_view(ws, view, result['title'][:40])
        else:
            route.payload["response_text"] = f"Lo siento, no pude acceder a {route.destination}."
        route.type = "talk"
    
    # ─── 2c. Búsqueda web ───
    if route.type == "search" and route.destination:
        await _send_status(ws, "browsing")
        result = await browser.search_and_read(route.destination)
        if result["status"] == "ok":
            await _send_status(ws, "reading")
            route.payload["response_text"] = result["text"][:600]
            view = await browser.capture_view("search")
            await _send_browser_view(ws, view, f'Busqueda: {route.destination[:30]}')
        else:
            route.payload["response_text"] = f"No encontré resultados para {route.destination}."
        route.type = "talk"

    # ─── 2d. System Status ───
    if route.type == "system":
        await _send_status(ws, "thinking")
        status = await system_monitor.get_status()
        if "error" in status:
            route.payload["response_text"] = "No tengo acceso al monitor del sistema en este momento."
        else:
            tts_text = await system_monitor.format_for_tts(status)
            route.payload["response_text"] = tts_text
            # Guardar status en sesión para referencia
            session["_last_system_status"] = status
        route.type = "talk"

    # ─── 2e. Click en elemento ───
    if route.type == "click":
        await _send_status(ws, "browsing")
        target = route.destination or route.payload.get("text", "")
        result = await browser.click(text=target) if target else await browser.click(selector=route.payload.get("selector", ""))
        route.payload["response_text"] = f"He hecho clic en '{target or 'el elemento'}'." if result["status"] == "ok" else f"No pude hacer clic: {result.get('error', 'error desconocido')}"
        route.type = "talk"

    # ─── 2f. Llenar formulario ───
    if route.type == "form":
        await _send_status(ws, "browsing")
        route.payload["response_text"] = "Dime qué campos quieres llenar y con qué valores. Por ejemplo: 'nombre: Juan, email: juan@mail.com'"
        route.type = "talk"

    # ─── 2g. Extraer información ───
    if route.type == "extract":
        await _send_status(ws, "reading")
        result = await browser.extract(route.payload.get("query", ""))
        if result["status"] == "ok":
            route.payload["response_text"] = f"Extraído: {result.get('data', 'sin datos')[:400]}"
        else:
            route.payload["response_text"] = f"No pude extraer información: {result.get('error', 'error desconocido')}"
        route.type = "talk"

    # ─── 2h. Captura de pantalla ───
    if route.type == "screenshot":
        await _send_status(ws, "browsing")
        result = await browser.screenshot(route.payload.get("url", "about:blank"))
        if result:
            route.payload["response_text"] = f"Captura tomada y guardada en {result}. Puedo describirte lo que veo si quieres."
        else:
            route.payload["response_text"] = "No pude tomar la captura."
        route.type = "talk"

    # ─── 2i. Ejecutar código ───
    if route.type == "code":
        await _send_status(ws, "thinking")
        route.payload["response_text"] = "Dime qué código quieres que ejecute o qué tarea necesita un script."
        route.type = "talk"

    # ─── 2j. Generar PDF ───
    if route.type == "pdf":
        await _send_status(ws, "thinking")
        route.payload["response_text"] = "Dime qué contenido quieres que incluya en el PDF. Por ejemplo: 'un reporte de ventas con...'"
        route.type = "talk"

    # ─── 2k. Email ───
    if route.type == "email":
        await _send_status(ws, "thinking")
        route.payload["response_text"] = "Para enviar un correo necesito: destinatario, asunto y mensaje. Dímelos y lo hago."
        route.type = "talk"

    # ─── 2l. Monitoreo ───
    if route.type == "monitor":
        await _send_status(ws, "thinking")
        route.payload["response_text"] = "Puedo monitorear páginas web por ti. Dime qué página quieres vigilar y qué cambios te interesan."
        route.type = "talk"

    # ─── 3. Elegir tono según intención ───
    tone_map = {
        "book_appointment": "warm",
        "buy_product": "energetic",
        "go_pricing": "energetic",
        "go_services": "warm",
        "go_contact": "professional",
        "general_chat": "warm",
        "check_system": "professional",
        "browse_web": "professional",
        "search_web": "professional",
        "fill_form": "professional",
        "click_element": "professional",
        "extract_info": "professional",
        "take_screenshot": "energetic",
        "monitor_page": "professional",
        "run_code": "energetic",
        "generate_pdf": "professional",
        "send_email": "professional",
    }
    session["tone"] = tone_map.get(route.payload.get("intent_id", ""), "warm")
    template_engine.set_tone(session["tone"])

    # ─── 4. Generar respuesta ───
    response_text = None

    # 4a. Usar respuesta pre-generada (browser action)
    if route.payload.get("response_text"):
        response_text = route.payload["response_text"]

    # 4b. Intentar template primero
    if not response_text and route.type != "talk":
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

        # Buscar memoria relevante en Engram para contexto
        memory_context = ""
        try:
            loop = asyncio.get_running_loop()
            mem_results = await loop.run_in_executor(
                None, engram_bridge.get_relevant_context, text, 5
            )
            if mem_results:
                memory_context = await loop.run_in_executor(
                    None, engram_bridge.format_memory_context, mem_results
                )
                logger.info(f"Injected {len(mem_results)} memory entries into context")
        except Exception as e:
            logger.warning(f"Memory context fetch failed (non-critical): {e}")

        reply = await ask_llm(persona, session["history"],
                              session_id=session.get("session_id"),
                              user_text=text,
                              memory_context=memory_context)
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
        # Guardar como archivo temporal y enviar URL
        sid = session.get("session_id", "unknown")
        audio_file = Path(f"/tmp/mystic-audio-{sid}-{int(time.time()*1000)}.mp3")
        audio_file.write_bytes(tts_audio)
        audio_url = f"/api/audio/{audio_file.name}"

        await _send(ws, {
            "type": "response.audio.url",
            "url": audio_url,
            "duration_s": len(tts_audio) / 48000,  # aprox
        })

    audio_mixer.set_speaking(False)

    # ─── 8. Enviar comando de redirección si aplica ───
    if route.redirect_url:
        await _send_status(ws, "redirecting")
        msg = route.response_override or template_engine.get_response(
            route.payload.get("intent_id", ""), {}
        )
        await _send_redirect(ws, route.redirect_url, msg)

    # ─── 9. Guardar interacción en SQLite ───
    session_id_str = session.get("session_id", "unknown")
    start_time = session.get("_last_interaction_start", time.time())
    latency_ms = int((time.time() - start_time) * 1000)
    try:
        loop = asyncio.get_running_loop()
        # Primero guardar sesión (para que exista el FK), luego interacciones
        user_id = session.get("user_id", "")
        await loop.run_in_executor(None, session_db.save_session,
            session_id_str, session.get("history", []),
            {"tone": session.get("tone", "warm"), "interactions": session.get("interaction_count", 0)},
            user_id)
        await loop.run_in_executor(None, session_db.add_interaction,
            session_id_str, "user", text,
            route.payload.get("intent_id", ""), latency_ms)
        if response_text:
            await loop.run_in_executor(None, session_db.add_interaction,
                session_id_str, "assistant", response_text,
                route.payload.get("intent_id", ""), None)
    except Exception as e:
        logger.warning(f"Session DB save failed (non-critical): {e}")

    # ─── 10. Guardar en Engram directo (memoria persistente, sin MCP) ───
    try:
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(
            None, engram_bridge.save_interaction,
            text, response_text,
            route.payload.get("intent_id", "chat"),
            route.destination,
            session.get("tone", "warm"),
            session_id_str,
            "medium",
            f"voice,{route.payload.get('intent_id', 'chat')}",
        )
    except Exception as e:
        logger.warning(f"Engram save failed (non-critical): {e}")

    # Fallback: intentar MCP si está disponible (no crítico)
    try:
        mcp = get_mcp_client()
        await mcp.engram_save(
            tenant_id="sonora-digital-corp",
            key=f"voice_session:{session_id_str}:{int(time.time())}",
            value=json.dumps({
                "user_text": text[:500],
                "response": response_text[:500] if response_text else "",
                "intent": route.payload.get("intent_id", ""),
                "destination": route.destination,
                "tone": session.get("tone", "warm"),
            }, ensure_ascii=False),
            user_id="mystic",
            layer=1,
            importance=2,
            tags=f"voice,{route.payload.get('intent_id', 'chat')}",
        )
    except Exception:
        pass  # MCP no disponible — el guardado directo ya se hizo

    # ─── 11. Finalizar ───
    await _send(ws, {"type": "response.done"})


async def session_handler(ws: WebSocket, session_id: str):
    """Manejador principal de sesión WebSocket."""
    audio_buffer = bytearray()
    session = SESSIONS.get(session_id, {
        "created_at": time.time(),
        "session_id": session_id,
        "mode": "wakeword",
        "wakeword_triggered": False,
    })
    session["ws"] = ws  # Guardar ref para proactive monitor
    SESSIONS[session_id] = session

    vad = VoiceActivityDetector(silence_timeout_ms=800)
    soundscape_task = None
    current_soundscape = b""

    # ─── Cargar historial desde SQLite ───
    loop = asyncio.get_running_loop()
    saved = await loop.run_in_executor(None, session_db.get_session, session_id)
    if saved and saved.get("history"):
        try:
            history = json.loads(saved["history"]) if isinstance(saved["history"], str) else saved["history"]
            session["history"] = history[-10:]
            session["interaction_count"] = len(history)
            logger.info(f"[{session_id}] Restored {len(history)} messages from DB")
        except (json.JSONDecodeError, TypeError) as e:
            logger.warning(f"[{session_id}] History parse error: {e}")
            session["history"] = []
    else:
        session["history"] = []

    # ─── Iniciar sesión ───
    await _send(ws, {
        "type": "session.created",
        "session": {
            "id": session_id,
            "version": "2.0",
            "features": ["text", "audio", "soundscape", "redirect", "system", "memory"],
            "soundscapes": audio_mixer.get_soundscape_list(),
            "agent": "Mystic",
            "history_restored": len(session.get("history", [])),
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

    await _send_status(ws, "wakeword")

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
                    chunk = base64.b64decode(msg["audio"])
                    audio_buffer.extend(chunk)
                    
                    # Wake word detection en modo wakeword
                    if session.get("mode") == "wakeword" and not session.get("wakeword_triggered"):
                        result = wakeword.process_chunk(chunk)
                        if result and result["detected"]:
                            session["wakeword_triggered"] = True
                            session["mode"] = "listening"
                            audio_buffer.clear()
                            wakeword.reset()
                            await _send_status(ws, "wakeword_detected")
                            logger.info(f"[{session_id}] 🔮 Wake word: {result['keyword']} ({result['score']:.2f})")
                            await _send(ws, {
                                "type": "wakeword.detected",
                                "keyword": result["keyword"],
                                "score": result["score"],
                            })
                except Exception as e:
                    logger.warning(f"Audio error: {e}")

            elif msg_type == "input_audio_buffer.commit":
                # Si modo wakeword y no activado, ignorar
                if session.get("mode") == "wakeword" and not session.get("wakeword_triggered"):
                    audio_buffer.clear()
                    continue
                
                # Resetear wakeword para próximo ciclo
                was_wakeword = session.get("wakeword_triggered", False)
                session["wakeword_triggered"] = False
                session["mode"] = "wakeword"
                
                if len(audio_buffer) < 640:
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

            elif msg_type == "identify":
                user_id = msg.get("user_id", "")
                if user_id:
                    session["user_id"] = user_id
                    # Cargar historial de TODAS las sesiones anteriores de este usuario
                    try:
                        loop = asyncio.get_running_loop()
                        past = await loop.run_in_executor(None, session_db.get_user_interactions, user_id, 20)
                        if past:
                            restored = [{"role": p["role"], "content": p["content"]} for p in past]
                            session["history"] = restored[-10:]
                            session["interaction_count"] = len(restored)
                            await _send(ws, {
                                "type": "memory.restored",
                                "count": len(restored),
                                "summary": f"Recuerdo nuestras {len(restored)} interacciones anteriores"
                            })
                            logger.info(f"[{session_id}] Restored {len(restored)} messages for user {user_id[:8]}...")
                    except Exception as e:
                        logger.warning(f"Memory restore error: {e}")

    except WebSocketDisconnect:
        logger.info(f"[{session_id}] disconnected")
    except asyncio.TimeoutError:
        logger.info(f"[{session_id}] timeout")
    finally:
        if soundscape_task:
            soundscape_task.cancel()
        # ─── Guardar sesión en SQLite ───
        try:
            history = session.get("history", [])
            if history:
                loop.run_in_executor(None, session_db.save_session,
                    session_id, history,
                    {"tone": session.get("tone", "warm"), "interactions": len(history)},
                    session.get("user_id", "")
                )
        except Exception as e:
            logger.warning(f"[{session_id}] Save error: {e}")

        # ─── Guardar resumen de sesión en Engram ───
        try:
            history = session.get("history", [])
            if history:
                loop.run_in_executor(None, engram_bridge.save_session_summary,
                    session_id, history,
                    session.get("tone", "warm"),
                    session.get("interaction_count", 0),
                )
        except Exception as e:
            logger.warning(f"[{session_id}] Engram session save error: {e}")

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
    """Sirve el frontend (Cosmic 3D si existe, fallback al clásico)."""
    frontend_cosmic = Path(__file__).parent / "frontend" / "mystic_cosmic.html"
    frontend_3d = Path(__file__).parent / "frontend" / "mystic_3d.html"
    frontend_classic = Path(__file__).parent / "frontend" / "mystic_voice.html"
    if frontend_cosmic.exists():
        return HTMLResponse(frontend_cosmic.read_text(encoding="utf-8"))
    if frontend_3d.exists():
        return HTMLResponse(frontend_3d.read_text(encoding="utf-8"))
    if frontend_classic.exists():
        return HTMLResponse(frontend_classic.read_text(encoding="utf-8"))
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


@app.get("/api/system")
async def system_status():
    """Estado del sistema VPS (CPU, RAM, disco, uptime)."""
    status = await system_monitor.get_status()
    return status


@app.get("/manifest.json")
async def manifest():
    """PWA manifest."""
    from fastapi.responses import FileResponse
    manifest_path = Path(__file__).parent / "frontend" / "manifest.json"
    if manifest_path.exists():
        return FileResponse(str(manifest_path), media_type="application/json")
    return HTMLResponse("{}")


@app.get("/sw.js")
async def service_worker():
    """Service worker para PWA."""
    from fastapi.responses import FileResponse
    sw_path = Path(__file__).parent / "frontend" / "sw.js"
    if sw_path.exists():
        return FileResponse(str(sw_path), media_type="application/javascript")
    return HTMLResponse("")


@app.get("/icon.svg")
@app.get("/icon-192.png")
@app.get("/icon-512.png")
async def pwa_icon():
    """Icono PWA."""
    from fastapi.responses import FileResponse
    icon_path = Path(__file__).parent / "frontend" / "icon.svg"
    if icon_path.exists():
        return FileResponse(str(icon_path), media_type="image/svg+xml")
    return HTMLResponse("")


# ─── Inicializar DB al arrancar ───
@app.on_event("startup")
async def startup():
    """Inicializa componentes al arrancar."""
    # init_db ya se llama en el constructor de SessionDB
    logger.info(f"Session DB ready at {session_db.db_path}")
    logger.info("Session DB initialized ✓")
    # Log system status at startup
    status = await system_monitor.get_status()
    if "error" not in status:
        logger.info(f"System: CPU {status.get('cpu_percent', '?')}% | "
                    f"RAM {status.get('ram_percent', '?')}% | "
                    f"Disk {status.get('disk_percent', '?')}%")
    # Start proactive monitor
    asyncio.create_task(_proactive_monitor_loop())
    logger.info("Proactive monitor started ✓")
    # Limpiar audios temporales viejos
    import glob
    for f in glob.glob("/tmp/mystic-audio-*.mp3"):
        try: os.remove(f)
        except: pass


async def _proactive_monitor_loop():
    """Monitoreo proactivo cada 30s. Notifica a sesiones activas si CPU/RAM alta."""
    while True:
        try:
            await asyncio.sleep(30)
            alert = await system_monitor.get_cpu_alert()
            if alert and SESSIONS:
                msg = {
                    "type": "proactive_alert",
                    "alert": alert,
                    "message": f"⚠️ {alert.get('message', 'Alerta del sistema')}",
                }
                # Enviar a todas las sesiones activas
                for sid, session in SESSIONS.items():
                    if session.get("ws"):
                        try:
                            await _send(session["ws"], msg)
                        except Exception:
                            pass
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.warning(f"Proactive monitor error: {e}")


@app.get("/api/audio/{filename}")
async def serve_audio(filename: str):
    """Sirve archivos de audio temporales."""
    from fastapi.responses import FileResponse
    import re
    if not re.match(r"^mystic-audio-.+\.mp3$", filename):
        return HTMLResponse("Invalid filename", status_code=400)
    audio_path = Path(f"/tmp/{filename}")
    if audio_path.exists():
        return FileResponse(str(audio_path), media_type="audio/mp3")
    return HTMLResponse("Audio not found", status_code=404)


@app.get("/api/browser-view/{filename}")
async def serve_browser_view(filename: str):
    """Sirve capturas de pantalla del navegador Playwright."""
    from fastapi.responses import FileResponse
    import re
    if not re.match(r"^browser-view-.+\.png$", filename):
        return HTMLResponse("Invalid", status_code=400)
    path = Path(f"/tmp/{filename}")
    if path.exists():
        return FileResponse(str(path), media_type="image/png")
    return HTMLResponse("Not found", status_code=404)


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("VOICE_PORT", "8900"))
    logging.basicConfig(level=logging.INFO)
    logger.info(f"Mystic Voice Realtime starting on :{port}")
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="info")
