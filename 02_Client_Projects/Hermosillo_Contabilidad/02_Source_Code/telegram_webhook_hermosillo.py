#!/usr/bin/env python3
"""Telegram Webhook — Hermosillo Contabilidad (@HermosilloCont_bot)

Recibe Updates de Telegram (webhook o polling), identifica tenant por token,
clasifica intención (nemotron free), ejecuta motor determinista y responde.

Modo webhook:  POST /webhook/<bot_token>  (Telegram envía updates aquí)
Modo polling:  python3 telegram_webhook_hermosillo.py --poll  (getUpdates, para test local)

SDD 0006 — T1.5. Regla: NUNCA inventar precios, derivar a Nathaly.
"""

import os
import sys
import json
import argparse
import urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(BASE / "01_Core_Platform" / "05_Shared_Libraries" / "SDK_Python"))
sys.path.insert(0, str(Path.home() / ".hermes" / "tenants"))

# Token del bot desde ~/.hermes/.env (NUNCA hardcodear)
TOKEN = os.environ.get("TELEGRAM_HERMOSILLOCONT_TOKEN", "")
API = f"https://api.telegram.org/bot{TOKEN}"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lead_classifier_hermosillo import classify_intent_hermosillo, LeadClassificationHC  # noqa: E402
from onboarding_hermosillo import OnboardingHermosillo  # noqa: E402

from tenant_router import get_tenant_for_token, init_registry  # noqa: E402

# DB del motor determinista (SQLite leads_hermosillo_cont.db)
DB_PATH = BASE / "01_Core_Platform" / "03_Agentic_Infrastructure" / "Databases" / "leads_hermosillo_cont.db"
ENGINE = OnboardingHermosillo(str(DB_PATH))


def telegram_call(method: str, payload: dict) -> dict:
    """Llama a la Bot API de Telegram."""
    req = urllib.request.Request(
        f"{API}/{method}",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read())
    except Exception as e:
        print(f"[TELEGRAM] {method} error: {e}")
        return {"ok": False, "error": str(e)}


def handle_update(update: dict) -> dict:
    """Procesa un Update de Telegram: mensaje → clasificar → motor → responder."""
    message = update.get("message") or update.get("edited_message") or {}
    chat = message.get("chat", {})
    chat_id = chat.get("id")
    text = message.get("text", "").strip()

    if not chat_id or not text:
        return {"ok": False, "reason": "sin chat_id o texto"}

    # 1. Clasificar intención (nemotron free + fallback pagado)
    cls = classify_intent_hermosillo("hermosillo-cont", text)
    print(f"[CLASSIFY] {cls.intencion} (conf={cls.confianza}) accion={cls.accion_requerida}")

    # 2. Motor determinista según acción
    reply = cls.respuesta_sugerida
    result = {"intencion": cls.intencion, "accion": cls.accion_requerida, "campos": cls.campos}

    if cls.accion_requerida == "capture":
        r = ENGINE.registrar_lead(str(chat_id), cls.campos)
        result["lead"] = {k: v for k, v in r.items() if k in ("id", "score", "classification", "nombre", "negocio", "servicio")}
        if r.get("classification") == "HOT":
            # Lead HOT → notificar a Nathaly (chat_id en env)
            nathaly_chat = os.environ.get("NATHALY_CHAT_ID", "")
            if nathaly_chat:
                notif = ENGINE.get_template_notificacion(r)
                telegram_call("sendMessage", {"chat_id": nathaly_chat, "text": notif})
        if r.get("nombre"):
            reply = f"¡Listo {r['nombre']}! Quedaste registrado. Te contacta Nathaly pronto. 🙌"
    elif cls.accion_requerida == "schedule":
        r = ENGINE.agendar_cita(str(chat_id), cls.campos.get("fecha", ""), cls.campos.get("hora", ""))
        result["cita"] = r
        if r.get("ok"):
            reply = f"¡Cita agendada para el {r.get('fecha')} a las {r.get('hora')}! Te confirmamos. 📅"
        else:
            reply = f"Lo siento, {r.get('error','no pude agendar')}. ¿Quieres otra fecha u hora?"
    elif cls.accion_requerida == "escalar":
        nathaly_chat = os.environ.get("NATHALY_CHAT_ID", "")
        if nathaly_chat:
            telegram_call("sendMessage", {
                "chat_id": nathaly_chat,
                "text": f"🔔 ESCALACIÓN de chat {chat_id}: \"{text[:200]}\""
            })
        reply = "Te paso con Nathaly directamente, en un momento te contacta. 🙌"

    # 3. Responder al lead
    telegram_call("sendMessage", {"chat_id": chat_id, "text": reply})
    result["respuesta"] = reply
    return {"ok": True, **result}


class WebhookHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print(f"[WEBHOOK] {datetime.utcnow().isoformat()} - {fmt % args}")

    def send_json(self, data, status=200):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        # Ruta: /webhook/<bot_token>
        if not self.path.startswith("/webhook/"):
            self.send_json({"ok": False, "error": "Not found"}, 404)
            return
        length = int(self.headers.get("Content-Length", 0))
        try:
            update = json.loads(self.rfile.read(length).decode())
        except json.JSONDecodeError:
            self.send_json({"ok": False, "error": "Invalid JSON"}, 400)
            return
        result = handle_update(update)
        self.send_json(result)

    def do_GET(self):
        if self.path == "/health":
            self.send_json({"status": "ok", "tenant": "hermosillo-cont", "bot": "@HermosilloCont_bot"})
        else:
            self.send_json({"ok": False, "error": "Not found"}, 404)


def run_webhook(port: int):
    init_registry()
    server = HTTPServer(("0.0.0.0", port), WebhookHandler)
    print(f"[WEBHOOK] Hermosillo Cont escuchando en :{port} (POST /webhook/<token>)")
    server.serve_forever()


def run_polling():
    """Modo polling: getUpdates — para test local sin URL pública."""
    init_registry()
    print("[POLLING] Leyendo updates del bot @HermosilloCont_bot...")
    offset = 0
    while True:
        try:
            req = urllib.request.Request(
                f"{API}/getUpdates?timeout=25&offset={offset}&allowed_updates=[\"message\"]"
            )
            with urllib.request.urlopen(req, timeout=35) as resp:
                data = json.loads(resp.read())
            for upd in data.get("result", []):
                offset = upd["update_id"] + 1
                handle_update(upd)
        except KeyboardInterrupt:
            print("\n[POLLING] Detenido.")
            break
        except Exception as e:
            print(f"[POLLING] error: {e}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Webhook Telegram Hermosillo Cont")
    ap.add_argument("--port", type=int, default=5291, help="Puerto webhook (default 5291)")
    ap.add_argument("--poll", action="store_true", help="Modo polling (getUpdates)")
    args = ap.parse_args()
    if args.poll:
        run_polling()
    else:
        run_webhook(args.port)