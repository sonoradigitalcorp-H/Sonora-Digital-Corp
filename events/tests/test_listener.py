"""Tests for EventListener (HAS-003)"""
import asyncio
import json
import tempfile
from pathlib import Path

import pytest

from events.listener import EventListener
from events.handlers import MemoryHandler, AlertHandler


@pytest.mark.asyncio
async def test_event_listener_start_stop():
    listener = EventListener()
    assert not listener.is_running
    await listener.start()
    assert listener.is_running
    await listener.stop()
    assert not listener.is_running


@pytest.mark.asyncio
async def test_event_listener_register():
    listener = EventListener()
    handler = MemoryHandler()
    listener.register(handler)
    stats = listener.get_stats()
    assert "memory" in stats["handlers"]


@pytest.mark.asyncio
async def test_alert_handler_critical():
    handler = AlertHandler()
    await handler.handle({
        "id": "evt_test",
        "type": "system.error.occurred",
        "timestamp": "2026-07-08T21:00:00Z",
        "payload": {"error": "Something broke"},
    })
    alerts = handler.recent_alerts()
    assert len(alerts) == 1
    assert alerts[0]["severity"] == "critical"


@pytest.mark.asyncio
async def test_alert_handler_ignores_info():
    handler = AlertHandler()
    await handler.handle({
        "id": "evt_info",
        "type": "artist.data_sync.completed",
        "timestamp": "2026-07-08T21:00:00Z",
    })
    alerts = handler.recent_alerts()
    assert len(alerts) == 0


@pytest.mark.asyncio
async def test_memory_handler():
    handler = MemoryHandler()
    await handler.handle({
        "id": "evt_mem",
        "type": "memory.stored",
        "timestamp": "2026-07-08T21:00:00Z",
        "payload": {"key": "test"},
    })
