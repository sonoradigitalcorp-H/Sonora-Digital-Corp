import asyncio
import json
import logging
from pathlib import Path
from typing import Any

log = logging.getLogger("events.listener")

EVENTS_FILE = Path("state/events/events.jsonl")


class EventListener:
    def __init__(self):
        self.handlers: list[Any] = []
        self._position = 0
        self._running = False

    def register_handler(self, handler: Any) -> None:
        self.handlers.append(handler)
        log.info("Handler registered: %s", type(handler).__name__)

    def _read_new_events(self) -> list[dict]:
        if not EVENTS_FILE.exists():
            return []
        try:
            with open(EVENTS_FILE) as f:
                lines = f.readlines()
            new_lines = lines[self._position:]
            self._position = len(lines)
            events = []
            for line in new_lines:
                line = line.strip()
                if line:
                    try:
                        events.append(json.loads(line))
                    except json.JSONDecodeError:
                        log.warning("Skipping invalid event line")
            return events
        except Exception as e:
            log.error("Error reading events: %s", e)
            return []

    async def _dispatch(self, event: dict) -> None:
        for handler in self.handlers:
            try:
                handler.handle(event)
            except Exception as e:
                log.error("Handler %s failed: %s", type(handler).__name__, e)

    async def poll_loop(self, interval: float = 0.5) -> None:
        self._running = True
        log.info("EventListener polling started (interval=%ss)", interval)
        while self._running:
            events = self._read_new_events()
            for event in events:
                await self._dispatch(event)
            await asyncio.sleep(interval)

    def stop(self) -> None:
        self._running = False
        log.info("EventListener stopped")
