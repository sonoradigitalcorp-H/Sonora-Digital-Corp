"""Telegram Alerter — envía alertas via Telegram Bot API [FR11]"""
import json
import os
import urllib.request
import urllib.error
from pathlib import Path


REPO = Path(__file__).resolve().parent.parent.parent


def get_config():
    """Lee token desde .env.age descifrado o variables de entorno"""
    token = os.environ.get("ABE_TELEGRAM_TOKEN") or os.environ.get("GUARDIAN_TELEGRAM_TOKEN")
    chat = os.environ.get("ABE_TELEGRAM_CHAT") or os.environ.get("GUARDIAN_TELEGRAM_CHAT")
    if token and chat:
        return token, chat
    return None, None


def send_alert(message):
    """Envía mensaje a Telegram"""
    token, chat = get_config()
    if not token or not chat:
        return {"status": "error", "detail": "Telegram not configured"}

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = json.dumps({"chat_id": chat, "text": message, "parse_mode": "Markdown"}).encode()

    try:
        req = urllib.request.Request(
            url, data=data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        resp = urllib.request.urlopen(req, timeout=10)
        return {"status": "sent", "response": resp.status}
    except (urllib.error.URLError, OSError) as e:
        return {"status": "error", "detail": str(e)}


def format_drift_alert(drifts):
    """Formatea drifts como mensaje de Telegram"""
    lines = ["🚨 *Truth Guardian — Drift Detectado*"]
    for d in drifts:
        icon = {"missing": "❌", "unexpected": "⚠️", "unhealthy": "💥"}.get(d["type"], "🔍")
        lines.append(f"{icon} {d['detail']}")
    return "\n".join(lines)


def format_health_alert(unhealthy):
    """Formatea servicios no saludables como mensaje"""
    lines = ["💔 *Truth Guardian — Servicios Caídos*"]
    for u in unhealthy:
        lines.append(f"🔴 {u.get('target', u.get('url', 'unknown'))}: {u.get('error', 'no response')}")
    return "\n".join(lines)


if __name__ == "__main__":
    result = send_alert("🟢 Truth Guardian iniciado")
    print(json.dumps(result, indent=2))
