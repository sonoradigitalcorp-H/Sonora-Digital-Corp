"""Tests for apps/whatsapp/webhook.py"""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO))

from apps.whatsapp import webhook


@pytest.fixture
def clean_seen(tmp_path, monkeypatch):
    seen_path = tmp_path / "seen_messages.json"
    monkeypatch.setattr(webhook, "SEEN_PATH", seen_path)
    return seen_path


# ─── Helpers ─────────────────────────────────────────────────────────

def _mock_fetch(messages):
    return patch.object(webhook, "_fetch_messages", return_value=messages)


def _mock_emit():
    return patch.object(webhook, "emit_event")


# ─── _normalize_sender ───────────────────────────────────────────────

@pytest.mark.parametrize("raw,expected", [
    ("5216623538272@s.whatsapp.net", "5216623538272"),
    ("5216623538272.0:1@s.whatsapp.net", "5216623538272.0:1"),
    ("6622681111", "6622681111"),
])
def test_normalize_sender(raw, expected):
    assert webhook._normalize_sender(raw) == expected


# ─── _process_message ────────────────────────────────────────────────

def test_process_message_new(clean_seen):
    msg = {"id": "MSG001", "sender": "5216623538272@s.whatsapp.net", "text": "Hola"}
    with _mock_emit():
        new = webhook._process_message(msg, set())
    assert new is True


def test_process_message_duplicate(clean_seen):
    msg = {"id": "MSG001", "sender": "5216623538272@s.whatsapp.net", "text": "Hola"}
    seen = {"MSG001"}
    with _mock_emit():
        new = webhook._process_message(msg, seen)
    assert new is False


def test_process_message_triggers_catalog(clean_seen):
    msg = {"id": "MSG002", "sender": "5216623538272@s.whatsapp.net", "text": "Envíame el catálogo"}
    emitted = []
    with patch.object(webhook, "emit_event", side_effect=lambda t, p: emitted.append((t, p))):
        webhook._process_message(msg, set())
    event_types = [e[0] for e in emitted]
    assert "whatsapp:message:received" in event_types
    assert "whatsapp:catalog:requested" in event_types


# ─── _load_seen / _save_seen ─────────────────────────────────────────

def test_load_save_seen(clean_seen):
    seen = {"a", "b"}
    webhook._save_seen(seen)
    loaded = webhook._load_seen()
    assert loaded == seen


def test_load_seen_missing_file(clean_seen):
    loaded = webhook._load_seen()
    assert loaded == set()


# ─── run_webhook ─────────────────────────────────────────────────────

@patch("time.sleep", return_value=None)
def test_run_webhook_processes_new_messages(mock_sleep, clean_seen):
    messages = [
        {"id": "M1", "sender": "5216623538272@s.whatsapp.net", "text": "Hola"},
        {"id": "M2", "sender": "5216623538272@s.whatsapp.net", "text": "catálogo"},
    ]
    emitted = []
    with patch.object(webhook, "_fetch_messages", return_value=messages), \
         patch.object(webhook, "emit_event", side_effect=lambda t, p: emitted.append((t, p))):
        webhook.run_webhook(interval=5, once=True)

    event_types = [e[0] for e in emitted]
    assert "whatsapp:message:received" in event_types
    # Verify seen state saved
    assert clean_seen.exists()


@patch("time.sleep", return_value=None)
def test_run_webhook_reconnect(mock_sleep, clean_seen):
    emitted = []
    with patch.object(webhook, "_fetch_messages", return_value=None), \
         patch.object(webhook, "emit_event", side_effect=lambda t, p: emitted.append((t, p))):
        try:
            webhook.run_webhook(interval=5, once=True)
        except Exception:
            pass
    event_types = [e[0] for e in emitted]
    assert "system:whatsapp:disconnected" in event_types


# ─── _fetch_messages ─────────────────────────────────────────────────

def test_fetch_messages_success():
    messages = [{"id": "M1", "text": "Hola"}]
    with patch.object(webhook, "_wacli", return_value={"success": True, "data": messages}):
        result = webhook._fetch_messages()
    assert result == messages


def test_fetch_messages_failure():
    with patch.object(webhook, "_wacli", return_value={"success": False, "error": "auth"}):
        result = webhook._fetch_messages()
    assert result == []


def test_fetch_messages_data_dict():
    with patch.object(webhook, "_wacli", return_value={"success": True, "data": {"messages": [{"id": "M1"}]}}):
        result = webhook._fetch_messages()
    assert len(result) == 1
    assert result[0]["id"] == "M1"
