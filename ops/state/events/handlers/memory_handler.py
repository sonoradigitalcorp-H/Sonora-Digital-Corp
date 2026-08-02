import json
import logging
from pathlib import Path
from typing import Any

log = logging.getLogger("events.memory_handler")

PROCESSED_DIR = Path("state/events/processed")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
MEMORY_FILE = Path("state/events/memory.jsonl")


class MemoryHandler:
    def handle(self, event: dict[str, Any]) -> None:
        event_id = event.get("id", "unknown")
        batch_path = PROCESSED_DIR / f"event-{event_id}.json"
        try:
            with open(batch_path, "w") as f:
                json.dump(event, f, indent=2)
            with open(MEMORY_FILE, "a") as f:
                f.write(json.dumps(event) + "\n")
            log.debug("Event stored: %s", event_id)
        except Exception as e:
            log.error("Failed to store event %s: %s", event_id, e)
