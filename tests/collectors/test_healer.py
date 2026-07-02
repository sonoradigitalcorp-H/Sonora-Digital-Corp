"""Mock tests for healer.py — docker restart + events + Telegram."""
from unittest.mock import patch, MagicMock, call
import json
import pytest
import tempfile
from pathlib import Path

from scripts.healer import (
    docker_ps, docker_restart, emit_event, read_events,
    check_recent_healing, send_telegram,
)


@pytest.fixture
def mock_events_file(tmp_path):
    """Create a temporary events.jsonl for testing."""
    events_file = tmp_path / "events.jsonl"
    events = [
        {"type": "container_down", "container": "sdc-test", "timestamp": "2026-07-01T18:00:00Z"},
        {"type": "container_down", "container": "sdc-other", "timestamp": "2026-07-01T18:00:05Z"},
    ]
    with open(events_file, "w") as f:
        for e in events:
            f.write(json.dumps(e) + "\n")
    return events_file


# ── docker_ps ──

@patch("scripts.healer.subprocess.run")
def test_docker_ps_healthy(mock_run):
    mock_run.return_value = MagicMock(stdout="Up 2 hours (healthy)", returncode=0)
    healthy, status = docker_ps("sdc-neo4j")
    assert healthy is True
    assert "healthy" in status


@patch("scripts.healer.subprocess.run")
def test_docker_ps_not_found(mock_run):
    mock_run.return_value = MagicMock(stdout="", returncode=0)
    healthy, status = docker_ps("sdc-nonexistent")
    assert healthy is False
    assert status == "not_found"


@patch("scripts.healer.subprocess.run")
def test_docker_ps_timeout(mock_run):
    mock_run.side_effect = __import__("subprocess").TimeoutExpired(cmd="docker", timeout=10)
    healthy, status = docker_ps("sdc-slow")
    assert healthy is False
    assert status == "timeout"


@patch("scripts.healer.subprocess.run")
def test_docker_ps_docker_not_found(mock_run):
    mock_run.side_effect = FileNotFoundError()
    healthy, status = docker_ps("sdc-any")
    assert healthy is False
    assert status == "docker_not_found"


# ── docker_restart ──

@patch("scripts.healer.subprocess.run")
def test_docker_restart_success(mock_run):
    mock_run.return_value = MagicMock(returncode=0)
    assert docker_restart("sdc-neo4j") is True
    mock_run.assert_called_once()
    assert "restart" in str(mock_run.call_args)


@patch("scripts.healer.subprocess.run")
def test_docker_restart_failure(mock_run):
    mock_run.return_value = MagicMock(returncode=1)
    assert docker_restart("sdc-neo4j") is False


# ── emit_event / read_events ──

def test_emit_event_creates_file(tmp_path):
    with patch("scripts.healer.EVENTS_FILE", tmp_path / "events.jsonl"):
        with patch("scripts.healer.MEMORY_EVENTS", tmp_path / "memory.jsonl"):
            emit_event({"type": "healing_success", "container": "sdc-test", "attempt": 1})
            assert (tmp_path / "events.jsonl").exists()
            content = (tmp_path / "events.jsonl").read_text()
            assert "healing_success" in content


def test_read_events_returns_recent(mock_events_file):
    with patch("scripts.healer.EVENTS_FILE", mock_events_file):
        events = read_events(10)
        assert len(events) == 2
        assert events[0]["type"] == "container_down"


def test_read_events_handles_corrupt(tmp_path):
    events_file = tmp_path / "events.jsonl"
    events_file.write_text('{"valid": true}\ncorrupt_line\n{"also_valid": true}\n')
    with patch("scripts.healer.EVENTS_FILE", events_file):
        events = read_events(10)
        assert len(events) == 2  # skips corrupt line


# ── check_recent_healing ──

def test_check_recent_healing_found(mock_events_file):
    # Add a healing success event
    with open(mock_events_file, "a") as f:
        from datetime import datetime, timezone
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        f.write(json.dumps({"type": "healing_success", "container": "sdc-test", "timestamp": ts}) + "\n")

    with patch("scripts.healer.EVENTS_FILE", mock_events_file):
        # Override HEALER_COOLDOWN to be long enough
        with patch("scripts.healer.HEALER_COOLDOWN", 999999):
            assert check_recent_healing("sdc-test") is True


def test_check_recent_healing_not_found(mock_events_file):
    with patch("scripts.healer.EVENTS_FILE", mock_events_file):
        assert check_recent_healing("sdc-unknown") is False


# ── send_telegram ──

@patch("httpx.post")
def test_send_telegram_success(mock_post):
    mock_post.return_value = MagicMock(status_code=200)
    with patch.dict("os.environ", {"ABE_FENIX_BOT_TOKEN": "test:token", "ABE_TELEGRAM_CHAT": "12345"}):
        send_telegram("sdc-test", 3)
        mock_post.assert_called_once()


@patch("httpx.post")
def test_send_telegram_no_token(mock_post):
    with patch.dict("os.environ", {}, clear=True):
        with patch("scripts.healer.Path.exists", return_value=False):
            send_telegram("sdc-test", 3)
            mock_post.assert_not_called()
