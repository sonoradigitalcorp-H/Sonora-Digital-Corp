"""Tests for agent infrastructure — Redis Stream + Ollama + Docker."""
from unittest.mock import patch, MagicMock
import json
import pytest

pytestmark = pytest.mark.filterwarnings("ignore")


# ── Monitor Agent ──

@patch("apps.agents.monitor_agent.subprocess.run")
def test_monitor_detect_all_healthy(mock_run):
    from apps.agents.monitor_agent import detect_dead_containers
    mock_run.return_value = MagicMock(stdout="sdc-neo4j|Up 8 minutes (healthy)\nsdc-qdrant|Up 24 hours (healthy)\n")
    result = detect_dead_containers()
    assert result == []


@patch("apps.agents.monitor_agent.subprocess.run")
def test_monitor_detect_dead_container(mock_run):
    from apps.agents.monitor_agent import detect_dead_containers
    mock_run.return_value = MagicMock(stdout="sdc-neo4j|Up 8 minutes (healthy)\nsdc-broken|Up 2 hours\n")
    # sdc-broken is up but no healthcheck — should be skipped
    result = detect_dead_containers()
    assert result == []


@patch("apps.agents.monitor_agent.subprocess.run")
def test_monitor_detect_truly_down(mock_run):
    from apps.agents.monitor_agent import detect_dead_containers
    mock_run.return_value = MagicMock(stdout="sdc-neo4j|Up 8 minutes (healthy)\nsdc-dead|Exited (137) 5 minutes ago\n")
    result = detect_dead_containers()
    assert len(result) == 1
    assert result[0]["container"] == "sdc-dead"


@patch("apps.agents.monitor_agent.subprocess.run")
def test_monitor_docker_timeout(mock_run):
    from apps.agents.monitor_agent import detect_dead_containers
    mock_run.side_effect = __import__("subprocess").TimeoutExpired(cmd="docker", timeout=15)
    result = detect_dead_containers()
    assert result == []


# ── Healer Agent ──

@patch("apps.agents.healer_agent.neo4j_query")
def test_healer_get_dependencies(mock_neo4j):
    from apps.agents.healer_agent import get_dependencies
    mock_neo4j.return_value = [{"name": "ABE Service"}, {"name": "JARVIS Web UI"}]
    result = get_dependencies("sdc-neo4j")
    assert len(result) == 2
    assert "ABE Service" in result


@patch("apps.agents.healer_agent.neo4j_query")
def test_healer_no_dependencies(mock_neo4j):
    from apps.agents.healer_agent import get_dependencies
    mock_neo4j.return_value = []
    result = get_dependencies("sdc-unknown")
    assert result == []


# ── Notifier Agent ──

@patch("httpx.post")
def test_notifier_send_telegram(mock_post):
    from apps.agents.notifier_agent import send_telegram
    import os
    with patch.dict(os.environ, {"ABE_FENIX_BOT_TOKEN": "test:token", "ABE_TELEGRAM_CHAT": "12345"}):
        import apps.agents.notifier_agent as na
        na.load_credentials()
        mock_post.return_value = MagicMock(status_code=200)
        na.send_telegram("sdc-test", "container_critical", "test details")
        assert mock_post.called
