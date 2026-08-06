"""Unit tests for Agent Registry."""

import pytest
from src.registry.registry import AgentRegistry, AgentInfo, AgentContract


class TestAgentRegistry:
    """Tests del Agent Registry."""

    def setup_method(self):
        self.registry = AgentRegistry()

    def test_get_agent(self):
        """Test obtener agente."""
        agent = self.registry.get_agent("openhands")
        assert agent is not None
        assert agent.id == "openhands"
        assert agent.name == "OpenHands"

    def test_list_agents(self):
        """Test listar agentes."""
        agents = self.registry.list_agents()
        assert len(agents) >= 4

    def test_list_agents_by_capability(self):
        """Test listar agentes por capacidad."""
        agents = self.registry.list_agents(capability="code")
        assert len(agents) >= 2
        agent_ids = [a.id for a in agents]
        assert "openhands" in agent_ids

    def test_list_agents_by_status(self):
        """Test listar agentes por estado."""
        agents = self.registry.list_agents(status="online")
        assert len(agents) >= 4

    def test_get_available_agents(self):
        """Test obtener agentes disponibles."""
        available = self.registry.get_available_agents()
        assert len(available) >= 4

    def test_update_status(self):
        """Test actualizar estado."""
        result = self.registry.update_status("openhands", "busy")
        assert result is True
        agent = self.registry.get_agent("openhands")
        assert agent.status == "busy"

    def test_increment_decrement_load(self):
        """Test incrementar/decrementar carga."""
        self.registry.increment_load("openhands")
        agent = self.registry.get_agent("openhands")
        assert agent.current_load == 1

        self.registry.decrement_load("openhands")
        agent = self.registry.get_agent("openhands")
        assert agent.current_load == 0

    def test_health_check(self):
        """Test health check."""
        result = self.registry.health_check("openhands")
        assert result["status"] == "healthy"

    def test_get_stats(self):
        """Test obtener estadísticas."""
        stats = self.registry.get_stats()
        assert "total_agents" in stats
        assert "online_agents" in stats
