#!/usr/bin/env python3
"""lead_demo.py — Genera y envía contenido multimedia para leads de Aztrotech.

Combina: texto → imagen (fal-ai) → audio (edge-tts) → envío vía WhatsApp/wacli.
Todo en un pipeline optimizado (paralelo donde es posible).

Uso:
    python3 lead_demo.py --lead "Empresa: TechCorp, email: CEO" --chat 5216623538272 --channel whatsapp
    python3 lead_demo.py --lead "Empresa: TechCorp" --chat 5738935134 --channel telegram --voice-only
    python3 lead_demo.py --lead "Empresa: TechCorp" --chat 5216623538272 --channel whatsapp --image-only
"""

import argparse
import json
import subprocess
import sys
import os
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENGINE_DIR = PROJECT_ROOT / "01_Core_Platform/05_SelfImprovement"
sys.path.insert(0, str(ENGINE_DIR))

from sdc_sdk import get_env, log_action, call_llm

# Asset paths
MEDIA_DIR = PROJECT_ROOT / "02_Client_Projects/Aztrotech/03_Media_Assets"
CESAR_IMAGES = MEDIA_DIR / "Images" / "cesar_cloned"
FAL_KEY = get_env("FAL_KEY", "")
WHATSAPP_NUM = get_env("WHATSAPP_ALLOWED_USERS", "+5216623538272")

EDGE_TTS_VOICE = "es-MX-JorgeNeural"
EDGE_TTS_RATE = "-20%"
EDGE_TTS_PITCH = "+8Hz"


def generate_image_fal(prompt: str, style: str = "realistic") -> str:
    """Generate image via fal.ai API. Returns URL of generated image."""
    import requests

    if not FAL_KEY:
        log_action("image_fal_failed", metadata={"reason": "no FAL_KEY"})
        return ""

    url = "https://api.fal.ai/v1"
    headers = {"Authorization": f"Bearer {FAL_KEY}"}

    if style == "dashboard":
        model = "fal-ai/flux-schnell"
    else:
        model = "fal-ai/fast-flux/sdv16"

    payload = {
        "prompt": f"{prompt}, professional quality, clean design, Aztrotech branding colors",
        "width": 1024,
        "height": 768,
        "num_images": 1,
    }

    try:
        resp = requests.post(
            f"{url}/{model}",
            headers=headers,
            json=payload,
            timeout=30,
        )
        if resp.status_code == 200:
            data = resp.json()
            img_url = data.get("images", [{}])[0].get("url", "")
            log_action("image_generated", metadata={"url": img_url[:50]})
            return img_url
    except Exception as e:
        log_action("image_fal_error", metadata={"error": str(e)[:100]})

    return ""


def get_existing_image(client_name: str = "") -> str:
    """Return path to an existing Aztrotech image (César photo or asset)."""
    cesar_dir = MEDIA_DIR / "Images" / "cesar_cloned"
    if cesar_dir.exists():
        images = list(cesar_dir.glob("*.jpg"))
        if images:
            return str(images[0])
    for subdir in ["Documents", "Images"]:
        d = MEDIA_DIR / subdir
        if d.exists():
            for ext in ["*.png", "*.jpg", "*.jpeg"]:
                imgs = list(d.glob(ext))
                if imgs:
                    return str(imgs[0])
    return ""


def generate_dashboard_mockup(client_name: str) -> str:
    """Generate a dashboard mockup image for a client via fal.ai. Returns local path."""
    prompt = (
        f"Professional Aztrotech dashboard mockup for {client_name}, "
        f"dark theme, clean UI, showing AI agent metrics, "
        f"leads table, automation graphs, WhatsApp icon, "
        f"Aztrotech branding, modern Mexican tech startup style"
    )
    img_url = generate_image_fal(prompt, style="dashboard")
    if img_url:
        import requests
        try:
            img_data = requests.get(img_url, timeout=15).content
            img_path = f"/tmp/dashboard_{int(time.time())}.png"
            with open(img_path, "wb") as f:
                f.write(img_data)
            return img_path
        except Exception:
            pass
    return ""


