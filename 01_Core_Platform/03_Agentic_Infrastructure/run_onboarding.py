#!/usr/bin/env python3
"""run_onboarding.py — Entry point unificado para Aztrotech Onboarding Inteligente.

Inicia:
- Webhook server (multi_tenant_webhook.py) en puerto 5289
- Scheduler de recordatorios (leads sin respuesta 24h)
- Health check endpoint
- Logging estructurado

Uso:
    python3 run_onboarding.py                    # defaults
    python3 run_onboarding.py --port 5289        # puerto custom
    python3 run_onboarding.py --tenant aztrotech # tenant específico
"""

import argparse
import json
import logging
import os
import signal
import sys
import threading
import time
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

import pytz

# Paths
BASE = Path(__file__).parent
INFRA = BASE.parent / "03_Agentic_Infrastructure"
sys.path.insert(0, str(INFRA))

from onboarding_engine import OnboardingEngine
from lead_classifier import classify_lead_intent
from lead_intelligence import generate_lead_intelligence
from lead_scoring import calculate_lead_score, get_template_notificacion_cesar
from feedback_loop import FeedbackLoop, FeedbackEvent

HERMOSILLO_TZ = pytz.timezone("America/Hermosillo")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("onboarding")


class OnboardingHandler(BaseHTTPRequestHandler):
    """Handler HTTP para webhook + health check."""

    engine = None
    tenant = "aztrotech"

    def log_message(self, format, *args):
        log.info(f"{self.address_string()} - {format % args}")

    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False, indent=2).encode())

    def do_GET(self):
        if self.path in ["/health", "/status"]:
            stats = self.engine.get_dashboard_stats() if self.engine else {}
            self.send_json({
                "status": "ok",
                "service": "Aztrotech Onboarding Engine",
                "version": "2.0",
                "tenant": self.tenant,
                "uptime": time.time() - START_TIME,
                "stats": stats,
            })
        elif self.path == "/leads":
            leads = self.engine.list_leads(limit=20) if self.engine else []
            self.send_json({"leads": leads, "count": len(leads)})
        elif self.path == "/leads/hoy":
            leads = self.engine.get_leads_hoy() if self.engine else []
            self.send_json({"leads": leads, "count": len(leads)})
        elif self.path.startswith("/lead/"):
            lead_id = self.path.split("/")[-1]
            lead = self.engine.get_lead(lead_id) if self.engine else None
            if lead:
                self.send_json(lead)
            else:
                self.send_json({"error": "Lead no encontrado"}, 404)
        else:
            self.send_json({"error": "Not found"}, 404)

    def do_POST(self):
        if self.path == "/webhook":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode()
            try:
                data = json.loads(body)
            except json.JSONDecodeError:
                self.send_json({"error": "Invalid JSON"}, 400)
                return

            result = self._process_message(data)
            self.send_json(result)

        elif self.path == "/webhook/voice":
            # Para widget voz web
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode()
            try:
                data = json.loads(body)
            except json.JSONDecodeError:
                self.send_json({"error": "Invalid JSON"}, 400)
                return

            result = self._process_voice(data)
            self.send_json(result)

        else:
            self.send_json({"error": "Not found"}, 404)

    def _process_message(self, data: dict) -> dict:
        """Procesa mensaje de texto entrante."""
        bot = data.get("bot", "")
        user_id = str(data.get("user_id", data.get("user", "")))
        message = data.get("message", "")

        log.info(f"[MSG] bot={bot} user={user_id} msg={message[:80]}")

        try:
            # 1. Clasificar intención
            classification = classify_lead_intent(self.tenant, message)
            log.info(f"[CLASSIFY] intent={classification.intencion} score={classification.confianza:.2f}")

            # 2. Ejecutar acción según clasificación
            action = classification.accion_requerida
            campos = classification.campos

            if action == "capture" or classification.intencion == "nuevo_lead":
                # Capturar lead + intelligence
                lead_id, scoring = self.engine.capture_lead(self.tenant, user_id, {
                    **campos,
                    "canal": "telegram",
                    "chat_id": user_id
                })

                # Generar intelligence si tenemos datos suficientes
                lead = self.engine.get_lead(lead_id)
                if lead and (lead.get("empresa") or lead.get("nombre")):
                    intel = generate_lead_intelligence(self.tenant, lead, {
                        "score": scoring.score,
                        "classification": scoring.classification
                    })
                    self.engine.save_intelligence(lead_id, intel.model_dump())

                # Registrar interacción
                self.engine.record_interaction(lead_id, "nuevo_lead", "telegram", metadata={
                    "confianza": classification.confianza
                })

                return {
                    "status": "captured",
                    "lead_id": lead_id,
                    "score": scoring.score,
                    "classification": scoring.classification,
                    "response": classification.respuesta_sugerida,
                    "next_action": scoring.next_action,
                }

            elif action == "schedule":
                lead_id = campos.get("lead_id")
                fecha = campos.get("fecha")
                hora = campos.get("hora")

                if fecha and hora:
                    # Buscar lead existente o crear
                    if not lead_id:
                        leads = self.engine.list_leads(tenant=self.tenant, limit=1)
                        lead_id = leads[0]["id"] if leads else None
                    if not lead_id:
                        lead_id, _ = self.engine.capture_lead(self.tenant, user_id, {
                            **campos, "canal": "telegram", "chat_id": user_id
                        })

                    result = self.engine.schedule_cita(lead_id, fecha, hora)
                    if result["success"]:
                        # Notificar a César
                        self.engine.notify_cesar(lead_id)
                        self.engine.record_interaction(lead_id, "cita_agendada", "telegram")
                        return {
                            "status": "scheduled",
                            "lead_id": lead_id,
                            "fecha": fecha,
                            "hora": hora,
                            "response": classification.respuesta_sugerida
                        }
                    else:
                        return {"status": "error", "error": result["error"]}
                else:
                    return {"status": "need_info", "response": "Necesito fecha y hora para agendar. ¿Qué día y a qué hora?"}

            elif action == "escalar":
                # Escalar a César
                lead_id = campos.get("lead_id")
                if not lead_id:
                    leads = self.engine.list_leads(tenant=self.tenant, limit=1)
                    lead_id = leads[0]["id"] if leads else None
                if not lead_id:
                    lead_id, _ = self.engine.capture_lead(self.tenant, user_id, {
                        "nombre": "Lead escalar", "empresa": "", "servicio": "consulta",
                        "canal": "telegram", "chat_id": user_id
                    })

                self.engine.notify_cesar(lead_id)
                self.engine.record_interaction(lead_id, "escalar", "telegram")
                return {
                    "status": "escalated",
                    "lead_id": lead_id,
                    "response": classification.respuesta_sugerida
                }

            elif action == "generate_asset":
                # Generar asset
                asset_type = classification.asset_type or "imagen"
                return {
                    "status": "asset_request",
                    "asset_type": asset_type,
                    "response": f"Voy a generar un {asset_type} para ti. Un momento..."
                }

            else:
                # Responder con OKF / FAQ
                return {
                    "status": "responded",
                    "response": classification.respuesta_sugerida
                }

        except Exception as e:
            log.error(f"[ERROR] {e}", exc_info=True)
            return {"status": "error", "error": str(e)}

    def _process_voice(self, data: dict) -> dict:
        """Procesa mensaje de voz entrante."""
        bot = data.get("bot", "")
        user_id = str(data.get("user_id", ""))
        audio_path = data.get("audio_path", "")

        log.info(f"[VOICE] bot={bot} user={user_id} audio={audio_path}")

        try:
            from voice_pipeline import process_voice_message
            result = process_voice_message(bot, user_id, audio_path, self.engine, tenant=self.tenant)
            return result
        except Exception as e:
            log.error(f"[VOICE ERROR] {e}", exc_info=True)
            return {"status": "error", "error": str(e)}


