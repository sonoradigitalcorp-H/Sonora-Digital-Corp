#!/usr/bin/env python3
"""Event Bus CLI — emite eventos validados al stream unificado (HAS-003)"""
import json
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent
EVENTS_FILE = REPO / "state" / "events" / "events.jsonl"
CATALOG = REPO / "state" / "events" / "catalog.yaml"
MAX_LINES = 10000


def load_catalog() -> set[str]:
    if not CATALOG.exists():
        return set()
    try:
        import yaml
        with open(CATALOG) as f:
            data = yaml.safe_load(f)
        events = set()
        for cat in data.get("categories", {}).values():
            for evt in cat.get("events", []):
                if isinstance(evt, dict):
                    events.add(evt.get("type", ""))
                else:
                    events.add(evt)
        return events
    except Exception:
        return set()


def validate_event(event: dict):
    required = ["id", "type", "timestamp", "source", "tenant", "subject"]
    for field in required:
        if field not in event:
            print(f"ERROR: missing required field '{field}'", file=sys.stderr)
            sys.exit(1)

    if not event.get("id", "").startswith("evt_"):
        print("WARNING: event id should start with 'evt_'", file=sys.stderr)

    if not isinstance(event.get("source"), str):
        print("ERROR: 'source' must be a string", file=sys.stderr)
        sys.exit(1)

    if not isinstance(event.get("subject"), dict):
        print("ERROR: 'subject' must be a dict", file=sys.stderr)
        sys.exit(1)

    if "type" not in event["subject"]:
        print("ERROR: 'subject.type' is required", file=sys.stderr)
        sys.exit(1)

    valid_events = load_catalog()
    if valid_events and event["type"] not in valid_events:
        print(f"WARNING: event type '{event['type']}' not in catalog", file=sys.stderr)


def rotate_if_needed():
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


def make_event_has(
    event_type: str,
    source: str,
    tenant: str = "default",
    subject_type: str = "system",
    subject_id: str = "",
    payload: dict | None = None,
    correlation_id: str | None = None,
    causation_id: str | None = None,
    metadata: dict | None = None,
) -> dict:
    return {
        "id": f"evt_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}",
        "type": event_type,
        "version": 1,
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": source,
        "tenant": tenant,
        "correlation_id": correlation_id or str(uuid.uuid4()),
        "subject": {"type": subject_type, "id": subject_id},
        "payload": payload or {},
        "metadata": metadata or {"cost": 0.0, "latency_ms": 0, "model": "", "agent": ""},
    }


def make_event_legacy(event_type, kernel, agent, subject_type, subject_id, subject_path=None, payload=None, trace=None, cost=None):
    evt = {
        "event": event_type,
        "id": f"evt_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}",
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": {"kernel": kernel, "agent": agent},
        "subject": {"type": subject_type, "id": subject_id},
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


def emit(event: dict, event_file: str | Path | None = None):
    rotate_if_needed()
    validate_event(event)
    line = json.dumps(event, sort_keys=True) + "\n"
    target = Path(event_file) if event_file else EVENTS_FILE
    target.parent.mkdir(parents=True, exist_ok=True)
    with open(target, "a") as f:
        f.write(line)
    print(f"Event emitted: {event['type'] if 'type' in event else event.get('event', '?')} ({event['id']})", file=sys.stderr)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Emit event to unified bus (HAS-003)")
    parser.add_argument("--type", help="Event type (HAS format, e.g. artist.data_sync.completed)")
    parser.add_argument("--event", help="Event type (legacy format)")
    parser.add_argument("--source", required=True, help="Source service/agent")
    parser.add_argument("--tenant", default="default", help="Tenant ID")
    parser.add_argument("--subject-type", default="system", help="Subject type")
    parser.add_argument("--subject-id", default="", help="Subject ID")
    parser.add_argument("--payload", help="JSON payload string")
    parser.add_argument("--correlation-id", help="Correlation ID")
    parser.add_argument("--kernel", help="Legacy: source kernel")
    parser.add_argument("--agent", help="Legacy: source agent")
    parser.add_argument("--subject-path", help="Legacy: subject path")
    parser.add_argument("--trace", help="Legacy: JSON trace array")
    parser.add_argument("--cost", help="Legacy: JSON cost object")
    args = parser.parse_args()

    payload = json.loads(args.payload) if args.payload else None

    if args.type:
        evt = make_event_has(
            event_type=args.type,
            source=args.source,
            tenant=args.tenant,
            subject_type=args.subject_type,
            subject_id=args.subject_id,
            payload=payload,
            correlation_id=args.correlation_id,
        )
    elif args.event:
        evt = make_event_legacy(
            args.event, args.kernel or args.source, args.agent or "unknown",
            args.subject_type, args.subject_id, args.subject_path,
            payload, json.loads(args.trace) if args.trace else None,
            json.loads(args.cost) if args.cost else None,
        )
    else:
        print("ERROR: --type or --event required", file=sys.stderr)
        sys.exit(1)

    emit(evt)
