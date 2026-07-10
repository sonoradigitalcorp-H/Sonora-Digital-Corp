import pytest
from apps.learn.heuristics import extract_heuristics


def test_extract_heuristics():
    heuristics = extract_heuristics()
    assert isinstance(heuristics, list)


def test_heuristics_types():
    heuristics = extract_heuristics()
    types = {h["type"] for h in heuristics}
    assert "error_pattern" in types or "lesson" in types or "next_step" in types


def test_heuristics_have_text():
    heuristics = extract_heuristics()
    for h in heuristics:
        assert "text" in h
        assert len(h["text"]) > 0


def test_error_patterns_have_count():
    heuristics = extract_heuristics()
    for h in heuristics:
        if h["type"] == "error_pattern":
            assert "count" in h
            assert h["count"] >= 1


def test_learning_pipeline_imports():
    from apps.learn.pipeline import run_learning_cycle, run_evolution_cycle
    assert callable(run_learning_cycle)
    assert callable(run_evolution_cycle)
