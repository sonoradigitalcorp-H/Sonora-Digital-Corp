"""Tests for Client API — 15 tests covering all endpoints"""

import json
import sys
from pathlib import Path

from fastapi.testclient import TestClient

REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO))

import pytest

from products.client_api.main import app, store

client = TestClient(app)

TEST_CLIENT_DIR = REPO / "memory" / "clients" / "test-client-001"


@pytest.fixture(autouse=True)
def clean_data():
    if TEST_CLIENT_DIR.exists():
        import shutil
        shutil.rmtree(TEST_CLIENT_DIR)
    yield
    if TEST_CLIENT_DIR.exists():
        import shutil
        shutil.rmtree(TEST_CLIENT_DIR)


def _setup_client():
    store._ensure_profile("test-client-001", {
        "name": "Juan Pérez",
        "phone": "5216622681111",
        "niche": "musico",
        "tenant": "sdc",
    })
    store.save_interaction("test-client-001", {
        "type": "message", "content": "Hola quiero un clon", "service": "clone-voice",
        "tokens_used": 10, "success": True, "satisfaction_score": 9,
    })
    store.save_interaction("test-client-001", {
        "type": "message", "content": "¿Cuánto cuesta?", "service": "photo-professional",
        "tokens_used": 5, "success": True, "satisfaction_score": 8,
    })


def test_health():
    r = client.get("/clients/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_stats_empty():
    r = client.get("/clients/stats")
    assert r.status_code == 200
    assert r.json()["total_clients"] == 0


def test_stats_with_data():
    _setup_client()
    r = client.get("/clients/stats")
    data = r.json()
    assert data["total_clients"] == 1
    assert data["total_interactions"] == 2


def test_list_clients_empty():
    r = client.get("/clients")
    assert r.json()["total"] == 0


def test_list_clients_with_data():
    _setup_client()
    r = client.get("/clients")
    assert r.json()["total"] == 1
    assert r.json()["clients"][0]["client_id"] == "test-client-001"


def test_list_clients_filter_niche():
    _setup_client()
    r = client.get("/clients?niche=musico")
    assert r.json()["total"] == 1
    r = client.get("/clients?niche=barbero")
    assert r.json()["total"] == 0


def test_get_client():
    _setup_client()
    r = client.get("/clients/test-client-001")
    assert r.status_code == 200
    data = r.json()
    assert data["profile"]["name"] == "Juan Pérez"
    assert len(data["recent_interactions"]) == 2
    assert data["analysis"]["total_interactions"] == 2


def test_get_client_nonexistent():
    r = client.get("/clients/nonexistent")
    assert r.status_code == 404


def test_record_interaction():
    _setup_client()
    r = client.post("/clients/test-client-001/interaction", json={
        "type": "message",
        "content": "Nueva interacción",
        "service": "video-talking-head",
        "tokens_used": 15,
        "success": True,
    })
    assert r.status_code == 200
    assert r.json()["ok"] is True
    profile = store.get_profile("test-client-001")
    assert profile["total_interactions"] == 3


def test_record_interaction_nonexistent():
    r = client.post("/clients/nonexistent/interaction", json={"type": "message", "content": "test"})
    assert r.status_code == 404


def test_update_client():
    _setup_client()
    r = client.put("/clients/test-client-001", json={"name": "Juan Actualizado", "niche": "barbero"})
    assert r.status_code == 200
    assert r.json()["profile"]["name"] == "Juan Actualizado"
    assert r.json()["profile"]["niche"] == "barbero"
    profile = store.get_profile("test-client-001")
    assert profile["name"] == "Juan Actualizado"


def test_update_client_nonexistent():
    r = client.put("/clients/nonexistent", json={"name": "test"})
    assert r.status_code == 404


def test_client_patterns():
    _setup_client()
    store.add_pattern("test-client-001", {"type": "FREQUENT_SERVICE", "service": "clone-voice"})
    r = client.get("/clients/test-client-001/patterns")
    assert r.status_code == 200
    assert len(r.json()["patterns"]) == 1
    assert r.json()["patterns"][0]["type"] == "FREQUENT_SERVICE"


def test_client_recommendations():
    _setup_client()
    store.add_recommendation("test-client-001", {"text": "Try clone-voice bundle"})
    r = client.get("/clients/test-client-001/recommendations")
    assert r.status_code == 200
    assert len(r.json()["recommendations"]) == 1
    assert r.json()["auto_recommendation"] != ""


def test_niche_insights():
    _setup_client()
    r = client.get("/niches/musico/insights")
    assert r.status_code == 200
    assert r.json()["client_count"] == 1
    assert r.json()["niche"] == "musico"


def test_niche_insights_nonexistent():
    r = client.get("/niches/nonexistent/insights")
    assert r.status_code == 404


def test_all_insights():
    _setup_client()
    r = client.get("/insights")
    assert r.status_code == 200
    assert len(r.json()["insights"]) >= 1


def test_learning_report():
    _setup_client()
    r = client.get("/report")
    assert r.status_code == 200
    assert r.json()["total_clients"] >= 1
