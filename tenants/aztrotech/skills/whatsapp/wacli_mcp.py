import json
import logging
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

logger = logging.getLogger("aztrotech.wacli")

WACLI_BIN = os.getenv("WACLI_BIN") or (
    "/usr/local/bin/wacli" if os.path.exists("/usr/local/bin/wacli")
    else os.path.expanduser("~/.local/bin/wacli")
)
WACLI_STORE = os.getenv("WACLI_STORE_DIR", os.path.expanduser("~/.wacli"))
EVENTS_PATH = Path(os.getenv("STATE_DIR", "state/events")) / "events.jsonl"


def _wacli(args: list, timeout: int = 30) -> dict:
    if not os.path.exists(WACLI_BIN):
        return {"success": False, "error": f"wacli not found at {WACLI_BIN}"}
    cmd = [WACLI_BIN] + args + ["--store", WACLI_STORE, "--json"]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        out = r.stdout.strip()
        if out:
            return json.loads(out)
        err = r.stderr.strip()
        return {"success": False, "error": err or "no output"}
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "timeout"}
    except json.JSONDecodeError:
        return {"success": False, "error": f"invalid json: {r.stdout[:200]}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def _ensure_jid(phone: str) -> str:
    phone = phone.strip()
    if phone.endswith("@s.whatsapp.net"):
        return phone
    if phone.startswith("521"):
        return f"{phone}@s.whatsapp.net"
    if phone.startswith("52"):
        return f"521{phone[2:]}@s.whatsapp.net"
    if len(phone) == 10:
        return f"521{phone}@s.whatsapp.net"
    return f"521662{phone}@s.whatsapp.net" if len(phone) == 7 else f"52{phone}@s.whatsapp.net"


def _emit_event(event_type: str, payload: dict) -> None:
    try:
        EVENTS_PATH.parent.mkdir(parents=True, exist_ok=True)
        entry = {
            "event": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "payload": payload,
        }
        with open(EVENTS_PATH, "a") as f:
            f.write(json.dumps(entry, sort_keys=False) + "\n")
    except Exception:
        pass


async def send_whatsapp(phone: str, message: str) -> dict:
    jid = _ensure_jid(phone)
    result = _wacli([
        "send", "text", "--message", message,
        "--to", jid, "--post-send-wait", "3s",
    ])
    data = result.get("data", {}) or {}
    sent = data.get("sent", False)
    msg_id = data.get("id", "")
    _emit_event("whatsapp:sent", {
        "to": phone, "jid": jid, "message": message,
        "sent": sent, "message_id": msg_id,
    })
    return {
        "success": sent,
        "message_id": msg_id,
        "to": phone,
        "error": result.get("error"),
    }


async def get_messages(limit: int = 20, chat_jid: Optional[str] = None) -> list[dict]:
    args = ["messages", "list", "--limit", str(limit)]
    if chat_jid:
        args += ["--chat", _ensure_jid(chat_jid)]
    result = _wacli(args)
    messages = result.get("data", []) if result.get("success") else []
    if not isinstance(messages, list):
        messages = []
    return messages


async def check_status() -> dict:
    result = _wacli(["auth", "status"])
    if result.get("success") and result.get("data", {}).get("authenticated"):
        return {
            "authenticated": True,
            "phone": result["data"].get("phone", ""),
        }
    return {
        "authenticated": False,
        "error": result.get("error", "unknown"),
    }


async def get_contacts() -> list[dict]:
    result = _wacli(["contacts", "list"])
    return result.get("data", []) if isinstance(result.get("data"), list) else []


MCP_TOOLS = {
    "whatsapp_send": {
        "description": "Send a WhatsApp text message via wacli",
        "input_schema": {
            "type": "object",
            "properties": {
                "phone": {"type": "string", "description": "Phone number (e.g. 521662xxxxxxx)"},
                "message": {"type": "string", "description": "Message text"},
            },
            "required": ["phone", "message"],
        },
        "handler": lambda args: send_whatsapp(args["phone"], args["message"]),
    },
    "whatsapp_messages": {
        "description": "Get recent WhatsApp messages from the local store",
        "input_schema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Max messages (default: 20)"},
                "chat_jid": {"type": "string", "description": "Filter by chat JID or phone"},
            },
        },
        "handler": lambda args: get_messages(
            limit=args.get("limit", 20),
            chat_jid=args.get("chat_jid"),
        ),
    },
    "whatsapp_status": {
        "description": "Check wacli WhatsApp authentication status",
        "input_schema": {"type": "object", "properties": {}},
        "handler": lambda _: check_status(),
    },
    "whatsapp_contacts": {
        "description": "List known WhatsApp contacts",
        "input_schema": {"type": "object", "properties": {}},
        "handler": lambda _: get_contacts(),
    },
}
