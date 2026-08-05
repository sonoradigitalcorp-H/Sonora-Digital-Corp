"""Dispatcher principal - Punto único de entrada de Harvis OS."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import uuid4

from .classifier import TaskClassifier, ClassificationResult
from .router import AgentRouter, RoutingResult


@dataclass
class IncomingRequest:
    """Petición entrante desde cualquier fuente."""
    source: str  # "telegram", "web", "cli", "api"
    user_id: str
    content: str
    metadata: dict = field(default_factory=dict)
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()


@dataclass
class ClassifiedTask:
    """Tarea clasificada lista para ser procesada."""
    id: str
    request: IncomingRequest
    category: str
    priority: str
    assigned_agent: str
    confidence: float
    routing_reason: str
    status: str = "classified"
    created_at: str = None
    routed_at: Optional[str] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow().isoformat()


class Dispatcher:
    """
    Dispatcher - Punto único de entrada (Principio I).

    Flujo: Usuario → Dispatcher → Planner → Agente → QA → Respuesta
    """

    def __init__(self):
        self.classifier = TaskClassifier()
        self.router = AgentRouter()
        self.tasks: dict[str, ClassifiedTask] = {}

    async def process_request(self, request: IncomingRequest) -> ClassifiedTask:
        """
        Procesa una petición entrante.

        Args:
            request: Petición desde cualquier fuente

        Returns:
            ClassifiedTask con tarea clasificada y agente asignado
        """
        # 1. Generar ID único para la tarea
        task_id = str(uuid4())

        # 2. Clasificar la tarea (determinista - Principio II)
        classification = self.classifier.classify(request.content)

        # 3. Obtener agente recomendado
        agent_id = self.classifier.get_agent_for_category(classification.category)

        # 4. Rutar al agente
        routing = self.router.route(agent_id, task_id)

        # 5. Crear tarea clasificada
        task = ClassifiedTask(
            id=task_id,
            request=request,
            category=classification.category,
            priority=self.classifier.get_priority_for_category(classification.category),
            assigned_agent=routing.agent_id if routing.status == "assigned" else "planner",
            confidence=classification.confidence,
            routing_reason=classification.routing_reason,
            status="assigned" if routing.status == "assigned" else routing.status,
            routed_at=routing.routed_at,
        )

        # 6. Almacenar tarea
        self.tasks[task_id] = task

        return task

    def get_task(self, task_id: str) -> Optional[ClassifiedTask]:
        """Obtiene una tarea por ID."""
        return self.tasks.get(task_id)

    def list_tasks(
        self,
        status: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 10,
    ) -> list[ClassifiedTask]:
        """Lista tareas con filtros."""
        tasks = list(self.tasks.values())

        if status:
            tasks = [t for t in tasks if t.status == status]
        if category:
            tasks = [t for t in tasks if t.category == category]

        return tasks[:limit]

    def update_task_status(self, task_id: str, status: str) -> bool:
        """Actualiza el estado de una tarea."""
        if task_id in self.tasks:
            self.tasks[task_id].status = status
            return True
        return False

    def get_stats(self) -> dict:
        """Obtiene estadísticas del dispatcher."""
        tasks = list(self.tasks.values())
        return {
            "total_tasks": len(tasks),
            "tasks_by_status": self._count_by_status(tasks),
            "tasks_by_category": self._count_by_category(tasks),
            "tasks_by_agent": self._count_by_agent(tasks),
        }

    def _count_by_status(self, tasks: list[ClassifiedTask]) -> dict:
        counts = {}
        for task in tasks:
            counts[task.status] = counts.get(task.status, 0) + 1
        return counts

    def _count_by_category(self, tasks: list[ClassifiedTask]) -> dict:
        counts = {}
        for task in tasks:
            counts[task.category] = counts.get(task.category, 0) + 1
        return counts

    def _count_by_agent(self, tasks: list[ClassifiedTask]) -> dict:
        counts = {}
        for task in tasks:
            counts[task.assigned_agent] = counts.get(task.assigned_agent, 0) + 1
        return counts
