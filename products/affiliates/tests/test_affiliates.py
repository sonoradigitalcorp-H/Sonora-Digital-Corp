"""Tests for Affiliates Portal"""

import sys
from pathlib import Path

from fastapi.testclient import TestClient

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO))


import pytest

from products.affiliates.main import AFFILIATES_FILE, EARNINGS_FILE, PAYOUTS_FILE, app

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_data():
    for f in [AFFILIATES_FILE, EARNINGS_FILE, PAYOUTS_FILE]:
        f.parent.mkdir(parents=True, exist_ok=True)
        if f.exists():
            f.unlink()
    yield
    for f in [AFFILIATES_FILE, EARNINGS_FILE, PAYOUTS_FILE]:
        if f.exists():
            f.unlink()


def test_health():
    r = client.get("/affiliates/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_create_affiliate():
    r = client.post("/affiliates", json={"name": "Luis", "email": "luis@test.com", "phone": "6621111111"})
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert data["affiliate"]["id"].startswith("AF-")
    assert data["affiliate"]["ref_code"].startswith("REF-")
    assert data["affiliate"]["name"] == "Luis"


def test_list_affiliates():
    client.post("/affiliates", json={"name": "A1"})
    client.post("/affiliates", json={"name": "A2"})
    r = client.get("/affiliates")
    assert r.json()["totals"]["total"] == 2


def test_get_affiliate():
    create = client.post("/affiliates", json={"name": "Test"}).json()
    aff_id = create["affiliate"]["id"]
    r = client.get(f"/affiliates/{aff_id}")
    assert r.status_code == 200
    assert r.json()["affiliate"]["name"] == "Test"


def test_get_nonexistent():
    r = client.get("/affiliates/AF-NONEXIST")
    assert r.status_code == 404


def test_update_affiliate():
    create = client.post("/affiliates", json={"name": "Old"}).json()
    aff_id = create["affiliate"]["id"]
    r = client.put(f"/affiliates/{aff_id}", json={"name": "New", "commission_pct": 15.0})
    assert r.status_code == 200
    assert r.json()["affiliate"]["name"] == "New"
    assert r.json()["affiliate"]["commission_pct"] == 15.0


def test_deactivate():
    create = client.post("/affiliates", json={"name": "Del"}).json()
    aff_id = create["affiliate"]["id"]
    r = client.delete(f"/affiliates/{aff_id}")
    assert r.status_code == 200
    get = client.get(f"/affiliates/{aff_id}")
    assert get.json()["affiliate"]["active"] is False


def test_resolve_ref_code():
    create = client.post("/affiliates", json={"name": "Ref"}).json()
    ref_code = create["affiliate"]["ref_code"]
    r = client.get(f"/affiliates/ref/{ref_code}")
    assert r.status_code == 200


def test_generate_wa_link():
    create = client.post("/affiliates", json={"name": "WA Link"}).json()
    aff_id = create["affiliate"]["id"]
    r = client.get(f"/affiliates/generate-link/{aff_id}")
    assert r.status_code == 200
    assert "wa.me/5216623538272" in r.json()["link"]


def test_add_earning():
    aff = client.post("/affiliates", json={"name": "Earnie"}).json()["affiliate"]
    r = client.post("/earnings", json={
        "affiliate_id": aff["id"],
        "amount_tokens": 50,
        "amount_mxn": 100.0,
        "source": "referral",
        "referral_id": "client-123",
        "description": "Cliente nuevo via referido",
    })
    assert r.status_code == 200
    assert r.json()["earning"]["amount_tokens"] == 50

    # Check affiliate total updated
    get = client.get(f"/affiliates/{aff['id']}").json()
    assert get["affiliate"]["total_tokens"] == 50
    assert get["affiliate"]["total_mxn"] == 100.0
    assert get["affiliate"]["referrals_count"] == 1


def test_list_earnings():
    aff = client.post("/affiliates", json={"name": "E"}).json()["affiliate"]
    client.post("/earnings", json={"affiliate_id": aff["id"], "amount_tokens": 10, "source": "bonus"})
    r = client.get("/earnings")
    assert r.json()["total"] == 1
    assert r.json()["total_tokens"] == 10


def test_request_payout():
    aff = client.post("/affiliates", json={"name": "Pay"}).json()["affiliate"]
    r = client.post("/payouts", json={
        "affiliate_id": aff["id"],
        "amount_mxn": 500.0,
        "method": "transferencia",
        "account_info": "Cuenta: 1234-5678",
    })
    assert r.status_code == 200
    assert r.json()["payout"]["status"] == "pending"


def test_process_payout():
    aff = client.post("/affiliates", json={"name": "Proc"}).json()["affiliate"]
    payout = client.post("/payouts", json={"affiliate_id": aff["id"], "amount_mxn": 300.0}).json()["payout"]
    r = client.post(f"/payouts/{payout['id']}/process")
    assert r.status_code == 200
    assert r.json()["payout"]["status"] == "paid"


def test_leaderboard():
    a1 = client.post("/affiliates", json={"name": "Top"}).json()["affiliate"]
    a2 = client.post("/affiliates", json={"name": "Low"}).json()["affiliate"]
    client.post("/earnings", json={"affiliate_id": a1["id"], "amount_tokens": 100, "source": "referral"})
    client.post("/earnings", json={"affiliate_id": a2["id"], "amount_tokens": 10, "source": "referral"})
    r = client.get("/affiliates/leaderboard")
    assert r.json()["leaderboard"][0]["name"] == "Top"
    assert r.json()["leaderboard"][1]["name"] == "Low"


def test_stats():
    aff = client.post("/affiliates", json={"name": "Stats"}).json()["affiliate"]
    client.post("/earnings", json={"affiliate_id": aff["id"], "amount_tokens": 25, "amount_mxn": 50.0, "source": "referral"})
    r = client.get("/affiliates/stats")
    assert r.json()["total_affiliates"] == 1
    assert r.json()["total_tokens_earned"] == 25
