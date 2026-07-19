"""Tests for evolution loop: PatternDetector, ProposalGenerator, AutoEvolve."""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch, PropertyMock

import pytest

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO))

from evolution.pattern_detector import PatternDetector, _read_json, _write_json
from evolution.proposal_generator import ProposalGenerator
from evolution.auto_evolve import AutoEvolve


# ─── Helpers ───────────────────────────────────────────────────────

def _make_session(overrides=None):
    base = {
        "id": "ses-test",
        "session_id": "ses-test",
        "command_type": "chat",
        "skill_used": "hermes",
        "user": "luis",
        "success": True,
        "duration": 10.0,
        "error": None,
        "user_rephrase": False,
        "outcome_completeness": 3,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "command": "run deploy",
        "what": "deploy the app",
        "score": 7,
    }
    if overrides:
        base.update(overrides)
    return base


def _make_session_v2(overrides=None):
    """Session format from session_store.py (YAML-based)."""
    base = {
        "session_id": "ses-v2-test",
        "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
        "user": "system",
        "type": "evento",
        "command": "",
        "success": True,
        "duration_ms": 1000,
        "tokens_used": 0,
        "outcome": "",
        "improvement": "",
        "client_impact": False,
        "skills_used": ["hermes"],
        "files_changed": [],
        "score": 0,
    }
    if overrides:
        base.update(overrides)
    return base


def _empty_learner_metrics():
    return {
        "_sessions": [],
        "_skills": [],
        "total_sessions": 0,
        "scored": 0,
        "unscored": 0,
        "overall_success_rate": 0.0,
        "by_type": {},
        "by_skill": {},
        "common_errors": [],
        "improvement_trend": [],
        "top_skills": [],
        "by_user": {},
    }


# ═══════════════════════════════════════════════════════════════════
# PATTERN DETECTOR TESTS
# ═══════════════════════════════════════════════════════════════════

class TestPatternDetectorFindFrequentErrors:
    def test_returns_empty_when_no_sessions(self):
        pd = PatternDetector(patterns_file=Path("/tmp/__test_patterns_empty.json"))
        assert pd.find_frequent_errors([]) == []

    def test_detects_frequent_error(self):
        pd = PatternDetector(patterns_file=Path("/tmp/__test_patterns_freq.json"))
        sessions = [
            _make_session({"id": "s1", "error": "timeout", "skill_used": "deploy"}),
            _make_session({"id": "s2", "error": "timeout", "skill_used": "deploy"}),
            _make_session({"id": "s3", "error": "timeout", "skill_used": "deploy"}),
            _make_session({"id": "s4", "error": None, "skill_used": "deploy"}),
        ]
        patterns = pd.find_frequent_errors(sessions)
        assert len(patterns) >= 1
        assert patterns[0]["type"] == "FREQUENT_ERROR"
        assert patterns[0]["evidence"]["count"] == 3

    def test_skips_low_frequency_errors(self):
        pd = PatternDetector(patterns_file=Path("/tmp/__test_patterns_low.json"))
        sessions = [_make_session({"id": "s1", "error": "rare_err"})]
        sessions += [_make_session({"id": f"s{i}", "error": None}) for i in range(20)]
        patterns = pd.find_frequent_errors(sessions)
        assert len(patterns) == 0

    def test_pattern_has_required_fields(self):
        pd = PatternDetector(patterns_file=Path("/tmp/__test_patterns_fields.json"))
        sessions = [
            _make_session({"id": "s1", "error": "auth_fail", "skill_used": "hermes"}),
            _make_session({"id": "s2", "error": "auth_fail", "skill_used": "hermes"}),
        ]
        patterns = pd.find_frequent_errors(sessions)
        p = patterns[0]
        assert "pattern_id" in p
        assert "type" in p
        assert "confidence" in p
        assert "title" in p
        assert "description" in p
        assert "evidence" in p
        assert "suggestion" in p
        assert "tags" in p


