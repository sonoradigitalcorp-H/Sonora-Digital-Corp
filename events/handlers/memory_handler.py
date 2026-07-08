"""Event Handler: stores events into Memory System (HAS-002/003)"""
from pathlib import Path
from typing import Any

from events.handlers.base import EventHandler

REPO = Path(__file__).resolve().parent.parent.parent


class MemoryHandler(EventHandler):
    name = "memory"

    def __init__(self):
        self._enabled = True

    async def handle(self, event: dict) -> None:
        if not self._enabled:
            return
        try:
            memory_dir = REPO / "state" / "events" / "processed"
            memory_dir.mkdir(parents=True, exist_ok=True)
            evt_type = event.get("type", event.get("event", "unknown"))
            safe_type = evt_type.replace(".", "_").replace("/", "_")
            path = memory_dir / f"{event.get('id', safe_type)}.json"
            import json
            path.write_text(json.dumps(event, indent=2, default=str))
        except Exception:
            pass
