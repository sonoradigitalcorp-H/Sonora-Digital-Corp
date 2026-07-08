"""Tests for Agent Runtime (HAS-006)"""
import pytest
from agents import AgentRuntime, AgentContext, AgentResult
from agents.base import HermesAgent


class DummyAgent(HermesAgent):
    agent_id = "dummy"
    name = "Dummy"
    capabilities = ["test"]
    model = "ollama/test"
    status = "active"

    async def think(self, context: AgentContext) -> AgentResult:
        return AgentResult(status="success", output={"handled": True}, reasoning="Test OK")


class FailingAgent(HermesAgent):
    agent_id = "failing"
    name = "Failing"
    capabilities = ["fail"]
    status = "active"

    async def think(self, context: AgentContext) -> AgentResult:
        raise RuntimeError("Test failure")


@pytest.fixture
def runtime():
    r = AgentRuntime()
    r.register(DummyAgent())
    return r


def test_agent_runtime_loads_registry(runtime):
    agents = runtime.list_agents()
    assert len(agents) >= 11


def test_agent_runtime_register(runtime):
    assert runtime.get("dummy") is not None
    assert runtime.get("dummy").name == "Dummy"


def test_agent_runtime_get_missing(runtime):
    assert runtime.get("nonexistent") is None


def test_agent_runtime_find_by_capability(runtime):
    matches = runtime.find_by_capability("test")
    assert "dummy" in matches


def test_agent_runtime_state(runtime):
    state = runtime.get_state("dummy")
    assert state == "idle"


@pytest.mark.asyncio
async def test_agent_runtime_execute_success(runtime):
    result = await runtime.execute("dummy", AgentContext(mission="test"))
    assert result.status == "success"
    assert result.output["handled"] is True


@pytest.mark.asyncio
async def test_agent_runtime_execute_missing(runtime):
    result = await runtime.execute("nonexistent", AgentContext(mission="test"))
    assert result.status == "failure"
    assert "not found" in result.reasoning


@pytest.mark.asyncio
async def test_agent_runtime_execute_failure(runtime):
    runtime.register(FailingAgent())
    result = await runtime.execute("failing", AgentContext(mission="test"))
    assert result.status == "failure"


def test_agent_runtime_stats(runtime):
    stats = runtime.get_stats()
    assert stats["registered"] >= 11
    assert stats["loaded"] >= 1
