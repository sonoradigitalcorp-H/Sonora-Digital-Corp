"""Twilio Voice Bridge — Llamadas telefónicas con Kokoro TTS + Whisper STT + deepseek.

Conecta la red telefónica (PSTN) con el pipeline de voz de Mystic.
Permite:
  - Recibir llamadas entrantes → Mystic contesta con voz natural
  - Hacer llamadas salientes a leads → el agente de ventas llama
  - Streaming de audio bidireccional vía Media Streams
  - Integración con el Grimoire para iniciar llamadas desde el dashboard

Arquitectura:
  Twilio (PSTN) ↔ WebSocket Media Streams ↔ Whisper STT → deepseek → Kokoro TTS

Uso:
  uvicorn apps.twilio_voice.server:app --host 127.0.0.1 --port 8700
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
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from twilio.twiml.voice_response import VoiceResponse, Connect, Stream

log = logging.getLogger("twilio-voice")

# ─── Config ───
REPO = Path(__file__).resolve().parent.parent
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN", "")
TWILIO_PHONE_NUMBER = os.environ.get("TWILIO_PHONE_NUMBER", "+526621072254")
BASE_URL = os.environ.get("BASE_URL", "https://voice.sonoradigitalcorp.com")

# ─── FastAPI App ───
app = FastAPI(title="Twilio Voice Bridge — Mystic Calls")

# Active calls tracking
ACTIVE_CALLS: dict[str, dict] = {}


# ═══════════════════════════════════════════════════════════
#  1. INCOMING CALL — TwiML webhook
# ═══════════════════════════════════════════════════════════

@app.post("/twilio/incoming")
async def incoming_call(request: Request):
    """Twilio webhook for incoming calls.
    
    Returns TwiML that connects to Media Streams WebSocket.
    Mystic answers the phone with Kokoro TTS.
    """
    form = await request.form()
    from_number = form.get("From", "")
    to_number = form.get("To", "")
    call_sid = form.get("CallSid", str(uuid.uuid4()))
    
    log.info(f"📞 Incoming call from {from_number} to {to_number} (SID: {call_sid})")
    
    # Build TwiML response
    response = VoiceResponse()
    
    # Greeting with Kokoro (via Media Streams)
    connect = Connect()
    stream = Stream(
        url=f"wss://{BASE_URL}/twilio/media-stream/{call_sid}",
        track="both_audio"  # Receive and send audio
    )
    connect.append(stream)
    response.append(connect)
    
    # Store call info
    ACTIVE_CALLS[call_sid] = {
        "type": "inbound",
        "from": from_number,
        "to": to_number,
        "status": "connected",
        "started_at": time.time(),
        "transcript": [],
    }
    
    return HTMLResponse(str(response), media_type="application/xml")


# ═══════════════════════════════════════════════════════════
#  2. OUTBOUND CALL — API endpoint
# ═══════════════════════════════════════════════════════════

@app.post("/twilio/call/outbound")
async def make_outbound_call(request: Request):
    """Initiate an outbound call to a lead.
    
    César or any partner can call leads from the Grimoire.
    Mystic speaks with Kokoro TTS in real-time.
    
    Body: {
        "to": "+526621072254",
        "from": "+526621072254",
        "agent": "sales-hunter",
        "lead_name": "Juan Pérez",
        "context": "Llamada de seguimiento de propuesta"
    }
    """
    body = await request.json()
    to_number = body.get("to", "")
    from_number = body.get("from", TWILIO_PHONE_NUMBER)
    agent = body.get("agent", "sales-hunter")
    lead_name = body.get("lead_name", "")
    context = body.get("context", "")
    
    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
        return JSONResponse(
            content={"error": "Twilio not configured", "call_sid": None},
            status_code=501,
        )
    
    # Twilio API URL
    twilio_url = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Calls.json"
    
    # The webhook that Twilio will request when the call connects
    status_callback = f"{BASE_URL}/twilio/status"
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            twilio_url,
            data={
                "To": to_number,
                "From": from_number,
                "Url": f"{BASE_URL}/twilio/outbound-twiml?agent={agent}&lead_name={lead_name}&context={context}",
                "StatusCallback": status_callback,
                "StatusCallbackEvent": ["initiated", "ringing", "answered", "completed"],
                "Timeout": 30,
            },
            auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN),
        )
        
        if response.status_code == 201:
            data = response.json()
            call_sid = data.get("sid", "")
            log.info(f"📞 Outbound call initiated: {call_sid} → {to_number}")
            
            ACTIVE_CALLS[call_sid] = {
                "type": "outbound",
                "to": to_number,
                "from": from_number,
                "agent": agent,
                "lead_name": lead_name,
                "context": context,
                "status": "initiated",
                "started_at": time.time(),
                "transcript": [],
            }
            
            return JSONResponse(content={
                "success": True,
                "call_sid": call_sid,
                "status": "initiated",
                "to": to_number,
            })
        else:
            log.error(f"Twilio API error: {response.status_code} {response.text[:200]}")
            return JSONResponse(
                content={"error": "Failed to initiate call", "detail": response.text[:200]},
                status_code=500,
            )


@app.post("/twilio/outbound-twiml")
async def outbound_twiml(request: Request):
    """TwiML for outbound calls — connects to Media Streams."""
    agent = request.query_params.get("agent", "sales-hunter")
    lead_name = request.query_params.get("lead_name", "")
    context = request.query_params.get("context", "")
    
    call_sid = str(uuid.uuid4())  # Will be replaced by actual SID from Twilio
    
    response = VoiceResponse()
    
    # Optional: initial greeting before connecting stream
    # (Kokoro will handle all speech via Media Streams)
    
    connect = Connect()
    stream = Stream(
        url=f"wss://{BASE_URL}/twilio/media-stream/{call_sid}?agent={agent}&lead_name={lead_name}&context={context}",
        track="both_audio",
    )
    connect.append(stream)
    response.append(connect)
    
    return HTMLResponse(str(response), media_type="application/xml")


# ═══════════════════════════════════════════════════════════
#  3. MEDIA STREAMS — WebSocket bidireccional
# ═══════════════════════════════════════════════════════════

@app.websocket("/twilio/media-stream/{call_sid}")
async def media_stream(ws: WebSocket, call_sid: str):
    """WebSocket para streaming de audio con Twilio Media Streams.
    
    Flujo:
      1. Twilio envía audio (PCMU/8000Hz) → Whisper STT
      2. Texto → deepseek genera respuesta
      3. Kokoro TTS sintetiza audio → Twilio lo reproduce
    """
    await ws.accept()
    log.info(f"🔊 Media Stream connected: {call_sid}")
    
    # Get call context
    call_info = ACTIVE_CALLS.get(call_sid, {
        "type": "unknown",
        "transcript": [],
    })
    
    # Pipeline state
    audio_buffer = bytearray()
    is_speaking = False
    stream_sid = None
    
    try:
        while True:
            message = await ws.receive_text()
            data = json.loads(message)
            event = data.get("event", "")
            
            if event == "media":
                # Audio chunk from Twilio (PCMU/8000Hz, base64 encoded)
                payload = data.get("media", {})
                payload = data.get("media", {})
                if not payload:
                    continue
                    
                audio_chunk = base64.b64decode(payload.get("payload", ""))
                stream_sid = data.get("streamSid", stream_sid)
                
                # Store stream SID for sending audio back
                if stream_sid:
                    call_info["stream_sid"] = stream_sid
                
                # Accumulate audio for STT
                audio_buffer.extend(audio_chunk)
                
                # Process when we have enough audio (~300ms at 8000Hz)
                if len(audio_buffer) >= 2400:  # 300ms * 8 samples/ms
                    text = await transcribe_audio(bytes(audio_buffer))
                    audio_buffer.clear()
                    
                    if text and text.strip():
                        call_info["transcript"].append({"role": "user", "text": text})
                        log.info(f"📝 User: {text}")
                        
                        # Generate response
                        response_text = await generate_response(text, call_info)
                        
                        if response_text:
                            log.info(f"🤖 Mystic: {response_text}")
                            call_info["transcript"].append({"role": "assistant", "text": response_text})
                            
                            # Synthesize with Kokoro and send back to Twilio
                            await synthesize_and_send(ws, stream_sid, response_text)
            
            elif event == "start":
                # Call started
                stream_sid = data.get("streamSid", "")
                call_sid = data.get("callSid", call_sid)
                log.info(f"📞 Call started: {call_sid} (stream: {stream_sid})")
                
                # Initial greeting
                greeting = "Hola, soy Mystic, tu asistente de Sonora Digital Corp. ¿En qué puedo ayudarte?"
                await synthesize_and_send(ws, stream_sid, greeting)
                
            elif event == "stop":
                log.info(f"📞 Call ended: {call_sid}")
                break
    
    except WebSocketDisconnect:
        log.info(f"🔌 WebSocket disconnected: {call_sid}")
    except Exception as e:
        log.error(f"❌ Media Stream error: {e}")
    finally:
        # Cleanup
        if call_sid in ACTIVE_CALLS:
            ACTIVE_CALLS[call_sid]["status"] = "completed"
            ACTIVE_CALLS[call_sid]["ended_at"] = time.time()


# ═══════════════════════════════════════════════════════════
#  4. CALL STATUS WEBHOOK
# ═══════════════════════════════════════════════════════════

@app.post("/twilio/status")
async def call_status(request: Request):
    """Twilio status callback for call state changes."""
    form = await request.form()
    call_sid = form.get("CallSid", "")
    call_status = form.get("CallStatus", "")
    
    if call_sid in ACTIVE_CALLS:
        ACTIVE_CALLS[call_sid]["status"] = call_status
    
    log.info(f"📊 Call {call_sid}: {call_status}")
    return PlainTextResponse("OK")


# ═══════════════════════════════════════════════════════════
#  5. API ENDPOINTS
# ═══════════════════════════════════════════════════════════

@app.get("/twilio/calls")
async def list_calls():
    """List all active and recent calls."""
    return {
        "active_calls": {
            sid: info for sid, info in ACTIVE_CALLS.items()
            if info.get("status") not in ("completed", "failed")
        },
        "total_calls": len(ACTIVE_CALLS),
    }


@app.get("/twilio/calls/{call_sid}")
async def get_call(call_sid: str):
    """Get details of a specific call."""
    call = ACTIVE_CALLS.get(call_sid)
    if not call:
        return JSONResponse(content={"error": "Call not found"}, status_code=404)
    return call


@app.get("/twilio/health")
async def health():
    """Health check for the Twilio bridge."""
    return {
        "status": "ok",
        "twilio_configured": bool(TWILIO_ACCOUNT_SID),
        "active_calls": len([c for c in ACTIVE_CALLS.values() if c.get("status") not in ("completed", "failed")]),
        "total_calls_tracked": len(ACTIVE_CALLS),
    }


# ═══════════════════════════════════════════════════════════
#  HELPERS — STT + LLM + TTS
# ═══════════════════════════════════════════════════════════

async def transcribe_audio(audio_bytes: bytes) -> str:
    """Transcribe audio chunk using Whisper STT (local, $0)."""
    try:
        import numpy as np
        import whisper
        
        model = whisper.load_model("base")
        # Convert PCMU (8000Hz, μ-law) to PCM16 (16000Hz, linear)
        # This is a simplified conversion
        samples = np.frombuffer(audio_bytes, dtype=np.uint8).astype(np.float32)
        samples = (samples - 128) / 128.0  # μ-law to linear approximation
        
        result = model.transcribe(samples, language="es", fp16=False)
        return result.get("text", "").strip()
    except Exception as e:
        log.warning(f"STT error: {e}")
        return ""


async def generate_response(text: str, call_info: dict) -> Optional[str]:
    """Generate response using deepseek or local model."""
    from core.router_inteligente import get_router
    
    router = get_router()
    route = router.route("complex_reasoning")
    
    if route.provider == "local":
        # Use llama3.2:3b for simple responses
        try:
            import ollama
            response = ollama.chat(model="llama3.2:3b", messages=[
                {"role": "system", "content": "Eres Mystic, asistente de Sonora Digital Corp. Responde de forma natural y conversacional por teléfono. Máximo 2 oraciones."},
                {"role": "user", "content": text},
            ])
            return response.get("message", {}).get("content", "")
        except Exception:
            pass
    
    # Use deepseek via OpenRouter
    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    if not api_key:
        return "Lo siento, tengo problemas para procesar tu solicitud. ¿Puedes repetirlo?"
    
    system_prompt = (
        "Eres Mystic, asistente de IA de Sonora Digital Corp. "
        "Estás en una llamada telefónica. Habla de forma natural, calmada y profesional. "
        "Máximo 2 oraciones por respuesta. Escucha más de lo que hablas. "
        "En español."
    )
    if call_info.get("lead_name"):
        system_prompt += f" Estás hablando con {call_info['lead_name']}."
    if call_info.get("context"):
        system_prompt += f" Contexto: {call_info['context']}"
    
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={
                    "model": "deepseek/deepseek-v4-flash",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        *[{"role": "user" if m["role"] == "user" else "assistant", "content": m["text"]}
                          for m in call_info.get("transcript", [])[-4:]],
                    ],
                    "max_tokens": 150,
                    "temperature": 0.7,
                },
            )
            if r.status_code == 200:
                return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        log.error(f"LLM error: {e}")
    
    return None


async def synthesize_and_send(ws: WebSocket, stream_sid: str, text: str):
    """Synthesize text with Kokoro TTS and send audio chunks to Twilio."""
    try:
        from apps.voice_realtime.pipeline.tts import TTSEngine
        
        tts = TTSEngine(provider="kokoro", voice="em_alex")
        audio_bytes = await tts.synthesize(text)
        
        if not audio_bytes:
            log.warning("Kokoro TTS returned no audio")
            return
        
        # Kokoro outputs WAV 24kHz. Twilio needs PCMU 8000Hz.
        # Convert using ffmpeg or sox if available
        import subprocess
        import tempfile
        
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f_in:
            f_in.write(audio_bytes)
            wav_path = f_in.name
        
        with tempfile.NamedTemporaryFile(suffix=".ulaw", delete=False) as f_out:
            ulaw_path = f_out.name
        
        # Convert 24kHz WAV → 8kHz μ-law for Twilio
        subprocess.run([
            "ffmpeg", "-y", "-i", wav_path,
            "-ar", "8000", "-ac", "1", "-c:a", "pcm_mulaw",
            "-f", "mulaw", ulaw_path,
        ], capture_output=True, check=True)
        
        with open(ulaw_path, "rb") as f:
            ulaw_data = f.read()
        
        os.unlink(wav_path)
        os.unlink(ulaw_path)
        
        # Send audio in chunks to Twilio
        chunk_size = 1600  # 200ms at 8000Hz
        for i in range(0, len(ulaw_data), chunk_size):
            chunk = ulaw_data[i:i + chunk_size]
            encoded = base64.b64encode(chunk).decode()
            
            await ws.send_text(json.dumps({
                "event": "media",
                "streamSid": stream_sid,
                "media": {
                    "payload": encoded,
                },
            }))
            
            # Small delay to simulate natural speech timing
            await asyncio.sleep(0.02)
        
        # Mark end of speech
        await ws.send_text(json.dumps({
            "event": "mark",
            "streamSid": stream_sid,
            "mark": {"name": "end_of_speech"},
        }))
        
        log.info(f"🔊 Sent {len(ulaw_data)} bytes of Kokoro TTS audio")
        
    except ImportError:
        log.warning("Kokoro TTS not available, cannot synthesize")
    except FileNotFoundError:
        log.warning("ffmpeg not found, cannot convert audio format")
    except Exception as e:
        log.error(f"TTS send error: {e}")


# ═══════════════════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("TWILIO_PORT", "8700"))
    logging.basicConfig(level=logging.INFO)
    log.info(f"📞 Twilio Voice Bridge starting on :{port}")
    log.info(f"🔌 Twilio configured: {bool(TWILIO_ACCOUNT_SID)}")
    log.info(f"📱 Phone: {TWILIO_PHONE_NUMBER}")
    log.info(f"🌐 Base URL: {BASE_URL}")
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="info")
