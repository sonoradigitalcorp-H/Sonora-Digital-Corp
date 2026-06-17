"""Tests for JARVIS Agent Orchestrator."""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from core.orchestrator import (
    AgentOrchestrator,
    ResearchAgent,
    CodeAgent,
    MemoryAgent,
    get_orchestrator,
    execute_task,
)


@pytest.fixture
def orchestrator():
    return AgentOrchestrator()


class TestAgentOrchestrator:
    def test_initialization(self, orchestrator):
        assert len(orchestrator.agents) == 11
        agent_names = [a.name for a in orchestrator.agents.values()]
        assert "research" in agent_names
        assert "code" in agent_names
        assert "memory" in agent_names
        assert "explore" in agent_names
        assert "skill" in agent_names
        assert "voice" in agent_names
        assert "review" in agent_names
        assert "hermes" in agent_names
        assert "openclaw" in agent_names
        assert "gbrain" in agent_names
        assert "pr" in agent_names

    def test_routing_gbrain(self, orchestrator):
        agent = orchestrator.route("sintetizá este conocimiento en el cerebro")
        assert agent == "gbrain"

    def test_routing_hermes(self, orchestrator):
        agent = orchestrator.route("mandá un mensaje por Telegram")
        assert agent == "hermes"

    def test_routing_openclaw(self, orchestrator):
        agent = orchestrator.route("delegá esta tarea al gateway")
        assert agent == "openclaw"

    def test_routing_pr(self, orchestrator):
        agent = orchestrator.route("creá un pull request")
        assert agent == "pr"

    def test_routing_pr_list(self, orchestrator):
        agent = orchestrator.route("listá los PRs")
        assert agent == "pr"

    def test_routing_pr_merge(self, orchestrator):
        agent = orchestrator.route("merge PR #42")
        assert agent == "pr"

    @pytest.mark.parametrize("task,expected_agent", [
        ("buscar información sobre IA", "research"),
        ("investigar cómo funciona Neo4j", "research"),
        ("search for documentation", "research"),
        ("escribe una función en Python", "code"),
        ("implementa un endpoint REST", "code"),
        ("arregla este bug en auth.py", "code"),
        ("explora el directorio src", "explore"),
        ("navega a la carpeta docker", "explore"),
        ("listar archivos del proyecto", "explore"),
        ("recuerda esta conversación", "memory"),
        ("guarda este contexto", "memory"),
        ("olvida lo que te dije antes", "memory"),
        ("ejecuta la skill analyze_code", "skill"),
        ("habla en voz alta", "voice"),
        ("dime el resultado", "voice"),
        ("revisa este código", "review"),
        ("valida el código nuevo", "review"),
        ("valida el pull request", "pr"),
    ])
    def test_routing(self, orchestrator, task, expected_agent):
        agent = orchestrator.route(task)
        assert agent == expected_agent, f"Expected {expected_agent} for '{task}', got {agent}"

    def test_routing_fallback(self, orchestrator):
        """Unknown tasks should fall back to research agent."""
        agent = orchestrator.route("tarea desconocida sin keywords")
        assert agent == "research"

    def test_list_agents(self, orchestrator):
        agents = orchestrator.list_agents()
        assert len(agents) == 11
        for a in agents:
            assert "name" in a
            assert "description" in a
            assert "timeout" in a

    @pytest.mark.asyncio
    async def test_execute_research(self, orchestrator):
        result = await orchestrator.execute("buscar información sobre Python")
        assert result["agent"] == "research"
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_execute_code(self, orchestrator):
        result = await orchestrator.execute("escribe una función hola mundo")
        assert result["agent"] == "code"
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_execute_memory(self, orchestrator):
        result = await orchestrator.execute("recuerda que me gusta Python")
        assert result["agent"] == "memory"
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_execute_parallel(self, orchestrator):
        results = await orchestrator.execute_parallel([
            "buscar información sobre Python",
            "escribe una función hola mundo",
        ])
        assert len(results) == 2
        assert results[0]["agent"] == "research"
        assert results[1]["agent"] == "code"

    def test_singleton_get_orchestrator(self):
        o1 = get_orchestrator()
        o2 = get_orchestrator()
        assert o1 is o2

    @pytest.mark.asyncio
    async def test_execute_task_convenience(self):
        result = await execute_task("buscar algo")
        assert result["status"] == "success"
        assert "execution_time" in result


class TestResearchAgent:
    @pytest.mark.asyncio
    async def test_run(self):
        agent = ResearchAgent()
        result = await agent.run("buscar información sobre Python")
        assert result["agent"] == "research"
        assert "sources" in result

    def test_calc_confidence(self):
        agent = ResearchAgent()
        sources = [
            {"data": {"text": "test1"}},
            {"data": {"text": "test2"}},
            {"data": None},
        ]
        confidence = agent._calc_confidence(sources)
        assert confidence == pytest.approx(0.67, 0.1)


class TestCodeAgent:
    @pytest.mark.asyncio
    async def test_run(self):
        agent = CodeAgent()
        result = await agent.run("escribe una función")
        assert result["agent"] == "code"


class TestMemoryAgent:
    @pytest.mark.asyncio
    async def test_run(self):
        agent = MemoryAgent()
        result = await agent.run("recuerda esto")
        assert result["agent"] == "memory"
