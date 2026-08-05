"""Base Agent - Clase base para todos los agentes."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import uuid4


@dataclass
class AgentTask:
    """Tarea para un agente."""
    id: str
    action: str
    inputs: dict
    timeout: int = 300
    metadata: dict = field(default_factory=dict)
    created_at: str = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow().isoformat()


@dataclass
class AgentResult:
    """Resultado de un agente."""
    task_id: str
    agent_id: str
    status: str  # "success", "error", "timeout"
    output: dict = field(default_factory=dict)
    error: Optional[str] = None
    duration: float = 0.0
    completed_at: str = None

    def __post_init__(self):
        if self.completed_at is None:
            self.completed_at = datetime.utcnow().isoformat()


class BaseAgent(ABC):
    """
    Base Agent - Clase base para todos los agentes.

    Cada agente debe implementar:
    - execute(): Ejecutar una tarea
    - get_capabilities(): Obtener capacidades del agente
    """

    def __init__(self, agent_id: str, name: str):
        self.agent_id = agent_id
        self.name = name
        self.status = "online"
        self.current_load = 0
        self.max_concurrent = 1
        self.tasks_executed = 0
        self.errors = 0

    @abstractmethod
    async def execute(self, task: AgentTask) -> AgentResult:
        """
        Ejecuta una tarea.

        Args:
            task: Tarea a ejecutar

        Returns:
            Resultado de la ejecución
        """
        pass

    @abstractmethod
    def get_capabilities(self) -> list[str]:
        """Obtiene las capacidades del agente."""
        pass

    def get_status(self) -> dict:
        """Obtiene el estado del agente."""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "status": self.status,
            "current_load": self.current_load,
            "max_concurrent": self.max_concurrent,
            "tasks_executed": self.tasks_executed,
            "errors": self.errors,
            "available": self.status == "online" and self.current_load < self.max_concurrent,
        }

    def can_execute(self) -> bool:
        """Verifica si el agente puede ejecutar una tarea."""
        return self.status == "online" and self.current_load < self.max_concurrent

    def start_task(self) -> bool:
        """Incrementa la carga al iniciar una tarea."""
        if self.can_execute():
            self.current_load += 1
            return True
        return False

    def end_task(self, success: bool = True):
        """Decrementa la carga al finalizar una tarea."""
        if self.current_load > 0:
            self.current_load -= 1
        self.tasks_executed += 1
        if not success:
            self.errors += 1
