"""Tests for planner event emitter."""
import json
from datetime import datetime

import pytest

from planner.events import (
    EVENTS_PATH,
    _emit,
    emit_capability_executed,
    emit_no_provider,
    emit_provider_degraded,
    emit_provider_failed,
    emit_provider_recovered,
    emit_registry_updated,
    emit_sync_completed,
    emit_sync_started,
)
from planner.models import CapabilityResult


@pytest.fixture(autouse=True)
def clean_events():
    """Ensure clean events file for each test."""
    if EVENTS_PATH.exists():
        EVENTS_PATH.unlink()
    EVENTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    yield
    if EVENTS_PATH.exists():
        EVENTS_PATH.unlink()


def read_events() -> list[dict]:
    if not EVENTS_PATH.exists():
        return []
    return [json.loads(line) for line in EVENTS_PATH.read_text().strip().split("\n") if line]


class TestEmitBase:
    def test_emit_creates_file(self):
        _emit("TestEvent", {"key": "value"})
        assert EVENTS_PATH.exists()

    def test_emit_appends(self):
        _emit("Event1", {"n": 1})
        _emit("Event2", {"n": 2})
        events = read_events()
        assert len(events) == 2
        assert events[0]["event"] == "Event1"
        assert events[1]["event"] == "Event2"

    def test_emit_valid_json(self):
        _emit("Test", {"data": "hello"})
        events = read_events()
        assert len(events) == 1
        e = events[0]
        assert e["event"] == "Test"
        assert e["producer"] == "decision-engine"
        assert "timestamp" in e
        assert e["payload"]["data"] == "hello"

    def test_timestamp_iso8601(self):
        _emit("Test", {})
        e = read_events()[0]
        ts = e["timestamp"]
        # Verify it's valid ISO 8601
        datetime.fromisoformat(ts.replace("Z", "+00:00"))


class TestEmitCapabilityExecuted:
    def test_success_event(self):
        result = CapabilityResult(
            capability_id="test-cap",
            provider_id="deezer",
            success=True,
            data={"followers": 100},
            latency_ms=150.0,
            cost_estimate=0.0,
        )
        emit_capability_executed(result)
        events = read_events()
        assert len(events) == 1
        e = events[0]
        assert e["event"] == "CapabilityExecuted"
        assert e["payload"]["capability_id"] == "test-cap"
        assert e["payload"]["provider_id"] == "deezer"
        assert e["payload"]["success"] is True

    def test_failure_event(self):
        result = CapabilityResult(
            capability_id="test-cap",
            provider_id="deezer",
            success=False,
            error="timeout",
            latency_ms=5000.0,
        )
        emit_capability_executed(result)
        e = read_events()[0]
        assert e["payload"]["success"] is False


class TestEmitProviderFailed:
    def test_failed_event(self):
        emit_provider_failed("deezer", "acquire-metadata", "HTTP 503")
        e = read_events()[0]
        assert e["event"] == "ProviderFailed"
        assert e["payload"]["provider_id"] == "deezer"
        assert e["payload"]["error"] == "HTTP 503"


class TestEmitProviderDegraded:
    def test_degraded_event(self):
        emit_provider_degraded("deezer", 3000.0, 2000.0)
        e = read_events()[0]
        assert e["event"] == "ProviderDegraded"
        assert e["payload"]["latency_ms"] == 3000.0


class TestEmitProviderRecovered:
    def test_recovered_event(self):
        emit_provider_recovered("deezer", 120.0)
        e = read_events()[0]
        assert e["event"] == "ProviderRecovered"
        assert e["payload"]["downtime_seconds"] == 120.0


class TestEmitNoProvider:
    def test_no_provider_event(self):
        emit_no_provider("acquire-metadata")
        e = read_events()[0]
        assert e["event"] == "NoProviderAvailable"
        assert e["payload"]["capability_id"] == "acquire-metadata"


class TestEmitRegistryUpdated:
    def test_registry_updated_event(self):
        emit_registry_updated(3, 8, "2.0.0")
        e = read_events()[0]
        assert e["event"] == "RegistryUpdated"
        assert e["payload"]["capability_count"] == 3
        assert e["payload"]["provider_count"] == 8


class TestEmitSync:
    def test_sync_started(self):
        emit_sync_started(5, ["acquire-metadata", "search-artist"])
        e = read_events()[0]
        assert e["event"] == "SyncCycleStarted"
        assert e["payload"]["artist_count"] == 5

    def test_sync_completed(self):
        emit_sync_completed(3, 1234.56)
        e = read_events()[0]
        assert e["event"] == "SyncCycleCompleted"
        assert e["payload"]["artists_synced"] == 3