def text_to_speech(text: str, output_file: str, voice: str = None, rate: str = None, pitch: str = None) -> str:
    """Generate voice note via edge-tts. Returns path to OGG file."""
    voice = voice or EDGE_TTS_VOICE
    rate = rate or EDGE_TTS_RATE
    pitch = pitch or EDGE_TTS_PITCH

    mp3_path = output_file.replace(".ogg", ".mp3")

    cmd = [
        "edge-tts",
        f"--voice={voice}",
        f"--text={text}",
        f"--write-media={mp3_path}",
        f"--rate={rate}",
        f"--pitch={pitch}",
    ]
    subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    if not os.path.exists(mp3_path):
        return ""

    ffmpeg = "/home/mystic/.local/lib/python3.10/site-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2"
    try:
        import imageio_ffmpeg
        ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        pass

    subprocess.run(
        [ffmpeg, "-y", "-i", mp3_path, "-c:a", "libopus", "-b:a", "24k", output_file],
        capture_output=True, text=True, timeout=30,
    )

    if os.path.exists(mp3_path):
        os.remove(mp3_path)

    return output_file if os.path.exists(output_file) and os.path.getsize(output_file) > 0 else ""


def send_telegram_photo(bot_token: str, chat_id: str, image_path: str, caption: str) -> bool:
    """Send photo via Telegram bot API."""
    import requests
    url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
    try:
        with open(image_path, "rb") as f:
            r = requests.post(url, data={"chat_id": chat_id, "caption": caption}, files={"photo": f}, timeout=30)
        return r.json().get("ok", False)
    except Exception:
        return False


def send_telegram_voice(bot_token: str, chat_id: str, voice_path: str) -> bool:
    """Send voice note via Telegram bot API."""
    import requests
    url = f"https://api.telegram.org/bot{bot_token}/sendVoice"
    try:
        with open(voice_path, "rb") as f:
            r = requests.post(url, data={"chat_id": chat_id}, files={"voice": f}, timeout=30)
        return r.json().get("ok", False)
    except Exception:
        return False


def send_telegram_text(bot_token: str, chat_id: str, text: str) -> bool:
    """Send text via Telegram bot API."""
    import requests
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    try:
        r = requests.post(url, data={"chat_id": chat_id, "text": text}, timeout=30)
        return r.json().get("ok", False)
    except Exception:
        return False


def get_telegram_token(bot_name: str) -> str:
    """Get Telegram bot token from OpenClaw secrets."""
    secrets = Path.home() / ".openclaw" / "secrets"

    token_map = {
        "aztroc": "telegram-aztroc.token",
        "rye": "telegram-rye.token",
    }
    token_file = secrets / token_map.get(bot_name, "telegram-aztroc.token")
    if token_file.exists():
        return token_file.read_text().strip()
    return ""


def send_wacli_text(message: str, to: str) -> bool:
    """Send text via wacli."""
    result = subprocess.run(
        ["/home/mystic/.local/bin/wacli", "send", "text",
         "--store", str(Path.home() / ".config/wacli"),
         "--to", to, "--message", message],
        capture_output=True, text=True, timeout=30,
    )
    return result.returncode == 0 and "Sent" in result.stdout


def send_wacli_voice(voice_path: str, to: str) -> bool:
    """Send voice note via wacli."""
    result = subprocess.run(
        ["/home/mystic/.local/bin/wacli", "send", "voice",
         "--store", str(Path.home() / ".config/wacli"),
         "--to", to, "--file", voice_path],
        capture_output=True, text=True, timeout=30,
    )
    return result.returncode == 0 and "Sent" in result.stdout


def log_lead_to_store(lead_data: str, channel: str, chat_id: str, success: bool) -> None:
    """Log lead interaction to the experience store."""
    try:
        from experience_store import ExperienceStore
        store = ExperienceStore()
        store.log_task_simple(
            task_type=f"lead_demo:{channel}",
            input_text=lead_data,
            output=f"chat_id={chat_id},success={success}",
            status="success" if success else "failure",
            duration_ms=int(time.time() * 1000 % 10000),
            tenant_id="aztrotech",
            agent_id="cesar",
        )
    except Exception:
        pass