class TestPatternDetectorFindSkillGaps:
    def test_detects_missing_skills(self):
        pd = PatternDetector(patterns_file=Path("/tmp/__test_gaps.json"))
        sessions = [
            _make_session({"id": "s1", "skill_used": "nonexistent-skill"}),
            _make_session({"id": "s2", "skill_used": "nonexistent-skill"}),
            _make_session({"id": "s3", "skill_used": "nonexistent-skill"}),
        ]
        patterns = pd.find_skill_gaps(sessions, ["hermes", "openclaw"])
        assert len(patterns) == 1
        assert patterns[0]["type"] == "SKILL_GAP"
        assert "nonexistent-skill" in patterns[0]["title"]

    def test_ignores_known_skills(self):
        pd = PatternDetector(patterns_file=Path("/tmp/__test_gaps_known.json"))
        sessions = [
            _make_session({"id": "s1", "skill_used": "hermes"}),
            _make_session({"id": "s2", "skill_used": "openclaw"}),
        ]
        patterns = pd.find_skill_gaps(sessions, ["hermes", "openclaw"])
        assert len(patterns) == 0

    def test_requires_minimum_count(self):
        pd = PatternDetector(patterns_file=Path("/tmp/__test_gaps_min.json"))
        sessions = [_make_session({"id": "s1", "skill_used": "rare-missing"})]
        patterns = pd.find_skill_gaps(sessions, ["hermes"])
        assert len(patterns) == 0


class TestPatternDetectorFindRegressions:
    def test_detects_regression(self):
        pd = PatternDetector(patterns_file=Path("/tmp/__test_reg.json"))
        metrics_by_day = {
            "2026-07-10": {"success_rate": 0.9, "by_skill": {"hermes": {"success_rate": 0.9}}, "by_type": {}},
            "2026-07-11": {"success_rate": 0.9, "by_skill": {"hermes": {"success_rate": 0.9}}, "by_type": {}},
            "2026-07-12": {"success_rate": 0.5, "by_skill": {"hermes": {"success_rate": 0.5}}, "by_type": {}},
        }
        patterns = pd.find_regressions(metrics_by_day)
        assert len(patterns) >= 1
        assert patterns[0]["type"] == "REGRESSION"

    def test_returns_empty_with_insufficient_data(self):
        pd = PatternDetector(patterns_file=Path("/tmp/__test_reg_empty.json"))
        patterns = pd.find_regressions({"2026-07-10": {"success_rate": 0.8}})
        assert len(patterns) == 0


class TestPatternDetectorFindOpportunities:
    def test_detects_opportunity(self):
        pd = PatternDetector(patterns_file=Path("/tmp/__test_opp.json"))
        sessions = [
            _make_session({"id": "s1", "command": "can you create a dashboard"}),
            _make_session({"id": "s2", "command": "can you create a dashboard"}),
        ]
        patterns = pd.find_opportunities(sessions)
        assert len(patterns) >= 1
        assert patterns[0]["type"] == "OPPORTUNITY"

    def test_requires_minimum_requests(self):
        pd = PatternDetector(patterns_file=Path("/tmp/__test_opp_min.json"))
        sessions = [_make_session({"id": "s1", "command": "create a thing"})]
        patterns = pd.find_opportunities(sessions)
        assert len(patterns) == 0


class TestPatternDetectorFindTimePatterns:
    def test_detects_time_pattern(self):
        pd = PatternDetector(patterns_file=Path("/tmp/__test_time.json"))
        ts = "2026-07-19T10:00:00+00:00"
        sessions = [_make_session({"id": f"s{i}", "error": "timeout", "timestamp": ts}) for i in range(5)]
        ts_ok = "2026-07-20T10:00:00+00:00"
        sessions += [_make_session({"id": f"s{i+5}", "error": None, "timestamp": ts_ok}) for i in range(2)]
        patterns = pd.find_time_patterns(sessions)
        assert len(patterns) >= 1
        assert patterns[0]["type"] == "TIME_CORRELATION"


