"""Tests for ClientLearner — 10 tests"""

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO))

import pytest

from evolution.client_learner import ClientLearner
from memory.client_store import ClientStore


@pytest.fixture
def store_and_learner(tmp_path):
    base = tmp_path / "clients"
    store = ClientStore(base_dir=base)
    learner = ClientLearner(store=store)
    return store, learner


def _setup_test_client(store, cid="c1", niche="musico"):
    store._ensure_profile(cid, {"name": "Test", "niche": niche})
    store.save_interaction(cid, {"type": "message", "content": "hola", "service": "clone-voice",
                                  "tokens_used": 10, "success": True, "satisfaction_score": 8})
    store.save_interaction(cid, {"type": "message", "content": "foto", "service": "photo-professional",
                                  "tokens_used": 5, "success": True, "satisfaction_score": 9})
    store.save_interaction(cid, {"type": "message", "content": "error", "service": "clone-voice",
                                  "tokens_used": 3, "success": False, "satisfaction_score": 4})


def test_analyze_client(store_and_learner):
    store, learner = store_and_learner
    _setup_test_client(store)
    analysis = learner.analyze_client("c1")
    assert analysis["total_interactions"] == 3
    assert analysis["total_tokens"] == 18
    assert analysis["success_rate"] == round(2 / 3, 3)
    assert analysis["top_service"] == "clone-voice"


def test_analyze_client_not_found(store_and_learner):
    _, learner = store_and_learner
    analysis = learner.analyze_client("nonexistent")
    assert "error" in analysis


def test_analyze_niche(store_and_learner):
    store, learner = store_and_learner
    _setup_test_client(store, "c1", "musico")
    _setup_test_client(store, "c2", "musico")
    analysis = learner.analyze_niche("musico")
    assert analysis["client_count"] == 2
    assert analysis["total_interactions"] == 6
    assert analysis["niche"] == "musico"


def test_analyze_niche_empty(store_and_learner):
    _, learner = store_and_learner
    analysis = learner.analyze_niche("unknown")
    assert analysis["client_count"] == 0
    assert "error" in analysis


def test_analyze_all(store_and_learner):
    store, learner = store_and_learner
    _setup_test_client(store, "c1", "musico")
    _setup_test_client(store, "c2", "barbero")
    result = learner.analyze_all()
    assert result["total_clients"] == 2
    assert "musico" in result["niches"]
    assert "barbero" in result["niches"]
    assert result["total_interactions"] == 6


def test_analyze_all_empty(store_and_learner):
    _, learner = store_and_learner
    result = learner.analyze_all()
    assert result["total_clients"] == 0


def test_get_recommendation(store_and_learner):
    store, learner = store_and_learner
    _setup_test_client(store)
    rec = learner.get_recommendation("c1")
    assert rec != ""
    assert "clone-voice" in rec or "bundle" in rec or "onboarding" in rec


def test_get_recommendation_not_found(store_and_learner):
    _, learner = store_and_learner
    rec = learner.get_recommendation("nonexistent")
    assert "not found" in rec.lower()


def test_niche_insights(store_and_learner):
    store, learner = store_and_learner
    _setup_test_client(store, "c1", "musico")
    _setup_test_client(store, "c2", "barbero")
    insights = learner.get_niche_insights()
    assert len(insights) == 2
    niches = {i["niche"] for i in insights}
    assert "musico" in niches
    assert "barbero" in niches


def test_cross_client_patterns(store_and_learner):
    store, learner = store_and_learner
    for i in range(3):
        cid = f"mc{i}"
        store._ensure_profile(cid, {"name": f"M{i}", "niche": "musico"})
        for _ in range(2):
            store.save_interaction(cid, {"type": "message", "service": "clone-voice",
                                          "tokens_used": 5, "success": True})
    result = learner.analyze_all()
    patterns = result.get("cross_client_patterns", [])
    musico_patterns = [p for p in patterns if p.get("niche") == "musico"]
    assert len(musico_patterns) >= 1
    assert "clone-voice" in musico_patterns[0]["service"]


def test_generate_insight_report(store_and_learner):
    store, learner = store_and_learner
    _setup_test_client(store, "c1", "musico")
    report = learner.generate_insight_report()
    assert "CLIENT LEARNING REPORT" in report
    assert "musico" in report


def test_generate_insight_report_empty(store_and_learner):
    _, learner = store_and_learner
    report = learner.generate_insight_report()
    assert "CLIENT LEARNING REPORT" in report
