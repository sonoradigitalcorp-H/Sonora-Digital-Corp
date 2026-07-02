#!/usr/bin/env python3
"""AgenteNotifier — escucha Redis Stream por eventos CRITICAL y envia Telegram.

Uso: python3 apps/agents/notifier_agent.py [--watch]
"""
import argparse
import json
import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE / "apps" / "jarvis" / "src"))

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("agent.notifier")

REDIS_STREAM = "agent:messages"
CONSUMER_GROUP = "notifier-group"
CONSUMER_NAME = "notifier-1"

TELEGRAM_TOKEN = ""
TELEGRAM_CHAT = ""


def load_credentials():
    """Load Telegram credentials from .env file or env vars."""
    global TELEGRAM_TOKEN, TELEGRAM_CHAT

    TELEGRAM_TOKEN = (__import__("os").environ.get("ABE_FENIX_BOT_TOKEN") or "").strip()
    TELEGRAM_CHAT = (__import__("os").environ.get("ABE_TELEGRAM_CHAT") or "").strip()

    if TELEGRAM_TOKEN and TELEGRAM_CHAT:
        return

    env_path = BASE / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if line.startswith("ABE_FENIX_BOT_TOKEN="):
                TELEGRAM_TOKEN = line.split("=", 1)[1].strip().strip('"\'')
            elif line.startswith("ABE_TELEGRAM_CHAT="):
                TELEGRAM_CHAT = line.split("=", 1)[1].strip().strip('"\'')


def send_telegram(container: str, event_type: str, details: str = ""):
    """Send critical alert to Telegram."""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT:
        log.warning("Telegram not configured")
        return

    icons = {"container_critical": "🔴", "healing_failure": "❌", "healing_escalated": "⚠️"}
    icon = icons.get(event_type, "🔔")

    message = (
        f"{icon} <b>AGENTE: {event_type}</b>\n"
        f"<code>{container}</code>\n"
        f"{details}\n"
        f"Servidor: sdc-prod (149.56.46.173)\n"
        f"Fuente: {__import__('socket').gethostname()}"
    )

    try:
        import httpx
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        resp = httpx.post(url, json={
            "chat_id": TELEGRAM_CHAT,
            "text": message,
            "parse_mode": "HTML",
        }, timeout=15)
        if resp.status_code == 200:
            log.info(f"Telegram sent for {container}")
        else:
            log.warning(f"Telegram error: {resp.status_code} {resp.text[:100]}")
    except Exception as e:
        log.warning(f"Telegram send failed: {e}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--watch", action="store_true", help="Loop escuchando Redis Stream")
    args = parser.parse_args()

    load_credentials()

    try:
        import redis as redis_lib
    except ImportError:
        log.error("redis library not installed")
        sys.exit(1)

    r = redis_lib.Redis(host="localhost", port=6379, db=0, socket_timeout=5, password="sdc2026prod", decode_responses=True)

    try:
        r.xgroup_create(REDIS_STREAM, CONSUMER_GROUP, id="0", mkstream=True)
    except redis_lib.ResponseError as e:
        if "BUSYGROUP" not in str(e):
            log.warning(f"Redis group error: {e}")

    log.info(f"Watching for CRITICAL events on {REDIS_STREAM}")

    while True:
        try:
            events = r.xreadgroup(CONSUMER_GROUP, CONSUMER_NAME, {REDIS_STREAM: ">"}, count=10, block=5000)
            if events:
                for stream_name, messages in events:
                    for msg_id, data in messages:
                        decoded = {k.decode() if isinstance(k, bytes) else k:
                                   v.decode() if isinstance(v, bytes) else v
                                   for k, v in data.items()}
                        etype = decoded.get("type", "")
                        container = decoded.get("container", "?")
                        details = decoded.get("details", "")

                        if etype in ("container_critical", "healing_failure", "healing_escalated"):
                            log.warning(f"CRITICAL: {etype} for {container}")
                            send_telegram(container, etype, details)

                        r.xack(REDIS_STREAM, CONSUMER_GROUP, msg_id)
        except Exception as e:
            log.error(f"Error: {e}")

        if not args.watch:
            break
        time.sleep(1)

    r.close()


if __name__ == "__main__":
    main()
