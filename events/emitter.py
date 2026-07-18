"""Event emitter utility — call from any agent to emit events.
Usage:
    from events.emitter import emit
    await emit("agent:task:completed", {"agent":"quality","task":"eval-123"})
"""
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

log = logging.getLogger("events.emitter")

EVENTS_FILE = (
    Path(__file__).resolve().parent.parent / "state" / "events" / "events.jsonl"
)


async def emit(event_type: str, payload: dict = None, source: str = None):
    entry = {
        "id": f"{event_type}_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}",
        "type": event_type,
        "version": "1",
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "source": source or "unknown",
    }
    if payload:
        entry["payload"] = payload

    EVENTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(EVENTS_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")

    log.debug("Emitted: %s", event_type)


def emit_sync(event_type: str, payload: dict = None, source: str = None):
    """Synchronous version for non-async contexts."""
    import asyncio
    try:
        loop = asyncio.get_running_loop()
        if loop.is_running():
            loop.create_task(emit(event_type, payload, source))
            return
    except RuntimeError:
        pass
    entry = {
        "id": f"{event_type}_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}",
        "type": event_type,
        "version": "1",
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "source": source or "unknown",
    }
    if payload:
        entry["payload"] = payload

    EVENTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(EVENTS_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")
