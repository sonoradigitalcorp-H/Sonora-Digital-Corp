"""
WhatsApp Voice Assistant — Pipeline Local v2
STT (faster-whisper) → LLM (Ollama llama3.2) → TTS (edge-tts) → WhatsApp (wacli)

100% local. Sin APIs externas.
Corre en VPS de Sonora Digital Corp.
"""

import json
import logging
import multiprocessing
import os
import subprocess
import sys
import time
from pathlib import Path

multiprocessing.set_start_method('fork', force=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s %(message)s",
)
log = logging.getLogger("wa-voice-v2")

# ========== POLICY ENGINE ==========
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from core.policy import PolicyEngine

POLICIES_YAML = Path(__file__).resolve().parent.parent.parent / "tenants" / "aztrotech" / "policies.yaml"
_policy = None
def get_policy() -> PolicyEngine:
    global _policy
    if _policy is None:
        if POLICIES_YAML.exists():
            _policy = PolicyEngine.from_yaml(str(POLICIES_YAML))
            log.info(f"Policy Engine loaded from {POLICIES_YAML.name}")
        else:
            _policy = PolicyEngine()
            log.warning("No policies.yaml, using defaults")
    return _policy

TENANT_ID = "aztrotech"
COST_LLM = 0.0001     # Ollama local
COST_TTS = 0.0        # edge-tts local gratuito
COST_STT = 0.0        # Whisper local gratuito

# ========== CONFIG ==========
WACLI_BIN = "/usr/local/bin/wacli"
WACLI_STORE = os.path.expanduser("~/.wacli")
MY_JID = "5216623538272@s.whatsapp.net"
OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3.2:3b"
WHISPER_MODEL = "small"
TTS_VOICE = "es-MX-DaliaNeural"
POLL_INTERVAL = 5
PROCESSED_FILE = "/tmp/wa-processed-ids.json"

SYSTEM_PROMPT = (
    "Eres Mystic, asistente de Sonora Digital Corp. "
    "Propiedad de Luis Daniel. Responde en español, "
    "cálido, directo y útil. Sé breve (máx 2-3 frases). "
    "No menciones que eres un modelo de IA."
)

# ========== WACLI HELPERS ==========
def _wacli(args: list, timeout: int = 30, read_only: bool = False) -> tuple[bool, str]:
    cmd = [WACLI_BIN, "--store", WACLI_STORE]
    if read_only:
        cmd.append("--read-only")
    cmd.append("--json")
    cmd.extend(args)
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        out = r.stdout.strip()
        if out:
            data = json.loads(out)
            return data.get("success", True), out
        return False, r.stderr.strip()[:200]
    except subprocess.TimeoutExpired:
        return False, "timeout"
    except Exception as e:
        return False, str(e)[:200]

def send_text(jid: str, message: str) -> bool:
    ok, out = _wacli(["send", "text", "--to", jid, "--message", message], timeout=15)
    if ok:
        log.info(f"Texto enviado a {jid[-8:]}")
        # Track sent message ID to avoid reprocessing
        try:
            data = json.loads(out)
            sent_id = data.get("data", {}).get("id", "")
            if sent_id:
                _processed_ids.add(sent_id)
                save_processed()
        except:
            pass
    return ok

def send_audio_ptt(jid: str, audio_path: str) -> bool:
    ok, out = _wacli(["send", "file", "--to", jid, "--file", audio_path, "--ptt"], timeout=30)
    if ok:
        log.info(f"Audio PTT enviado a {jid[-8:]}")
        # Track sent message ID
        try:
            data = json.loads(out)
            sent_id = data.get("data", {}).get("id", "")
            if sent_id:
                _processed_ids.add(sent_id)
                save_processed()
        except:
            pass
    return ok

def get_messages(limit: int = 5) -> list[dict]:
    ok, out = _wacli(["messages", "list", "--limit", str(limit)], timeout=15, read_only=True)
    if not ok:
        return []
    try:
        data = json.loads(out)
        return [m for m in data.get("data", {}).get("messages", []) if isinstance(m, dict)]
    except:
        return []