class TestPatternDetectorAnalyze:
    def test_analyze_returns_patterns(self):
        pd = PatternDetector(patterns_file=Path("/tmp/__test_analyze.json"))
        sessions = [
            _make_session({"id": "s1", "error": "timeout", "skill_used": "deploy"}),
            _make_session({"id": "s2", "error": "timeout", "skill_used": "deploy"}),
            _make_session({"id": "s3", "error": "timeout", "skill_used": "deploy"}),
            _make_session({"id": "s4", "skill_used": "nonexistent"}),
        ]
        metrics = _empty_learner_metrics()
        metrics["_sessions"] = sessions
        patterns = pd.analyze(metrics)
        assert len(patterns) >= 1

    def test_analyze_empty_metrics(self):
        pd = PatternDetector(patterns_file=Path("/tmp/__test_analyze_empty.json"))
        patterns = pd.analyze(_empty_learner_metrics())
        assert patterns == []

    def test_get_patterns_caching(self):
        pd = PatternDetector(patterns_file=Path("/tmp/__test_cache.json"))
        _write_json(pd.patterns_file, [{"pattern_id": "pat-001", "type": "FREQUENT_ERROR"}])
        pd._cached = None
        result = pd.get_patterns()
        assert len(result) == 1
        assert result[0]["pattern_id"] == "pat-001"

    def test_patterns_summary(self):
        pd = PatternDetector(patterns_file=Path("/tmp/__test_summary.json"))
        pd._cached = [{"pattern_id": "pat-001", "type": "FREQUENT_ERROR", "confidence": 0.85,
                       "title": "test pattern", "suggestion": "fix it"}]
        summary = pd.patterns_summary()
        assert "PATTERN DETECTOR SUMMARY" in summary
        assert "test pattern" in summary


# ═══════════════════════════════════════════════════════════════════
# PROPOSAL GENERATOR TESTS
# ═══════════════════════════════════════════════════════════════════

class TestProposalGeneratorGenerate:
    def test_generate_from_skill_gap(self, tmp_path):
        pg = ProposalGenerator(proposals_dir=tmp_path)
        pattern = {
            "pattern_id": "pat-gap-001",
            "type": "SKILL_GAP",
            "confidence": 0.7,
            "title": "Missing skill 'foo'",
            "evidence": {"missing_skill": "foo", "count": 3},
            "tags": ["skill-gap"],
        }
        proposals = pg.generate([pattern])
        assert len(proposals) == 1
        assert proposals[0]["type"] == "CREATE_SKILL"
        assert proposals[0]["pattern_id"] == "pat-gap-001"

    def test_generate_from_error(self, tmp_path):
        pg = ProposalGenerator(proposals_dir=tmp_path)
        pattern = {
            "pattern_id": "pat-freq-001",
            "type": "FREQUENT_ERROR",
            "confidence": 0.85,
            "title": "timeout error frequent",
            "evidence": {"count": 5, "total": 10, "top_skill": "deploy"},
            "tags": ["deploy"],
        }
        proposals = pg.generate([pattern])
        assert len(proposals) == 1
        assert proposals[0]["type"] == "FIX_SKILL"

    def test_generate_from_opportunity(self, tmp_path):
        pg = ProposalGenerator(proposals_dir=tmp_path)
        pattern = {
            "pattern_id": "pat-opp-001",
            "type": "OPPORTUNITY",
            "confidence": 0.6,
            "title": "3 users want dashboard",
            "evidence": {"count": 3, "request_excerpt": "create a dashboard"},
        }
        proposals = pg.generate([pattern])
        assert len(proposals) == 1
        assert proposals[0]["type"] == "NEW_PRODUCT"

    def test_generate_from_regression(self, tmp_path):
        pg = ProposalGenerator(proposals_dir=tmp_path)
        pattern = {
            "pattern_id": "pat-reg-001",
            "type": "REGRESSION",
            "confidence": 0.8,
            "title": "deploy skill regressed",
            "evidence": {"skill": "deploy", "drop": 0.3, "initial_rate": 0.9, "latest_rate": 0.6, "days_analyzed": 3},
        }
        proposals = pg.generate([pattern])
        assert len(proposals) == 1
        assert proposals[0]["type"] == "FIX_SKILL"

    def test_generate_ignores_unknown_pattern(self, tmp_path):
        pg = ProposalGenerator(proposals_dir=tmp_path)
        pattern = {"pattern_id": "pat-xxx", "type": "UNKNOWN_TYPE", "evidence": {}}
        proposals = pg.generate([pattern])
        assert len(proposals) == 0

    def test_generate_returns_multiple(self, tmp_path):
        pg = ProposalGenerator(proposals_dir=tmp_path)
        patterns = [
            {"pattern_id": "p1", "type": "SKILL_GAP", "evidence": {"missing_skill": "x", "count": 2}},
            {"pattern_id": "p2", "type": "FREQUENT_ERROR", "evidence": {"count": 3, "total": 5, "top_skill": "y"}},
            {"pattern_id": "p3", "type": "UNKNOWN_TYPE", "evidence": {}},
        ]
        proposals = pg.generate(patterns)
        assert len(proposals) == 2


