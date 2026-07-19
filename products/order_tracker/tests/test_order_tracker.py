"""Tests for Order Tracker"""

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO))

from products.order_tracker.main import ORDERS_FILE, app

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_orders():
    ORDERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    if ORDERS_FILE.exists():
        ORDERS_FILE.unlink()
    yield
    if ORDERS_FILE.exists():
        ORDERS_FILE.unlink()


def test_health():
    r = client.get("/tracker/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_create_order():
    r = client.post("/tracker/orders", json={
        "client_id": "test-client",
        "client_phone": "5216622681111",
        "service_type": "photo",
        "description": "Foto profesional",
        "tokens_cost": 10,
    })
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert data["order"]["id"].startswith("ORD-")
    assert data["order"]["status"] == "queued"


def test_list_orders_empty():
    r = client.get("/tracker/orders")
    assert r.status_code == 200
    assert r.json()["total"] == 0


def test_list_orders_with_data():
    client.post("/tracker/orders", json={"client_id": "c1", "service_type": "photo", "description": "Test"})
    r = client.get("/tracker/orders")
    assert r.json()["total"] == 1


def test_get_order():
    create = client.post("/tracker/orders", json={"client_id": "c1", "service_type": "video"}).json()
    order_id = create["order"]["id"]
    r = client.get(f"/tracker/orders/{order_id}")
    assert r.status_code == 200
    assert r.json()["order"]["id"] == order_id


def test_get_nonexistent_order():
    r = client.get("/tracker/orders/ORD-NONEXIST")
    assert r.status_code == 404


def test_update_order_status():
    create = client.post("/tracker/orders", json={"client_id": "c1", "service_type": "photo"}).json()
    order_id = create["order"]["id"]
    r = client.put(f"/tracker/orders/{order_id}", json={"status": "processing", "notes": "Working on it"})
    assert r.status_code == 200
    assert r.json()["order"]["status"] == "processing"
    assert len(r.json()["order"]["status_history"]) == 2


def test_update_invalid_status():
    create = client.post("/tracker/orders", json={"client_id": "c1", "service_type": "photo"}).json()
    r = client.put(f"/tracker/orders/{create['order']['id']}", json={"status": "invalid_status"})
    assert r.status_code == 400


def test_next_status():
    create = client.post("/tracker/orders", json={"client_id": "c1", "service_type": "photo"}).json()
    order_id = create["order"]["id"]
    # queued → processing
    r = client.post(f"/tracker/orders/{order_id}/next")
    assert r.status_code == 200
    assert r.json()["order"]["status"] == "processing"
    # processing → completed
    r = client.post(f"/tracker/orders/{order_id}/next")
    assert r.json()["order"]["status"] == "completed"


def test_next_status_at_final():
    """Should fail when trying to advance past delivered."""
    create = client.post("/tracker/orders", json={"client_id": "c1", "service_type": "photo"}).json()
    order_id = create["order"]["id"]
    for _ in range(4):  # queued → processing → completed → delivered
        client.post(f"/tracker/orders/{order_id}/next")
    r = client.post(f"/tracker/orders/{order_id}/next")
    assert r.status_code == 400


def test_set_delivery_url():
    create = client.post("/tracker/orders", json={"client_id": "c1", "service_type": "photo"}).json()
    order_id = create["order"]["id"]
    r = client.put(f"/tracker/orders/{order_id}", json={
        "status": "completed",
        "delivery_url": "https://cdn.sonora.com/photo.jpg",
    })
    assert r.json()["order"]["delivery_url"] == "https://cdn.sonora.com/photo.jpg"


def test_filter_by_client():
    client.post("/tracker/orders", json={"client_id": "c1", "service_type": "photo"})
    client.post("/tracker/orders", json={"client_id": "c2", "service_type": "video"})
    r = client.get("/tracker/orders?client_id=c1")
    assert r.json()["total"] == 1


def test_tracker_stats():
    client.post("/tracker/orders", json={"client_id": "c1", "service_type": "photo"})
    client.post("/tracker/orders", json={"client_id": "c2", "service_type": "video"})
    r = client.get("/tracker/stats")
    assert r.json()["total"] == 2
    assert "queued" in r.json()["by_status"]