def scheduler_recordatorios(engine: OnboardingEngine, interval_hours: int = 24):
    """Scheduler que revisa leads sin respuesta cada N horas."""
    while True:
        try:
            time.sleep(interval_hours * 3600)
            log.info("[SCHEDULER] Revisando leads sin respuesta...")

            leads = engine.list_leads(limit=100)
            now = datetime.now(HERMOSILLO_TZ)

            for lead in leads:
                if lead.get("estado") == "nuevo" and lead.get("classification") in ["WARM", "HOT"]:
                    creado = datetime.fromisoformat(lead.get("creado_en", now.isoformat()))
                    if hasattr(creado, 'tzinfo') and creado.tzinfo is None:
                        creado = UTC_TZ.localize(creado)
                    horas_desde = (now - creado).total_seconds() / 3600

                    if horas_desde > 12:
                        log.info(f"[RE-ENGAGE] Lead {lead['id']} ({lead.get('classification')}) sin respuesta {horas_desde:.0f}h")
                        # TODO: enviar re-engagement automático

        except Exception as e:
            log.error(f"[SCHEDULER ERROR] {e}")
            time.sleep(3600)


START_TIME = time.time()


def main():
    parser = argparse.ArgumentParser(description="Aztrotech Onboarding Engine")
    parser.add_argument("--port", type=int, default=5289)
    parser.add_argument("--tenant", default="aztrotech")
    parser.add_argument("--db", default=None)
    parser.add_argument("--no-scheduler", action="store_true")
    args = parser.parse_args()

    db_path = args.db or str(Path.home() / ".openclaw" / "workspace" / f"leads_{args.tenant}.db")
    engine = OnboardingEngine(db_path, args.tenant)

    OnboardingHandler.engine = engine
    OnboardingHandler.tenant = args.tenant

    # Scheduler
    if not args.no_scheduler:
        t = threading.Thread(target=scheduler_recordatorios, args=(engine,), daemon=True)
        t.start()

    # Server
    server = HTTPServer(("0.0.0.0", args.port), OnboardingHandler)
    log.info(f"[ONBOARDING] {args.tenant} Engine v2 running on port {args.port}")
    log.info(f"[ONBOARDING] Endpoints: POST /webhook, POST /webhook/voice, GET /health, GET /leads")

    def shutdown(sig, frame):
        log.info("[SHUTDOWN] Cerrando...")
        server.shutdown()

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    server.serve_forever()


if __name__ == "__main__":
    main()