class TestProposalGeneratorEvaluateRisk:
    def test_fix_skill_low_risk_for_few_errors(self, tmp_path):
        pg = ProposalGenerator(proposals_dir=tmp_path)
        prop = {
            "type": "FIX_SKILL",
            "evidence": {"count": 3, "top_skill": "deploy"},
        }
        assert pg.evaluate_risk(prop) == "low"

    def test_fix_skill_high_risk_for_many_errors(self, tmp_path):
        pg = ProposalGenerator(proposals_dir=tmp_path)
        prop = {
            "type": "FIX_SKILL",
            "evidence": {"count": 15, "top_skill": "deploy"},
        }
        assert pg.evaluate_risk(prop) == "high"

    def test_create_skill_medium_risk(self, tmp_path):
        pg = ProposalGenerator(proposals_dir=tmp_path)
        assert pg.evaluate_risk({"type": "CREATE_SKILL"}) == "medium"

    def test_infra_change_high_risk(self, tmp_path):
        pg = ProposalGenerator(proposals_dir=tmp_path)
        assert pg.evaluate_risk({"type": "INFRA_CHANGE"}) == "high"


class TestProposalGeneratorEstimateImpact:
    def test_fix_skill_impact_scales_with_count(self, tmp_path):
        pg = ProposalGenerator(proposals_dir=tmp_path)
        prop = {"type": "FIX_SKILL", "evidence": {"count": 6, "top_skill": "deploy"}}
        impact = pg.estimate_impact(prop)
        assert impact["score_impact"] >= 2

    def test_new_product_high_impact(self, tmp_path):
        pg = ProposalGenerator(proposals_dir=tmp_path)
        impact = pg.estimate_impact({"type": "NEW_PRODUCT"})
        assert impact["score_impact"] == 5

    def test_create_skill_medium_impact(self, tmp_path):
        pg = ProposalGenerator(proposals_dir=tmp_path)
        impact = pg.estimate_impact({"type": "CREATE_SKILL"})
        assert impact["score_impact"] == 3


