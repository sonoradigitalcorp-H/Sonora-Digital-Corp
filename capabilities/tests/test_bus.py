"""Tests for CapabilityBus (HAS-005)"""
import pytest
from capabilities.bus import CapabilityBus


@pytest.fixture
def bus():
    return CapabilityBus()


def test_bus_loads_registry(bus):
    statuses = bus.list_status()
    assert len(statuses) == 8
    ids = [s["id"] for s in statuses]
    assert "analyze-artist" in ids
    assert "search-knowledge" in ids
    assert "sync-artist-data" in ids
    assert "generate-video" in ids
    assert "score-artist" in ids
    assert "manage-crm" in ids
    assert "publish-track" in ids
    assert "process-payment" in ids


def test_bus_discover(bus):
    results = bus.discover("video")
    assert len(results) >= 1
    assert results[0].id == "generate-video"


def test_bus_discover_all(bus):
    results = bus.discover()
    assert len(results) == 8


def test_bus_health_unknown(bus):
    health = bus.health("nonexistent")
    assert health["status"] == "unknown"


@pytest.mark.asyncio
async def test_bus_resolve_existing(bus):
    cap = await bus.resolve("search-knowledge")
    assert cap is not None
    assert cap.manifest.id == "search-knowledge"
    assert cap.manifest.status == "active"


@pytest.mark.asyncio
async def test_bus_resolve_missing(bus):
    cap = await bus.resolve("nonexistent")
    assert cap is None


@pytest.mark.asyncio
async def test_bus_execute_unknown(bus):
    result = await bus.execute("nonexistent", {})
    assert result.status == "rejected"
    assert "not found" in (result.error or "")


@pytest.mark.asyncio
async def test_bus_execute_existing(bus):
    result = await bus.execute("search-knowledge", {"query": "test"})
    assert result.status == "success"
