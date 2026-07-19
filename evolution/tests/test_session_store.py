"""Tests for Session Store — save, get, list, count, stats, errors."""
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO))

from evolution.session_store import SessionStore


@pytest.fixture
def store(tmp_path):
    return SessionStore(base_dir=tmp_path)


def make_session(overrides: dict = None) -> dict:
    base = {
        "user": "test-user",
        "type": "comando",
        "command": "/test",
        "success": True,
        "duration_ms": 100,
        "tokens_used": 50,
        "outcome": "ok",
        "improvement": "",
        "client_impact": False,
        "skills_used": ["bash"],
        "files_changed": [],
        "score": 0,
    }
    if overrides:
        base.update(overrides)
    return base


class TestSaveAndGet:
    def test_save_returns_session_id(self, store):
        sid = store.save(make_session())
        assert sid.startswith("ses-")

    def test_get_returns_saved_session(self, store):
        sid = store.save(make_session({"command": "/generar-nicho"}))
        session = store.get(sid)
        assert session is not None
        assert session["session_id"] == sid
        assert session["command"] == "/generar-nicho"

    def test_get_nonexistent_returns_none(self, store):
        assert store.get("ses-nonexistent") is None

    def test_save_sets_defaults(self, store):
        sid = store.save({"type": "evento"})
        session = store.get(sid)
        assert session["user"] == "system"
        assert session["success"] is True
        assert session["duration_ms"] == 0
        assert session["score"] == 0
        assert session["session_id"] == sid

    def test_save_preserves_all_fields(self, store):
        session = make_session({
            "command": "/deploy",
            "duration_ms": 4200,
            "tokens_used": 1500,
            "outcome": "Deployed successfully",
            "improvement": "Add rollback",
            "client_impact": True,
            "skills_used": ["bash", "docker"],
            "files_changed": ["docker-compose.yml", "deploy.sh"],
            "score": 8,
        })
        sid = store.save(session)
        loaded = store.get(sid)
        assert loaded["command"] == "/deploy"
        assert loaded["duration_ms"] == 4200
        assert loaded["tokens_used"] == 1500
        assert loaded["outcome"] == "Deployed successfully"
        assert loaded["improvement"] == "Add rollback"
        assert loaded["client_impact"] is True
        assert loaded["skills_used"] == ["bash", "docker"]
        assert loaded["files_changed"] == ["docker-compose.yml", "deploy.sh"]
        assert loaded["score"] == 8


class TestList:
    def test_list_returns_in_order(self, store):
        store.save(make_session({"command": "first"}))
        store.save(make_session({"command": "second"}))
        sessions = store.list()
        assert len(sessions) == 2
        assert sessions[0]["command"] == "second"  # most recent first

    def test_list_limit(self, store):
        for i in range(5):
            store.save(make_session({"command": f"cmd-{i}"}))
        assert len(store.list(limit=3)) == 3

    def test_list_filter_by_user(self, store):
        store.save(make_session({"user": "alice", "command": "a"}))
        store.save(make_session({"user": "bob", "command": "b"}))
        bob_sessions = store.list(user="bob")
        assert len(bob_sessions) == 1
        assert bob_sessions[0]["user"] == "bob"

    def test_list_filter_by_since(self, store):
        store.save(make_session({"command": "old"}))
        recent = store.list(since="2099-01-01T00:00:00Z")
        assert len(recent) == 0


class TestCount:
    def test_count_total(self, store):
        store.save(make_session())
        store.save(make_session())
        assert store.count() == 2

    def test_count_empty(self, store):
        assert store.count() == 0

    def test_count_with_since(self, store):
        store.save(make_session({"command": "old"}))
        store.save(make_session({"command": "new"}))
        count = store.count(since="2099-01-01T00:00:00Z")
        assert count == 0


class TestSuccessRate:
    def test_success_rate_all_success(self, store):
        store.save(make_session({"success": True}))
        store.save(make_session({"success": True}))
        assert store.success_rate() == 1.0

    def test_success_rate_mixed(self, store):
        store.save(make_session({"success": True}))
        store.save(make_session({"success": False}))
        assert store.success_rate() == 0.5

    def test_success_rate_empty(self, store):
        assert store.success_rate() == 0.0


class TestByType:
    def test_by_type_counts(self, store):
        store.save(make_session({"type": "comando"}))
        store.save(make_session({"type": "comando"}))
        store.save(make_session({"type": "error"}))
        result = store.by_type()
        assert result["comando"] == 2
        assert result["error"] == 1

    def test_by_type_empty(self, store):
        assert store.by_type() == {}


class TestStats:
    def test_stats_total(self, store):
        store.save(make_session())
        store.save(make_session())
        stats = store.stats()
        assert stats["total"] == 2

    def test_stats_by_type(self, store):
        store.save(make_session({"type": "comando"}))
        store.save(make_session({"type": "error"}))
        assert store.stats()["by_type"]["comando"] == 1
        assert store.stats()["by_type"]["error"] == 1

    def test_stats_success_rate(self, store):
        store.save(make_session({"success": True}))
        store.save(make_session({"success": False}))
        assert store.stats()["success_rate"] == 0.5

    def test_stats_avg_duration(self, store):
        store.save(make_session({"duration_ms": 100}))
        store.save(make_session({"duration_ms": 300}))
        assert store.stats()["avg_duration_ms"] == 200.0

    def test_stats_recent(self, store):
        store.save(make_session({"command": "a"}))
        store.save(make_session({"command": "b"}))
        assert len(store.stats()["recent"]) == 2

    def test_stats_empty(self, store):
        stats = store.stats()
        assert stats["total"] == 0
        assert stats["success_rate"] == 0.0
        assert stats["avg_duration_ms"] == 0.0
        assert stats["by_type"] == {}

    def test_stats_avg_duration_no_sessions(self, store):
        assert store.stats()["avg_duration_ms"] == 0.0


class TestRecentErrors:
    def test_recent_errors_filters_success(self, store):
        store.save(make_session({"success": True, "command": "ok"}))
        sid = store.save(make_session({"success": False, "command": "fail"}))
        errors = store.recent_errors()
        assert len(errors) == 1
        assert errors[0]["session_id"] == sid
        assert errors[0]["command"] == "fail"

    def test_recent_errors_limit(self, store):
        for _ in range(5):
            store.save(make_session({"success": False}))
        assert len(store.recent_errors(limit=2)) == 2

    def test_recent_errors_no_errors(self, store):
        store.save(make_session({"success": True}))
        assert store.recent_errors() == []


class TestMultipleUsers:
    def test_multiple_users(self, store):
        store.save(make_session({"user": "alice", "command": "a"}))
        store.save(make_session({"user": "bob", "command": "b"}))
        store.save(make_session({"user": "alice", "command": "c"}))
        assert store.count() == 3
        assert len(store.list(user="alice")) == 2
        assert len(store.list(user="bob")) == 1
        assert len(store.list(user="charlie")) == 0

    def test_stats_with_multiple_users(self, store):
        store.save(make_session({"user": "alice", "type": "comando", "success": True}))
        store.save(make_session({"user": "bob", "type": "error", "success": False}))
        stats = store.stats()
        assert stats["total"] == 2
        assert stats["success_rate"] == 0.5
