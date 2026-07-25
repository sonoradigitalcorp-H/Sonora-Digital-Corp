"""Notify César via Telegram when a booking is made."""

import json
import os
import urllib.request
import urllib.error
from typing import Optional
from .models import Booking

SECRETS_FILE = os.path.join(os.path.dirname(__file__), "..", "ai", "secrets.yaml")


def _get_bot_token() -> Optional[str]:
    if not os.path.exists(SECRETS_FILE):
        return None
    with open(SECRETS_FILE) as f:
        for line in f:
            if "telegram_bot_token:" in line:
                return line.split(":", 1)[1].strip().strip('"').strip("'")
    return None


def _get_cesar_chat_id() -> Optional[str]:
    if not os.path.exists(SECRETS_FILE):
        return None
    with open(SECRETS_FILE) as f:
        for line in f:
            if "cesar_telegram_chat_id:" in line:
                return line.split(":", 1)[1].strip().strip('"').strip("'")
    return None


def notify_cesar(booking: Booking) -> bool:
    token = _get_bot_token()
    chat_id = _get_cesar_chat_id()
    if not token or not chat_id:
        return False

    msg = (
        f" Nueva cita agendada\n"
        f"Cliente: {booking.prospect_name}\n"
        f"Email: {booking.prospect_email}\n"
        f"Tel: {booking.prospect_phone or '—'}\n"
        f"Empresa: {booking.company or '—'}\n"
        f"Fecha: {booking.slot.date}\n"
        f"Hora: {booking.slot.start_time} — {booking.slot.end_time}\n"
        f"ID: {booking.id}"
    )

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = json.dumps({
        "chat_id": chat_id,
        "text": msg,
        "parse_mode": "HTML",
    }).encode()

    try:
        req = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except Exception:
        return False
