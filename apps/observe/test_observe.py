import pytest
from pathlib import Path
from apps.observe.pipeline import load_registry, normalize, emit_event


def test_load_registry():
    registry = load_registry()
    assert registry is not None
    assert "platforms" in registry
    assert "artists" in registry
    assert registry["artists"][0]["id"] == "hector-rubio"


def test_normalize_spotify():
    registry = load_registry()
    raw = {"monthly_listeners": 1000000, "followers": 50000, "popularity": 85}
    result = normalize("spotify", raw, registry)
    assert result["streams"] == 1000000
    assert result["followers"] == 50000
    assert result["popularity_score"] == 85


def test_normalize_instagram():
    registry = load_registry()
    raw = {"followers_count": 10000, "media_count": 200, "avg_likes": 500}
    result = normalize("instagram", raw, registry)
    assert result["followers"] == 10000
    assert result["posts_count"] == 200
    assert result["avg_likes"] == 500


def test_normalize_unknown_platform():
    registry = load_registry()
    raw = {"something": 42}
    result = normalize("unknown", raw, registry)
    assert result["platform"] == "unknown"
    assert result["_raw"] == raw


def test_emit_event(tmp_path):
    original = Path("state/events/events.jsonl")
    if original.exists():
        backup = original.read_text()
    else:
        backup = None

    try:
        emit_event("test.event", {"key": "value"})
        assert original.exists()
        content = original.read_text()
        assert "test.event" in content
    finally:
        if backup is not None:
            original.write_text(backup)
        elif original.exists():
            original.unlink()
