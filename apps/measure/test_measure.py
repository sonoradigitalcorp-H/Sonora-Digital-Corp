import json
import pytest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent


def test_scoreboard_import():
    from apps.measure.scoreboard import compute_scoreboard
    assert callable(compute_scoreboard)


def test_drift_scanner_import():
    from apps.measure.guardian.drift_scanner import scan
    assert callable(scan)


def test_health_checker_import():
    from apps.measure.guardian.health_checker import check_all
    assert callable(check_all)


def test_compliance_auditor_import():
    from apps.measure.guardian.compliance_auditor import run_all as compliance_run
    assert callable(compliance_run)


def test_telegram_alerter_import():
    from apps.measure.guardian.telegram_alerter import send_alert
    assert callable(send_alert)


def test_status_api_import():
    from apps.measure.guardian.status_api import StatusHandler
    assert StatusHandler is not None


def test_violations_file_structure():
    vio_path = REPO / "state" / "quality" / "violations.jsonl"
    if vio_path.exists():
        with open(vio_path) as f:
            for line in f:
                line = line.strip()
                if line:
                    entry = json.loads(line)
                    assert "timestamp" in entry


def test_drift_scanner_runs():
    from apps.measure.guardian.drift_scanner import scan
    result = scan()
    assert isinstance(result, (list, dict))


def test_health_checker_runs():
    from apps.measure.guardian.health_checker import check_all
    result = check_all()
    assert isinstance(result, (list, dict))


def test_compliance_auditor_runs():
    from apps.measure.guardian.compliance_auditor import run_all
    result = run_all()
    assert isinstance(result, (list, dict))


def test_enterprise_score_threshold():
    score_path = REPO / "metrics" / "enterprise-score.md"
    if score_path.exists():
        content = score_path.read_text()
        scores = []
        for line in content.splitlines():
            for word in line.split():
                if "/10" in word or "/100" in word:
                    try:
                        parts = word.split("/")
                        scores.append(int(parts[0]))
                    except ValueError:
                        pass
        assert len(scores) > 0, "No numeric scores found"
        overall = scores[-1] if scores else 0
        assert overall > 0, f"Enterprise Score {overall} should be positive"
