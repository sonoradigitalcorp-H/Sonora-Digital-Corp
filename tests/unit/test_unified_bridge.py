"""Tests for the Unified Bridge (JARVIS + Hermes + OpenClaw integration)."""

import pytest
from unittest.mock import patch, MagicMock
from src.core.unified_bridge import (
    HermesBridge, GbrainBridge, OpenClawBridge,
    UnifiedMemory, HumanInTheLoop, UnifiedSystem
)


class TestHermesBridge:
    @patch("src.core.unified_bridge.requests.get")
    def test_health_offline(self, mock_get):
        mock_get.side_effect = Exception("Connection refused")
        bridge = HermesBridge()
        result = bridge.health()
        assert result["status"] == "error"

    @patch("src.core.unified_bridge.requests.post")
    def test_send_telegram_offline(self, mock_post):
        mock_post.side_effect = Exception("Connection refused")
        bridge = HermesBridge()
        result = bridge.send_telegram("test", "hello")
        assert result["status"] == "error"

    @patch("src.core.unified_bridge.requests.post")
    def test_send_whatsapp_offline(self, mock_post):
        mock_post.side_effect = Exception("Connection refused")
        bridge = HermesBridge()
        result = bridge.send_whatsapp("test", "hello")
        assert result["status"] == "error"

    @patch("src.core.unified_bridge.requests.post")
    def test_trigger_n8n_offline(self, mock_post):
        mock_post.side_effect = Exception("Connection refused")
        bridge = HermesBridge()
        result = bridge.trigger_n8n("test-workflow")
        assert result["status"] == "error"

    @patch("src.core.unified_bridge.requests.get")
    def test_get_messages_offline(self, mock_get):
        mock_get.side_effect = Exception("Connection refused")
        bridge = HermesBridge()
        result = bridge.get_messages(10)
        assert isinstance(result, list)


class TestGbrainBridge:
    def test_search(self):
        import subprocess
        from unittest.mock import patch
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 1
            mock_run.return_value.stdout = ""
            mock_run.return_value.stderr = "Not available"
            bridge = GbrainBridge()
            result = bridge.search("test")
            assert "status" in result

    def test_think(self):
        import subprocess
        from unittest.mock import patch
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 1
            mock_run.return_value.stdout = ""
            mock_run.return_value.stderr = "Not available"
            bridge = GbrainBridge()
            result = bridge.think("test")
            assert "status" in result

    def test_capture(self):
        import subprocess
        from unittest.mock import patch
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 1
            mock_run.return_value.stdout = ""
            mock_run.return_value.stderr = "Not available"
            bridge = GbrainBridge()
            result = bridge.capture("test")
            assert "status" in result

    def test_status(self):
        bridge = GbrainBridge()
        result = bridge.status()
        assert "status" in result

    def test_health(self):
        bridge = GbrainBridge()
        result = bridge.health()
        assert result["status"] in ("ok", "offline", "error")


class TestOpenClawBridge:
    @patch("src.core.unified_bridge.requests.get")
    def test_health_offline(self, mock_get):
        mock_get.side_effect = Exception("Connection refused")
        bridge = OpenClawBridge()
        result = bridge.health()
        assert result["status"] == "error"

    @patch("src.core.unified_bridge.requests.get")
    def test_list_agents_offline(self, mock_get):
        mock_get.side_effect = Exception("Connection refused")
        bridge = OpenClawBridge()
        result = bridge.list_agents()
        assert result == []

    @patch("src.core.unified_bridge.requests.get")
    def test_list_models_offline(self, mock_get):
        mock_get.side_effect = Exception("Connection refused")
        bridge = OpenClawBridge()
        result = bridge.list_models()
        assert result == []

    @patch("src.core.unified_bridge.requests.post")
    def test_chat_offline(self, mock_post):
        mock_post.side_effect = Exception("Connection refused")
        bridge = OpenClawBridge()
        result = bridge.chat("agent-1", "hello")
        assert result["status"] == "error"


class TestUnifiedMemory:
    def setup_method(self):
        self.memory = UnifiedMemory()

    def test_store_recall(self):
        self.memory.store("test-key", {"data": "value"})
        result = self.memory.recall("test-key")
        assert result == {"data": "value"}

    def test_recall_missing(self):
        result = self.memory.recall("nonexistent")
        assert result is None

    def test_search_no_qdrant(self):
        results = self.memory.search("hello")
        assert results == []

    def test_status(self):
        self.memory.store("k", {"v": 1})
        result = self.memory.status()
        assert result["cache_entries"] >= 1
        assert result["neo4j"] is False
        assert result["qdrant"] is False

    def test_store_returns_bool(self):
        result = self.memory.store("key", "value")
        assert isinstance(result, bool)


class TestHumanInTheLoop:
    def setup_method(self):
        self.control = HumanInTheLoop()

    def test_request_creates_ticket(self):
        ticket = self.control.request("test-action", {"cmd": "rm -rf /"})
        assert ticket is not None
        assert ticket in self.control.pending

    def test_requires_approval_true(self):
        assert self.control.requires_approval("execute_command") is True

    def test_requires_approval_false(self):
        assert self.control.requires_approval("code_gen") is False

    def test_approve(self):
        ticket = self.control.request("test", {"a": 1})
        assert self.control.approve(ticket) is True
        assert self.control.pending[ticket]["status"] == "approved"

    def test_reject(self):
        ticket = self.control.request("test", {"a": 1})
        assert self.control.reject(ticket) is True
        assert self.control.pending[ticket]["status"] == "rejected"

    def test_approve_invalid(self):
        assert self.control.approve("nonexistent") is False

    def test_reject_invalid(self):
        assert self.control.reject("nonexistent") is False

    def test_pending_count(self):
        self.control.request("a", {})
        self.control.request("b", {})
        assert self.control.pending_count() == 2
        self.control.approve(list(self.control.pending.keys())[0])
        assert self.control.pending_count() == 1

    def test_list_pending(self):
        self.control.request("test", {"x": 1})
        pending = self.control.list_pending()
        assert len(pending) == 1
        assert pending[0]["action"] == "test"


class TestUnifiedSystem:
    def test_init(self):
        system = UnifiedSystem()
        result = system.init()
        assert "status" in result
        assert "hermes" in result
        assert "openclaw" in result

    def test_status(self):
        system = UnifiedSystem()
        result = system.status()
        assert "hermes" in result
        assert "openclaw" in result
