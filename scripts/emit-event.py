#!/usr/bin/env python3
"""Event Bus CLI — emite eventos validados al stream unificado [FR14-FR20]"""
import json
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
EVENTS_FILE = REPO / "state" / "events" / "events.jsonl"
CATALOG = REPO / "state" / "events" / "catalog.yaml"
MAX_LINES = 10000


def load_catalog():
    """Carga catálogo de eventos válidos"""
    if not CATALOG.exists():
        return set()
    try:
        import yaml
        with open(CATALOG) as f:
            data = yaml.safe_load(f)
        events = set()
        for cat in data.get("categories", {}).values():
            for evt in cat.get("events", []):
                events.add(evt)
        return events
    except Exception:
        return set()


def validate_event(event):
    """Valida schema del evento"""
    required = ["event", "id", "timestamp", "source", "subject"]
    for field in required:
        if field not in event:
            print(f"ERROR: missing required field '{field}'", file=sys.stderr)
            sys.exit(1)

    valid_events = load_catalog()
    if valid_events and event["event"] not in valid_events:
        print(f"WARNING: event '{event['event']}' not in catalog", file=sys.stderr)

    if not isinstance(event.get("source"), dict):
        print("ERROR: 'source' must be a dict", file=sys.stderr)
        sys.exit(1)

    if "kernel" not in event["source"]:
        print("ERROR: 'source.kernel' is required", file=sys.stderr)
        sys.exit(1)

    if not isinstance(event.get("subject"), dict):
        print("ERROR: 'subject' must be a dict", file=sys.stderr)
        sys.exit(1)

    if "type" not in event["subject"]:
        print("ERROR: 'subject.type' is required", file=sys.stderr)
        sys.exit(1)


def rotate_if_needed():
    """Rota el archivo si excede MAX_LINES"""
    if not EVENTS_FILE.exists():
        return

    with open(EVENTS_FILE) as f:
        line_count = sum(1 for _ in f)

    if line_count < MAX_LINES:
        return

    archive_num = 1
    while True:
        archive = EVENTS_FILE.parent / f"events.archive.{archive_num:03d}.jsonl"
        if not archive.exists():
            break
        archive_num += 1

    EVENTS_FILE.rename(archive)
    print(f"Rotated: {EVENTS_FILE.name} → {archive.name}", file=sys.stderr)


def emit(event, event_file=None):
    """Emite un evento al stream unificado"""
    rotate_if_needed()
    validate_event(event)

    line = json.dumps(event, sort_keys=True) + "\n"
    target = event_file or EVENTS_FILE
    target.parent.mkdir(parents=True, exist_ok=True)

    with open(target, "a") as f:
        f.write(line)

    print(f"Event emitted: {event['event']} ({event['id']})", file=sys.stderr)


def make_event(event_type, kernel, agent, subject_type, subject_id, subject_path=None, payload=None, trace=None, cost=None):
    """Construye un evento con schema completo"""
    evt = {
        "event": event_type,
        "id": f"evt_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}",
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": {
            "kernel": kernel,
            "agent": agent,
        },
        "subject": {
            "type": subject_type,
            "id": subject_id,
        },
    }
    if subject_path:
        evt["subject"]["path"] = subject_path
    if payload:
        evt["payload"] = payload
    if trace:
        evt["trace"] = trace
    if cost:
        evt["cost"] = cost
    return evt


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Emit event to unified bus")
    parser.add_argument("--event", required=True, help="Event type (e.g., module.completed)")
    parser.add_argument("--kernel", required=True, help="Source kernel")
    parser.add_argument("--agent", default="mystic", help="Source agent")
    parser.add_argument("--subject-type", required=True, help="Subject type (e.g., module, spec)")
    parser.add_argument("--subject-id", required=True, help="Subject ID")
    parser.add_argument("--subject-path", help="Subject path")
    parser.add_argument("--payload", help="JSON payload string")
    parser.add_argument("--trace", help="JSON trace array string")
    parser.add_argument("--cost", help="JSON cost object string")
    args = parser.parse_args()

    payload = json.loads(args.payload) if args.payload else None
    trace = json.loads(args.trace) if args.trace else None
    cost = json.loads(args.cost) if args.cost else None

    evt = make_event(
        args.event, args.kernel, args.agent,
        args.subject_type, args.subject_id, args.subject_path,
        payload, trace, cost
    )
    emit(evt)
