import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from memory.base import MemoryResult, MemoryStore

REPO = Path(__file__).resolve().parent.parent.parent
EVENTS_FILE = REPO / "state" / "events" / "events.jsonl"
CATALOG = REPO / "state" / "events" / "catalog.yaml"


class EventMemory(MemoryStore):
    name = "event"

    def __init__(self, events_file: str | Path | None = None):
        self.events_file = Path(events_file) if events_file else EVENTS_FILE
        self.events_file.parent.mkdir(parents=True, exist_ok=True)

    async def _emit(self, event_type: str, data: dict) -> dict:
        event = {
            "event": event_type,
            "id": f"evt_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}",
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "source": {"kernel": "memory", "agent": "memory-system"},
            "subject": {"type": "system", "id": data.get("key", "unknown")},
            "payload": data,
        }
        line = json.dumps(event, sort_keys=True) + "\n"
        with open(self.events_file, "a") as f:
            f.write(line)
        return event

    async def store(self, key: str, data: dict, ttl: int | None = None) -> MemoryResult:
        event = await self._emit("memory.stored", {"key": key, "size": len(json.dumps(data))})
        return MemoryResult(key=key, data=event, found=True, store_type="event")

    async def retrieve(self, key: str) -> MemoryResult:
        events = []
        if self.events_file.exists():
            with open(self.events_file) as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        evt = json.loads(line)
                        if evt.get("payload", {}).get("key") == key:
                            events.append(evt)
                    except json.JSONDecodeError:
                        continue
        if events:
            return MemoryResult(key=key, data={"events": events[-5:]}, found=True, store_type="event")
        return MemoryResult(key=key, found=False, store_type="event")

    async def search(self, query: str | dict, top_k: int = 5) -> list[MemoryResult]:
        if isinstance(query, dict):
            query = str(query)
        q = query.lower()
        results: list[MemoryResult] = []
        if not self.events_file.exists():
            return results
        with open(self.events_file) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    evt = json.loads(line)
                    if q in json.dumps(evt).lower():
                        results.append(MemoryResult(
                            key=evt.get("id", ""),
                            data=evt,
                            found=True,
                            store_type="event",
                        ))
                        if len(results) >= top_k:
                            break
                except json.JSONDecodeError:
                    continue
        return results

    async def delete(self, key: str) -> bool:
        return False

    async def list_keys(self, prefix: str = "") -> list[str]:
        keys: list[str] = []
        if not self.events_file.exists():
            return keys
        with open(self.events_file) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    evt = json.loads(line)
                    evt_key = evt.get("payload", {}).get("key", "")
                    if evt_key.startswith(prefix):
                        keys.append(evt_key)
                except json.JSONDecodeError:
                    continue
        return list(set(keys))
