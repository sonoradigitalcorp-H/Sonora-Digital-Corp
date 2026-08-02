import pytest
from unittest.mock import patch
from metrics.enterprise_score import (
    get_test_coverage_score,
    get_availability_score,
    get_doc_coverage,
    get_security_score,
    compute_enterprise_score,
)


@pytest.fixture(autouse=True)
def mock_slow_calls():
    with patch("metrics.enterprise_score.run_tests") as mock_tests, \
         patch("metrics.enterprise_score.check_services_health") as mock_health:
        mock_tests.return_value = {"passed": 100, "failed": 0, "total": 100, "pass_rate": 100}
        mock_health.return_value = {"alive": 8, "total": 8, "availability_pct": 100}
        yield


def test_get_test_coverage_score():
    assert get_test_coverage_score({"pass_rate": 100}) == 10
    assert get_test_coverage_score({"pass_rate": 97}) == 9
    assert get_test_coverage_score({"pass_rate": 92}) == 8
    assert get_test_coverage_score({"pass_rate": 50}) == 5


def test_get_availability_score():
    assert get_availability_score({"availability_pct": 100}) == 10
    assert get_availability_score({"availability_pct": 85}) == 8
    assert get_availability_score({"availability_pct": 0}) == 0


def test_get_doc_coverage():
    result = get_doc_coverage()
    assert "doc_files" in result
    assert result["doc_files"] > 0


def test_get_security_score():
    score = get_security_score()
    assert 1 <= score <= 10


def test_compute_enterprise_score_structure():
    result = compute_enterprise_score()
    assert "enterprise_score" in result
    assert "threshold_met" in result
    assert "metrics" in result
    assert "sources" in result
    assert 0 <= result["enterprise_score"] <= 100


def test_compute_enterprise_score_metrics():
    result = compute_enterprise_score()
    metrics = result["metrics"]
    assert len(metrics) == 10
    for name, score in metrics.items():
        assert 0 <= score <= 10, f"{name}: {score} not in 0-10"
