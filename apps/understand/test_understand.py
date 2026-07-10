import pytest
from pathlib import Path
from apps.understand.pipeline import consume_observe_events, route_to_ingestor
from apps.understand.knowledge import search_all_sources, recent_sessions, synthesize
from apps.understand.truth import load_constitution, verify_against_constitution


def test_consume_observe_events():
    events = consume_observe_events()
    assert isinstance(events, list)


def test_route_to_ingestor():
    assert route_to_ingestor({"event": "artist.data_collected.spotify"}) == "events_ingestor"
    assert route_to_ingestor({"event": "artist.analysis.completed"}) == "hermes_ingestor"
    assert route_to_ingestor({"event": "knowledge.search.completed"}) == "lecciones_ingestor"
    assert route_to_ingestor({"event": "unknown.type"}) is None


def test_search_all_sources():
    results = search_all_sources("test")
    assert isinstance(results, list)


def test_recent_sessions():
    sessions = recent_sessions(3)
    assert isinstance(sessions, list)
    if sessions:
        assert "session" in sessions[0]
        assert "path" in sessions[0]


def test_synthesize():
    result = synthesize({"user": "test"}, "test query")
    assert "query" in result
    assert "sources_found" in result
    assert "recent_sessions" in result


def test_load_constitution():
    rules = load_constitution()
    assert isinstance(rules, dict)
    if rules:
        assert any(k for k in rules)


def test_verify_against_constitution():
    result = verify_against_constitution({"agent": "test", "timestamp": "now"})
    assert "constitution_files" in result
    assert "checks_passed" in result
    assert "compliant" in result


def test_verify_non_compliant():
    result = verify_against_constitution({})
    assert result["checks_passed"] < result["checks_total"]
    assert not result["compliant"]
