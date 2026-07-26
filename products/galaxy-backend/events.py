"""Event logging system for Agent Galaxy backend.

Persists events to JSONL files for observability, audit, and replay.
Follows SDC event naming conventions (snake_case, domain-prefixed).
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from models import GalaxyEvent

log = logging.getLogger("galaxy.events")

DEFAULT_EVENT_PATH = os.getenv(
    "GALAXY_EVENT_LOG",
    str(Path(__file__).resolve().parent.parent / "state" / "galaxy_events.jsonl"),
)


class EventLogger:
    """Append-only JSONL event logger with optional in-memory buffer."""

    def __init__(self, path: str = DEFAULT_EVENT_PATH, buffer_size: int = 100):
        self.path = path
        self.buffer: list[dict] = []
        self.buffer_size = buffer_size
        self._ensure_dir()

    def _ensure_dir(self) -> None:
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)

    def emit(self, event: GalaxyEvent) -> dict:
        """Log an event and return the serialized record."""
        record = event.model_dump()
        self.buffer.append(record)
        if len(self.buffer) >= self.buffer_size:
            self.flush()
        log.info(f"event={event.event_type} tenant={event.tenant_id}")
        return record

    def flush(self) -> None:
        """Write buffered events to the JSONL file."""
        if not self.buffer:
            return
        try:
            with open(self.path, "a", encoding="utf-8") as f:
                for record in self.buffer:
                    f.write(json.dumps(record, ensure_ascii=False) + "\n")
            self.buffer.clear()
        except IOError as e:
            log.error(f"Failed to flush events: {e}")

    def query(
        self,
        event_type: Optional[str] = None,
        tenant_id: Optional[str] = None,
        limit: int = 50,
    ) -> list[dict]:
        """Read events from the JSONL log with optional filters."""
        results: list[dict] = []
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        record = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if event_type and record.get("event_type") != event_type:
                        continue
                    if tenant_id and record.get("tenant_id") != tenant_id:
                        continue
                    results.append(record)
                    if len(results) >= limit:
                        break
        except FileNotFoundError:
            pass
        results.reverse()
        return results

    def count(self, event_type: Optional[str] = None) -> int:
        """Count total events, optionally filtered by type."""
        count = 0
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        record = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if event_type and record.get("event_type") != event_type:
                        continue
                    count += 1
        except FileNotFoundError:
            pass
        return count


event_logger = EventLogger()
