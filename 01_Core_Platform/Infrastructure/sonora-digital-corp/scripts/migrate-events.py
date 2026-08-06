#!/usr/bin/env python3
"""Migra todos los events.jsonl dispersos a state/events/events.jsonl unificado [FR17]"""
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PROCESS_COMPLETED = REPO / "process" / "completed"
OUTPUT = REPO / "state" / "events" / "events.jsonl"


def find_event_files():
    """Encuentra todos los events.jsonl en process/completed/"""
    return sorted(PROCESS_COMPLETED.rglob("events.jsonl"))


def migrate(dry_run=False):
    files = find_event_files()
    total = 0
    migrated = 0
    errors = 0

    for f in files:
        try:
            with open(f) as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    total += 1
                    try:
                        evt = json.loads(line)
                        # Handle both old schema (name) and new schema (event)
                        if "event" not in evt and "name" in evt:
                            evt["event"] = evt.pop("name")
                        if "id" not in evt:
                            evt["id"] = f"migrated_{Path(f).parent.name}_{total}"
                        if "timestamp" not in evt:
                            evt["timestamp"] = "2026-07-03T00:00:00Z"
                        migrated += 1
                        if not dry_run:
                            OUTPUT.parent.mkdir(parents=True, exist_ok=True)
                            with open(OUTPUT, "a") as out:
                                out.write(json.dumps(evt, sort_keys=True) + "\n")
                    except json.JSONDecodeError:
                        errors += 1
        except Exception as e:
            print(f"Error reading {f}: {e}", file=sys.stderr)
            errors += 1

    return {"files": len(files), "total": total, "migrated": migrated, "errors": errors}


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv

    if not dry_run:
        # Backup existing events file if any
        if OUTPUT.exists():
            backup = OUTPUT.with_name("events.jsonl.pre-migration.bak")
            OUTPUT.rename(backup)
            print(f"Backed up existing events → {backup.name}")

    result = migrate(dry_run)

    if dry_run:
        print(f"DRY RUN: {result['files']} files, {result['total']} events found, {result['migrated']} valid")
    else:
        # Add migration marker event
        import subprocess
        subprocess.run(
            [sys.executable, str(REPO / "scripts" / "emit-event.py"),
             "--event", "eventbus.migrated",
             "--kernel", "eventbus",
             "--agent", "migrate-events",
             "--subject-type", "system",
             "--subject-id", "event-bus",
             "--payload", json.dumps({"files_migrated": result["files"], "events_migrated": result["migrated"]})],
            capture_output=True, timeout=5
        )

        print(f"Migration complete: {result['files']} files, {result['total']} events, {result['migrated']} migrated, {result['errors']} errors")
        print(f"Output: {OUTPUT}")
