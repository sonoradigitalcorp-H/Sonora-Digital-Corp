"""
Tests de integración para Ce-Son API.
Usa TestClient de FastAPI con DB en memoria (:memory:) para evitar locks.
"""
import json
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO))

import pytest
from fastapi.testclient import TestClient

import apps.whatsapp.order_store as store

from products.ce_son.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    """Create a fresh temporary database for each test."""
    import tempfile
    tmp = tempfile.mktemp(suffix=".db")
    store.DEFAULT_DB = Path(tmp)
    conn = store.get_db(str(store.DEFAULT_DB))
    conn.close()
    yield
    import time
    time.sleep(0.1)
    for ext in ["", "-wal", "-shm"]:
        p = tmp + ext
        if os.path.exists(p):
            try:
                os.unlink(p)
            except OSError:
                pass


class TestCeSonAPI:
    def test_health(self):
        resp = client.get("/api/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["service"] == "ce-son-v3"

    def test_register_seller(self):
        resp = client.post("/api/sellers/register", json={
            "name": "Pedro Vendedor",
            "phone": "5216621111111",
            "email": "pedro@test.com",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["ok"] is True
        assert data["seller"]["name"] == "Pedro Vendedor"

    def test_register_duplicate_seller(self):
        client.post("/api/sellers/register", json={
            "name": "Pedro Vendedor", "phone": "5216621111111",
        })
        resp = client.post("/api/sellers/register", json={
            "name": "Pedro Again", "phone": "5216621111111",
        })
        assert resp.status_code == 200
        assert resp.json()["seller"]["name"] == "Pedro Vendedor"

    def test_get_seller(self):
        client.post("/api/sellers/register", json={
            "name": "Test", "phone": "5216621111111",
        })
        resp = client.get("/api/sellers/by-phone/5216621111111")
        assert resp.status_code == 200
        assert resp.json()["seller"]["phone"] == "5216621111111"

    def test_get_seller_not_found(self):
        resp = client.get("/api/sellers/by-phone/5216620000000")
        assert resp.status_code == 404

    def test_create_order(self):
        resp = client.post("/api/orders", json={
            "client_name": "Juan Pérez",
            "client_phone": "5216623446953",
            "client_address": "Calle 1 #123",
            "items": [{"flavor": "uva", "qty": 2, "price": 250, "name": "Uva", "emoji": "🍇"}],
            "total": 500,
            "payment_method": "efectivo",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["ok"] is True
        assert data["order"]["id"].startswith("ORD-")

    def test_list_orders(self):
        client.post("/api/orders", json={
            "client_name": "Test", "total": 350,
            "items": [{"flavor": "fresa", "qty": 1, "price": 350}],
        })
        resp = client.get("/api/orders")
        assert resp.status_code == 200
        data = resp.json()
        assert "orders" in data
        assert len(data["orders"]) > 0

    def test_get_order(self):
        resp = client.post("/api/orders", json={
            "client_name": "Test Order", "total": 350,
            "items": [{"flavor": "fresa", "qty": 1, "price": 350}],
        })
        oid = resp.json()["order"]["id"]
        resp = client.get(f"/api/orders/{oid}")
        assert resp.status_code == 200
        assert resp.json()["order"]["id"] == oid

    def test_get_order_not_found(self):
        resp = client.get("/api/orders/NONEXISTENT")
        assert resp.status_code == 404

    def test_seller_dashboard(self):
        resp = client.post("/api/sellers/register", json={
            "name": "Ana Dashboard", "phone": "5216622222222",
        })
        sid = resp.json()["seller"]["id"]
        resp = client.get(f"/api/sellers/{sid}/dashboard")
        assert resp.status_code == 200
        data = resp.json()
        assert data["seller"] is not None
        assert "total_orders" in data

    def test_award_badge(self):
        resp = client.post("/api/sellers/register", json={
            "name": "Badge Test", "phone": "5216623333333",
        })
        sid = resp.json()["seller"]["id"]
        resp = client.post(f"/api/sellers/{sid}/award-badge?badge_id=primera_venta")
        assert resp.status_code == 200
        assert resp.json()["ok"] is True

    def test_add_tokens(self):
        resp = client.post("/api/sellers/register", json={
            "name": "Token Test", "phone": "5216624444444",
        })
        sid = resp.json()["seller"]["id"]
        resp = client.post(f"/api/sellers/{sid}/tokens?amount=100&reason=venta")
        assert resp.status_code == 200
        assert resp.json()["tokens"] == 100

    def test_get_badges(self):
        resp = client.post("/api/sellers/register", json={
            "name": "Badges List", "phone": "5216625555555",
        })
        sid = resp.json()["seller"]["id"]
        client.post(f"/api/sellers/{sid}/award-badge?badge_id=primera_venta")
        resp = client.get(f"/api/sellers/{sid}/badges")
        assert resp.status_code == 200
        assert len(resp.json()["badges"]) >= 1

    def test_register_client(self):
        resp = client.post("/api/sellers/register", json={
            "name": "Vendedor Clients", "phone": "5216626666666",
        })
        sid = resp.json()["seller"]["id"]
        resp = client.post("/api/clients", json={
            "seller_id": sid, "name": "Cliente Test",
            "phone": "5216627777777", "address": "Av. Test 123",
        })
        assert resp.status_code == 200
        assert resp.json()["client"]["name"] == "Cliente Test"

    def test_list_clients(self):
        resp = client.post("/api/sellers/register", json={
            "name": "V List", "phone": "5216628888888",
        })
        sid = resp.json()["seller"]["id"]
        resp = client.get(f"/api/clients?seller_id={sid}")
        assert resp.status_code == 200
        assert "clients" in resp.json()

    def test_owner_report(self):
        resp = client.get("/api/owner/report")
        assert resp.status_code == 200
        data = resp.json()
        assert "total_orders" in data
        assert "total_sellers" in data

    def test_order_lifecycle(self):
        resp = client.post("/api/orders", json={
            "client_name": "Lifecycle Test", "total": 550,
            "items": [{"flavor": "nuez", "qty": 1, "price": 550}],
        })
        oid = resp.json()["order"]["id"]
        assert resp.json()["order"]["status"] == "pendiente"

        resp = client.post(f"/api/orders/{oid}/status?status=entregado&actor=e2e")
        assert resp.status_code == 200
        assert resp.json()["order"]["status"] == "entregado"
