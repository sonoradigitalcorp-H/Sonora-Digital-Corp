#!/usr/bin/env python3
"""
WhatsApp Inbox — Revisa mensajes nuevos del fundador.

Lee state/inbox/founder.jsonl y muestra los mensajes no leídos.
Usa state/inbox/read.json para trackear qué se ha leído.

Uso:
  python3 scripts/check-inbox.py          # Muestra mensajes nuevos
  python3 scripts/check-inbox.py --all    # Muestra todos los mensajes
  python3 scripts/check-inbox.py --watch  # Sigue nuevos mensajes en tiempo real
  python3 scripts/check-inbox.py --mark-read  # Marca todo como leído
"""

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
INBOX_FILE = REPO / "state" / "inbox" / "founder.jsonl"
READ_FILE = REPO / "state" / "inbox" / "read.json"


def _load_read() -> set:
    if not READ_FILE.exists():
        return set()
    try:
        with open(READ_FILE) as f:
            return set(json.load(f).get("read_ids", []))
    except Exception:
        return set()


def _save_read(read_ids: set) -> None:
    READ_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(READ_FILE, "w") as f:
        json.dump({"read_ids": sorted(read_ids), "updated": datetime.now().isoformat()}, f)


def get_messages(include_read: bool = False) -> list:
    if not INBOX_FILE.exists():
        return []
    read_ids = _load_read()
    messages = []
    with open(INBOX_FILE) as f:
        for line in f:
            if line.strip():
                try:
                    entry = json.loads(line)
                    msg_id = entry.get("payload", {}).get("message_id", "")
                    entry["is_read"] = msg_id in read_ids
                    messages.append(entry)
                except json.JSONDecodeError:
                    continue
    if not include_read:
        messages = [m for m in messages if not m["is_read"]]
    return messages


def print_messages(messages: list) -> None:
    if not messages:
        print("\n📭 Bandeja de entrada vacía. No hay mensajes nuevos.")
        return

    print(f"\n📩 {len(messages)} mensaje(s) nuevo(s):")
    print("=" * 60)
    for m in messages:
        p = m.get("payload", {})
        ts = m.get("timestamp", p.get("timestamp", "?"))
        fr = p.get("from", "?")
        text = p.get("text", "")
        msg_id = p.get("message_id", "")
        read_status = "✅" if m.get("is_read") else "🆕"
        print(f"\n{read_status} De: {fr}")
        print(f"   Hora: {ts}")
        print(f"   Mensaje: {text}")
        print(f"   ID: {msg_id}")

    # Mark as read
    ids = set()
    for m in messages:
        msg_id = m.get("payload", {}).get("message_id", "")
        if msg_id:
            ids.add(msg_id)
    if ids:
        all_read = _load_read()
        all_read.update(ids)
        _save_read(all_read)


def watch_inbox():
    print("\n👀 Observando bandeja de entrada... (Ctrl+C para salir)")
    last_count = 0
    try:
        while True:
            messages = get_messages(include_read=False)
            if len(messages) > last_count:
                new_ones = messages[last_count:]
                print_messages(new_ones)
                last_count = len(messages)
            time.sleep(5)
    except KeyboardInterrupt:
        print("\n👋 Observación terminada.")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="WhatsApp Inbox Checker")
    parser.add_argument("--all", action="store_true", help="Mostrar todos los mensajes (incluyendo leídos)")
    parser.add_argument("--watch", action="store_true", help="Seguir nuevos mensajes en tiempo real")
    parser.add_argument("--mark-read", action="store_true", help="Marcar todo como leído")
    args = parser.parse_args()

    if args.mark_read:
        if INBOX_FILE.exists():
            ids = set()
            with open(INBOX_FILE) as f:
                for line in f:
                    if line.strip():
                        try:
                            entry = json.loads(line)
                            msg_id = entry.get("payload", {}).get("message_id", "")
                            if msg_id:
                                ids.add(msg_id)
                        except Exception:
                            continue
            _save_read(ids)
            print(f"✅ {len(ids)} mensajes marcados como leídos.")
        return

    if args.watch:
        watch_inbox()
        return

    messages = get_messages(include_read=args.all)
    print_messages(messages)


if __name__ == "__main__":
    main()
