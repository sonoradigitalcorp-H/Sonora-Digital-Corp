"""Agent router - Enrutamiento de tareas a agentes."""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class RoutingResult:
    """Resultado de routing."""
    agent_id: str
    agent_name: str
    status: str  # "assigned", "queued", "error"
    queue_position: Optional[int] = None
    estimated_wait: Optional[int] = None  # segundos
    routed_at: str = None

    def __post_init__(self):
        if self.routed_at is None:
            self.routed_at = datetime.utcnow().isoformat()


# Configuración de agentes (Principio II - determinista)
AGENT_CONFIG = {
    "openhands": {
        "name": "OpenHands",
        "max_concurrent": 2,
        "current_load": 0,
        "status": "online",
        "capabilities": ["code", "debug", "test", "deploy", "browser", "terminal"],
    },
    "opencode": {
        "name": "OpenCode",
        "max_concurrent": 1,
        "current_load": 0,
        "status": "online",
        "capabilities": ["code", "edit", "refactor"],
    },
    "hermes": {
        "name": "Hermes",
        "max_concurrent": 3,
        "current_load": 0,
        "status": "online",
        "capabilities": ["mcp", "integration", "workflow"],
    },
    "aider": {
        "name": "Aider",
        "max_concurrent": 1,
        "current_load": 0,
        "status": "online",
        "capabilities": ["git", "commit", "changelog", "multi-file"],
    },
    "planner": {
        "name": "Planner",
        "max_concurrent": 5,
        "current_load": 0,
        "status": "online",
        "capabilities": ["planning", "analysis"],
    },
    "data_agent": {
        "name": "Data Agent",
        "max_concurrent": 2,
        "current_load": 0,
        "status": "online",
        "capabilities": ["query", "database", "analytics"],
    },
}


class AgentRouter:
    """Router determinista de agentes (Principio II)."""

    def __init__(self):
        import copy
        self.agents = copy.deepcopy(AGENT_CONFIG)

    def route(self, agent_id: str, task_id: str) -> RoutingResult:
        """
        Rutea una tarea al agente especificado.

        Args:
            agent_id: ID del agente destino
            task_id: ID de la tarea

        Returns:
            RoutingResult con resultado del routing
        """
        # Verificar que el agente existe
        if agent_id not in self.agents:
            return RoutingResult(
                agent_id=agent_id,
                agent_name="Unknown",
                status="error",
            )

        agent = self.agents[agent_id]

        # Verificar que el agente está online
        if agent["status"] != "online":
            return RoutingResult(
                agent_id=agent_id,
                agent_name=agent["name"],
                status="error",
            )

        # Verificar capacidad
        if agent["current_load"] >= agent["max_concurrent"]:
            return RoutingResult(
                agent_id=agent_id,
                agent_name=agent["name"],
                status="queued",
                queue_position=1,
                estimated_wait=30,
            )

        # Asignar tarea
        agent["current_load"] += 1

        return RoutingResult(
            agent_id=agent_id,
            agent_name=agent["name"],
            status="assigned",
        )

    def release_agent(self, agent_id: str) -> bool:
        """Libera una unidad de carga del agente."""
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            if agent["current_load"] > 0:
                agent["current_load"] -= 1
                return True
        return False

    def get_agent_status(self, agent_id: str) -> Optional[dict]:
        """Obtiene el estado de un agente."""
        return self.agents.get(agent_id)

    def get_available_agents(self) -> list[str]:
        """Obtiene lista de agentes disponibles."""
        available = []
        for agent_id, agent in self.agents.items():
            if agent["status"] == "online" and agent["current_load"] < agent["max_concurrent"]:
                available.append(agent_id)
        return available

    def get_agents_for_capability(self, capability: str) -> list[str]:
        """Obtiene agentes con una capacidad específica."""
        agents = []
        for agent_id, agent in self.agents.items():
            if capability in agent["capabilities"]:
                agents.append(agent_id)
        return agents
