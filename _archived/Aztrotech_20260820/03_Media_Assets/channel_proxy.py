#!/usr/bin/env python3
"""Channel Proxy — Multi-Bot Gateway para OpenClaw.

Este proxy permite múltiples bots Telegram conectar al mismo agente.
Funciona como:
  - Escucha mensajes de ambos bots
  - Reenvía al webhook de enrutamiento
  - Mantiene el estado de ambos bots

Para usar:
  python3 channel_proxy.py --token @Aztro_tech_bot --target-agent cesar &
  python3 channel_proxy.py --token @RyE_production_bot --target-agent rye &
"""
import os, sys, json, argparse, threading, time
from pathlib import Path
from datetime import datetime

try:
    import requests
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "requests"], check=True)
    import requests

# Config
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "http://localhost:5289/webhook")
TENANT_ROUTER = Path.home() / ".openclaw" / "workspace" / "tenant_registry.json"


def load_registry():
    if TENANT_ROUTER.exists():
        with open(TENANT_ROUTER) as f:
            return json.load(f)
    return {}


def send_to_webhook(bot_name: str, user_id: int, message: str, media_path: str = None):
    """Reenvía mensaje al webhook de enrutamiento."""
    payload = {
        "bot": bot_name.replace("@", ""),
        "user_id": user_id,
        "message": message,
        "media_path": media_path,
        "timestamp": datetime.utcnow().isoformat()
    }

    try:
        resp = requests.post(WEBHOOK_URL, json=payload, timeout=10)
        if resp.status_code == 200:
            print(f"[FORWARD] {bot_name} → {user_id}: {message[:50]}...")
            return True
        else:
            print(f"[ERROR] Webhook returned {resp.status_code}")
    except Exception as e:
        print(f"[ERROR] Forward failed: {e}")
    return False


def poll_bot(token: str, bot_name: str, target_agent: str):
    """Poll messages from a Telegram bot and forward to webhook."""
    base_url = f"https://api.telegram.org/bot{token}"

    # Get updates (polling)
    offset = 0
    while True:
        try:
            resp = requests.get(f"{base_url}/getUpdates", params={
                "offset": offset,
                "timeout": 30
            }, timeout=35)

            data = resp.json()
            for update in data.get("result", []):
                update_id = update.get("update_id", 0)
                offset = update_id + 1

                message = update.get("message", {})
                if not message:
                    continue

                user = message.get("from", {})
                user_id = user.get("id", 0)
                text = message.get("text", "")

                # Handle media messages
                if "voice" in message:
                    file_id = message["voice"].get("file_id")
                    if file_id:
                        # Download voice note
                        file_resp = requests.get(f"{base_url}/getFile", params={"file_id": file_id})
                        file_path = file_resp.json().get("result", {}).get("file_path", "")
                        if file_path:
                            download_url = f"https://api.telegram.org/file/bot{token}/{file_path}"
                            media_path = f"/tmp/voice_{user_id}_{time.time()}.ogg"
                            with requests.get(download_url, stream=True) as r:
                                with open(media_path, "wb") as f:
                                    for chunk in r.iter_content(chunk_size=8192):
                                        f.write(chunk)
                            text = f"[VOICE] {media_path}"
                            media_path = media_path
                        else:
                            continue
                    else:
                        continue
                elif "photo" in message:
                    photos = message.get("photo", [])
                    if photos:
                        file_id = photos[-1].get("file_id")  # Highest resolution
                        file_resp = requests.get(f"{base_url}/getFile", params={"file_id": file_id})
                        file_path = file_resp.json().get("result", {}).get("file_path", "")
                        if file_path:
                            download_url = f"https://api.telegram.org/file/bot{token}/{file_path}"
                            media_path = f"/tmp/photo_{user_id}_{time.time()}.jpg"
                            with requests.get(download_url, stream=True) as r:
                                with open(media_path, "wb") as f:
                                    for chunk in r.iter_content(chunk_size=8192):
                                        f.write(chunk)
                            text = f"[PHOTO] {media_path}"
                            media_path = media_path
                        else:
                            continue

                if text:
                    send_to_webhook(bot_name, user_id, text, media_path if "VOICE" in text or "PHOTO" in text else None)

        except Exception as e:
            print(f"[POLL ERROR] {bot_name}: {e}")
            time.sleep(5)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--token", required=True, help="Bot token")
    ap.add_argument("--name", required=True, help="Bot name (e.g., Aztro_tech_bot)")
    ap.add_argument("--target-agent", required=True, help="Target OpenClaw agent ID")
    args = ap.parse_args()

    # Extract bot username from token (approximation)
    bot_name = f"@{args.name}"

    print(f"🚀 Channel Proxy started: {bot_name} → agent:{args.target_agent}")
    poll_bot(args.token, bot_name, args.target_agent)


if __name__ == "__main__":
    main()