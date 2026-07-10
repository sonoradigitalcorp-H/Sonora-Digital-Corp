import pytest
from fastapi.testclient import TestClient
from products.mystik.main import app, PRODUCT_CATALOG

client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_list_products():
    resp = client.get("/api/products")
    assert resp.status_code == 200
    assert len(resp.json()["products"]) == 5


def test_chat():
    resp = client.post("/api/chat", json={"message": "qué es content studio?"})
    assert resp.status_code == 200
    data = resp.json()
    assert "response" in data
    assert len(data["response"]) > 0


def test_chat_no_message():
    resp = client.post("/api/chat", json={"message": ""})
    assert resp.status_code == 200


def test_create_lead():
    resp = client.post("/api/leads", json={
        "name": "Test Lead", "email": "test@example.com", "company": "TestCorp",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "created"


def test_create_lead_minimal():
    resp = client.post("/api/leads", json={"name": "Minimal", "email": "min@test.com"})
    assert resp.status_code == 200


def test_list_leads():
    resp = client.get("/api/leads")
    assert resp.status_code == 200
    assert "leads" in resp.json()


def test_qualify_lead():
    resp = client.post("/api/leads/999/qualify", json={"tenant": "sonora"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "qualified"


def test_knowledge_search():
    resp = client.post("/api/knowledge?query=omnivoice&tenant=sonora")
    assert resp.status_code == 200
    assert "results" in resp.json()


def test_tenant_config():
    resp = client.get("/api/tenant/sonora/config")
    assert resp.status_code == 200
    assert resp.json()["tenant"] == "sonora"
    assert resp.json()["branding"]["name"] == "Mystik AI"


def test_root_html():
    resp = client.get("/")
    assert resp.status_code == 200
    assert "Mystik AI" in resp.text


def test_products_have_all_fields():
    for p in PRODUCT_CATALOG:
        assert "id" in p
        assert "name" in p
        assert "description" in p
        assert "price" in p
