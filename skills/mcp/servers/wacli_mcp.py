"""
WACLI MCP Server — WhatsApp messaging via wacli.

Tools:
  whatsapp_check_status     — Check authentication status
  whatsapp_send_text        — Send text message
  whatsapp_send_file        — Send file (PDF, image, audio, document)
  whatsapp_send_voice       — Send voice note (auto-converts MP3 to OGG Opus)
  whatsapp_send_audio_thumbnail — Generate and send waveform thumbnail
  whatsapp_create_wa_me_link — Generate wa.me link with optional ref/UTM
  whatsapp_create_qr         — Generate QR code for a wa.me link
  whatsapp_read_qr           — Decode a QR code image
  whatsapp_get_contacts      — List known WhatsApp contacts

Requires: wacli installed at ~/.local/bin/wacli
Store: ~/.config/ai.opencode.desktop/wacli
"""

import json
import os
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

WACLI = os.path.expanduser("~/.local/bin/wacli")
STORE = os.path.expanduser("~/.config/ai.opencode.desktop/wacli")
PHONE = "5216623538272"  # Cuenta autenticada
EVENTS_PATH = Path("state/events/events.jsonl")


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
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "timeout"}
    except json.JSONDecodeError:
        return {"success": False, "error": f"invalid json: {r.stdout[:200]}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def _ensure_to(to: str) -> str:
    to = to.strip()
    if not to.endswith("@s.whatsapp.net"):
        if to.startswith("521"):
            to = f"{to}@s.whatsapp.net"
        elif to.startswith("52"):
            to = f"521{to[2:]}@s.whatsapp.net"
        elif to.startswith("66"):
            to = f"521662{to[3:]}@s.whatsapp.net"
        elif len(to) == 10 and to.startswith("1"):
            # US/Canada fallback
            to = f"1{to}@s.whatsapp.net"
        else:
            # Default: Mexican local 7 digits or full number
            to = f"521662{to}@s.whatsapp.net" if len(to) == 7 else f"52{to}@s.whatsapp.net"
    return to


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
        pass  # events are best-effort


def _result(data: dict) -> str:
    return json.dumps(data, ensure_ascii=False)


async def whatsapp_check_status() -> str:
    result = _wacli(["auth", "status"])
    if result.get("success") and result.get("data", {}).get("authenticated"):
        phone = result["data"].get("phone", PHONE)
        return _result({"status": "authenticated", "phone": phone})
    return _result({"status": "unauthenticated", "detail": result.get("error", "unknown")})


async def whatsapp_send_text(to: str, message: str) -> str:
    to = _ensure_to(to)
    result = _wacli(["send", "text", "--message", message, "--to", to, "--post-send-wait", "3s"])
    sent = result.get("data", {}).get("sent", False) if result.get("data") else False
    msg_id = result.get("data", {}).get("id", "") if result.get("data") else ""
    _emit_event("whatsapp:message:sent", {
        "to": to,
        "type": "text",
        "message": message,
        "sent": sent,
        "message_id": msg_id,
    })
    return _result({"sent": sent, "id": msg_id, "to": to, "error": result.get("error")})


async def whatsapp_send_file(to: str, file_path: str, caption: str = "") -> str:
    to = _ensure_to(to)
    if not os.path.exists(file_path):
        return _result({"sent": False, "error": f"file not found: {file_path}"})
    args = ["send", "file", "--file", file_path, "--to", to, "--post-send-wait", "5s"]
    if caption:
        args += ["--caption", caption]
    result = _wacli(args)
    sent = result.get("data", {}).get("sent", False) if result.get("data") else False
    msg_id = result.get("data", {}).get("id", "") if result.get("data") else ""
    _emit_event("whatsapp:message:sent", {
        "to": to,
        "type": "file",
        "file_path": file_path,
        "caption": caption,
        "sent": sent,
        "message_id": msg_id,
    })
    return _result({"sent": sent, "id": msg_id, "to": to, "error": result.get("error")})


async def whatsapp_send_voice(to: str, file_path: str) -> str:
    to = _ensure_to(to)
    if not os.path.exists(file_path):
        return _result({"sent": False, "error": f"file not found: {file_path}"})
    ext = os.path.splitext(file_path)[1].lower()
    ogg_path = file_path
    cleanup = False
    if ext == ".mp3":
        tmp = tempfile.NamedTemporaryFile(suffix=".ogg", delete=False)
        ogg_path = tmp.name
        tmp.close()
        subprocess.run([
            "ffmpeg", "-y", "-i", file_path,
            "-c:a", "libopus", "-b:a", "16k", "-ar", "16000", ogg_path
        ], capture_output=True, timeout=60)
        cleanup = True
    result = _wacli([
        "send", "file", "--file", ogg_path,
        "--mime", "audio/ogg; codecs=opus", "--ptt",
        "--to", to, "--post-send-wait", "5s",
    ])
    if cleanup and os.path.exists(ogg_path):
        os.unlink(ogg_path)
    sent = result.get("data", {}).get("sent", False) if result.get("data") else False
    msg_id = result.get("data", {}).get("id", "") if result.get("data") else ""
    _emit_event("whatsapp:message:sent", {
        "to": to,
        "type": "voice",
        "file_path": file_path,
        "sent": sent,
        "message_id": msg_id,
    })
    return _result({"sent": sent, "id": msg_id, "to": to, "error": result.get("error")})


async def whatsapp_send_audio_thumbnail(to: str, file_path: str, caption: str = "🎙️ Audio") -> str:
    """Generate a waveform thumbnail and send it as a preview image."""
    to = _ensure_to(to)
    if not os.path.exists(file_path):
        return _result({"sent": False, "error": f"file not found: {file_path}"})

    try:
        from PIL import Image, ImageDraw
    except ImportError:
        return _result({"sent": False, "error": "Pillow not installed"})

    # Generate fake waveform data (no audio analysis yet)
    width, height = 400, 200
    img = Image.new("RGB", (width, height), "#111827")
    draw = ImageDraw.Draw(img)
    bar_count = 40
    bar_width = width // bar_count
    import random
    random.seed(os.path.getsize(file_path))
    for i in range(bar_count):
        h = random.randint(20, height - 20)
        x = i * bar_width + 2
        y = (height - h) // 2
        draw.rectangle([x, y, x + bar_width - 4, y + h], fill="#FF6B35")

    tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    png_path = tmp.name
    tmp.close()
    img.save(png_path, "PNG")

    result = await whatsapp_send_file(to, png_path, caption)
    os.unlink(png_path)
    data = json.loads(result)
    data["thumbnail_type"] = "audio_waveform"
    _emit_event("whatsapp:message:sent", {
        "to": to,
        "type": "audio_thumbnail",
        "file_path": file_path,
        "sent": data.get("sent", False),
        "message_id": data.get("id", ""),
    })
    return _result(data)


async def whatsapp_create_wa_me_link(text: str = "", ref_code: str = "", utm_source: str = "", utm_medium: str = "", utm_campaign: str = "") -> str:
    """Generate a wa.me link for the system WhatsApp number."""
    params = {}
    parts = []
    if ref_code:
        parts.append(ref_code)
    if text:
        parts.append(text)
    if parts:
        params["text"] = " | ".join(parts)
    if utm_source:
        params["utm_source"] = utm_source
    if utm_medium:
        params["utm_medium"] = utm_medium
    if utm_campaign:
        params["utm_campaign"] = utm_campaign

    from urllib.parse import urlencode
    query = urlencode(params)
    link = f"https://wa.me/{PHONE}?{query}" if query else f"https://wa.me/{PHONE}"
    _emit_event("whatsapp:wa_me_link:created", {
        "phone": PHONE,
        "ref_code": ref_code,
        "text": text,
        "link": link,
    })
    return _result({"link": link, "phone": PHONE, "ref_code": ref_code})


async def whatsapp_create_qr(data: str = "", ref_code: str = "", output_path: str = "") -> str:
    """Generate a QR code PNG for a wa.me link or arbitrary data."""
    try:
        import qrcode
    except ImportError:
        return _result({"created": False, "error": "qrcode not installed"})

    if not data:
        data = json.loads(await whatsapp_create_wa_me_link(ref_code=ref_code))
        data = data["link"]

    if not output_path:
        tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        output_path = tmp.name
        tmp.close()

    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#111827", back_color="white")
    img.save(output_path)

    _emit_event("whatsapp:qr:created", {
        "data": data,
        "ref_code": ref_code,
        "output_path": output_path,
    })
    return _result({"created": True, "path": output_path, "data": data})


async def whatsapp_read_qr(file_path: str) -> str:
    """Decode a QR code image. Requires pyzbar or opencv."""
    if not os.path.exists(file_path):
        return _result({"valid": False, "data": None, "error": f"file not found: {file_path}"})

    try:
        from PIL import Image
        img = Image.open(file_path)
    except Exception as e:
        return _result({"valid": False, "data": None, "error": f"invalid image: {e}"})

    # Try pyzbar first
    try:
        from pyzbar import pyzbar
        decoded = pyzbar.decode(img)
        if decoded:
            data = decoded[0].data.decode("utf-8")
            _emit_event("whatsapp:qr:read", {"data": data, "valid": True})
            return _result({"valid": True, "data": data})
    except ImportError:
        pass

    # Fallback: try opencv QRCodeDetector
    try:
        import cv2
        arr = cv2.imread(file_path)
        detector = cv2.QRCodeDetector()
        data, _, _ = detector.detectAndDecode(arr)
        if data:
            _emit_event("whatsapp:qr:read", {"data": data, "valid": True})
            return _result({"valid": True, "data": data})
    except ImportError:
        pass

    _emit_event("whatsapp:qr:read", {"data": None, "valid": False})
    return _result({"valid": False, "data": None, "error": "qr decoder not available or unreadable"})


async def whatsapp_get_contacts() -> str:
    """List known WhatsApp contacts. Returns cached data if wacli doesn't support it."""
    result = _wacli(["contacts", "list"])
    if result.get("success"):
        contacts = result.get("data", [])
        _emit_event("whatsapp:contacts:list", {"count": len(contacts)})
        return _result({"contacts": contacts, "count": len(contacts)})

    # Fallback: return empty list with note
    _emit_event("whatsapp:contacts:list", {"count": 0, "note": "wacli contacts list not supported"})
    return _result({"contacts": [], "count": 0, "note": "wacli contacts list not supported or not authenticated"})


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
    "whatsapp_send_audio_thumbnail": {
        "name": "whatsapp_send_audio_thumbnail",
        "description": "Generate a waveform thumbnail image from an audio file and send it via WhatsApp",
        "inputSchema": {
            "type": "object",
            "properties": {
                "to": {"type": "string", "description": "Phone number"},
                "file_path": {"type": "string", "description": "Path to audio file (MP3 or OGG)"},
                "caption": {"type": "string", "description": "Optional caption"},
            },
            "required": ["to", "file_path"],
        },
        "handler": whatsapp_send_audio_thumbnail,
    },
    "whatsapp_create_wa_me_link": {
        "name": "whatsapp_create_wa_me_link",
        "description": "Generate a wa.me link for the system WhatsApp number with optional referral code and UTM",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Pre-filled message text"},
                "ref_code": {"type": "string", "description": "Referral code (e.g., REF-ABC123)"},
                "utm_source": {"type": "string", "description": "UTM source"},
                "utm_medium": {"type": "string", "description": "UTM medium"},
                "utm_campaign": {"type": "string", "description": "UTM campaign"},
            },
            "required": [],
        },
        "handler": whatsapp_create_wa_me_link,
    },
    "whatsapp_create_qr": {
        "name": "whatsapp_create_qr",
        "description": "Generate a QR code PNG for a wa.me link or arbitrary data",
        "inputSchema": {
            "type": "object",
            "properties": {
                "data": {"type": "string", "description": "Data to encode (optional, defaults to wa.me link)"},
                "ref_code": {"type": "string", "description": "Referral code for wa.me link"},
                "output_path": {"type": "string", "description": "Path to save PNG (optional)"},
            },
            "required": [],
        },
        "handler": whatsapp_create_qr,
    },
    "whatsapp_read_qr": {
        "name": "whatsapp_read_qr",
        "description": "Decode a QR code image (requires pyzbar or opencv)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Path to QR image"},
            },
            "required": ["file_path"],
        },
        "handler": whatsapp_read_qr,
    },
    "whatsapp_get_contacts": {
        "name": "whatsapp_get_contacts",
        "description": "List known WhatsApp contacts from the authenticated session",
        "inputSchema": {"type": "object", "properties": {}},
        "handler": whatsapp_get_contacts,
    },
}