def download_media(msg_id: str, chat_jid: str, dest: str) -> bool:
    ok, _ = _wacli([
        "media", "download", "--id", msg_id, "--chat", chat_jid, "--output", dest
    ], timeout=45)
    return ok and os.path.exists(dest) and os.path.getsize(dest) > 100

# ========== STT ==========
_stt_model = None

def load_stt_model():
    global _stt_model
    if _stt_model is None:
        from faster_whisper import WhisperModel
        log.info(f"Cargando Whisper: {WHISPER_MODEL} (CPU, int8)")
        _stt_model = WhisperModel(WHISPER_MODEL, device="cpu", compute_type="int8")
        log.info("Whisper cargado ✓")
    return _stt_model

def transcribe(audio_path: str) -> str:
    model = load_stt_model()
    segs, info = model.transcribe(audio_path, language="es", beam_size=2)
    text = " ".join(s.text.strip() for s in segs).strip()
    log.info(f"STT: {info.language} {info.language_probability:.0%} → '{text[:80]}'")
    return text

# ========== LLM ==========
def ask_ollama(prompt: str) -> str:
    import urllib.request
    body = json.dumps({
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        "stream": False,
        "options": {"temperature": 0.7, "num_predict": 200}
    }).encode()
    req = urllib.request.Request(f"{OLLAMA_URL}/api/chat", data=body, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read())
            return data.get("message", {}).get("content", "").strip()
    except Exception as e:
        log.error(f"Ollama error: {e}")
        return ""

# ========== TTS ==========
def text_to_audio(text: str, output_path: str) -> bool:
    import asyncio
    import edge_tts
    async def _gen():
        mp3 = output_path.replace(".ogg", ".mp3")
        comm = edge_tts.Communicate(text, TTS_VOICE)
        await comm.save(mp3)
        subprocess.run(["ffmpeg","-y","-i",mp3,"-c:a","libopus","-b:a","64k","-application","voip",output_path], capture_output=True, check=True)
        os.remove(mp3)
    try:
        asyncio.run(_gen())
        return os.path.exists(output_path)
    except Exception as e:
        log.error(f"TTS error: {e}")
        return False

# ========== PROCESADOR ==========
_processed_ids = set()

def load_processed():
    global _processed_ids
    if os.path.exists(PROCESSED_FILE):
        try:
            with open(PROCESSED_FILE) as f:
                _processed_ids = set(json.load(f))
            log.info(f"IDs cargados: {len(_processed_ids)}")
        except:
            pass

def preload_all_ids():
    """Precarga TODOS los IDs del store para no procesar mensajes viejos."""
    global _processed_ids
    ok, out = _wacli(["messages", "list", "--limit", "100"], timeout=15, read_only=True)
    if not ok:
        return
    try:
        data = json.loads(out)
        msgs = data.get("data", {}).get("messages", [])
        count = 0
        for m in msgs:
            mid = m.get("MsgID", "")
            if mid:
                _processed_ids.add(mid)
                count += 1
        save_processed()
        log.info(f"Preloaded {count} existing message IDs (no se procesarán)")
    except Exception as e:
        log.error(f"preload error: {e}")

def save_processed():
    with open(PROCESSED_FILE, "w") as f:
        json.dump(list(_processed_ids), f)

def process(msg: dict) -> bool:
    msg_id = msg.get("MsgID", "")
    if not msg_id or msg_id in _processed_ids:
        return False

    # SANDBOX: solo tu chat personal, nada de grupos ni otros contactos
    jid = msg.get("ChatJID", "")
    if jid != MY_JID:
        return False

    # Ignorar mensajes que son nuestras propias respuestas (por si algún filtro falla)
    text = msg.get("Text", "").strip()
    if text and any(text.startswith(p) for p in ["🎙️", "🎧", "📝", "⚠️"]):
        _processed_ids.add(msg_id)
        save_processed()
        return False

    _processed_ids.add(msg_id)
    save_processed()

    msg_type = msg.get("MediaType", "").lower()
    text = msg.get("Text", "").strip()

    log.info(f"📨 tipo={msg_type} | text='{text[:50]}' | id={msg_id[:10]}")

    if msg_type == "audio":
        return handle_audio(jid, msg_id)
    elif text:
        return handle_text(jid, text)

    return False

