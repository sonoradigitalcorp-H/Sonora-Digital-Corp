"""wacli skill for Hermes - Send WhatsApp messages/voice via wacli CLI."""
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

WACLI_BIN = os.environ.get("WACLI_BIN", "/home/mystic/wacli")
WACLI_STORE = os.environ.get("WACLI_STORE", "/home/mystic/.wacli")

def _run_wacli(args: list) -> tuple[bool, str]:
    """Run wacli command and return (success, output)."""
    cmd = [WACLI_BIN, "--store", WACLI_STORE] + args
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        return result.returncode == 0, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return False, "timeout"
    except Exception as e:
        return False, str(e)

def send_whatsapp_text(phone: str, text: str) -> dict:
    """Send a text message via WhatsApp."""
    # Normalize phone to JID format
    digits = "".join(c for c in phone if c.isdigit())
    if len(digits) == 10:
        digits = "52" + digits
    elif len(digits) == 11 and digits.startswith("1"):
        digits = "52" + digits[1:]
    jid = f"{digits}@s.whatsapp.net"
    
    success, output = _run_wacli(["send", "text", "--to", jid, "--message", text])
    return {"success": success, "output": output.strip(), "to": jid}

def send_whatsapp_voice(phone: str, audio_path: str) -> dict:
    """Send a voice message (OGG/Opus) via WhatsApp."""
    digits = "".join(c for c in phone if c.isdigit())
    if len(digits) == 10:
        digits = "52" + digits
    elif len(digits) == 11 and digits.startswith("1"):
        digits = "52" + digits[1:]
    jid = f"{digits}@s.whatsapp.net"
    
    if not Path(audio_path).exists():
        return {"success": False, "error": f"audio not found: {audio_path}", "to": jid}
    
    success, output = _run_wacli(["send", "voice", "--to", jid, "--file", audio_path])
    return {"success": success, "output": output.strip(), "to": jid}

def send_whatsapp_document(phone: str, file_path: str, caption: str = "") -> dict:
    """Send a document via WhatsApp."""
    digits = "".join(c for c in phone if c.isdigit())
    if len(digits) == 10:
        digits = "52" + digits
    elif len(digits) == 11 and digits.startswith("1"):
        digits = "52" + digits[1:]
    jid = f"{digits}@s.whatsapp.net"
    
    if not Path(file_path).exists():
        return {"success": False, "error": f"file not found: {file_path}", "to": jid}
    
    args = ["send", "document", "--to", jid, "--file", file_path]
    if caption:
        args += ["--caption", caption]
    success, output = _run_wacli(args)
    return {"success": success, "output": output.strip(), "to": jid}

def send_whatsapp_image(phone: str, image_path: str, caption: str = "") -> dict:
    """Send an image via WhatsApp."""
    digits = "".join(c for c in phone if c.isdigit())
    if len(digits) == 10:
        digits = "52" + digits
    elif len(digits) == 11 and digits.startswith("1"):
        digits = "52" + digits[1:]
    jid = f"{digits}@s.whatsapp.net"
    
    if not Path(image_path).exists():
        return {"success": False, "error": f"image not found: {image_path}", "to": jid}
    
    args = ["send", "image", "--to", jid, "--file", image_path]
    if caption:
        args += ["--caption", caption]
    success, output = _run_wacli(args)
    return {"success": success, "output": output.strip(), "to": jid}

def check_auth() -> dict:
    """Check if wacli is authenticated."""
    success, output = _run_wacli(["doctor"])
    return {"authenticated": "AUTHENTICATED" in output and "true" in output,
            "output": output.strip()}

# Tool definitions for Hermes
TOOLS = {
    "send_whatsapp_text": {
        "description": "Send a WhatsApp text message",
        "parameters": {
            "type": "object",
            "properties": {
                "phone": {"type": "string", "description": "Phone number (e.g., 5216623538272)"},
                "text": {"type": "string", "description": "Message text"}
            },
            "required": ["phone", "text"]
        }
    },
    "send_whatsapp_voice": {
        "description": "Send a WhatsApp voice message (OGG/Opus)",
        "parameters": {
            "type": "object",
            "properties": {
                "phone": {"type": "string", "description": "Phone number"},
                "audio_path": {"type": "string", "description": "Path to OGG audio file"}
            },
            "required": ["phone", "audio_path"]
        }
    },
    "send_whatsapp_document": {
        "description": "Send a WhatsApp document",
        "parameters": {
            "type": "object",
            "properties": {
                "phone": {"type": "string"},
                "file_path": {"type": "string"},
                "caption": {"type": "string", "default": ""}
            },
            "required": ["phone", "file_path"]
        }
    },
    "send_whatsapp_image": {
        "description": "Send a WhatsApp image",
        "parameters": {
            "type": "object",
            "properties": {
                "phone": {"type": "string"},
                "image_path": {"type": "string"},
                "caption": {"type": "string", "default": ""}
            },
            "required": ["phone", "image_path"]
        }
    },
    "check_whatsapp_auth": {
        "description": "Check WhatsApp authentication status",
        "parameters": {"type": "object", "properties": {}}
    }
}