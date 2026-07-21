"""
Diagnosis request handler — receives form submissions, saves to DB, notifies Mystic admin.
"""

import json
import os
import subprocess
import smtplib
from datetime import datetime, timezone
from email.mime.text import MIMEText
from pathlib import Path

REQUESTS_DIR = Path("state/mystic-shield/requests")
REQUESTS_DIR.mkdir(parents=True, exist_ok=True)

ADMIN_PHONE = os.environ.get("MYSTIC_ADMIN_PHONE", "5216623538272")
ADMIN_EMAIL = os.environ.get("MYSTIC_ADMIN_EMAIL", "hola@sonoracorp.mx")


def save_request(email: str, company: str, phone: str) -> dict:
    req = {
        "id": f"REQ-{datetime.now():%Y%m%d-%H%M%S}",
        "email": email,
        "company": company,
        "phone": phone,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "pending",
    }
    path = REQUESTS_DIR / f"{req['id']}.json"
    path.write_text(json.dumps(req, indent=2))
    return req


def notify_admin(req: dict):
    """Send WhatsApp + Email to you about new lead."""
    msg = (
        f"🆕 *Nuevo lead Mystic Shield*\n\n"
        f"Empresa: {req['company']}\n"
        f"Contacto: {req['email']}\n"
        f"Teléfono: {req['phone']}\n"
        f"ID: {req['id']}"
    )
    WACLI = os.path.expanduser("~/.local/bin/wacli")
    STORE = os.path.expanduser("~/.config/ai.opencode.desktop/wacli")
    if os.path.exists(WACLI):
        try:
            to = f"{ADMIN_PHONE}@s.whatsapp.net"
            subprocess.run(
                [WACLI, "send", "text", "--message", msg, "--to", to, "--store", STORE, "--json"],
                capture_output=True, text=True, timeout=30,
            )
        except Exception as e:
            print(f"[notify] WhatsApp error: {e}")

    try:
        msg_email = MIMEText(msg.replace("*", ""), "plain", "utf-8")
        msg_email["From"] = ADMIN_EMAIL
        msg_email["To"] = ADMIN_EMAIL
        msg_email["Subject"] = f"🆕 Nuevo lead Mystic Shield: {req['company']}"
        with smtplib.SMTP(os.environ.get("SMTP_SERVER", "localhost"),
                          int(os.environ.get("SMTP_PORT", "25")), timeout=10) as server:
            server.sendmail(ADMIN_EMAIL, [ADMIN_EMAIL], msg_email.as_string())
    except Exception as e:
        print(f"[notify] Email error: {e}")


def list_requests(limit: int = 20) -> list:
    files = sorted(REQUESTS_DIR.glob("REQ-*.json"), key=os.path.getmtime, reverse=True)
    result = []
    for p in files[:limit]:
        result.append(json.loads(p.read_text()))
    return result
