"""Tests for evolution/learner.py — Learner Engine."""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO))

from evolution.learner import Learner, SessionStore


@pytest.fixture
def mock_store(tmp_path):
    """SessionStore backed by a temp file so tests don't touch real state."""
    sessions_file = tmp_path / "sessions.jsonl"
    return SessionStore(sessions_file=str(sessions_file))


@pytest.fixture
def learner(mock_store):
    return Learner(store=mock_store)


def _make_session(overrides=None):
    base = {
        "id": "sess-test",
        "command_type": "chat",
        "skill_used": "hermes",
        "user": "luis",
        "success": True,
        "duration": 10.0,
        "error": None,
        "user_rephrase": False,
        "outcome_completeness": 3,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    if overrides:
        base.update(overrides)
    return base


def _seed(store, sessions: list[dict]):
    for s in sessions:
        store.save_session(s)


class TestScoreSession:
    def test_success_gets_4_points(self, learner):
        s = _make_session({"success": True})
        score = learner.score_session(s)
        assert score >= 4

    def test_failure_gets_no_success_points(self, learner):
        s = _make_session({"success": False, "outcome_completeness": 0, "duration": 100})
        score = learner.score_session(s)
        assert score < 4

    def test_error_deducts_2(self, learner):
        s = _make_session({"success": True, "error": "timeout"})
        score = learner.score_session(s)
        assert score == 5  # 4 (success) + 0 (avg duration) - 2 (error) + 3 (completeness) = 5

    def test_user_rephrase_deducts_1(self, learner):
        s = _make_session({"success": True, "user_rephrase": True})
        score = learner.score_session(s)
        assert score == 6  # 4 + 0 (avg) - 1 + 3 = 6

    def test_outcome_completeness_adds_points(self, learner):
        s = _make_session({"success": True, "outcome_completeness": 2})
        score = learner.score_session(s)
        assert score == 6  # 4 + 0 (avg) + 2 = 6

    def test_score_capped_at_10(self, learner):
        s = _make_session({"success": True, "outcome_completeness": 3, "duration": 1.0})
        score = learner.score_session(s)
        assert score <= 10

    def test_score_floor_at_0(self, learner):
        s = _make_session({
            "success": False,
            "outcome_completeness": 0,
            "error": "crash",
            "user_rephrase": True,
            "duration": 999,
        })
        assert learner.score_session(s) == 0


class TestScoreAllPending:
    def test_scores_unscored_sessions(self, learner):
        _seed(learner.store, [
            _make_session({"id": "s1"}),
            _make_session({"id": "s2"}),
        ])
        count = learner.score_all_pending()
        assert count == 2

    def test_does_not_rescore(self, learner):
        _seed(learner.store, [
            _make_session({"id": "s1", "score": 8}),
            _make_session({"id": "s2"}),
        ])
        count = learner.score_all_pending()
        assert count == 1

    def test_returns_zero_when_none_pending(self, learner):
        count = learner.score_all_pending()
        assert count == 0


class TestGetMetrics:
    def test_returns_empty_when_no_sessions(self, learner):
        metrics = learner.get_metrics()
        assert metrics["total_sessions"] == 0

    def test_aggregates_success_rate(self, learner):
        _seed(learner.store, [
            _make_session({"id": "s1", "success": True, "score": 8}),
            _make_session({"id": "s2", "success": True, "score": 7}),
            _make_session({"id": "s3", "success": False, "score": 3}),
        ])
        metrics = learner.get_metrics()
        assert metrics["overall_success_rate"] == pytest.approx(0.667, abs=0.01)

    def test_by_type_groups_correctly(self, learner):
        _seed(learner.store, [
            _make_session({"id": "s1", "command_type": "chat", "success": True, "score": 8}),
            _make_session({"id": "s2", "command_type": "chat", "success": False, "score": 3}),
            _make_session({"id": "s3", "command_type": "code", "success": True, "score": 9}),
        ])
        metrics = learner.get_metrics()
        assert metrics["by_type"]["chat"]["count"] == 2
        assert metrics["by_type"]["chat"]["success_rate"] == 0.5
        assert metrics["by_type"]["code"]["count"] == 1
        assert metrics["by_type"]["code"]["success_rate"] == 1.0

    def test_by_skill_groups_correctly(self, learner):
        _seed(learner.store, [
            _make_session({"id": "s1", "skill_used": "hermes", "success": True, "score": 8}),
            _make_session({"id": "s2", "skill_used": "hermes", "success": True, "score": 7}),
            _make_session({"id": "s3", "skill_used": "openclaw", "success": False, "score": 2}),
        ])
        metrics = learner.get_metrics()
        assert metrics["by_skill"]["hermes"]["count"] == 2
        assert metrics["by_skill"]["hermes"]["success_rate"] == 1.0
        assert metrics["by_skill"]["hermes"]["avg_score"] == 7.5
        assert metrics["by_skill"]["openclaw"]["count"] == 1

    def test_common_errors_identifies_frequent(self, learner):
        _seed(learner.store, [
            _make_session({"id": "s1", "error": "timeout", "success": False, "score": 2}),
            _make_session({"id": "s2", "error": "timeout", "success": False, "score": 2}),
            _make_session({"id": "s3", "error": "auth_failed", "success": False, "score": 2}),
        ])
        metrics = learner.get_metrics()
        assert len(metrics["common_errors"]) == 2
        assert metrics["common_errors"][0]["error"] == "timeout"
        assert metrics["common_errors"][0]["count"] == 2

    def test_improvement_trend_has_7_days(self, learner):
        _seed(learner.store, [
            _make_session({"id": "s1", "success": True, "score": 8}),
        ])
        metrics = learner.get_metrics()
        assert len(metrics["improvement_trend"]) == 7

    def test_by_user_groups_correctly(self, learner):
        _seed(learner.store, [
            _make_session({"id": "s1", "user": "luis", "success": True, "score": 8}),
            _make_session({"id": "s2", "user": "luis", "success": False, "score": 3}),
            _make_session({"id": "s3", "user": "abraham", "success": True, "score": 9}),
        ])
        metrics = learner.get_metrics()
        assert metrics["by_user"]["luis"]["count"] == 2
        assert metrics["by_user"]["luis"]["success_rate"] == 0.5
        assert metrics["by_user"]["abraham"]["count"] == 1
        assert metrics["by_user"]["abraham"]["success_rate"] == 1.0


class TestTopSkills:
    def test_skills_sorted_by_effectiveness(self, learner):
        _seed(learner.store, [
            _make_session({"id": "s1", "skill_used": "hermes", "success": True, "score": 9}),
            _make_session({"id": "s2", "skill_used": "openclaw", "success": False, "score": 2}),
            _make_session({"id": "s3", "skill_used": "hermes", "success": True, "score": 8}),
        ])
        metrics = learner.get_metrics()
        assert metrics["top_skills"][0]["name"] == "hermes"


class TestGenerateReport:
    def test_text_format(self, learner):
        _seed(learner.store, [
            _make_session({"id": "s1", "success": True, "score": 8}),
        ])
        report = learner.generate_report(format="text")
        assert "LEARNER REPORT" in report
        assert "Success Rate" in report

    def test_json_format(self, learner):
        _seed(learner.store, [
            _make_session({"id": "s1", "success": True, "score": 8}),
        ])
        report = learner.generate_report(format="json")
        data = json.loads(report)
        assert data["total_sessions"] == 1

    def test_markdown_format(self, learner):
        _seed(learner.store, [
            _make_session({"id": "s1", "success": True, "score": 8}),
        ])
        report = learner.generate_report(format="markdown")
        assert "# Learner Report" in report
        assert "By Command Type" in report

    def test_invalid_format_falls_back(self, learner):
        report = learner.generate_report(format="invalid")
        assert isinstance(report, str)


class TestGetImprovementTip:
    def test_returns_tip_when_patterns_exist(self, learner):
        _seed(learner.store, [
            _make_session({"id": "s1", "error": "timeout", "success": False, "score": 2}),
            _make_session({"id": "s2", "error": "timeout", "success": False, "score": 2}),
        ])
        tip = learner.get_improvement_tip()
        assert tip
        assert "timeout" in tip

    def test_empty_when_no_sessions(self, learner):
        tip = learner.get_improvement_tip()
        assert "No sessions scored" in tip


class TestSessionStore:
    def test_save_and_get_all(self, tmp_path):
        store = SessionStore(sessions_file=str(tmp_path / "sessions.jsonl"))
        store.save_session({"id": "s1", "success": True})
        store.save_session({"id": "s2", "success": False})
        all_s = store.get_all()
        assert len(all_s) == 2

    def test_get_unscored(self, tmp_path):
        store = SessionStore(sessions_file=str(tmp_path / "sessions.jsonl"))
        store.save_session({"id": "s1", "success": True})
        store.save_session({"id": "s2", "success": True, "score": 8})
        unscored = store.get_unscored()
        assert len(unscored) == 1
        assert unscored[0]["id"] == "s1"

    def test_mark_scored(self, tmp_path):
        store = SessionStore(sessions_file=str(tmp_path / "sessions.jsonl"))
        store.save_session({"id": "s1"})
        result = store.mark_scored("s1", 7)
        assert result is True
        sessions = store.get_all()
        assert sessions[0]["score"] == 7
        assert "scored_at" in sessions[0]
