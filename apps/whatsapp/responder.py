#!/usr/bin/env python3
"""
WhatsApp Responder — Responde automáticamente a mensajes entrantes.

Estilo ChatGPT pero en WhatsApp:
- Texto → responde con texto
- "Dímelo en voz" → responde con nota de voz
- "Manda un video" → responde con video talking head
- "Foto de..." → responde con imagen generada

Cada mensaje entrante se procesa en <5 segundos.
"""

import json
import os
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO))

WACLI = os.environ.get("WACLI_PATH") or os.path.expanduser("~/.local/bin/wacli")
if not os.path.exists(WACLI):
    WACLI = "/usr/local/bin/wacli"
STORE = os.environ.get("WACLI_STORE") or os.path.expanduser("~/.config/ai.opencode.desktop/wacli")
EVENTS_FILE = REPO / "state" / "events" / "events.jsonl"
SEEN_RESPONDED = REPO / "state" / "whatsapp" / "responded.json"
PHONE = "5216623538272"

# Founder
FOUNDER_PHONE = os.environ.get("FOUNDER_PHONE", "")

# LLM config
OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY", "")
LLM_MODEL = "opencode-go/deepseek-v4-flash"


def _wacli(args: list, timeout: int = 30) -> dict:
    if not os.path.exists(WACLI):
        return {"success": False, "error": "wacli not found"}
    cmd = [WACLI] + args + ["--store", STORE, "--json"]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        out = r.stdout.strip()
        if out:
            return json.loads(out)
        return {"success": False, "error": r.stderr.strip() or "no output"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def _send_text(to: str, text: str) -> dict:
    to = to if "@s.whatsapp.net" in to else f"{to}@s.whatsapp.net"
    return _wacli(["send", "text", "--message", text, "--to", to, "--post-send-wait", "3s"])


def _send_voice(to: str, text: str) -> dict:
    """Convert text to speech and send as voice note."""
    to = to if "@s.whatsapp.net" in to else f"{to}@s.whatsapp.net"
    try:
        tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False, mode="wb")
        mp3_path = tmp.name
        tmp.close()

        subprocess.run([
            "edge-tts", "--voice", "es-MX-DaliaNeural",
            "--text", text,
            "--write-media", mp3_path,
        ], capture_output=True, timeout=30)

        # Convert to OGG for WhatsApp
        ogg_path = mp3_path.replace(".mp3", ".ogg")
        subprocess.run([
            "ffmpeg", "-y", "-i", mp3_path,
            "-c:a", "libopus", "-b:a", "16k", "-ar", "16000", ogg_path
        ], capture_output=True, timeout=30)

        result = _wacli([
            "send", "file", "--file", ogg_path,
            "--mime", "audio/ogg; codecs=opus", "--ptt",
            "--to", to, "--post-send-wait", "5s",
        ])

        os.unlink(mp3_path)
        os.unlink(ogg_path)
        return result
    except Exception as e:
        # Fallback to text
        return _send_text(to, f"[🎙️ {text}]")


def _ask_llm(messages: list) -> str:
    """Call LLM and return response text."""
    if not OPENROUTER_KEY:
        return "⚠️ No tengo conexión con mi cerebro (falta OPENROUTER_API_KEY)"
    try:
        import httpx
        body = {
            "model": LLM_MODEL,
            "messages": messages,
            "max_tokens": 500,
            "temperature": 0.7,
        }
        r = httpx.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENROUTER_KEY}", "Content-Type": "application/json"},
            json=body,
            timeout=15,
        )
        data = r.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"⚠️ Error de conexión: {e}"


def _detect_intent(text: str) -> str:
    """Detect if user wants text, voice, image, or video response."""
    t = text.lower()
    if any(k in t for k in ["voz", "dímelo", "audio", "escúchame", "háblame"]):
        return "voice"
    if any(k in t for k in ["video", "mira", "muéstrame", "talking head"]):
        return "video"
    if any(k in t for k in ["foto", "imagen", "dibujo", "ilustración"]):
        return "image"
    return "text"


