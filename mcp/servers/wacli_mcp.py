"""
WACLI MCP Server — WhatsApp messaging via wacli.

Tools:
  whatsapp_send_text     — Send text message
  whatsapp_send_file     — Send file (PDF, image, audio, etc.)
  whatsapp_send_voice    — Send voice note (auto-converts MP3 to OGG Opus)
  whatsapp_check_status  — Check authentication status

Requires: wacli installed at ~/.local/bin/wacli
Store: ~/.config/ai.opencode.desktop/wacli
"""

import json
import os
import subprocess
import tempfile

WACLI = os.path.expanduser("~/.local/bin/wacli")
STORE = os.path.expanduser("~/.config/ai.opencode.desktop/wacli")
PHONE = "5216623538272"  # Cuenta autenticada


def _wacli(args: list, timeout: int = 30) -> dict:
    cmd = [WACLI] + args + ["--store", STORE, "--json"]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        out = r.stdout.strip()
        if out:
            return json.loads(out)
        return {"success": False, "error": r.stderr.strip() or "no output"}
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "timeout"}
    except json.JSONDecodeError:
        return {"success": False, "error": f"invalid json: {r.stdout[:200]}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def whatsapp_check_status() -> str:
    result = _wacli(["auth", "status"])
    if result.get("success") and result.get("data", {}).get("authenticated"):
        phone = result["data"].get("phone", PHONE)
        return json.dumps({"status": "authenticated", "phone": phone})
    return json.dumps({"status": "unauthenticated", "detail": result.get("error", "unknown")})


async def whatsapp_send_text(to: str, message: str) -> str:
    if not to.startswith("521"):
        to = f"521{to}" if to.startswith("66") else to
    if not to.endswith("@s.whatsapp.net"):
        to = f"{to}@s.whatsapp.net"
    result = _wacli(["send", "text", "--message", message, "--to", to, "--post-send-wait", "3s"])
    return json.dumps(result.get("data", result))


async def whatsapp_send_file(to: str, file_path: str, caption: str = "") -> str:
    if not to.startswith("521"):
        to = f"521{to}" if to.startswith("66") else to
    if not to.endswith("@s.whatsapp.net"):
        to = f"{to}@s.whatsapp.net"
    result = _wacli([
        "send", "file",
        "--file", file_path,
        "--caption", caption,
        "--to", to,
        "--post-send-wait", "5s",
    ])
    return json.dumps(result.get("data", result))


async def whatsapp_send_voice(to: str, file_path: str) -> str:
    if not to.startswith("521"):
        to = f"521{to}" if to.startswith("66") else to
    if not to.endswith("@s.whatsapp.net"):
        to = f"{to}@s.whatsapp.net"
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".mp3":
        with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as tmp:
            ogg_path = tmp.name
        subprocess.run([
            "ffmpeg", "-y", "-i", file_path,
            "-c:a", "libopus", "-b:a", "16k", "-ar", "16000", ogg_path
        ], capture_output=True, timeout=60)
        file_path = ogg_path
    result = _wacli([
        "send", "file", "--file", file_path,
        "--mime", "audio/ogg; codecs=opus", "--ptt",
        "--to", to, "--post-send-wait", "5s",
    ])
    if ext == ".mp3" and os.path.exists(ogg_path):
        os.unlink(ogg_path)
    return json.dumps(result.get("data", result))


TOOLS = {
    "whatsapp_check_status": {
        "name": "whatsapp_check_status",
        "description": "Check if WhatsApp session is authenticated and working",
        "inputSchema": {"type": "object", "properties": {}},
        "handler": whatsapp_check_status,
    },
    "whatsapp_send_text": {
        "name": "whatsapp_send_text",
        "description": "Send a WhatsApp text message to a phone number (Mexico: 662xxxxxxx or full 521662xxxxxxx)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "to": {"type": "string", "description": "Phone number (6622681111 or 5216622681111)"},
                "message": {"type": "string", "description": "Text message content"},
            },
            "required": ["to", "message"],
        },
        "handler": whatsapp_send_text,
    },
    "whatsapp_send_file": {
        "name": "whatsapp_send_file",
        "description": "Send a file (PDF, image, audio, document) via WhatsApp",
        "inputSchema": {
            "type": "object",
            "properties": {
                "to": {"type": "string", "description": "Phone number"},
                "file_path": {"type": "string", "description": "Absolute path to file"},
                "caption": {"type": "string", "description": "Optional caption"},
            },
            "required": ["to", "file_path"],
        },
        "handler": whatsapp_send_file,
    },
    "whatsapp_send_voice": {
        "name": "whatsapp_send_voice",
        "description": "Send a voice note via WhatsApp (auto-converts MP3 to OGG Opus)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "to": {"type": "string", "description": "Phone number"},
                "file_path": {"type": "string", "description": "Path to audio file (MP3 or OGG)"},
            },
            "required": ["to", "file_path"],
        },
        "handler": whatsapp_send_voice,
    },
}
