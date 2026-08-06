"""Ops Agent → Supabase + RabbitMQ emitter.
Empuja eventos de monitoreo a Supabase Realtime y RabbitMQ.
"""
import json
import logging
import os
import subprocess
from datetime import datetime, timezone

log = logging.getLogger("ops.emitter")

SUPABASE_URL = os.environ.get("SUPABASE_URL", "http://localhost:8000")
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")
RABBITMQ_API = os.environ.get("RABBITMQ_API", "http://localhost:15672")
RABBITMQ_USER = os.environ.get("RABBITMQ_USER", "sdc")
RABBITMQ_PASS = os.environ.get("RABBITMQ_PASS", os.environ.get("RABBITMQ_DEFAULT_PASS", ""))


def emit_to_supabase(event_type: str, payload: dict, severity: str = "info"):
    if not SUPABASE_SERVICE_KEY:
        return

    try:
        import httpx

        r = httpx.post(
            f"{SUPABASE_URL}/rest/v1/agent_events",
            headers={
                "apikey": SUPABASE_SERVICE_KEY,
                "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
                "Content-Type": "application/json",
                "Prefer": "return=minimal",
            },
            json={
                "event_type": event_type,
                "payload": payload,
                "severity": severity,
            },
            timeout=5,
        )
        if r.is_success:
            log.debug("Supabase event: %s", event_type)
    except Exception as e:
        log.debug("Supabase emit failed: %s", e)


def emit_to_rabbitmq(event_type: str, payload: dict):
    if not RABBITMQ_PASS:
        return

    try:
        exchange = "sdc.topic"
        routing_key = f"event.{event_type}"

        body = json.dumps({"type": event_type, "payload": payload, "timestamp": datetime.now(timezone.utc).isoformat()})

        r = subprocess.run(
            [
                "curl", "-s", "-u", f"{RABBITMQ_USER}:{RABBITMQ_PASS}",
                "-X", "POST",
                f"{RABBITMQ_API}/api/exchanges/%2F/{exchange}/publish",
                "-H", "Content-Type: application/json",
                "-d", json.dumps({
                    "properties": {"delivery_mode": 2, "content_type": "application/json"},
                    "routing_key": routing_key,
                    "payload": body,
                    "payload_encoding": "string",
                }),
            ],
            capture_output=True, text=True, timeout=5,
        )
        if r.returncode == 0:
            log.debug("RabbitMQ event: %s", event_type)
    except Exception as e:
        log.debug("RabbitMQ emit failed: %s", e)


def emit_service_status(services: dict):
    """Update service_status table in Supabase with current state."""
    if not SUPABASE_SERVICE_KEY:
        return

    try:
        import httpx

        for name, status in services.items():
            if name in ("disk", "disk_status"):
                continue

            state = "operational"
            if "down" in status or "not_found" in status:
                state = "down"
            elif "degraded" in status:
                state = "degraded"

            # Upsert
            r = httpx.patch(
                f"{SUPABASE_URL}/rest/v1/service_status?name=eq.{name}",
                headers={
                    "apikey": SUPABASE_SERVICE_KEY,
                    "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
                    "Content-Type": "application/json",
                    "Prefer": "return=minimal",
                },
                json={"status": state, "last_checked": datetime.now(timezone.utc).isoformat()},
                timeout=5,
            )
            if r.status_code == 404:
                # Insert if not exists
                httpx.post(
                    f"{SUPABASE_URL}/rest/v1/service_status",
                    headers={
                        "apikey": SUPABASE_SERVICE_KEY,
                        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
                        "Content-Type": "application/json",
                    },
                    json={"name": name, "status": state},
                    timeout=5,
                )
    except Exception as e:
        log.debug("Supabase status update failed: %s", e)