# ─── HTTP Server Mode (optional) ─────────────────────────────────────

def main_http(port: int = 8901):
    """Run as HTTP MCP server for quick health checks."""
    import asyncio
    from http.server import BaseHTTPRequestHandler, HTTPServer

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    class MCPHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == "/health":
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                status = _wacli(["auth", "status"])
                self.wfile.write(json.dumps(status.get("data", status)).encode())
            else:
                self.send_response(404)
                self.end_headers()

        def do_POST(self):
            if self.path == "/mcp":
                content_len = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_len)
                try:
                    msg = json.loads(body)
                except json.JSONDecodeError:
                    self._respond(400, {"jsonrpc": "2.0", "error": {"code": -32700, "message": "Parse error"}})
                    return
                response = self._handle_message(msg)
                self._respond(200, response)
            else:
                self.send_response(404)
                self.end_headers()

        def _handle_message(self, msg):
            msg_id = msg.get("id")
            method = msg.get("method")
            params = msg.get("params", {})
            if method == "initialize":
                return {
                    "jsonrpc": "2.0", "id": msg_id,
                    "result": {
                        "protocolVersion": "0.1.0",
                        "capabilities": {"tools": {}},
                        "serverInfo": {"name": "wacli-mcp", "version": "2.0.0"},
                    }
                }
            elif method == "tools/list":
                tools = []
                for name, t in TOOLS.items():
                    tools.append({"name": name, "description": t["description"], "inputSchema": t["inputSchema"]})
                return {"jsonrpc": "2.0", "id": msg_id, "result": {"tools": tools}}
            elif method == "tools/call":
                tool_name = params.get("name")
                tool_args = params.get("arguments", {})
                handler = TOOLS.get(tool_name, {}).get("handler")
                if handler:
                    try:
                        result_text = loop.run_until_complete(handler(**tool_args))
                        result_json = json.loads(result_text)
                        return {
                            "jsonrpc": "2.0", "id": msg_id,
                            "result": {"content": [{"type": "text", "text": json.dumps(result_json, indent=2)}]}
                        }
                    except Exception as e:
                        return {
                            "jsonrpc": "2.0", "id": msg_id,
                            "result": {"content": [{"type": "text", "text": json.dumps({"error": str(e)})}]}
                        }
                return {
                    "jsonrpc": "2.0", "id": msg_id,
                    "result": {"content": [{"type": "text", "text": json.dumps({"error": f"unknown tool: {tool_name}"})}]}
                }
            return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32601, "message": f"Method not found: {method}"}}

        def _respond(self, code, body):
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(body).encode())

        def log_message(self, fmt, *args):
            pass

    server = HTTPServer(("127.0.0.1", port), MCPHandler)
    print(f"wacli MCP server running on http://127.0.0.1:{port}/mcp", file=os.sys.stderr)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--http":
        port = int(sys.argv[2]) if len(sys.argv) > 2 else 8901
        main_http(port)
    else:
        print("Use --http <port> to run HTTP mode, or import tools directly.", file=sys.stderr)