class TestProposalGeneratorSaveAndList:
    def test_save_proposal_creates_file(self, tmp_path):
        pg = ProposalGenerator(proposals_dir=tmp_path)
        prop = {
            "pattern_id": "pat-001",
            "type": "FIX_SKILL",
            "title": "Fix deploy error",
            "description": "fix it",
            "action": "patch it",
            "files_to_change": ["skills/deploy/SKILL.md"],
            "evidence": {"count": 2},
            "tags": ["deploy"],
        }
        pid = pg.save_proposal(prop)
        assert pid.startswith("prop-")
        assert (tmp_path / f"{pid}.json").exists()

    def test_list_proposals_filters_by_status(self, tmp_path):
        pg = ProposalGenerator(proposals_dir=tmp_path)
        pg.save_proposal({"pattern_id": "p1", "type": "FIX_SKILL", "title": "a", "description": "d",
                          "action": "act", "files_to_change": [], "evidence": {}, "tags": []})
        pg.save_proposal({"pattern_id": "p2", "type": "CREATE_SKILL", "title": "b", "description": "d",
                          "action": "act", "files_to_change": [], "evidence": {}, "tags": []})
        pending = pg.list_proposals(status="pending")
        assert len(pending) == 2

    def test_save_proposal_generates_adr(self, tmp_path):
        pg = ProposalGenerator(proposals_dir=tmp_path)
        prop = {
            "pattern_id": "pat-001",
            "type": "FIX_SKILL",
            "title": "Fix deploy error",
            "description": "fix the deploy error",
            "action": "add validation",
            "files_to_change": ["skills/deploy/SKILL.md"],
            "evidence": {"count": 3},
            "tags": ["deploy"],
        }
        pg.save_proposal(prop)
        adr_dir = tmp_path / "adr"
        assert adr_dir.exists()
        adr_files = list(adr_dir.glob("ADR-*.md"))
        assert len(adr_files) >= 1


# ═══════════════════════════════════════════════════════════════════
# AUTO-EVOLVE TESTS
# ═══════════════════════════════════════════════════════════════════

