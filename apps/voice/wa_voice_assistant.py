"""
WhatsApp Voice Assistant — Pipeline Local Completo
STT (faster-whisper) → LLM (Ollama llama3.2) → TTS (edge-tts) → WhatsApp (wacli)

100% local. Sin APIs externas.
"""

import json
import logging
import multiprocessing
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Optional

# Fix Python 3.14 multiprocessing spawn
multiprocessing.set_start_method('fork', force=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s %(message)s",
)
log = logging.getLogger("wa-voice-assistant")

# ========== CONFIG ==========
WACLI_BIN = "/usr/local/bin/wacli"
WACLI_STORE = os.path.expanduser("~/.wacli")
OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3.2:3b"
WHISPER_MODEL = "small"  # small, medium, large
TTS_VOICE = "es-MX-DaliaNeural"
POLL_INTERVAL = 3  # segundos entre revisiones

# Contacto autorizado para responder (tu número)
AUTHORIZED_JIDS = {
    "5216623538272@s.whatsapp.net",  # Luis Daniel
}

# ========== STT ==========
_stt_model = None

def load_stt_model():
    global _stt_model
    if _stt_model is None:
        from faster_whisper import WhisperModel
        log.info(f"Cargando Whisper model: {WHISPER_MODEL} (CPU, int8)")
        _stt_model = WhisperModel(WHISPER_MODEL, device="cpu", compute_type="int8")
        log.info("Whisper model cargado ✓")
    return _stt_model

def transcribe_audio(audio_path: str) -> str:
    """Transcribe audio a texto con faster-whisper."""
    model = load_stt_model()
    segments, info = model.transcribe(audio_path, language="es", beam_size=2)
    text = " ".join(s.text.strip() for s in segments).strip()
    lang_conf = info.language_probability
    log.info(f"STT: {lang_conf:.0%} español → '{text[:80]}...'")
    return text

# ========== LLM (Ollama) ==========
def ask_ollama(prompt: str, system: str = "", max_tokens: int = 500) -> str:
    """Consulta Ollama local."""
    import urllib.request

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    body = json.dumps({
        "model": OLLAMA_MODEL,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": 0.7,
            "num_predict": max_tokens,
        }
    }).encode()

    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/chat",
        data=body,
        headers={"Content-Type": "application/json"},
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read())
            return data.get("message", {}).get("content", "").strip()
    except Exception as e:
        log.error(f"Ollama error: {e}")
        return ""

# ========== TTS ==========
def text_to_speech(text: str, output_path: str) -> Optional[str]:
    """Genera audio desde texto con edge-tts, convierte a OGG Opus."""
    import asyncio
    import edge_tts

    async def _gen():
        mp3_tmp = output_path.replace(".ogg", ".mp3")
        communicate = edge_tts.Communicate(text, TTS_VOICE)
        await communicate.save(mp3_tmp)

        # Convertir a OGG Opus para WhatsApp PTT
        subprocess.run([
            "ffmpeg", "-y", "-i", mp3_tmp,
            "-c:a", "libopus", "-b:a", "64k",
            "-application", "voip", output_path
        ], check=True, capture_output=True)

        os.remove(mp3_tmp)  # limpiar
        return output_path

    try:
        return asyncio.run(_gen())
    except Exception as e:
        log.error(f"TTS error: {e}")
        return None

# ========== WACLI ==========
def _run_wacli(args: list, timeout: int = 30) -> tuple[bool, str]:
    cmd = [WACLI_BIN] + args + ["--store", WACLI_STORE, "--json"]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        out = r.stdout.strip()
        if out:
            data = json.loads(out)
            return data.get("success", False), out
        return False, r.stderr.strip()
    except Exception as e:
        return False, str(e)

def send_text(jid: str, message: str) -> bool:
    ok, _ = _run_wacli([
        "send", "text", "--to", jid, "--message", message
    ], timeout=15)
    if ok:
        log.info(f"Texto enviado a {jid}")
    return ok

def send_audio_ptt(jid: str, audio_path: str) -> bool:
    ok, _ = _run_wacli([
        "send", "file", "--to", jid, "--file", audio_path, "--ptt"
    ], timeout=30)
    if ok:
        log.info(f"Audio PTT enviado a {jid}")
    return ok

def get_messages(limit: int = 5) -> list[dict]:
    """Obtiene mensajes recientes, retorna solo no-leídos."""
    ok, out = _run_wacli(["messages", "list", "--limit", str(limit)], timeout=15)
    if not ok:
        return []
    try:
        data = json.loads(out)
        msgs = data.get("data", {}).get("messages", [])
        return [m for m in msgs if isinstance(m, dict)]
    except:
        return []

def download_media(msg: dict, dest: str) -> bool:
    """Descarga media de un mensaje (audio, imagen, etc)."""
    msg_id = msg.get("MsgID", msg.get("id", ""))
    if not msg_id:
        return False
    ok, _ = _run_wacli([
        "media", "download", "--id", msg_id, "--output", dest
    ], timeout=30)
    return ok

# ========== PROCESADOR ==========
_processed_ids = set()

SYSTEM_PROMPT = (
    "Eres Mystic, asistente de Sonora Digital Corp. "
    "Propiedad de Luis Daniel. Responde en español, "
    "cálido, directo y útil. Sé breve. "
    "No menciones que eres un modelo de IA."
)

