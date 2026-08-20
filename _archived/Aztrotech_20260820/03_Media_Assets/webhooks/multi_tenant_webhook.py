#!/usr/bin/env python3
"""Multi-Tenant Webhook — Recibe de todos los bots y enruta a agentes correctos.

Este webhook puede servir para:
- WhatsApp Business API (si tienes)
- Telegram Bot API forwarding
- Pruebas locales con Flask/FastAPI

Uso directo: curl -X POST http://localhost:5289/webhook -d '{"bot":"Aztro_tech_bot","message":"hola"}'
"""
import os, sys, json
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from datetime import datetime

# Agregar paths necesarios
sys.path.insert(0, str(Path(__file__).parent.parent / "Scripts"))

try:
    from tenant_router import route_by_bot_name, init_registry, load_registry
except ImportError:
    # Fallback simple
    init_registry = lambda: None
    load_registry = lambda: {}
    def route_by_bot_name(bot, user, msg, media=None):
        return {}

TENANT_REGISTRY_PATH = Path.home() / ".openclaw" / "workspace" / "tenant_registry.json"


class WebhookHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        print(f"[Webhook] {datetime.utcnow().isoformat()} - {format % args}")

    def send_json_response(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())

    def do_POST(self):
        if self.path == "/webhook" or self.path == "/":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode()
            try:
                data = json.loads(body)
            except json.JSONDecodeError:
                self.send_json_response({"error": "Invalid JSON"}, 400)
                return

            # Extraer campos
            bot_name = data.get("bot") or data.get("bot_name", "").replace("@", "")
            user_id = data.get("user_id") or data.get("user", 0)
            message = data.get("message", "")
            media_path = data.get("media_path") or data.get("media")

            # Route to appropriate tenant
            result = route_by_bot_name(bot_name, user_id, message, media_path)
            self.send_json_response({
                "status": "routed",
                "tenant": result.get("tenant_id"),
                "agent": result.get("agent_id"),
                "user": user_id,
                "message": message[:50] + "..." if len(message) > 50 else message
            })
        else:
            self.send_json_response({"error": "Not found"}, 404)

    def do_GET(self):
        if self.path == "/health" or self.path == "/status":
            self.send_json_response({
                "status": "ok",
                "registry": str(TENANT_REGISTRY_PATH),
                "tenants": list(load_registry().keys()) if TENANT_REGISTRY_PATH.exists() else []
            })
        else:
            self.send_json_response({"error": "Not found"}, 404)


def run_server(port=5289):
    init_registry()
    server = HTTPServer(("0.0.0.0", port), WebhookHandler)
    print(f"[WEBHOOK] Multi-tenant server running on port {port}")
    print(f"[WEBHOOK] Endpoints: POST /webhook, GET /health")
    server.serve_forever()


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Multi-Tenant Webhook")
    ap.add_argument("--port", type=int, default=5289, help="Port to listen on")
    args = ap.parse_args()
    run_server(args.port)