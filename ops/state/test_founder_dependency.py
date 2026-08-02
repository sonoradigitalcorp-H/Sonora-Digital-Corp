import pytest
from metrics.founder_dependency import (
    count_manual_interventions_in_session,
    count_slash_commands_in_agents_md,
    count_scripts,
    compute_index,
)
from pathlib import Path


def test_count_slash_commands():
    result = count_slash_commands_in_agents_md()
    assert "slash_commands" in result
    assert result["slash_commands"] > 0


def test_count_scripts():
    result = count_scripts()
    assert result["total"] > 0


def test_compute_index_structure():
    result = compute_index()
    assert "founder_dependency_index" in result
    assert "autonomy_score" in result
    assert "details" in result
    assert "components" in result
    assert 0 <= result["autonomy_score"] <= 100


def test_compute_index_details():
    result = compute_index()
    details = result["details"]
    assert "sessions_analyzed" in details
    assert "total_auto_events" in details
    assert "total_manual_events" in details
    assert "autonomy_rate_pct" in details


def test_compute_index_components():
    result = compute_index()
    components = result["components"]
    assert "autonomy_rate_weighted" in components
    assert "script_automation" in components
    assert "commands_coverage" in components


@pytest.fixture
def temp_session(tmp_path):
    session = tmp_path / "SPEC-2026-test"
    session.mkdir()
    (session / "LECCION.md").write_text("## Qué falló\n- **Founder manually fixed docker**\n")
    (session / "events.jsonl").write_text('{"type": "manual", "founder": true}\n{"type": "auto"}\n')
    return session


def test_count_manual_interventions(temp_session):
    stats = count_manual_interventions_in_session(temp_session)
    assert stats["manual"] >= 1
    assert stats["total"] >= 1
