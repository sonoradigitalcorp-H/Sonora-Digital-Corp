#!/usr/bin/env python3
"""
WACLI MCP Server — WhatsApp messaging.

Usage:
  python3 wacli_server.py              # Run as stdio MCP server
  python3 wacli_server.py --http 8900  # Run as HTTP MCP server

Dependencies: mcp (pip install mcp), ffmpeg, wacli
"""

import json
import os
import sys
import subprocess
import tempfile

WACLI = os.path.expanduser("~/.local/bin/wacli")
STORE = os.path.expanduser("~/.config/ai.opencode.desktop/wacli")


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


def _ensure_to(to: str) -> str:
    to = to.strip()
    if not to.endswith("@s.whatsapp.net"):
        if to.startswith("521"):
            to = f"{to}@s.whatsapp.net"
        elif to.startswith("52"):
            to = f"521{to[2:]}@s.whatsapp.net"
        elif to.startswith("66"):
            to = f"521662{to[3:]}@s.whatsapp.net"
        else:
            to = f"521662{to}@s.whatsapp.net" if len(to) == 7 else f"52{to}@s.whatsapp.net"
    return to


async def handle_check_status() -> str:
    result = _wacli(["auth", "status"])
    if result.get("success") and result.get("data", {}).get("authenticated"):
        return json.dumps({"status": "ok", "phone": result["data"].get("phone", "unknown")})
    return json.dumps({"status": "error", "detail": str(result.get("error", "unauthenticated"))})


async def handle_send_text(to: str, message: str) -> str:
    to = _ensure_to(to)
    result = _wacli(["send", "text", "--message", message, "--to", to, "--post-send-wait", "3s"])
    sent = result.get("data", {}).get("sent", False) if result.get("data") else False
    return json.dumps({"sent": sent, "id": result.get("data", {}).get("id", ""), "to": to, "error": result.get("error")})


async def handle_send_file(to: str, file_path: str, caption: str = "") -> str:
    to = _ensure_to(to)
    if not os.path.exists(file_path):
        return json.dumps({"sent": False, "error": f"file not found: {file_path}"})
    args = ["send", "file", "--file", file_path, "--to", to, "--post-send-wait", "5s"]
    if caption:
        args += ["--caption", caption]
    result = _wacli(args)
    sent = result.get("data", {}).get("sent", False) if result.get("data") else False
    return json.dumps({"sent": sent, "id": result.get("data", {}).get("id", ""), "to": to, "error": result.get("error")})


async def handle_send_voice(to: str, file_path: str) -> str:
    to = _ensure_to(to)
    if not os.path.exists(file_path):
        return json.dumps({"sent": False, "error": f"file not found: {file_path}"})
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
    return json.dumps({"sent": sent, "id": result.get("data", {}).get("id", ""), "to": to, "error": result.get("error")})


TOOL_HANDLERS = {
    "whatsapp_check_status": {
        "description": "Check WhatsApp authentication status",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
        "handler": handle_check_status,
    },
    "whatsapp_send_text": {
        "description": "Send a WhatsApp text message",
        "inputSchema": {
            "type": "object",
            "properties": {
                "to": {"type": "string", "description": "Phone number (10 digits or with country code)"},
                "message": {"type": "string", "description": "Message text"},
            },
            "required": ["to", "message"],
        },
        "handler": handle_send_text,
    },
    "whatsapp_send_file": {
        "description": "Send a file via WhatsApp (PDF, image, audio, document)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "to": {"type": "string", "description": "Phone number"},
                "file_path": {"type": "string", "description": "Absolute path to file"},
                "caption": {"type": "string", "description": "Optional caption"},
            },
            "required": ["to", "file_path"],
        },
        "handler": handle_send_file,
    },
    "whatsapp_send_voice": {
        "description": "Send a voice note (auto-converts MP3 to OGG Opus)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "to": {"type": "string", "description": "Phone number"},
                "file_path": {"type": "string", "description": "Path to MP3 or OGG audio file"},
            },
            "required": ["to", "file_path"],
        },
        "handler": handle_send_voice,
    },
}


# ─── MCP Server (stdio) ────────────────────────────────────────────

def main_stdio():
    """Run as stdio MCP server using JSON-RPC."""
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        msg_id = msg.get("id")
        method = msg.get("method")
        params = msg.get("params", {})

        if method == "initialize":
            response = {
                "jsonrpc": "2.0", "id": msg_id,
                "result": {
                    "protocolVersion": "0.1.0",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "wacli-mcp", "version": "1.0.0"},
                }
            }
        elif method == "notified":
            response = {"jsonrpc": "2.0", "id": msg_id, "result": {}}
        elif method == "tools/list":
            tools = []
            for name, t in TOOL_HANDLERS.items():
                tools.append({"name": name, "description": t["description"], "inputSchema": t["inputSchema"]})
            response = {"jsonrpc": "2.0", "id": msg_id, "result": {"tools": tools}}
        elif method == "tools/call":
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})
            handler = TOOL_HANDLERS.get(tool_name, {}).get("handler")
            if handler:
                try:
                    if tool_name == "whatsapp_check_status":
                        result_text = loop.run_until_complete(handler())
                    elif tool_name == "whatsapp_send_text":
                        result_text = loop.run_until_complete(handler(**tool_args))
                    elif tool_name == "whatsapp_send_file":
                        result_text = loop.run_until_complete(handler(**tool_args))
                    elif tool_name == "whatsapp_send_voice":
                        result_text = loop.run_until_complete(handler(**tool_args))
                    else:
                        result_text = json.dumps({"error": f"unknown tool: {tool_name}"})
                    result_json = json.loads(result_text)
                    response = {
                        "jsonrpc": "2.0", "id": msg_id,
                        "result": {"content": [{"type": "text", "text": json.dumps(result_json, indent=2)}]}
                    }
                except Exception as e:
                    response = {
                        "jsonrpc": "2.0", "id": msg_id,
                        "result": {"content": [{"type": "text", "text": json.dumps({"error": str(e)})}]}
                    }
            else:
                response = {
                    "jsonrpc": "2.0", "id": msg_id,
                    "result": {"content": [{"type": "text", "text": json.dumps({"error": f"tool not found: {tool_name}"})}]}
                }
        elif method == "shutdown":
            response = {"jsonrpc": "2.0", "id": msg_id, "result": None}
            print(json.dumps(response), flush=True)
            break
        else:
            response = {"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32601, "message": f"Method not found: {method}"}}

        print(json.dumps(response), flush=True)


# ─── HTTP Server Mode ──────────────────────────────────────────────

def main_http(port: int = 8901):
    """Run as HTTP MCP server."""
    from http.server import HTTPServer, BaseHTTPRequestHandler
    import asyncio
    import json

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
                        "serverInfo": {"name": "wacli-mcp", "version": "1.0.0"},
                    }
                }
            elif method == "tools/list":
                tools = []
                for name, t in TOOL_HANDLERS.items():
                    tools.append({"name": name, "description": t["description"], "inputSchema": t["inputSchema"]})
                return {"jsonrpc": "2.0", "id": msg_id, "result": {"tools": tools}}
            elif method == "tools/call":
                tool_name = params.get("name")
                tool_args = params.get("arguments", {})
                handler = TOOL_HANDLERS.get(tool_name, {}).get("handler")
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
            pass  # quiet

    server = HTTPServer(("127.0.0.1", port), MCPHandler)
    print(f"wacli MCP server running on http://127.0.0.1:{port}/mcp", file=sys.stderr)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--http":
        port = int(sys.argv[2]) if len(sys.argv) > 2 else 8901
        main_http(port)
    else:
        main_stdio()
