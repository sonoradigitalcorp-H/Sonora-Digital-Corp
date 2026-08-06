"""Agent Registry - Catálogo centralizado de agentes."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class AgentInfo:
    """Información completa de un agente."""
    id: str
    name: str
    description: str
    capabilities: list[str]
    tools_allowed: list[str]
    status: str = "offline"  # "online", "offline", "busy", "error"
    max_concurrent: int = 1
    current_load: int = 0
    health_endpoint: Optional[str] = None
    last_health_check: Optional[str] = None
    metadata: dict = field(default_factory=dict)

    @property
    def available(self) -> bool:
        """Verifica si el agente está disponible."""
        return self.status == "online" and self.current_load < self.max_concurrent


@dataclass
class AgentContract:
    """Contrato de integración para un agente."""
    agent_id: str
    input_schema: dict
    output_schema: dict
    events_consume: list[str]
    events_publish: list[str]
    timeout: int = 300
    retry_policy: dict = field(default_factory=lambda: {
        "max_retries": 3,
        "backoff": "exponential",
        "initial_delay": 1,
        "max_delay": 60,
    })


# Agentes por defecto
DEFAULT_AGENTS = {
    "openhands": AgentInfo(
        id="openhands",
        name="OpenHands",
        description="Agente autónomo para código, debugging y deploy",
        capabilities=["code", "debug", "test", "deploy", "browser", "terminal"],
        tools_allowed=["filesystem", "terminal", "browser", "git"],
        status="online",
        max_concurrent=2,
        health_endpoint="http://localhost:3000/health",
    ),
    "opencode": AgentInfo(
        id="opencode",
        name="OpenCode",
        description="IDE interactivo para desarrollo",
        capabilities=["code", "edit", "refactor"],
        tools_allowed=["filesystem", "terminal", "lsp"],
        status="online",
        max_concurrent=1,
        health_endpoint="http://localhost:3001/health",
    ),
    "hermes": AgentInfo(
        id="hermes",
        name="Hermes",
        description="Orquestador MCP para integraciones",
        capabilities=["mcp", "integration", "workflow"],
        tools_allowed=["mcp", "api"],
        status="online",
        max_concurrent=3,
        health_endpoint="http://localhost:3002/health",
    ),
    "aider": AgentInfo(
        id="aider",
        name="Aider",
        description="Especialista en Git y cambios múltiples",
        capabilities=["git", "commit", "changelog", "multi-file"],
        tools_allowed=["filesystem", "terminal", "git"],
        status="online",
        max_concurrent=1,
        health_endpoint=None,
    ),
    "planner": AgentInfo(
        id="planner",
        name="Planner",
        description="Planificador de tareas complejas",
        capabilities=["planning", "analysis", "decomposition"],
        tools_allowed=["memory", "registry"],
        status="online",
        max_concurrent=5,
        health_endpoint=None,
    ),
    "data_agent": AgentInfo(
        id="data_agent",
        name="Data Agent",
        description="Agente para consultas y análisis de datos",
        capabilities=["query", "database", "analytics"],
        tools_allowed=["database", "cache"],
        status="online",
        max_concurrent=2,
        health_endpoint=None,
    ),
}


class AgentRegistry:
    """
    Agent Registry - Catálogo centralizado de agentes.

    Responsabilidades:
    - Registrar y gestionar agentes
    - Verificar salud de agentes
    - Consultar capacidades
    - Gestión de carga
    """

    def __init__(self):
        import copy
        self.agents: dict[str, AgentInfo] = copy.deepcopy(DEFAULT_AGENTS)
        self.contracts: dict[str, AgentContract] = {}

    def register(self, agent: AgentInfo) -> bool:
        """
        Registra un agente.

        Args:
            agent: Información del agente

        Returns:
            True si se registró exitosamente
        """
        if agent.id in self.agents:
            return False  # Ya existe

        self.agents[agent.id] = agent
        return True

    def deregister(self, agent_id: str) -> bool:
        """Elimina un agente del registro."""
        if agent_id in self.agents:
            del self.agents[agent_id]
            if agent_id in self.contracts:
                del self.contracts[agent_id]
            return True
        return False

    def get_agent(self, agent_id: str) -> Optional[AgentInfo]:
        """Obtiene información de un agente."""
        return self.agents.get(agent_id)

    def list_agents(
        self,
        capability: Optional[str] = None,
        status: Optional[str] = None,
    ) -> list[AgentInfo]:
        """Lista agentes con filtros."""
        agents = list(self.agents.values())

        if capability:
            agents = [a for a in agents if capability in a.capabilities]
        if status:
            agents = [a for a in agents if a.status == status]

        return agents

    def get_available_agents(self) -> list[AgentInfo]:
        """Obtiene agentes disponibles."""
        return [a for a in self.agents.values() if a.available]

    def get_agents_for_capability(self, capability: str) -> list[AgentInfo]:
        """Obtiene agentes con una capacidad específica."""
        return [a for a in self.agents.values() if capability in a.capabilities]

    def update_status(self, agent_id: str, status: str) -> bool:
        """Actualiza el estado de un agente."""
        if agent_id in self.agents:
            self.agents[agent_id].status = status
            return True
        return False

    def increment_load(self, agent_id: str) -> bool:
        """Incrementa la carga de un agente."""
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            if agent.current_load < agent.max_concurrent:
                agent.current_load += 1
                return True
        return False

    def decrement_load(self, agent_id: str) -> bool:
        """Decrementa la carga de un agente."""
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            if agent.current_load > 0:
                agent.current_load -= 1
                return True
        return False

    def register_contract(self, contract: AgentContract) -> bool:
        """Registra el contrato de un agente."""
        if contract.agent_id in self.agents:
            self.contracts[contract.agent_id] = contract
            return True
        return False

    def get_contract(self, agent_id: str) -> Optional[AgentContract]:
        """Obtiene el contrato de un agente."""
        return self.contracts.get(agent_id)

    def health_check(self, agent_id: str) -> dict:
        """Realiza health check de un agente."""
        agent = self.agents.get(agent_id)
        if not agent:
            return {"status": "error", "message": "Agent not found"}

        # Por ahora, retornar estado simulado
        return {
            "agent_id": agent_id,
            "status": "healthy" if agent.status == "online" else "unhealthy",
            "last_check": datetime.utcnow().isoformat(),
            "uptime": 3600,
        }

    def get_stats(self) -> dict:
        """Obtiene estadísticas del registry."""
        agents = list(self.agents.values())
        return {
            "total_agents": len(agents),
            "online_agents": len([a for a in agents if a.status == "online"]),
            "available_agents": len([a for a in agents if a.available]),
            "total_capacity": sum(a.max_concurrent for a in agents),
            "current_load": sum(a.current_load for a in agents),
        }
