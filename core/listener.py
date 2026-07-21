"""EventListener (HAS-003)
Watches events.jsonl for new lines and dispatches to registered handlers.
Runs as a background asyncio task in production.
"""
import asyncio
import json
from pathlib import Path
from typing import Any

from events.handlers.base import EventHandler

REPO = Path(__file__).resolve().parent.parent
EVENTS_FILE = REPO / "state" / "events" / "events.jsonl"
POLL_INTERVAL = 0.5


class EventListener:
    def __init__(self):
        self._handlers: dict[str, EventHandler] = {}
        self._last_position: int = 0
        self._running = False
        self._task: asyncio.Task | None = None

    def register(self, handler: EventHandler):
        self._handlers[handler.name] = handler

    def unregister(self, name: str):
        self._handlers.pop(name, None)

    async def _process_event(self, event: dict):
        for handler in self._handlers.values():
            try:
                await handler.handle(event)
            except Exception as e:
                print(f"[events] Handler '{handler.name}' error: {e}")

    async def _poll(self):
        while self._running:
            try:
                if EVENTS_FILE.exists():
                    current_size = EVENTS_FILE.stat().st_size
                    if current_size > self._last_position:
                        with open(EVENTS_FILE) as f:
                            f.seek(self._last_position)
                            for line in f:
                                line = line.strip()
                                if line:
                                    try:
                                        event = json.loads(line)
                                        await self._process_event(event)
                                    except json.JSONDecodeError:
                                        continue
                        self._last_position = current_size
            except Exception:
                pass
            await asyncio.sleep(POLL_INTERVAL)

    async def start(self):
        if self._running:
            return
        self._running = True
        if EVENTS_FILE.exists():
            self._last_position = EVENTS_FILE.stat().st_size
        print(f"[events] Listener started — watching {EVENTS_FILE}")
        self._task = asyncio.create_task(self._poll())

    async def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()
            self._task = None
        print("[events] Listener stopped")

    @property
    def is_running(self) -> bool:
        return self._running

    def get_stats(self) -> dict:
        return {
            "running": self._running,
            "handlers": list(self._handlers.keys()),
            "file_size": EVENTS_FILE.stat().st_size if EVENTS_FILE.exists() else 0,
        }
