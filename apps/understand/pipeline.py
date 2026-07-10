import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

EVENTS_PATH = Path("state/events/events.jsonl")
PROCESSED_DIR = Path("state/events/processed")


def consume_observe_events() -> list[dict]:
    if not EVENTS_PATH.exists():
        return []
    events = []
    with open(EVENTS_PATH) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                try:
                    import yaml
                    events.append(yaml.safe_load(line))
                except Exception:
                    logger.warning("Skipping unparseable event line")
    return events


def route_to_ingestor(event: dict) -> str | None:
    event_type = event.get("event", "")
    if event_type.startswith("artist.data_collected"):
        return "events_ingestor"
    if event_type.startswith("artist.analysis"):
        return "hermes_ingestor"
    if event_type.startswith("knowledge.search"):
        return "lecciones_ingestor"
    return None


def ingest_to_brain(ingestor_name: str, data: dict) -> bool:
    try:
        ingestor_path = f"apps.brain.ingestors.{ingestor_name.replace('.py', '')}"
        import importlib
        module = importlib.import_module(ingestor_path)
        if hasattr(module, "ingest"):
            module.ingest(data)
            return True
        logger.warning("Ingestor %s has no ingest() function", ingestor_name)
        return False
    except Exception as e:
        logger.error("Failed to ingest via %s: %s", ingestor_name, e)
        return False


def mark_processed(event_ids: list[str]) -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    (PROCESSED_DIR / f"{stamp}.json").write_text(
        json.dumps({"processed_at": stamp, "event_ids": event_ids}, indent=2)
    )


async def run_understand_pipeline() -> dict:
    events = consume_observe_events()
    if not events:
        return {"status": "no_events", "ingested": 0}

    ingested = 0
    errors = []
    processed_ids = []

    for ev in events:
        event_id = ev.get("timestamp", "")
        ingestor = route_to_ingestor(ev)
        if not ingestor:
            continue
        payload = ev.get("payload", {})
        ok = ingest_to_brain(ingestor, payload)
        if ok:
            ingested += 1
            processed_ids.append(event_id)
        else:
            errors.append({"event": ev.get("event"), "timestamp": event_id})

    if processed_ids:
        mark_processed(processed_ids)

    return {
        "status": "completed",
        "events_found": len(events),
        "ingested": ingested,
        "errors": errors,
    }
