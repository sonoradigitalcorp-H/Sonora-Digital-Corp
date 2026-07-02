"""Tests for V2 agents (BaseAgentV2 + V2 agents)."""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock


# ── AgentBaseV2 ──

def test_base_v2_think():
    from apps.jarvis.src.core.agents_v2.agent_base_v2 import ask_ollama, ask_local_impl
    original = ask_local_impl
    try:
        import apps.jarvis.src.core.agents_v2.agent_base_v2 as v2
        v2.ask_local_impl = lambda prompt, model="": "test response"
        result = ask_ollama("test prompt")
        assert result == "test response"
    finally:
        v2.ask_local_impl = original


def test_base_v2_think_error():
    from apps.jarvis.src.core.agents_v2.agent_base_v2 import ask_ollama, ask_local_impl
    import apps.jarvis.src.core.agents_v2.agent_base_v2 as v2
    original = v2.ask_local_impl
    try:
        v2.ask_local_impl = lambda prompt, model="": (_ for _ in ()).throw(Exception("Ollama down"))
        result = ask_ollama("test prompt")
        assert "Error" in result
    finally:
        v2.ask_local_impl = original


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
    mock_agent = ResearchAgentV2()
    mock_agent.run = AsyncMock(return_value={"status": "success", "v2": True, "agent": "research", "task": "test"})
    mock_agent.think = MagicMock(return_value="test")
    mock_agent.hermes = MagicMock()
    mock_agent.publish = MagicMock()
    orch.agents["research"] = mock_agent
    result = await orch.execute("test task")
    assert result["status"] == "success"
    assert result["v2"] is True


# ── All V2 Agent Routing Tests ──

def test_orchestrator_routing_all_agents():
    from apps.jarvis.src.core.agents_v2 import OrchestratorV2
    from apps.jarvis.src.core.agents_v2 import (
        ResearchAgentV2, MemoryAgentV2, ReviewAgentV2, CodeAgentV2,
        ExploreAgentV2, SkillAgentV2, VoiceAgentV2, PRAgentV2,
        SalesAgentV2, HermesAgentV2, OpenClawAgentV2, GbrainAgentV2,
    )
    orch = OrchestratorV2()
    assert len(orch.agents) == 12, f"Expected 12 agents, got {len(orch.agents)}"
    for name in ["research", "memory", "review", "code", "explore", "skill", "voice", "pr", "sales", "hermes", "openclaw", "gbrain"]:
        assert name in orch.agents, f"Missing agent: {name}"
        assert orch.agents[name].name == name


# ── V2 Agent Run Mock Tests ──

@pytest.mark.asyncio
async def test_all_v2_agents_run():
    """Test that all V2 agents have a run() method and return correct structure."""
    from apps.jarvis.src.core.agents_v2 import OrchestratorV2
    orch = OrchestratorV2()
    for name, agent in orch.agents.items():
        assert hasattr(agent, "run"), f"{name} missing run()"
        assert agent.name == name, f"{name} has wrong name"

        # Mock think to prevent Ollama calls
        agent.think = MagicMock(return_value="mock response")

        # Mock hermes with AsyncMock for await support
        mock_hermes = MagicMock()
        for method in ["health_status", "list_tools", "git_log", "query_neo4j", "search_qdrant", "call_tool"]:
            setattr(mock_hermes, method, AsyncMock(return_value={"success": True, "data": {}}))
        agent.hermes = mock_hermes

        agent.publish = MagicMock()

        try:
            result = await agent.run(f"test task for {name}")
            assert result["status"] == "success", f"{name}: {result}"
            assert result["v2"] is True, f"{name}: v2 flag missing"
        except Exception as e:
            pytest.fail(f"{name} run failed: {e}")


# ── MCP Healer V2 Tests ──

@pytest.mark.asyncio
async def test_healer_v2_git_mcp():
    """Test healer_v2 uses Git MCP via HermesClient."""
    from apps.agents.hermes_client import HermesClient
    client = HermesClient()
    with patch.object(client, "git_commit", AsyncMock()) as mock_git:
        mock_git.return_value = {"success": True, "data": {"commit": "abc123"}}
        result = await client.git_commit("test commit")
        assert result["success"] is True


@pytest.mark.asyncio
async def test_healer_v2_memory_mcp():
    """Test healer_v2 uses Memory MCP via HermesClient."""
    from apps.agents.hermes_client import HermesClient
    client = HermesClient()
    with patch.object(client, "memory_create_entities", AsyncMock()) as mock_mem:
        mock_mem.return_value = {"success": True, "data": {"created": 1}}
        entities = [{"name": "test", "entityType": "event", "observations": ["test"]}]
        result = await client.memory_create_entities(entities)
        assert result["success"] is True
