"""
ActivityBroadcaster — global event bus for real-time agent activity.
SSE clients subscribe and receive live events as they happen.
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any

log = logging.getLogger("jarvis.activity")


class ActivityBroadcaster:
    def __init__(self, max_history: int = 500):
        self._subscribers: list[asyncio.Queue] = []
        self._history: list[dict[str, Any]] = []
        self._max_history = max_history

    def subscribe(self) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue()
        self._subscribers.append(q)
        return q

    def unsubscribe(self, q: asyncio.Queue):
        if q in self._subscribers:
            self._subscribers.remove(q)

    def publish(self, event_type: str, data: dict[str, Any]):
        event = {
            "type": event_type,
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._history.append(event)
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history :]
        for q in self._subscribers:
            try:
                q.put_nowait(event)
            except asyncio.QueueFull:
                pass

    def recent(self, limit: int = 50) -> list[dict[str, Any]]:
        return self._history[-limit:]


_broadcaster: ActivityBroadcaster | None = None


def get_broadcaster() -> ActivityBroadcaster:
    global _broadcaster
    if _broadcaster is None:
        _broadcaster = ActivityBroadcaster()
    return _broadcaster
