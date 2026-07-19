"""
Notifier Core — Worker que lee eventos y dispara notificaciones.

Modo daemon:
  PYTHONPATH=. python3 -m products.notifier.core

Lee eventos de state/events/events.jsonl y los compara contra las
reglas de notificación. Cuando hay match, entrega por el channel
correspondiente (WhatsApp, Telegram, Email).
"""

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO))

from mcp.servers import wacli_mcp

RULES_FILE = REPO / "state" / "notifier" / "rules.json"
EVENTS_FILE = REPO / "state" / "events" / "events.jsonl"
LOG_FILE = REPO / "state" / "notifier" / "log.jsonl"
SEEN_FILE = REPO / "state" / "notifier" / "seen_events.json"
POLL_INTERVAL = 5


def _load_seen() -> set:
    if not SEEN_FILE.exists():
        return set()
    try:
        with open(SEEN_FILE) as f:
            return set(json.load(f).get("ids", []))
    except Exception:
        return set()


def _save_seen(ids: set) -> None:
    SEEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(SEEN_FILE, "w") as f:
        json.dump({"ids": sorted(ids), "updated": datetime.now(timezone.utc).isoformat()}, f)


def _load_rules() -> list[dict]:
    if not RULES_FILE.exists():
        return []
    try:
        with open(RULES_FILE) as f:
            return json.load(f)
    except Exception:
        return []


def _log_delivery(entry: dict) -> None:
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def _render(template: str, payload: dict) -> str:
    try:
        result = template
        for key, value in payload.items():
            result = result.replace("{{" + key + "}}", str(value))
        return result
    except Exception:
        return template


def _send_whatsapp(to: str, message: str) -> dict:
    try:
        result = json.loads(wacli_mcp.whatsapp_send_text(to, message))
        return result
    except Exception as e:
        return {"sent": False, "error": str(e)}


def _send_telegram(token: str, chat_id: str, message: str) -> dict:
    try:
        import telegram
        bot = telegram.Bot(token=token)
        import asyncio
        result = asyncio.run(bot.send_message(chat_id=chat_id, text=message))
        return {"sent": True, "id": str(result.message_id)}
    except Exception as e:
        return {"sent": False, "error": str(e)}


def _send_email(smtp_host: str, smtp_port: int, from_addr: str, to_addr: str, subject: str, body: str) -> dict:
    try:
        import smtplib
        from email.mime.text import MIMEText
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = from_addr
        msg["To"] = to_addr
        with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as s:
            s.send_message(msg)
        return {"sent": True}
    except Exception as e:
        return {"sent": False, "error": str(e)}


def check_rules(event: dict, rules: list[dict]) -> list[dict]:
    event_type = event.get("event") or event.get("type") or ""
    matches = []
    for rule in rules:
        if not rule.get("enabled"):
            continue
        # Match by exact event type or wildcard
        rule_type = rule.get("event_type", "")
        if rule_type and rule_type != event_type:
            if rule_type.endswith("*") and event_type.startswith(rule_type[:-1]):
                pass  # wildcard match
            elif "*" not in rule_type:
                continue
        matches.append(rule)
    return matches


def deliver(rule: dict, event: dict) -> dict:
    payload = event.get("payload", {})
    payload["event_type"] = event.get("event") or event.get("type", "")
    message = _render(rule.get("template", ""), payload)
    channel = rule.get("channel", "whatsapp")
    recipients = rule.get("recipients", [])

    result = {"rule_id": rule.get("id"), "channel": channel, "deliveries": []}

    for recipient in recipients:
        delivery = {"recipient": recipient, "status": "queued", "error": ""}
        try:
            if channel == "whatsapp":
                resp = _send_whatsapp(recipient, message)
                delivery["status"] = "sent" if resp.get("sent") else "failed"
                delivery["error"] = resp.get("error", "")
            elif channel == "telegram":
                token = os.getenv("TELEGRAM_BOT_TOKEN", "")
                resp = _send_telegram(token, recipient, message)
                delivery["status"] = "sent" if resp.get("sent") else "failed"
                delivery["error"] = resp.get("error", "")
            elif channel == "email":
                host = os.getenv("SMTP_HOST", "localhost")
                port = int(os.getenv("SMTP_PORT", "25"))
                from_addr = os.getenv("SMTP_FROM", "noreply@sonoradigitalcorp.com")
                resp = _send_email(host, port, from_addr, recipient, message[:100], message)
                delivery["status"] = "sent" if resp.get("sent") else "failed"
                delivery["error"] = resp.get("error", "")
            else:
                delivery["status"] = "failed"
                delivery["error"] = f"unknown channel: {channel}"
        except Exception as e:
            delivery["status"] = "failed"
            delivery["error"] = str(e)

        result["deliveries"].append(delivery)
        _log_delivery({
            "rule_id": rule.get("id"),
            "tenant": rule.get("tenant", "default"),
            "event_type": event.get("event") or event.get("type", ""),
            "channel": channel,
            "recipient": recipient,
            "status": delivery["status"],
            "error": delivery.get("error", ""),
            "delivered_at": datetime.now(timezone.utc).isoformat(),
            "created_at": datetime.now(timezone.utc).isoformat(),
        })

    return result


def run_worker(once: bool = False):
    print("[notifier] Worker started", file=sys.stderr)
    seen = _load_seen()

    while True:
        try:
            rules = _load_rules()
            active_rules = [r for r in rules if r.get("enabled")]
            new_events = 0

            if EVENTS_FILE.exists():
                with open(EVENTS_FILE) as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            event = json.loads(line)
                        except json.JSONDecodeError:
                            continue

                        event_id = event.get("type", "") + ":" + event.get("timestamp", "")
                        if event_id in seen:
                            continue
                        seen.add(event_id)

                        matches = check_rules(event, active_rules)
                        for rule in matches:
                            deliver(rule, event)
                            new_events += 1

            if new_events > 0:
                _save_seen(seen)
                print(f"[notifier] Processed {new_events} notifications", file=sys.stderr)

            if once:
                break
            time.sleep(POLL_INTERVAL)

        except KeyboardInterrupt:
            print("[notifier] Stopped", file=sys.stderr)
            _save_seen(seen)
            break
        except Exception as e:
            print(f"[notifier] Error: {e}", file=sys.stderr)
            time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Notifier Worker")
    parser.add_argument("--once", action="store_true", help="Process once and exit")
    args = parser.parse_args()

    if args.once:
        run_worker(once=True)
    else:
        run_worker()