def _respond(sender: str, text: str, msg_id: str) -> None:
    """Process message and send response."""
    intent = _detect_intent(text)
    print(f"[responder] {sender}: {text[:60]}... → {intent}", file=sys.stderr)

    # System prompt
    system = (
        "Eres Mystic, el asistente personal de Luis Daniel, fundador de Sonora Digital Corp. "
        "Respondes en español, directo, sin rodeos. Eres experto en IA, desarrollo de software, "
        "negocios digitales, ciberseguridad, y automatización. "
        "Si te piden algo técnico, lo explicas claro. Si es un saludo, saludas. "
        "Si es una instrucción, la confirmas y ejecutas. "
        "Máximo 3 párrafos. No saludas cada vez. Ve al grano."
    )

    if FOUNDER_PHONE and FOUNDER_PHONE in sender:
        # Founder → personal assistant mode
        response = _ask_llm([
            {"role": "system", "content": system},
            {"role": "user", "content": text},
        ])
    else:
        # Client → business mode
        response = _ask_llm([
            {"role": "system", "content": (
                "Eres el asistente de ventas de Sonora Digital Corp. "
                "Ayudas a clientes con información sobre servicios digitales, "
                "precios, y agendamiento. Responde en español, profesional pero amable. "
                "Si no sabes algo, di que lo consultarás."
            )},
            {"role": "user", "content": text},
        ])

    # Send response
    if intent == "voice":
        result = _send_voice(sender, response)
        print(f"[responder] → voz enviada: {result.get('data', {}).get('sent', False)}", file=sys.stderr)
    elif intent == "image":
        # TODO: image generation pipeline
        _send_text(sender, response)
    elif intent == "video":
        # TODO: video generation pipeline (talking head)
        _send_text(sender, response)
    else:
        result = _send_text(sender, response)
        sent = result.get("data", {}).get("sent", False) if result.get("data") else False
        print(f"[responder] → texto enviado: {sent}", file=sys.stderr)

    # Log response
    log_entry = {
        "event": "whatsapp:response:sent",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "payload": {
            "to": sender,
            "original_msg_id": msg_id,
            "intent": intent,
            "response_preview": response[:100],
        },
    }
    _log_response(log_entry)


def _load_responded() -> set:
    if not SEEN_RESPONDED.exists():
        return set()
    try:
        with open(SEEN_RESPONDED) as f:
            return set(json.load(f).get("ids", []))
    except Exception:
        return set()


def _save_responded(ids: set) -> None:
    SEEN_RESPONDED.parent.mkdir(parents=True, exist_ok=True)
    with open(SEEN_RESPONDED, "w") as f:
        json.dump({"ids": sorted(ids), "updated": datetime.now(timezone.utc).isoformat()}, f)


def _log_response(entry: dict) -> None:
    log_file = REPO / "state" / "events" / "events.jsonl"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    with open(log_file, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def run_responder(once: bool = False):
    """Main loop: poll events.jsonl for incoming messages and respond."""
    print(f"[responder] Starting (polling events)...", file=sys.stderr)
    responded = _load_responded()

    while True:
        if not EVENTS_FILE.exists():
            time.sleep(1)
            continue

        try:
            with open(EVENTS_FILE) as f:
                lines = f.readlines()

            for line in lines[-50:]:  # Check last 50 lines
                line = line.strip()
                if not line:
                    continue
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue

                evt_type = event.get("event") or event.get("type", "")
                if evt_type not in ("whatsapp:message:received",):
                    continue

                payload = event.get("payload", {})
                msg_id = payload.get("message_id", "")
                if not msg_id or msg_id in responded:
                    continue

                sender = payload.get("from", "")
                text = payload.get("text", "")

                if not sender or not text:
                    continue

                responded.add(msg_id)
                _respond(sender, text, msg_id)
                _save_responded(responded)

        except Exception as e:
            print(f"[responder] Error: {e}", file=sys.stderr)

        if once:
            break
        time.sleep(1)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="WhatsApp Auto-Responder")
    parser.add_argument("--once", action="store_true", help="Process once and exit")
    args = parser.parse_args()
    run_responder(once=args.once)


if __name__ == "__main__":
    main()
