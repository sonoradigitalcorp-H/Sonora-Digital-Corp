#!/usr/bin/env python3
"""
WhatsApp Gateway + CRM for Sonora Digital Corp.
Uso: python3 scripts/wa.py inbox|ls|send|contacts|contact <número>

Dependencias: psycopg2-binary (installed in Hermes container, accessed via docker)
"""
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent
INBOX_FILE = PROJECT_DIR / "data" / "wa-inbox.json"

# Hermes WA API
WA_BASE = os.environ.get("WA_BASE", "http://localhost:3001")
WA_KEY = os.environ.get("WHATSAPP_API_KEY", "")

# PostgreSQL for reading WA sessions
PG_USER = os.environ.get("WA_PG_USER", "mystic_user")
PG_PASS = os.environ.get("WA_PG_PASS", "")
PG_HOST = os.environ.get("WA_PG_HOST", "localhost")
PG_PORT = os.environ.get("WA_PG_PORT", "5432")
PG_DB = os.environ.get("WA_PG_DB", "mystic_db")
PG_URL = f"postgresql://{PG_USER}:{PG_PASS}@{PG_HOST}:{PG_PORT}/{PG_DB}"


def _send_wa(to: str, message: str) -> dict:
    """Send WhatsApp message via hermes_wa API."""
    import urllib.request
    import urllib.error
    data = json.dumps({"to": to, "message": message}).encode()
    req = urllib.request.Request(
        f"{WA_BASE}/send",
        data=data,
        headers={"Content-Type": "application/json", "x-api-key": WA_KEY},
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return {"ok": False, "error": f"HTTP {e.code}: {e.read().decode()[:200]}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def _wa_status() -> dict:
    """Check WhatsApp connection status."""
    import urllib.request
    try:
        req = urllib.request.Request(
            f"{WA_BASE}/status",
            headers={"x-api-key": WA_KEY},
        )
        with urllib.request.urlopen(req, timeout=5) as r:
            return json.loads(r.read())
    except Exception as e:
        return {"state": "error", "error": str(e)}


def _load_inbox() -> list:
    """Load pending messages from local inbox file."""
    if not INBOX_FILE.exists():
        return []
    try:
        data = json.loads(INBOX_FILE.read_text())
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, Exception):
        return []


def _save_inbox(messages: list):
    """Save inbox to file."""
    INBOX_FILE.parent.mkdir(parents=True, exist_ok=True)
    INBOX_FILE.write_text(json.dumps(messages, indent=2, default=str))


def cmd_inbox():
    """Read pending WhatsApp messages from PostgreSQL brain_sessions."""
    import subprocess
    result = subprocess.run(
        ["docker", "exec", "hermes_api", "python3", "-c", f"""
from sqlalchemy import create_engine, text
import json as _json
engine = create_engine('{PG_URL.replace('localhost', 'postgres')}')
with engine.connect() as conn:
    rows = conn.execute(text(\"\"\"
        SELECT session_id, messages, last_activity, created_at
        FROM brain_sessions
        WHERE session_id LIKE 'whatsapp:%'
        ORDER BY last_activity DESC
        LIMIT 30
    \"\"\")).fetchall()
    out = []
    for r in rows:
        msgs = r.messages
        if isinstance(msgs, str):
            msgs = _json.loads(msgs)
        if msgs and isinstance(msgs, list) and len(msgs) > 0:
            first = msgs[-1] if len(msgs) > 0 else msgs[0]
        else:
            first = {{}}
        out.append({{
            "session_id": r.session_id,
            "from": r.session_id.replace('whatsapp:', ''),
            "last_message": first.get('content', '')[:200] if isinstance(first, dict) else str(first)[:200],
            "total_messages": len(msgs) if isinstance(msgs, list) else 0,
            "last_activity": str(r.last_activity),
        }})
    print(_json.dumps(out, indent=2))
"""],
        capture_output=True, text=True, timeout=30,
    )
    if result.returncode == 0 and result.stdout.strip():
        data = json.loads(result.stdout)
        if not data:
            print(json.dumps({"status": "empty", "message": "No hay conversaciones WhatsApp"}, indent=2))
            return
        print(json.dumps({"status": "ok", "count": len(data), "conversations": data}, indent=2))
    else:
        print(json.dumps({"status": "error", "error": result.stderr[:500]}, indent=2))


def cmd_send():
    """Send a WhatsApp message. Usage: --to 5216623538272 --msg "Hola" """
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--to", required=True)
    parser.add_argument("--msg", required=True)
    args = parser.parse_args()
    result = _send_wa(args.to, args.msg)
    print(json.dumps(result, indent=2))


def cmd_status():
    """Check WhatsApp connection status."""
    result = _wa_status()
    print(json.dumps(result, indent=2))


def cmd_conversation():
    """Get full conversation with a contact. Usage: --phone 5216623538272"""
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--phone", required=True)
    args = parser.parse_args()

    import subprocess
    clean = args.phone.replace("521", "", 1).replace("52", "", 1) if args.phone.startswith("52") else args.phone
    result = subprocess.run(
        ["docker", "exec", "hermes_api", "python3", "-c", f"""
from sqlalchemy import create_engine, text
import json as _json
engine = create_engine('{PG_URL.replace('localhost', 'postgres')}')
session_id = 'whatsapp:{clean}'
with engine.connect() as conn:
    rows = conn.execute(text(\"\"\"
        SELECT session_id, messages, last_activity, created_at
        FROM brain_sessions
        WHERE session_id = :sid
        ORDER BY last_activity DESC
        LIMIT 50
    \"\"\"), {{"sid": session_id}}).fetchall()
    out = []
    for r in rows:
        msgs = r.messages
        if isinstance(msgs, str):
            msgs = _json.loads(msgs)
        out.append({{
            "from": r.session_id.replace('whatsapp:', ''),
            "messages": msgs[:20] if isinstance(msgs, list) else [],
            "last_activity": str(r.last_activity),
        }})
    print(_json.dumps(out, indent=2))
"""],
        capture_output=True, text=True, timeout=30,
    )
    if result.returncode == 0 and result.stdout.strip():
        data = json.loads(result.stdout)
        print(json.dumps({"status": "ok", "count": len(data), "conversations": data}, indent=2))
    else:
        print(json.dumps({"status": "error", "error": result.stderr[:500]}, indent=2))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 scripts/wa.py <comando> [args]")
        print("Comandos:")
        print("  status                      - Estado de conexión WhatsApp")
        print("  inbox                       - Mensajes recientes de WhatsApp")
        print('  send --to <num> --msg <txt> - Enviar mensaje WhatsApp')
        print('  conversation --phone <num>  - Historial completo con un contacto')
        sys.exit(1)

    cmd = sys.argv[1]
    cmds = {
        "status": cmd_status,
        "inbox": cmd_inbox,
        "send": cmd_send,
        "conversation": cmd_conversation,
    }
    if cmd in cmds:
        cmds[cmd]()
    else:
        print(f"Comando desconocido: {cmd}")
        sys.exit(1)
