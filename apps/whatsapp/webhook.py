#!/usr/bin/env python3
"""
WhatsApp Webhook — Persistent listener for incoming WhatsApp messages.

This module polls the local wacli message store and emits events to the
Sonora event bus. It is designed to run as a long-lived process (systemd
service or tmux session).

Events emitted:
  whatsapp:message:received
  whatsapp:catalog:requested
  system:whatsapp:reconnected
  system:whatsapp:disconnected

Usage:
  python3 -m apps.whatsapp.webhook
  python3 apps/whatsapp/webhook.py --interval 5
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Allow imports from repo root
REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO))

EVENTS_FILE = REPO / "state" / "events" / "events.jsonl"


def emit_event(event_type: str, payload: dict) -> None:
    """Emit event as JSON line (not YAML like the pipeline)."""
    EVENTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "event": event_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "payload": payload,
    }
    with open(EVENTS_FILE, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

WACLI = os.environ.get("WACLI_PATH") or os.path.expanduser("~/.local/bin/wacli")
if not os.path.exists(WACLI):
    WACLI = "/usr/local/bin/wacli"
STORE = os.environ.get("WACLI_STORE") or os.path.expanduser("~/.config/ai.opencode.desktop/wacli")
SEEN_PATH = Path("state/whatsapp/seen_messages.json")
FOUNDER_INBOX = Path("state/inbox/founder.jsonl")
DEFAULT_INTERVAL = 2  # seconds (reduced from 5 for lower latency)
BACKOFF_MAX = 60  # seconds

# Founder's phone number — set via FOUNDER_PHONE env var
# This is YOUR number. When you send a WhatsApp, it goes to the inbox.
FOUNDER_PHONE = os.environ.get("FOUNDER_PHONE", "")


def _wacli(args: list, timeout: int = 30) -> dict:
    if not os.path.exists(WACLI):
        return {"success": False, "error": "wacli not found"}
    cmd = [WACLI] + args + ["--store", STORE, "--json", "--read-only"]
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


def _load_seen() -> set:
    SEEN_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not SEEN_PATH.exists():
        return set()
    try:
        with open(SEEN_PATH) as f:
            data = json.load(f)
        return set(data.get("ids", []))
    except Exception:
        return set()


def _save_seen(seen: set) -> None:
    SEEN_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(SEEN_PATH, "w") as f:
        json.dump({"ids": sorted(seen), "updated": datetime.now(timezone.utc).isoformat()}, f)


def _normalize_sender(sender: str) -> str:
    """Return clean phone number from JID."""
    if "@" in sender:
        sender = sender.split("@", 1)[0]
    if sender.endswith(".net"):
        sender = sender[:-4]
    return sender


def _fetch_messages(limit: int = 50) -> list:
    result = _wacli(["messages", "list", "--from-them", "--limit", str(limit)])
    if not result.get("success"):
        return []
    data = result.get("data", [])
    if isinstance(data, list):
        return data
    # wacli wraps messages under data.messages
    return data.get("messages", []) if isinstance(data, dict) else []


def _process_message(msg: dict, seen: set) -> bool:
    # ONLY process messages from founder (5216623538272)
    sender = msg.get("SenderJID", "") or msg.get("sender", "") or msg.get("from", "")
    sender_clean = sender.split("@")[0] if "@" in sender else sender
    founder = "5216623538272"
    env_phone = os.environ.get("FOUNDER_PHONE", "")
    if sender_clean != founder and sender_clean != env_phone:
        return False  # silently ignore messages from anyone else
    """Process a single message. Returns True if it was new."""
    msg_id = msg.get("MsgID") or msg.get("id") or msg.get("message_id") or msg.get("key", {}).get("id")
    if not msg_id or msg_id in seen:
        return False

    seen.add(msg_id)
    sender = _normalize_sender(msg.get("SenderJID", msg.get("sender", "")))
    text = msg.get("Text", "") or msg.get("DisplayText", "") or msg.get("text", "") or msg.get("message", "") or msg.get("body", "")
    timestamp = msg.get("Timestamp", "") or msg.get("timestamp", "") or msg.get("time", "")

    payload = {
        "from": sender,
        "text": text,
        "timestamp": timestamp,
        "message_id": msg_id,
    }
    emit_event("whatsapp:message:received", payload)

    # If message is from the founder → save to inbox
    if FOUNDER_PHONE and FOUNDER_PHONE in sender:
        FOUNDER_INBOX.parent.mkdir(parents=True, exist_ok=True)
        inbox_entry = {
            "event": "founder:message:received",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "payload": payload,
        }
        with open(FOUNDER_INBOX, "a") as f:
            f.write(json.dumps(inbox_entry, ensure_ascii=False) + "\n")
        emit_event("founder:message:received", payload)
        print(f"[whatsapp-webhook] 📩 MENSAJE DEL FUNDADOR: {text[:100]}", file=sys.stderr)

    # Trigger catalog request if text mentions catalog
    catalog_keywords = ["catálogo", "catalogo", "catalog", "servicios", "productos", "planes"]
    if text and any(k in text.lower() for k in catalog_keywords):
        emit_event("whatsapp:catalog:requested", {"client_id": sender, "timestamp": timestamp})

    return True


def run_webhook(interval: int = DEFAULT_INTERVAL, once: bool = False) -> None:
    print(f"[whatsapp-webhook] Starting with interval={interval}s", file=sys.stderr)
    seen = _load_seen()
    backoff = 1

    try:
        while True:
            messages = _fetch_messages()
            if messages is None:
                # wacli error or auth issue
                emit_event("system:whatsapp:disconnected", {"error": "messages fetch failed"})
                print(f"[whatsapp-webhook] Disconnected, retrying in {backoff}s", file=sys.stderr)
                time.sleep(backoff)
                backoff = min(backoff * 2, BACKOFF_MAX)
                if once:
                    break
                continue

            if backoff > 1:
                emit_event("system:whatsapp:reconnected", {"timestamp": datetime.now(timezone.utc).isoformat()})
                print("[whatsapp-webhook] Reconnected", file=sys.stderr)
                backoff = 1

            new_count = 0
            for msg in messages:
                if _process_message(msg, seen):
                    new_count += 1

            if new_count > 0:
                _save_seen(seen)
                print(f"[whatsapp-webhook] Processed {new_count} new messages", file=sys.stderr)

            if once:
                break

            time.sleep(interval)
    except KeyboardInterrupt:
        print("[whatsapp-webhook] Stopped by user", file=sys.stderr)
        _save_seen(seen)
    except Exception as e:
        emit_event("system:whatsapp:disconnected", {"error": str(e)})
        _save_seen(seen)
        raise


def main():
    parser = argparse.ArgumentParser(description="WhatsApp webhook listener")
    parser.add_argument("--interval", type=int, default=DEFAULT_INTERVAL, help="Polling interval in seconds")
    parser.add_argument("--once", action="store_true", help="Run one poll and exit")
    args = parser.parse_args()
    run_webhook(interval=args.interval, once=args.once)


if __name__ == "__main__":
    main()
