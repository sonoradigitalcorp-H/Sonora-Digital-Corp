"""Tests for Agent Harnesses."""

import pytest
from src.harnesses import AgentHarness, MockAgent
from src.harnesses.openhands import OpenHandsHarness
from src.harnesses.opencode import OpenCodeHarness
from src.harnesses.hermes import HermesHarness
from src.harnesses.aider import AiderHarness


class TestMockAgent:
    """Tests del MockAgent."""

    def test_mock_agent_execute(self):
        """Test ejecutar mock agent."""
        mock = MockAgent("test")
        task = type('Task', (), {'id': 't1', 'action': 'test', 'inputs': {}})()
        result = mock.execute_sync(task)
        assert result["status"] == "success"
        assert result["mock"] is True

    def test_mock_agent_custom_response(self):
        """Test respuesta personalizada."""
        mock = MockAgent("test")
        mock.set_response("custom", {"custom": True})
        task = type('Task', (), {'id': 't1', 'action': 'custom', 'inputs': {}})()
        result = mock.execute_sync(task)
        assert result["custom"] is True

    def test_mock_agent_call_count(self):
        """Test contador de llamadas."""
        mock = MockAgent("test")
        task1 = type('Task', (), {'id': 't1', 'action': 'test', 'inputs': {}})()
        task2 = type('Task', (), {'id': 't2', 'action': 'test', 'inputs': {}})()
        mock.execute_sync(task1)
        mock.execute_sync(task2)
        assert mock.call_count["test"] == 2


class TestAgentHarness:
    """Tests del AgentHarness base."""

    def test_harness_with_mock(self):
        """Test harness con mock agent."""
        mock = MockAgent("test")
        harness = AgentHarness(mock)

        result = harness.execute("test_action", {"key": "value"})
        assert result.passed is True

    def test_harness_with_expected(self):
        """Test harness con resultado esperado."""
        mock = MockAgent("test")
        harness = AgentHarness(mock)

        # Mock retorna dict con status=success
        result = harness.execute(
            "test_action",
            {"key": "value"},
            expected={"status": "success"},
        )
        assert result.passed is True

    def test_harness_stats(self):
        """Test estadísticas del harness."""
        mock = MockAgent("test")
        harness = AgentHarness(mock)

        harness.execute("action1", {})
        harness.execute("action2", {})

        stats = harness.get_stats()
        assert stats["total_tests"] == 2
        assert stats["passed"] == 2

    def test_harness_assert_all_passed(self):
        """Test assert_all_passed."""
        mock = MockAgent("test")
        harness = AgentHarness(mock)

        harness.execute("action1", {})
        harness.assert_all_passed()  # No debe lanzar excepción


class TestOpenHandsHarness:
    """Tests del OpenHandsHarness."""

    def test_create_function(self):
        """Test crear función."""
        harness = OpenHandsHarness()
        result = harness.test_create_function("mi_funcion")
        assert result.passed is True

    def test_fix_bug(self):
        """Test corregir bug."""
        harness = OpenHandsHarness()
        result = harness.test_fix_bug("error en login")
        assert result.passed is True

    def test_run_tests(self):
        """Test ejecutar tests."""
        harness = OpenHandsHarness()
        result = harness.test_run_tests("test_main.py")
        assert result.passed is True


class TestOpenCodeHarness:
    """Tests del OpenCodeHarness."""

    def test_edit_code(self):
        """Test editar código."""
        harness = OpenCodeHarness()
        result = harness.test_edit_code("main.py")
        assert result.passed is True

    def test_refactor(self):
        """Test refactorizar."""
        harness = OpenCodeHarness()
        result = harness.test_refactor("utils.py")
        assert result.passed is True


class TestHermesHarness:
    """Tests del HermesHarness."""

    def test_mcp_call(self):
        """Test llamada MCP."""
        harness = HermesHarness()
        result = harness.test_mcp_call("filesystem")
        assert result.passed is True

    def test_workflow(self):
        """Test workflow."""
        harness = HermesHarness()
        result = harness.test_workflow("deploy_pipeline")
        assert result.passed is True


class TestAiderHarness:
    """Tests del AiderHarness."""

    def test_commit(self):
        """Test commit."""
        harness = AiderHarness()
        result = harness.test_commit("feat: add new feature")
        assert result.passed is True

    def test_branch(self):
        """Test branch."""
        harness = AiderHarness()
        result = harness.test_branch("feature/new-stuff")
        assert result.passed is True

    def test_changelog(self):
        """Test changelog."""
        harness = AiderHarness()
        result = harness.test_changelog()
        assert result.passed is True
