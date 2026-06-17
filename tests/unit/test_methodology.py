"""Tests for the unified methodology stack (SDD + GSD + Self-Improve)."""

import pytest
from webui.routes.commands_router import METHODOLOGY_COMMANDS, handle_methodology_command


class TestMethodologyCommands:
    def test_all_commands_defined(self):
        assert "/gsd" in METHODOLOGY_COMMANDS
        assert "/wrap-up" in METHODOLOGY_COMMANDS
        assert "/reflect" in METHODOLOGY_COMMANDS
        assert "/learn" in METHODOLOGY_COMMANDS

    def test_gsd_structure(self):
        cmd = METHODOLOGY_COMMANDS["/gsd"]
        assert cmd["type"] == "gsd"
        assert "title" in cmd
        assert "description" in cmd
        assert "steps" in cmd
        assert len(cmd["steps"]) >= 4

    def test_wrap_up_structure(self):
        cmd = METHODOLOGY_COMMANDS["/wrap-up"]
        assert cmd["type"] == "wrap-up"
        assert "Ship State" in cmd["steps"][0]
        assert "Memory" in cmd["steps"][1]
        assert "Self-Improve" in cmd["steps"][2]

    def test_reflect_structure(self):
        cmd = METHODOLOGY_COMMANDS["/reflect"]
        assert cmd["type"] == "reflect"
        assert "Scan" in cmd["steps"][0]
        assert "Apply" in cmd["steps"][3]

    def test_learn_structure(self):
        cmd = METHODOLOGY_COMMANDS["/learn"]
        assert cmd["type"] == "learn"
        assert "Analysis" in cmd["steps"][0]
        assert "Confidence" in cmd["steps"][1]

    def test_handle_gsd(self):
        result = handle_methodology_command("/gsd")
        assert result["type"] == "gsd"
        assert "GSD" in result["content"]

    def test_handle_wrap_up(self):
        result = handle_methodology_command("/wrap-up")
        assert result["type"] == "wrap-up"
        assert "Close-Loop" in result["content"]

    def test_handle_reflect(self):
        result = handle_methodology_command("/reflect")
        assert result["type"] == "reflect"
        assert "Reflect" in result["content"]

    def test_handle_learn(self):
        result = handle_methodology_command("/learn")
        assert result["type"] == "learn"
        assert "Learning-Loop" in result["content"]

    def test_handle_unknown(self):
        result = handle_methodology_command("/nonexistent")
        assert result["type"] == "error"

    def test_help_includes_methodology(self):
        from webui.fastapp import app
        from fastapi.testclient import TestClient
        client = TestClient(app)
        r = client.post("/api/commands", json={"command": "/help", "session_id": "default"})
        assert r.status_code == 200
        data = r.json()
        assert "/gsd" in data["content"]
        assert "/wrap-up" in data["content"]
