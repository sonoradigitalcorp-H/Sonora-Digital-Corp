import pytest
import sys
from pathlib import Path
from unittest.mock import patch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))


@patch("metrics.enterprise_score.run_tests")
@patch("metrics.enterprise_score.check_services_health")
def test_enterprise_score_cli(mock_health, mock_tests):
    mock_tests.return_value = {"passed": 100, "failed": 0, "total": 100, "pass_rate": 100}
    mock_health.return_value = {"alive": 8, "total": 8, "availability_pct": 100}
    from metrics.enterprise_score import compute_enterprise_score
    result = compute_enterprise_score()
    assert 0 <= result["enterprise_score"] <= 100
    assert len(result["metrics"]) == 10


@patch("metrics.enterprise_score.run_tests")
@patch("metrics.enterprise_score.check_services_health")
def test_enterprise_score_threshold(mock_health, mock_tests):
    mock_tests.return_value = {"passed": 100, "failed": 0, "total": 100, "pass_rate": 100}
    mock_health.return_value = {"alive": 8, "total": 8, "availability_pct": 100}
    from metrics.enterprise_score import compute_enterprise_score
    result = compute_enterprise_score()
    assert result["threshold_met"] is True


def test_founder_dependency_cli():
    from metrics.founder_dependency import compute_index
    result = compute_index()
    assert 0 <= result["autonomy_score"] <= 100
    assert "founder_dependency_index" in result


def test_weekly_report_structure():
    sys.path.insert(0, str(REPO / "scripts"))
    import importlib
    spec = importlib.util.spec_from_file_location("wer", REPO / "scripts" / "weekly-executive-report.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    result = mod.generate_all_reports()
    assert result["report_count"] == 11
    assert result["report_id"].startswith("WER-")


def test_ingest_session_script():
    sys.path.insert(0, str(REPO / "scripts"))
    import importlib
    spec = importlib.util.spec_from_file_location("ingest", REPO / "scripts" / "ingest-session-knowledge.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    result = mod.ingest_session("20260710-full-inventory")
    assert result["status"] in ("ingested", "not_found")
