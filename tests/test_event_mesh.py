"""Tests for Event Mesh (HAS-003)"""
import importlib.util
import json
import os
import sys
import tempfile
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parent.parent

spec = importlib.util.spec_from_file_location("emit_event", REPO / "scripts" / "emit-event.py")
emit_event_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(emit_event_mod)

load_catalog = emit_event_mod.load_catalog
make_event_has = emit_event_mod.make_event_has
validate_event = emit_event_mod.validate_event
emit = emit_event_mod.emit
EVENTS_FILE = emit_event_mod.EVENTS_FILE
CATALOG = emit_event_mod.CATALOG


def test_catalog_exists():
    assert CATALOG.exists()
    with open(CATALOG) as f:
        data = yaml.safe_load(f)
    assert data["version"] == 2
    assert "categories" in data
    assert "artist" in data["categories"]
    assert "agent" in data["categories"]


def test_load_catalog():
    events = load_catalog()
    assert "artist.data_sync.completed" in events
    assert "agent.action.executed" in events
    assert "system.error.occurred" in events
    assert "memory.stored" in events
    assert "constitution.gate.violation" in events
    assert "evolution.adr.proposed" in events
    assert "track.published" in events
    assert "video.generated" in events
    assert "revenue.updated" in events


def test_make_event_has_schema():
    evt = make_event_has(
        event_type="artist.data_sync.completed",
        source="sync-cron",
        tenant="abe-music",
        subject_type="artist",
        subject_id="abc123",
        payload={"artists_synced": 5},
    )
    assert evt["id"].startswith("evt_")
    assert evt["type"] == "artist.data_sync.completed"
    assert evt["version"] == 1
    assert evt["source"] == "sync-cron"
    assert evt["tenant"] == "abe-music"
    assert evt["subject"]["type"] == "artist"
    assert evt["subject"]["id"] == "abc123"
    assert evt["payload"]["artists_synced"] == 5
    assert evt["correlation_id"] is not None


def test_validate_event_passes():
    evt = make_event_has("agent.action.executed", "kernel", "default", "system", "test")
    validate_event(evt)


def test_validate_event_missing_id():
    with pytest.raises(SystemExit):
        validate_event({"type": "test", "timestamp": "now", "source": "x", "tenant": "x", "subject": {"type": "system"}})


def test_emit_writes_to_file():
    with tempfile.TemporaryDirectory() as tmp:
        events_file = os.path.join(tmp, "events.jsonl")
        evt = make_event_has("memory.stored", "test", "default", "system", "k1")
        emit(evt, events_file)
        with open(events_file) as f:
            lines = f.readlines()
        assert len(lines) == 1
        parsed = json.loads(lines[0])
        assert parsed["type"] == "memory.stored"


def test_emit_multiple_events():
    with tempfile.TemporaryDirectory() as tmp:
        events_file = os.path.join(tmp, "events.jsonl")
        for i in range(3):
            evt = make_event_has("agent.action.executed", "agent", "default", "system", f"t{i}")
            emit(evt, events_file)
        with open(events_file) as f:
            lines = f.readlines()
        assert len(lines) == 3


def test_catalog_all_events_parseable():
    with open(CATALOG) as f:
        data = yaml.safe_load(f)
    all_events = set()
    for cat_name, cat_data in data["categories"].items():
        for evt in cat_data["events"]:
            if isinstance(evt, dict):
                all_events.add(evt["type"])
            else:
                all_events.add(evt)
    assert len(all_events) > 30, f"Expected 30+ events, got {len(all_events)}"