def handle_text(jid: str, text: str) -> bool:
    log.info(f"🧠 Texto: '{text[:60]}'")

    # === POLICY GATE: LLM ===
    policy = get_policy()
    llm_decision = policy.validate_sync(TENANT_ID, "llm", cost=COST_LLM)
    if not llm_decision.allowed:
        send_text(jid, f"⛔ {llm_decision.reason}")
        return False

    response = ask_ollama(text)
    if not response:
        return False
    policy.record(TENANT_ID, "llm", COST_LLM, OLLAMA_MODEL)

    # === POLICY GATE: TTS ===
    tts_decision = policy.validate_sync(TENANT_ID, "tts", cost=COST_TTS)
    if tts_decision.allowed:
        audio_out = f"/tmp/wa-r-{int(time.time())}.ogg"
        if text_to_audio(response, audio_out):
            send_audio_ptt(jid, audio_out)
            os.remove(audio_out)
            policy.record(TENANT_ID, "tts", COST_TTS, TTS_VOICE)

    # Siempre enviar texto (es gratis)
    send_text(jid, response)

    return True

def handle_audio(jid: str, msg_id: str) -> bool:
    log.info(f"🎤 Audio ID: {msg_id[:12]}")

    audio_in = f"/tmp/wa-in-{msg_id[:8]}.ogg"
    if not download_media(msg_id, jid, audio_in):
        log.warning(f"Media no disponible aún, se reintentará: {msg_id[:12]}")
        _processed_ids.discard(msg_id)
        return False

    text = transcribe(audio_in)
    os.remove(audio_in)

    if not text:
        return False

    # === POLICY GATE: LLM ===
    policy = get_policy()
    llm_decision = policy.validate_sync(TENANT_ID, "llm", cost=COST_LLM)
    if not llm_decision.allowed:
        send_text(jid, f"⛔ {llm_decision.reason}")
        return False

    response = ask_ollama(text)
    if not response:
        return False
    policy.record(TENANT_ID, "llm", COST_LLM, OLLAMA_MODEL)

    # === POLICY GATE: TTS ===
    tts_decision = policy.validate_sync(TENANT_ID, "tts", cost=COST_TTS)
    if tts_decision.allowed:
        audio_out = f"/tmp/wa-r-{int(time.time())}.ogg"
        if text_to_audio(response, audio_out):
            send_audio_ptt(jid, audio_out)
            os.remove(audio_out)
            policy.record(TENANT_ID, "tts", COST_TTS, TTS_VOICE)
    else:
        # Si TTS está bloqueado, al menos envía texto
        send_text(jid, response)

    return True

# ========== LOOP ==========
def main():
    log.info("=" * 50)
    log.info("🎙️ WA Voice Assistant v2 — Pipeline Local")
    log.info(f"   STT: faster-whisper ({WHISPER_MODEL})")
    log.info(f"   LLM: Ollama ({OLLAMA_MODEL})")
    log.info(f"   TTS: edge-tts ({TTS_VOICE})")
    log.info("=" * 50)

    load_stt_model()
    load_processed()
    preload_all_ids()

    # Verificar Ollama
    try:
        r = ask_ollama("di ok")
        if r:
            log.info(f"Ollama OK ✓")
    except:
        log.error("Ollama NO responde")

    while True:
        try:
            msgs = get_messages(limit=10)
            for msg in reversed(msgs):
                try:
                    process(msg)
                except Exception as e:
                    log.error(f"Error: {e}")
            time.sleep(POLL_INTERVAL)
        except KeyboardInterrupt:
            break
        except Exception as e:
            log.error(f"Loop error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    main()
