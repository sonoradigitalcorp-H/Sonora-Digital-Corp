#!/usr/bin/env python3
"""demo_server.py — STAGING SANITIZADO para César (Aztrotech).

Aísla el workspace interno: expone SOLO health limpio y respuestas de
demostración. NUNCA: registry de tenants, rutas de archivos, tracebacks,
logs crudos, prompts internos ni mensajes de debug.

Uso:
    python3 demo_server.py --port 5290
    # o como systemd user: sdc-aztrotech-demo.service

Endpoints:
    GET  /status   → health limpio (para César / dashboards)
    GET  /         → landing demo
    POST /webhook  → demo de conversación (responde neutro, sin internals)
"""
import json
import os
import sys
import logging
from datetime import datetime, timezone
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

# ── Config ──────────────────────────────────────────────────────────────
PORT = int(os.environ.get("DEMO_PORT", "5290"))
TENANT_NAME = "aztrotech"
BOT_NAME = "Aztro_tech_bot"
LEDGER_PATH = Path(os.environ.get("DEMO_LEDGER", str(Path.home() / ".openclaw" / "logs" / "demo-ledger.jsonl")))

# Logging SOLO a archivo local (permisos 600, ~/.openclaw/logs = solo mystic)
LOG_PATH = Path(os.environ.get("DEMO_LOG", str(Path.home() / ".openclaw" / "logs" / "demo-service.log")))
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.FileHandler(LOG_PATH, encoding="utf-8")],
)
log = logging.getLogger("demo")


class DemoHandler(BaseHTTPRequestHandler):
    """Servidor demo: devuelve SOLO datos limpios. Nunca internals."""

    # ── Silenciar log de requests por defecto (los controlamos nosotros) ──
    def log_message(self, fmt, *args):
        log.info("http %s - %s", self.address_string(), fmt % args)

    # ── Helpers ──────────────────────────────────────────────────────────
    def _send(self, payload: dict, status: int = 200):
        body = json.dumps(payload, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _record(self, kind: str, detail: str = ""):
        """Registro local privado (solo MYSTIC lee esto). Nunca se expone."""
        try:
            with LEDGER_PATH.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps({
                    "ts": datetime.now(timezone.utc).isoformat(),
                    "kind": kind,
                    "detail": detail,
                }, ensure_ascii=False) + "\n")
        except Exception:  # nunca romper el server por el ledger
            log.exception("ledger write failed")

    # ── GET ──────────────────────────────────────────────────────────────
    def do_GET(self):
        if self.path in ("/status", "/health", "/healthz"):
            self._send({
                "status": "operativo",
                "servicio": "Asistente Virtual Aztrotech",
                "bot": BOT_NAME,
                "canal": "Telegram",
                "atencion": "24/7",
                "ts": datetime.now(timezone.utc).isoformat(),
            })
            self._record("status_check")
        elif self.path in ("/", "/landing"):
            self._send({
                "name": "Asistente Virtual Aztrotech",
                "tagline": "Tu Empleado Digital, disponible 24/7",
                "acceso": "Busca @Aztro_tech_bot en Telegram",
                "demo_webhook": "POST /webhook",
            })
        else:
            self._send({"error": "ruta no encontrada"}, 404)

    # ── POST ─────────────────────────────────────────────────────────────
    def do_POST(self):
        if self.path not in ("/webhook", "/"):
            self._send({"error": "ruta no encontrada"}, 404)
            return

        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length).decode("utf-8", errors="replace") if length else ""
        self._record("incoming", raw[:200])

        try:
            data = json.loads(raw or "{}")
        except json.JSONDecodeError:
            # Respuesta limpia SIEMPRE: nunca exponer el error técnico
            self._record("bad_json", raw[:200])
            self._send({
                "respuesta": "No entendí el mensaje. Escríbeme normal y con gusto te ayudo.",
                "next": "Escribe 'hola' para comenzar.",
            }, 400)
            return

        message = str(data.get("message", "")).strip()
        if not message:
            self._send({
                "respuesta": "¿En qué puedo ayudarte? Puedo darte un diagnóstico IA gratuito, cotizarte un plan o agendar una llamada.",
            })
            return

        # Demo: respuesta de ejemplo neutral (la producción real enruta
        # vía el agente cesar de OpenClaw — aquí NO se expone nada interno)
        low = message.lower()
        if any(k in low for k in ("diagnóstico", "diagnostico", "consulta")):
            reply = "¡Claro! Agenda tu Diagnóstico IA Gratuito de 30 minutos y armamos un plan a tu medida."
        elif any(k in low for k in ("precio", "costo", "cotiza", "cuánto", "cuanto", "$")):
            reply = "Con gusto te cotizo: el Empleado Digital va de $999 a $3,999 USD según el plan. ¿Quieres el detalle?"
        elif any(k in low for k in ("hola", "buenas", "hello", "hi")):
            reply = "¡Hola! Soy el asistente virtual de Aztrotech. Cuéntame, ¿qué necesitas hoy?"
        else:
            reply = "Entiendo. Un asesor de Aztrotech te atenderá con detalle en breve. ¿Te dejo agendada una llamada?"

        self._record("replied", reply[:200])
        self._send({
            "respuesta": reply,
            "next": "Para una conversación completa escribe al bot @Aztro_tech_bot en Telegram.",
        })

    # ── Seguridad: ante cualquier excepción NO filtrar traceback ─────────
    def handle_one_request(self):
        try:
            super().handle_one_request()
        except (ConnectionError, BrokenPipeError):
            pass
        except Exception as exc:
            log.exception("request failed (sanitized)")
            try:
                self._send({"error": "error interno del servicio"}, 500)
            except Exception:
                pass


def run_server(port: int = PORT, host: str = "0.0.0.0"):
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    server = HTTPServer((host, port), DemoHandler)
    log.info("demo server up on %s:%s", host, port)
    print(f"[DEMO] Servidor demo (sanitizado) en http://{host}:{port} — /status")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        log.info("demo server down")


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Demo sanitizado Aztrotech")
    ap.add_argument("--port", type=int, default=PORT)
    ap.add_argument("--host", default="0.0.0.0")
    args = ap.parse_args()
    run_server(args.port, args.host)