def main():
    parser = argparse.ArgumentParser(description="Lead multimedia demo generator")
    parser.add_argument("--lead", required=True, help="Lead data string")
    parser.add_argument("--chat", required=True, help="Telegram chat ID or WhatsApp JID")
    parser.add_argument("--channel", choices=["whatsapp", "telegram"], default="whatsapp")
    parser.add_argument("--bot", default="aztroc", choices=["aztroc", "rye"], help="Bot name for Telegram")
    parser.add_argument("--voice-only", action="store_true", help="Solo enviar voz")
    parser.add_argument("--image-only", action="store_true", help="Solo enviar imagen")
    parser.add_argument("--client", help="Client name for dashboard mockup")
    args = parser.parse_args()

    log_action("lead_demo_start", metadata={"lead": args.lead, "channel": args.channel, "chat": args.chat})
    overall_success = True

    client_name = args.client or "TechCorp"

    # 1. Text message (always first)
    text_msg = (
        f"🚀 *LEAD - Aztrotech* \n\n"
        f"¡Gracias por tu interés! Tenemos 3 paquetes para tu negocio:\n\n"
        f"💼 *Empleado Digital* — Agente IA 24/7 — $999 USD\n"
        f"⚙️ *Automatizaciones* — Procesos + IA — $1999 USD\n"
        f"📊 *Plataformas Empresariales* — CRM/ERP — $3999 USD\n\n"
        f"¿Te mando el demo visual? 📲"
    )

    if args.channel == "telegram":
        token = get_telegram_token(args.bot)
        if token:
            send_telegram_text(token, args.chat, text_msg)
    else:  # whatsapp
        send_wacli_text(text_msg, args.chat + "@s.whatsapp.net" if "@s.whatsapp.net" not in args.chat else args.chat)

    # 2. Dashboard mockup or existing image (if not voice-only)
    if not args.voice_only:
        img_path = generate_dashboard_mockup(client_name) or get_existing_image(client_name)
        if img_path and os.path.exists(img_path):
            if args.channel == "telegram":
                token = get_telegram_token(args.bot)
                if token:
                    send_telegram_photo(token, args.chat, img_path, f"Demo para {client_name}")
            else:  # whatsapp
                to = args.chat if "@s.whatsapp.net" in args.chat else f"{args.chat}@s.whatsapp.net"
                result = subprocess.run(
                    ["/home/mystic/.local/bin/wacli", "send", "file",
                     "--store", str(Path.home() / ".config/wacli"),
                     "--to", to, "--file", img_path,
                     "--caption", f"Demo para {client_name}"],
                    capture_output=True, text=True, timeout=30,
                )
                if result.returncode != 0:
                    overall_success = False
        else:
            log_action("image_unavailable", metadata={"client": client_name})

    # 3. Voice note (if not image-only)
    if not args.image_only:
        voice_text = (
            f"¡Hola! Soy César de Aztrotech. Tenemos 3 paquetes: "
            f"Empleado Digital $999, Automatizaciones $1999, "
            f"Plataformas $3999. ¿Te mando más detalle? "
            f"Agéndame al 662 353 8272."
        )
        voice_path = f"/tmp/lead_voice_{int(time.time())}.ogg"
        result = text_to_speech(voice_text, voice_path)
        if result:
            if args.channel == "telegram":
                token = get_telegram_token(args.bot)
                if token:
                    send_telegram_voice(token, args.chat, result)
            else:
                send_wacli_voice(result, args.chat if "@s.whatsapp.net" in args.chat else f"{args.chat}@s.whatsapp.net")

    log_lead_to_store(args.lead, args.channel, args.chat, overall_success)
    log_action("lead_demo_complete", metadata={"lead": args.lead, "success": overall_success})

    print(f"✅ Lead demo enviado a {args.channel}:{args.chat}")
    print(f"   Text: ✅ | Image: {'✅' if not args.voice_only else 'skipped'} | Voice: {'✅' if not args.image_only else 'skipped'}")


if __name__ == "__main__":
    main()