def process_message(msg: dict) -> bool:
    """Procesa un mensaje entrante (texto o audio)."""
    msg_id = msg.get("MsgID", msg.get("id", msg.get("msg_id", "")))
    if not msg_id or msg_id in _processed_ids:
        return False
    _processed_ids.add(msg_id)

    jid = msg.get("ChatJID", msg.get("chatJid", msg.get("ChatJid", "")))
    if not jid or jid.endswith("@g.us"):
        return False  # ignorar grupos

    # Nota: FromMe=True es NORMAL porque wacli está vinculado a la cuenta del usuario.
    # Procesamos TODOS los mensajes del chat personal (del usuario).

    msg_type = msg.get("MediaType", msg.get("type", "")).lower()
    text = msg.get("Text", msg.get("text", msg.get("body", ""))).strip()

    log.info(f"📨 {jid} | tipo: {msg_type} | texto: '{text[:60]}'")

    # ---- CASO 1: Texto directo ----
    if text and msg_type != "audio":
        return handle_text(jid, text)

    # ---- CASO 2: Audio / nota de voz ----
    if msg_type == "audio":
        return handle_audio(jid, msg)

    return False

def handle_text(jid: str, text: str) -> bool:
    """Procesa texto → LLM → responde texto + audio."""
    log.info(f"🧠 Procesando texto: '{text[:80]}'")

    # Enviar ack inmediato
    send_text(jid, "🎙️ Procesando...")

    # LLM local
    response = ask_ollama(text, SYSTEM_PROMPT)
    if not response:
        send_text(jid, "⚠️ No pude procesar tu mensaje. Intenta de nuevo.")
        return False

    # Responder texto
    send_text(jid, response)
    time.sleep(1)

    # Responder audio
    audio_path = f"/tmp/wa-response-{int(time.time())}.ogg"
    ogg = text_to_speech(response, audio_path)
    if ogg and os.path.exists(ogg):
        send_audio_ptt(jid, ogg)
        os.remove(ogg)

    return True

def handle_audio(jid: str, msg: dict) -> bool:
    """Procesa audio → STT → LLM → responde audio."""
    log.info(f"🎤 Procesando audio...")

    # Enviar ack
    send_text(jid, "🎧 Escuchando...")

    # Descargar audio
    audio_path = f"/tmp/wa-incoming-{int(time.time())}.ogg"
    if not download_media(msg, audio_path):
        send_text(jid, "⚠️ No pude descargar tu audio.")
        return False

    if not os.path.exists(audio_path) or os.path.getsize(audio_path) < 100:
        send_text(jid, "⚠️ El audio está vacío o corrupto.")
        return False

    # STT
    text = transcribe_audio(audio_path)
    os.remove(audio_path)  # limpiar

    if not text:
        send_text(jid, "⚠️ No pude entender tu audio. ¿Puedes repetirlo?")
        return False

    log.info(f"📝 Transcrito: '{text}'")

    # LLM local
    response = ask_ollama(text, SYSTEM_PROMPT)
    if not response:
        send_text(jid, "⚠️ Error procesando tu mensaje.")
        return False

    # Responder audio
    audio_out = f"/tmp/wa-response-{int(time.time())}.ogg"
    ogg = text_to_speech(response, audio_out)
    if ogg and os.path.exists(ogg):
        send_audio_ptt(jid, ogg)
        time.sleep(0.5)
        send_text(jid, f"📝 Entendí: \"{text[:100]}\"")
        os.remove(ogg)

    return True

# ========== LOOP PRINCIPAL ==========
def listen_loop():
    log.info("=" * 50)
    log.info("🎙️ WhatsApp Voice Assistant — Pipeline Local")
    log.info(f"   STT: faster-whisper ({WHISPER_MODEL})")
    log.info(f"   LLM: Ollama ({OLLAMA_MODEL})")
    log.info(f"   TTS: edge-tts ({TTS_VOICE})")
    log.info(f"   WA:  wacli → {WACLI_STORE}")
    log.info("=" * 50)

    # Cargar modelo STT al inicio
    load_stt_model()

    # Verificar Ollama
    try:
        resp = ask_ollama("di ok", max_tokens=5)
        if resp:
            log.info(f"Ollama OK ✓ (modelo responde)")
    except Exception as e:
        log.error(f"Ollama NO responde: {e}")

    last_sync = 0
    while True:
        try:
            # Sync periódico de wacli
            now = time.time()
            if now - last_sync > 30:
                _run_wacli(["sync", "--max-db-size=1GB"], timeout=60)
                last_sync = now

            # Procesar mensajes
            msgs = get_messages(limit=10)
            for msg in reversed(msgs):
                try:
                    process_message(msg)
                except Exception as e:
                    log.error(f"Error procesando mensaje: {e}")

            time.sleep(POLL_INTERVAL)

        except KeyboardInterrupt:
            log.info("Detenido por usuario")
            break
        except Exception as e:
            log.error(f"Error en loop: {e}")
            time.sleep(10)

if __name__ == "__main__":
    if "--listen" in sys.argv:
        listen_loop()
    elif "--test-stt" in sys.argv:
        audio = sys.argv[2] if len(sys.argv) > 2 else "/tmp/recorrido-hoy.ogg"
        print(f"Transcribiendo: {audio}")
        print(transcribe_audio(audio))
    elif "--test-tts" in sys.argv:
        text = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "Hola, soy Mystic."
        out = "/tmp/test-tts.ogg"
        result = text_to_speech(text, out)
        print(f"TTS: {result}")
    elif "--test-llm" in sys.argv:
        text = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "¿Quién eres?"
        print(f"LLM: {ask_ollama(text, SYSTEM_PROMPT)}")
    else:
        print("Uso:")
        print("  python3 wa_voice_assistant.py --listen")
        print("  python3 wa_voice_assistant.py --test-stt <audio.ogg>")
        print("  python3 wa_voice_assistant.py --test-tts <texto>")
        print("  python3 wa_voice_assistant.py --test-llm <texto>")
