#!/usr/bin/env python3
"""Event Pipeline — Procesa eventos de events.jsonl y los encola L1→L2→L3.

Lee events.jsonl, clasifica cada evento por tipo, lo enruta al nivel
de kernel correspondiente, y archiva los procesados.

Uso: python3 scripts/event-pipeline.py [--all] [--watch] [--rotate]
"""

import json
import logging
import shutil
from datetime import datetime, timezone
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

REPO = Path(__file__).resolve().parent.parent
EVENTS_PATH = REPO / "state" / "events" / "events.jsonl"
PROCESSED_DIR = REPO / "state" / "events" / "processed"
ARCHIVE_DIR = REPO / "state" / "events" / "archive"

# Ruteo de eventos por tipo → nivel de kernel
EVENT_ROUTES = {
    "artist.data_collected": "L1-observe",
    "instagram": "L1-observe",
    "spotify": "L1-observe",
    "youtube": "L1-observe",
    "knowledge_stored": "L2-understand",
    "knowledge.indexed": "L2-understand",
    "knowledge_updated": "L2-understand",
    "session.started": "L2-understand",
    "graph.populated": "L2-understand",
    "skill_execution": "L3-decide",
    "lead_received": "L3-decide",
    "lead_qualified": "L3-decide",
    "deal_created": "L3-decide",
    "deployment_completed": "L3-decide",
    "container_down": "L4-act",
    "container_recovered": "L4-act",
    "healing_attempt": "L4-act",
    "healing_success": "L4-act",
    "healing_failure": "L4-act",
    "score_calculated": "L5-measure",
    "quality_pass": "L5-measure",
    "security_scan_completed": "L5-measure",
    "agent_health_report": "L5-measure",
    "evolution": "L6-learn",
    "adr_created": "L6-learn",
    "session": "L6-learn",
}


def route_event(event_type: str) -> str:
    for prefix, level in EVENT_ROUTES.items():
        if event_type.startswith(prefix):
            return level
    return "unclassified"


def load_events() -> list[dict]:
    if not EVENTS_PATH.exists():
        return []
    events = []
    with open(EVENTS_PATH) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            for decoder in (json.loads, _yaml_load):
                try:
                    ev = decoder(line)
                    if isinstance(ev, dict):
                        events.append(ev)
                    break
                except Exception:
                    continue
    return events


def _yaml_load(line: str) -> dict | None:
    try:
        import yaml
        return yaml.safe_load(line)
    except Exception:
        raise ValueError("not yaml")


def process_event(event: dict) -> dict:
    event_type = event.get("event") or event.get("type", "unknown")
    level = route_event(event_type)
    payload = event.get("payload", {})
    source = event.get("source") or payload.get("source", "unknown")
    timestamp = event.get("timestamp", datetime.now(timezone.utc).isoformat())

    result = {
        "event": event_type,
        "level": level,
        "source": source,
        "timestamp": timestamp,
        "processed_at": datetime.now(timezone.utc).isoformat(),
        "status": "processed",
    }

    if level == "L1-observe":
        result["action"] = "normalize_and_store"
    elif level == "L2-understand":
        result["action"] = "ingest_to_knowledge_graph"
    elif level == "L3-decide":
        result["action"] = "evaluate_and_queue"
    elif level == "L4-act":
        result["action"] = "trigger_remediation"
    elif level == "L5-measure":
        result["action"] = "update_metrics"
    elif level == "L6-learn":
        result["action"] = "extract_heuristics"
    else:
        result["action"] = "log_only"

    return result


def save_processed(results: list[dict]) -> Path:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    out_path = PROCESSED_DIR / f"batch-{stamp}.json"
    with open(out_path, "w") as f:
        json.dump({"batch": stamp, "count": len(results), "results": results}, f, indent=2)
    logger.info("Saved %d processed events to %s", len(results), out_path)
    return out_path


def rotate_events(keep_lines: int = 0) -> None:
    if not EVENTS_PATH.exists():
        return
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    archive_name = f"events-{stamp}.jsonl"
    shutil.copy2(EVENTS_PATH, ARCHIVE_DIR / archive_name)
    if keep_lines == 0:
        EVENTS_PATH.write_text("")
        logger.info("Rotated: %s → archive/%s (cleared)", EVENTS_PATH.name, archive_name)
    else:
        lines = EVENTS_PATH.read_text().splitlines()
        with open(EVENTS_PATH, "w") as f:
            f.write("\n".join(lines[-keep_lines:]) + "\n")
        logger.info("Rotated: kept last %d lines in %s", keep_lines, EVENTS_PATH.name)


def run_pipeline(rotate: bool = False) -> dict:
    events = load_events()
    if not events:
        return {"status": "no_events", "count": 0}

    results = [process_event(ev) for ev in events]
    save_processed(results)

    level_counts = {}
    for r in results:
        level = r["level"]
        level_counts[level] = level_counts.get(level, 0) + 1

    if rotate:
        rotate_events()

    return {
        "status": "completed",
        "total": len(results),
        "levels": level_counts,
        "archive": rotate,
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Event Pipeline: L1→L2→L3→L4→L5→L6")
    parser.add_argument("--all", action="store_true", help="Process all events")
    parser.add_argument("--watch", action="store_true", help="Watch mode (process every 60s)")
    parser.add_argument("--rotate", action="store_true", help="Rotate events after processing")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    if args.watch:
        import time
        while True:
            result = run_pipeline(rotate=args.rotate)
            if args.json:
                print(json.dumps(result))
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] {result['status']}: {result['total']} events")
            time.sleep(60)
    else:
        result = run_pipeline(rotate=args.rotate)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print("\n=== Event Pipeline ===")
            print(f"Status: {result['status']}")
            print(f"Total: {result['total']} events")
            print("\nBy kernel level:")
            for level, count in sorted(result.get("levels", {}).items()):
                print(f"  {level}: {count} events")


if __name__ == "__main__":
    main()