class TestAutoEvolveRunOnce:
    @patch("evolution.auto_evolve.AutoEvolve._run_enterprise_score", return_value={"enterprise_score": 75, "threshold_met": True})
    def test_run_once_completes_cycle(self, mock_es):
        mock_learner = MagicMock()
        mock_learner.score_all_pending.return_value = 2
        mock_learner.get_metrics.return_value = {
            **_empty_learner_metrics(),
            "total_sessions": 2,
            "overall_success_rate": 0.5,
            "by_skill": {"hermes": {"success_rate": 0.5, "count": 2, "avg_score": 5}},
            "common_errors": [],
            "improvement_trend": [],
        }
        mock_learner.store.get_all.return_value = []

        mock_detector = MagicMock()
        mock_detector.analyze.return_value = [
            {"pattern_id": "pat-001", "type": "FREQUENT_ERROR", "confidence": 0.8,
             "title": "test", "description": "d", "evidence": {"count": 2, "total": 5, "top_skill": "x"},
             "suggestion": "s", "tags": ["x"], "first_seen": "2026-07-19", "last_seen": "2026-07-19",
             "risk": "low"},
        ]

        mock_generator = MagicMock()
        mock_generator.generate.return_value = []
        mock_generator.list_proposals.return_value = []

        evo = AutoEvolve(learner=mock_learner, pattern_detector=mock_detector, proposal_generator=mock_generator)
        report = evo.run_once()
        assert report["sessions_scored"] == 2
        assert report["patterns_found"] == 1
        assert "enterprise_score" in report

    @patch("evolution.auto_evolve.AutoEvolve._run_enterprise_score", return_value={"enterprise_score": 0, "threshold_met": False})
    def test_run_once_with_no_sessions(self, mock_es):
        mock_learner = MagicMock()
        mock_learner.score_all_pending.return_value = 0
        mock_learner.get_metrics.return_value = _empty_learner_metrics()
        mock_learner.store.get_all.return_value = []

        mock_detector = MagicMock()
        mock_detector.analyze.return_value = []

        mock_generator = MagicMock()
        mock_generator.generate.return_value = []
        mock_generator.list_proposals.return_value = []

        evo = AutoEvolve(learner=mock_learner, pattern_detector=mock_detector, proposal_generator=mock_generator)
        report = evo.run_once()
        assert report["sessions_scored"] == 0
        assert report["patterns_found"] == 0

    @patch("evolution.auto_evolve.AutoEvolve._run_enterprise_score", return_value={"enterprise_score": 80, "threshold_met": True})
    def test_run_once_with_patterns_and_proposals(self, mock_es):
        mock_learner = MagicMock()
        mock_learner.score_all_pending.return_value = 1
        mock_learner.get_metrics.return_value = {
            **_empty_learner_metrics(),
            "total_sessions": 1,
            "overall_success_rate": 1.0,
        }
        mock_learner.store.get_all.return_value = []

        mock_detector = MagicMock()
        mock_detector.analyze.return_value = [
            {"pattern_id": "pat-001", "type": "SKILL_GAP", "confidence": 0.7,
             "title": "missing skill", "description": "d", "evidence": {"missing_skill": "foo", "count": 2},
             "suggestion": "s", "tags": ["x"], "first_seen": "2026-07-19", "last_seen": "2026-07-19",
             "risk": "low"},
        ]

        mock_generator = MagicMock()
        mock_generator.generate.return_value = [
            {"proposal_id": "prop-001", "type": "CREATE_SKILL", "title": "Create foo",
             "risk": "low", "estimated_score_impact": 3, "status": "pending"},
        ]
        mock_generator.list_proposals.return_value = []

        evo = AutoEvolve(learner=mock_learner, pattern_detector=mock_detector, proposal_generator=mock_generator)
        report = evo.run_once()
        assert report["patterns_found"] == 1
        assert report["proposals_generated"] == 1

    @patch("evolution.auto_evolve.AutoEvolve._run_enterprise_score", return_value={})
    def test_auto_apply_low_risk_proposal(self, mock_es):
        mock_generator = MagicMock()
        evo = AutoEvolve(proposal_generator=mock_generator)
        proposal = {
            "proposal_id": "prop-001",
            "title": "Fix deploy",
            "risk": "low",
            "estimated_score_impact": 2,
        }
        result = evo.auto_apply(proposal)
        assert result["status"] == "applied"
        assert result["proposal_id"] == "prop-001"
        mock_generator.save_proposal.assert_called_once()

    @patch("evolution.auto_evolve.AutoEvolve._run_enterprise_score", return_value={})
    def test_auto_apply_skips_non_low_risk(self, mock_es):
        evo = AutoEvolve()
        for risk in ["medium", "high"]:
            result = evo.auto_apply({"proposal_id": "p1", "risk": risk, "title": "test"})
            assert result["status"] == "skipped"

    @patch("evolution.auto_evolve.AutoEvolve._run_enterprise_score", return_value={})
    def test_status_returns_summary(self, mock_es):
        mock_learner = MagicMock()
        mock_learner.get_metrics.return_value = {
            **{"total_sessions": 10, "overall_success_rate": 0.8},
        }
        mock_detector = MagicMock()
        mock_detector.get_patterns.return_value = [{"pattern_id": "pat-001"}]
        mock_generator = MagicMock()
        mock_generator.list_proposals.return_value = [{"proposal_id": "prop-001"}]

        evo = AutoEvolve(learner=mock_learner, pattern_detector=mock_detector, proposal_generator=mock_generator)
        s = evo.status()
        assert s["total_sessions"] == 10
        assert s["overall_success_rate"] == 0.8
        assert s["patterns_found"] == 1
        assert s["pending_proposals"] == 1

    def test_get_report_returns_string(self):
        evo = AutoEvolve()
        report = evo.get_report()
        assert isinstance(report, str)

    @patch("evolution.auto_evolve.AutoEvolve._run_enterprise_score", return_value={"enterprise_score": 75, "threshold_met": True})
    def test_run_daily_calls_notify(self, mock_es):
        mock_learner = MagicMock()
        mock_learner.score_all_pending.return_value = 0
        mock_learner.get_metrics.return_value = _empty_learner_metrics()
        mock_learner.store.get_all.return_value = []

        mock_detector = MagicMock()
        mock_detector.analyze.return_value = []

        mock_generator = MagicMock()
        mock_generator.generate.return_value = []
        mock_generator.list_proposals.return_value = []

        evo = AutoEvolve(learner=mock_learner, pattern_detector=mock_detector, proposal_generator=mock_generator)
        with patch("evolution.auto_evolve.logger") as mock_logger:
            report = evo.run_daily()
            assert mock_logger.info.called
