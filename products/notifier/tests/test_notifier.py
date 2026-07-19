"""Tests for Sonora Notifier"""

import sys
from pathlib import Path
from unittest.mock import patch

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO))

from products.notifier import core, main

# ─── Core tests ──────────────────────────────────────────────────────

def test_check_rules_match_exact():
    event = {"event": "whatsapp:message:received", "payload": {"from": "test"}}
    rules = [{"event_type": "whatsapp:message:received", "enabled": True}]
    matches = core.check_rules(event, rules)
    assert len(matches) == 1


def test_check_rules_no_match():
    event = {"event": "whatsapp:message:received", "payload": {}}
    rules = [{"event_type": "onboarding:completed", "enabled": True}]
    matches = core.check_rules(event, rules)
    assert len(matches) == 0


def test_check_rules_disabled():
    event = {"event": "whatsapp:message:received", "payload": {}}
    rules = [{"event_type": "whatsapp:message:received", "enabled": False}]
    matches = core.check_rules(event, rules)
    assert len(matches) == 0


def test_check_rules_wildcard():
    event = {"event": "whatsapp:message:received", "payload": {}}
    rules = [{"event_type": "whatsapp:*", "enabled": True}]
    matches = core.check_rules(event, rules)
    assert len(matches) == 1


def test_render_template():
    result = core._render("Hola {{name}}!", {"name": "Luis"})
    assert result == "Hola Luis!"


def test_render_template_missing_var():
    result = core._render("Hola {{name}}!", {})
    assert "{{name}}" in result  # Leaves variable as-is when missing


@patch.object(core, "_send_whatsapp", return_value={"sent": True})
def test_deliver_whatsapp(mock_send):
    rule = {
        "id": "rule-001",
        "channel": "whatsapp",
        "template": "Test {{name}}",
        "recipients": ["5216622681111"],
        "tenant": "default",
    }
    event = {"payload": {"name": "Luis"}}
    result = core.deliver(rule, event)
    assert result["rule_id"] == "rule-001"
    assert result["deliveries"][0]["status"] == "sent"


def test_deliver_unknown_channel():
    rule = {
        "id": "rule-002",
        "channel": "fax",
        "template": "Test",
        "recipients": ["123"],
        "tenant": "default",
    }
    event = {"payload": {}}
    result = core.deliver(rule, event)
    assert result["deliveries"][0]["status"] == "failed"
    assert "unknown channel" in result["deliveries"][0]["error"]


# ─── API tests ───────────────────────────────────────────────────────

from fastapi.testclient import TestClient

client = TestClient(main.app)


def test_health():
    r = client.get("/notifier/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_list_rules():
    r = client.get("/notifier/rules")
    assert r.status_code == 200
    assert "rules" in r.json()
    assert "total" in r.json()


def test_create_rule():
    r = client.post("/notifier/rules", json={
        "event_type": "test:event",
        "channel": "email",
        "template": "Test {{x}}",
        "recipients": ["admin@test.com"],
    })
    assert r.status_code == 200
    assert r.json()["ok"] is True
    assert r.json()["id"].startswith("rule-")


def test_create_and_delete_rule():
    r = client.post("/notifier/rules", json={
        "event_type": "test:delete",
        "channel": "whatsapp",
        "template": "Delete me",
    })
    rule_id = r.json()["id"]
    r = client.delete(f"/notifier/rules/{rule_id}")
    assert r.status_code == 200
    assert r.json()["ok"] is True


def test_delete_nonexistent():
    r = client.delete("/notifier/rules/rule-nonexistent")
    assert r.status_code == 404


def test_stats():
    r = client.get("/notifier/stats")
    assert r.status_code == 200
    assert "rules" in r.json()
    assert "enabled" in r.json()


def test_delivery_log():
    r = client.get("/notifier/log")
    assert r.status_code == 200
    assert "entries" in r.json()
    assert "total" in r.json()
