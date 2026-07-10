import pytest
from fastapi.testclient import TestClient
from capabilities.bus.router import load_registry, match_intent, route, get_capability, validate_policies

# Minimal test app
from fastapi import FastAPI
app = FastAPI()
from capabilities.bus.web import router
app.include_router(router)
client = TestClient(app)


def test_load_registry():
    registry = load_registry()
    assert "capabilities" in registry
    assert len(registry["capabilities"]) >= 8


def test_match_intent_known():
    cap_id, conf = match_intent("sync artist data")
    assert cap_id == "sync-artist-data"
    assert conf > 0.0


def test_match_intent_unknown():
    cap_id, conf = match_intent("xyzzy magic foo")
    assert cap_id is None
    assert conf == 0.0


def test_match_intent_crm():
    cap_id, _ = match_intent("create new lead in crm")
    assert cap_id == "manage-crm"


def test_match_intent_payment():
    cap_id, _ = match_intent("process payment for invoice")
    assert cap_id == "process-payment"


def test_match_intent_video():
    cap_id, _ = match_intent("generate video for artist")
    assert cap_id == "generate-video"


def test_route_success():
    result = route("sync artist data", {})
    assert result["status"] == "routed"
    assert result["capability"] == "sync-artist-data"
    assert result["policies"]["passed"]


def test_route_high_cost_needs_approval():
    result = route("generate video for artist", {})
    assert result["status"] == "policy_blocked"
    assert "cost" in str(result)


def test_route_high_cost_approved():
    result = route("generate video for artist", {"approved": True, "allow_experimental": True})
    assert result["status"] == "routed"


def test_get_capability():
    cap = get_capability("sync-artist-data")
    assert cap is not None
    assert cap["id"] == "sync-artist-data"


def test_get_capability_not_found():
    cap = get_capability("nonexistent")
    assert cap is None


def test_validate_policies_pass():
    cap = {"cost_tier": 1, "status": "active", "agent": None}
    result = validate_policies(cap, {})
    assert result["passed"]


def test_validate_policies_fail_cost():
    cap = {"cost_tier": 4, "status": "active", "agent": None}
    result = validate_policies(cap, {})
    assert not result["passed"]


def test_api_list_capabilities():
    resp = client.get("/api/v1/capability-bus/capabilities")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["capabilities"]) >= 8


def test_api_get_capability():
    resp = client.get("/api/v1/capability-bus/capabilities/sync-artist-data")
    assert resp.status_code == 200
    assert resp.json()["id"] == "sync-artist-data"


def test_api_get_capability_404():
    resp = client.get("/api/v1/capability-bus/capabilities/nonexistent")
    assert resp.status_code == 404


def test_api_route_success():
    resp = client.post("/api/v1/capability-bus/route", json={"query": "sync artist data"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "routed"


def test_api_route_no_match():
    resp = client.post("/api/v1/capability-bus/route", json={"query": "xyzzy magic foo"})
    assert resp.status_code == 404


def test_api_route_policy_blocked():
    resp = client.post("/api/v1/capability-bus/route", json={"query": "generate video"})
    assert resp.status_code == 403
