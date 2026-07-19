"""Tests for ClientStore — 8 tests"""

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO))

import pytest

from memory.client_store import ClientStore


@pytest.fixture
def store(tmp_path):
    return ClientStore(base_dir=tmp_path / "clients")


def test_ensure_profile(store):
    profile = store._ensure_profile("c1", {"name": "Test", "niche": "musico"})
    assert profile["client_id"] == "c1"
    assert profile["name"] == "Test"
    assert profile["niche"] == "musico"
    assert profile["total_interactions"] == 0


def test_get_profile(store):
    store._ensure_profile("c1", {"name": "Test"})
    profile = store.get_profile("c1")
    assert profile["name"] == "Test"


def test_get_profile_nonexistent(store):
    assert store.get_profile("nonexistent") is None


def test_save_and_get_interactions(store):
    store._ensure_profile("c1", {"name": "Test"})
    store.save_interaction("c1", {"type": "message", "content": "hello", "tokens_used": 5})
    store.save_interaction("c1", {"type": "order", "content": "buy clone", "tokens_used": 10})
    interactions = store.get_interactions("c1")
    assert len(interactions) == 2
    types = {i["type"] for i in interactions}
    assert "message" in types
    assert "order" in types


def test_interaction_updates_profile(store):
    store._ensure_profile("c1", {"name": "Test"})
    store.save_interaction("c1", {"type": "message", "tokens_used": 10, "service": "clone-voice"})
    profile = store.get_profile("c1")
    assert profile["total_interactions"] == 1
    assert profile["total_tokens_spent"] == 10
    assert "clone-voice" in profile["services_used"]


def test_satisfaction_score_computed(store):
    store._ensure_profile("c1", {"name": "Test"})
    store.save_interaction("c1", {"satisfaction_score": 8})
    store.save_interaction("c1", {"satisfaction_score": 9})
    profile = store.get_profile("c1")
    assert profile["satisfaction_score"] == 8.5  # (8+9)/2


def test_add_get_patterns(store):
    store._ensure_profile("c1", {"name": "Test"})
    store.add_pattern("c1", {"type": "FREQUENT_SERVICE", "service": "clone"})
    store.add_pattern("c1", {"type": "HIGH_VALUE", "score": 9})
    patterns = store.get_patterns("c1")
    assert len(patterns) == 2
    assert patterns[0]["type"] == "FREQUENT_SERVICE"


def test_add_get_recommendations(store):
    store._ensure_profile("c1", {"name": "Test"})
    store.add_recommendation("c1", {"text": "Try bundle A"})
    recs = store.get_recommendations("c1")
    assert len(recs) == 1
    assert recs[0]["text"] == "Try bundle A"


def test_all_clients(store):
    store._ensure_profile("c1", {"name": "A"})
    store._ensure_profile("c2", {"name": "B"})
    clients = store.all_clients()
    assert len(clients) == 2
    assert "c1" in clients
    assert "c2" in clients


def test_stats(store):
    store._ensure_profile("c1", {"name": "A", "niche": "musico"})
    store._ensure_profile("c2", {"name": "B", "niche": "barbero", "active": False})
    store.save_interaction("c1", {"type": "message"})
    store.add_pattern("c1", {"type": "TEST"})
    stats = store.stats()
    assert stats["total_clients"] == 2
    assert stats["active_clients"] == 1
    assert stats["total_interactions"] == 1
    assert stats["total_patterns"] == 1
    assert stats["niches"]["musico"] == 1
    assert stats["niches"]["barbero"] == 1


def test_update_profile(store):
    store._ensure_profile("c1", {"name": "Old", "niche": "musico"})
    store.update_profile("c1", {"name": "New", "active": False})
    profile = store.get_profile("c1")
    assert profile["name"] == "New"
    assert profile["active"] is False
    assert profile["niche"] == "musico"
