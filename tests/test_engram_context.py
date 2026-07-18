"""Tests para Context Recovery — query, filter, periods, summaries [FR-08]"""
import sys
from pathlib import Path
from unittest.mock import MagicMock

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from scripts.engram_autocapture import ContextRecovery, EngramClientAdapter


class TestContextRecovery:
    def make_mock_client(self, observations=None):
        mock = MagicMock(spec=EngramClientAdapter)
        mock.available = True
        mock.search.return_value = observations or []
        return mock

    def test_returns_expected_structure(self):
        mock = self.make_mock_client()
        cr = ContextRecovery(client=mock)
        result = cr.recover("sonora-digital-corp", days=7)
        assert "decisions" in result
        assert "bugs_fixed" in result
        assert "configs" in result
        assert "git_activity" in result
        assert "env_changes" in result
        assert "processes" in result
        assert "llm_summary" in result

    def test_empty_project_returns_empty_fields(self):
        mock = self.make_mock_client()
        cr = ContextRecovery(client=mock)
        result = cr.recover("proyecto-nuevo", days=7)
        assert result["decisions"] == []
        assert result["bugs_fixed"] == []
        assert result["configs"] == []
        assert result["env_changes"] == []

    def test_filters_by_type(self):
        obs = [
            {"type": "decision", "title": "d1"},
            {"type": "bugfix", "title": "b1"},
            {"type": "config", "title": "c1"},
        ]
        mock = self.make_mock_client(obs)
        cr = ContextRecovery(client=mock)
        result = cr.recover("sonora-digital-corp", days=7, types=["decision", "bugfix"])
        assert len(result["decisions"]) == 1
        assert len(result["bugs_fixed"]) == 1

    def test_respects_days_param(self):
        mock = self.make_mock_client()
        cr = ContextRecovery(client=mock)
        r7 = cr.recover("sonora-digital-corp", days=7)
        r30 = cr.recover("sonora-digital-corp", days=30)
        assert isinstance(r7, dict)
        assert isinstance(r30, dict)

    def test_llm_summary_empty_project(self):
        mock = self.make_mock_client([])
        cr = ContextRecovery(client=mock)
        result = cr.recover("proyecto-nuevo", days=7)
        assert result["llm_summary"] == "No hay actividad reciente en este proyecto."

    def test_llm_summary_with_data(self):
        obs = [
            {"type": "decision", "title": "d1"},
            {"type": "bugfix", "title": "b1"},
        ]
        mock = self.make_mock_client(obs)
        cr = ContextRecovery(client=mock)
        result = cr.recover("proyecto", days=7)
        assert "Actividad reciente" in result["llm_summary"]
