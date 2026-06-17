#!/usr/bin/env python3
"""
Booking Webhook Receiver — recibe solicitudes y notifica al artista vía Telegram/WhatsApp.

Uso: python3 webhook.py
Endpoints:
  POST /booking  — recibe formulario de booking
  POST /confirm  — artista confirma fecha (click en botón)
"""
import json, os, logging
from http.server import HTTPServer, BaseHTTPRequestHandler

HERMES_API = os.getenv("HERMES_API", "http://localhost:8000")
TELEGRAM_BOT = os.getenv("TELEGRAM_BOT", "@hermes_ceo_sdc_bot")
ARTISTA_TELEGRAM = os.getenv("ARTISTA_TELEGRAM", "@hermes_ceo_sdc_bot")
WHATSAPP_NUMBER = os.getenv("WHATSAPP_NUMBER", "526621234567")
PORT = int(os.getenv("PORT", "8766"))

log = logging.getLogger("booking-webhook")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")

def send_telegram(text):
    try:
        import urllib.request
        data = json.dumps({"channel": "telegram", "to": ARTISTA_TELEGRAM, "text": text}).encode()
        req = urllib.request.Request(f"{HERMES_API}/api/send-message", data=data,
                                      headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=10)
    except Exception as e:
        log.error(f"Telegram: {e}")

def send_whatsapp(text):
    try:
        import urllib.request
        data = json.dumps({"channel": "whatsapp", "to": WHATSAPP_NUMBER, "text": text}).encode()
        req = urllib.request.Request(f"{HERMES_API}/api/send-message", data=data,
                                      headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=10)
    except Exception as e:
        log.warning(f"WhatsApp: {e}")

class BookingHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length)) if length else {}

        if self.path == "/booking":
            nombre = body.get("nombre", "Cliente")
            telefono = body.get("telefono", "")
            email = body.get("email", "")
            tipo = body.get("tipo", "No especificado")
            fecha = body.get("fecha", "")
            ubicacion = body.get("ubicacion", "")
            presupuesto = body.get("presupuesto", "No especificado")
            detalles = body.get("detalles", "Ninguno")

            msg = f"""📩 NUEVA SOLICITUD DE BOOKING

👤 Cliente: {nombre}
📱 Teléfono: {telefono}
✉️ Email: {email}
🎭 Tipo: {tipo}
📅 Fecha: {fecha}
📍 Ubicación: {ubicacion}
💰 Presupuesto: {presupuesto}
📝 Detalles: {detalles}

Para ACEPTAR: http://localhost:{PORT}/confirm?ok=1&nombre={nombre}
Para RECHAZAR: http://localhost:{PORT}/confirm?ok=0&nombre={nombre}"""
            send_telegram(msg)
            send_whatsapp(msg)
            log.info(f"Booking de {nombre} — {fecha}")
            self._respond(200, {"status": "sent", "message": "Notificación enviada al artista"})

        elif self.path == "/confirm":
            ok = body.get("ok", True)
            nombre = body.get("nombre", "Cliente")
            if ok:
                msg = f"✅ *Confirmado!* El booking de {nombre} fue aceptado. Te contactamos para detalles."
            else:
                msg = f"❌ El booking de {nombre} fue rechazado. Se notificó al cliente."
            send_telegram(msg)
            self._respond(200, {"status": "confirmed" if ok else "rejected"})

        else:
            self._respond(404, {"error": "Not found"})

    def do_GET(self):
        if self.path.startswith("/confirm"):
            from urllib.parse import urlparse, parse_qs
            params = parse_qs(urlparse(self.path).query)
            ok = params.get("ok", ["0"])[0] == "1"
            nombre = params.get("nombre", ["Cliente"])[0]
            if ok:
                msg = f"✅ *Confirmado!* Booking de {nombre} aceptado."
            else:
                msg = f"❌ Booking de {nombre} rechazado."
            send_telegram(msg)
            self._respond(200, {"status": "ok" if ok else "rejected"})
        else:
            self._respond(200, {"status": "booking-webhook running", "endpoints": ["POST /booking", "GET /confirm", "POST /confirm"]})

    def _respond(self, code, data):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def log_message(self, *a): pass

if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", PORT), BookingHandler)
    log.info(f"Booking webhook on port {PORT}")
    server.serve_forever()
