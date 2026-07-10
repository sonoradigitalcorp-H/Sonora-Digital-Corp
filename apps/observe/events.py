import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

EVENTS_PATH = Path("state/events/events.jsonl")
PROCESSED_DIR = Path("state/events/processed")


def consume_unprocessed() -> list[dict]:
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


def mark_processed(event_ids: list[str]) -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    log = {"processed_at": stamp, "event_ids": event_ids}
    (PROCESSED_DIR / f"{stamp}.json").write_text(json.dumps(log, indent=2))
    logger.info("Marked %d events as processed", len(event_ids))


def dispatch_to_understand(events: list[dict]) -> list[dict]:
    forwarded = []
    for ev in events:
        event_type = ev.get("event", "unknown")
        if event_type.startswith("artist.data_collected"):
            forwarded.append({
                "target": "understand",
                "event": "understand.data.ingest",
                "payload": ev.get("payload", {}),
                "source_ts": ev.get("timestamp"),
            })
    return forwarded
