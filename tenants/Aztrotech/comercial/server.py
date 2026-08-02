#!/usr/bin/env python3
"""AztroTech Portal + API Proxy — Sirve portal white-label y proxy de chat."""
import json, os
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import urllib.request
import ssl

PORT = int(os.environ.get("PORT", 8080))
API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
MODEL = "deepseek/deepseek-chat"
DIR = Path(__file__).parent / "portal"

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIR), **kwargs)
    
    def do_POST(self):
        if self.path == "/api/chat":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))
            payload = json.dumps({
                "model": MODEL,
                "messages": body.get("messages", []),
            }).encode()
            req = urllib.request.Request(
                "https://openrouter.ai/api/v1/chat/completions",
                data=payload,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {API_KEY}",
                }
            )
            try:
                resp = urllib.request.urlopen(req, timeout=120, context=ssl._create_unverified_context())
                data = json.loads(resp.read())
                self._json(200, data)
            except Exception as e:
                self._json(500, {"error": str(e)})
        else:
            self.send_error(404)
    
    def _json(self, s, d):
        self.send_response(s)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(d).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
    
    def log_message(self, fmt, *a):
        pass

if __name__ == "__main__":
    if not API_KEY:
        print("⚠️  OPENROUTER_API_KEY no configurada")
        exit(1)
    print(f"✦ AztroTech Portal → http://localhost:{PORT}/mystic.html")
    print(f"✦ Chat API → http://localhost:{PORT}/api/chat")
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    server.serve_forever()
