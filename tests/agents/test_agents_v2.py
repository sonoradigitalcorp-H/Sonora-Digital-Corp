"""Tests for V2 agents (BaseAgentV2 + V2 agents)."""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock


# ── AgentBaseV2 ──

@pytest.mark.asyncio
async def test_base_v2_think():
    from apps.jarvis.src.core.agents_v2.agent_base_v2 import AgentBaseV2, ask_ollama
    with patch("apps.jarvis.src.core.agents_v2.agent_base_v2.ask_local") as mock_ask:
        mock_ask.return_value = "test response"
        result = ask_ollama("test prompt")
        assert result == "test response"


@pytest.mark.asyncio
async def test_base_v2_think_error():
    from apps.jarvis.src.core.agents_v2.agent_base_v2 import ask_ollama
    with patch("apps.jarvis.src.core.agents_v2.agent_base_v2.ask_local") as mock_ask:
        mock_ask.side_effect = Exception("Ollama down")
        result = ask_ollama("test prompt")
        assert "Error" in result


def test_base_v2_redis_publish():
    from apps.jarvis.src.core.agents_v2.agent_base_v2 import publish_to_redis
    with patch("redis.Redis") as mock_redis:
        mock_instance = MagicMock()
        mock_redis.return_value = mock_instance
        publish_to_redis("test_event", "test_agent", {"key": "value"})
        assert mock_instance.xadd.called


@pytest.mark.asyncio
async def test_base_v2_hermes():
    from apps.jarvis.src.core.agents_v2.agent_base_v2 import AgentBaseV2
    agent = AgentBaseV2()
    with patch.object(agent.hermes, "health_status", AsyncMock()) as mock_health:
        mock_health.return_value = {"success": True, "data": {"healthy": True}}
        result = await agent.health()
        assert result["success"] is True


# ── OrchestratorV2 Routing ──

def test_orchestrator_routing():
    from apps.jarvis.src.core.agents_v2 import OrchestratorV2
    orch = OrchestratorV2()
    assert orch.route("recuerda algo") == "memory"
    assert orch.route("revisa este codigo") == "review"
    assert orch.route("busca informacion sobre Neo4j") == "research"


@pytest.mark.asyncio
async def test_orchestrator_execute():
    from apps.jarvis.src.core.agents_v2 import OrchestratorV2
    from apps.jarvis.src.core.agents_v2.research_v2 import ResearchAgentV2
    orch = OrchestratorV2()
    original_agent = orch.agents["research"]
    mock_agent = ResearchAgentV2()
    mock_agent.run = AsyncMock(return_value={"status": "success", "v2": True, "agent": "research", "task": "test"})
    mock_agent.think = MagicMock(return_value="test")
    mock_agent.hermes = MagicMock()
    mock_agent.publish = MagicMock()
    orch.agents["research"] = mock_agent
    result = await orch.execute("test task")
    assert result["status"] == "success"
    assert result["v2"] is True
