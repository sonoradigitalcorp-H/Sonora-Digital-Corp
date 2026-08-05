"""Planner - Motor de planificación de tareas."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import uuid4


@dataclass
class PlanStep:
    """Step de un plan de ejecución."""
    id: str
    order: int
    description: str
    agent: str
    action: str
    inputs: dict = field(default_factory=dict)
    expected_output: str = ""
    dependencies: list[str] = field(default_factory=list)
    retry_policy: dict = field(default_factory=lambda: {
        "max_retries": 3,
        "backoff": "linear",
    })
    timeout: int = 300
    status: str = "pending"  # pending, in_progress, completed, failed


@dataclass
class ExecutionPlan:
    """Plan de ejecución con tareas secuenciadas."""
    id: str
    task_id: str
    objective: str
    steps: list[PlanStep]
    estimated_duration: int  # segundos
    required_agents: list[str]
    dependencies: list[str] = field(default_factory=list)
    created_at: str = None
    status: str = "pending"  # pending, approved, in_progress, completed, failed

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow().isoformat()


# Patrones de planificación conocidos (Principio II - determinista)
KNOWN_PATTERNS = {
    "crud": {
        "trigger": r"CRUD|crear.*tabla|endpoint.*REST|api.*rest",
        "steps": [
            {"description": "Definir esquema", "agent": "planner", "action": "define_schema"},
            {"description": "Crear migración", "agent": "openhands", "action": "create_migration"},
            {"description": "Implementar modelo", "agent": "openhands", "action": "implement_model"},
            {"description": "Crear endpoints", "agent": "openhands", "action": "create_endpoints"},
            {"description": "Escribir tests", "agent": "openhands", "action": "write_tests"},
            {"description": "Documentar API", "agent": "openhands", "action": "document_api"},
        ],
    },
    "bugfix": {
        "trigger": r"bug|error|fix|arreglar|corregir",
        "steps": [
            {"description": "Reproducir bug", "agent": "openhands", "action": "reproduce_bug"},
            {"description": "Identificar causa raíz", "agent": "openhands", "action": "find_root_cause"},
            {"description": "Implementar fix", "agent": "openhands", "action": "implement_fix"},
            {"description": "Escribir test de regresión", "agent": "openhands", "action": "write_regression_test"},
            {"description": "Verificar fix", "agent": "openhands", "action": "verify_fix"},
        ],
    },
    "refactor": {
        "trigger": r"refactor|mejorar|optimizar|limpiar",
        "steps": [
            {"description": "Analizar código actual", "agent": "openhands", "action": "analyze_code"},
            {"description": "Diseñar nueva estructura", "agent": "planner", "action": "design_structure"},
            {"description": "Implementar cambios", "agent": "openhands", "action": "implement_changes"},
            {"description": "Ejecutar tests existentes", "agent": "openhands", "action": "run_tests"},
            {"description": "Actualizar documentación", "agent": "openhands", "action": "update_docs"},
        ],
    },
    "feature": {
        "trigger": r"feature|funcionalidad|nueva.*función|agregar|añadir",
        "steps": [
            {"description": "Analizar requisitos", "agent": "planner", "action": "analyze_requirements"},
            {"description": "Diseñar solución", "agent": "planner", "action": "design_solution"},
            {"description": "Implementar feature", "agent": "openhands", "action": "implement_feature"},
            {"description": "Escribir tests", "agent": "openhands", "action": "write_tests"},
            {"description": "Documentar", "agent": "openhands", "action": "document"},
        ],
    },
    "simple": {
        "trigger": r"commit|push|pull|deploy|git",
        "steps": [
            {"description": "Ejecutar tarea simple", "agent": "aider", "action": "execute_simple"},
        ],
    },
}


class Planner:
    """
    Planner - Motor de planificación de tareas.

    Convierte objetivos complejos en planes de ejecución secuenciados.
    """

    def __init__(self):
        self.plans: dict[str, ExecutionPlan] = {}
        self.patterns = KNOWN_PATTERNS

    def create_plan(self, task_id: str, content: str) -> ExecutionPlan:
        """
        Crea un plan de ejecución para una tarea.

        Args:
            task_id: ID de la tarea
            content: Contenido/descripción de la tarea

        Returns:
            ExecutionPlan con los steps a ejecutar
        """
        # Buscar patrón conocido
        pattern = self._match_pattern(content)

        if pattern:
            steps = self._create_steps_from_pattern(pattern)
        else:
            # Fallback: crear plan genérico
            steps = self._create_generic_plan(content)

        # Calcular agentes requeridos
        required_agents = list(set(step.agent for step in steps))

        # Estimar duración (30 segundos por step por defecto)
        estimated_duration = len(steps) * 30

        plan = ExecutionPlan(
            id=str(uuid4()),
            task_id=task_id,
            objective=content,
            steps=steps,
            estimated_duration=estimated_duration,
            required_agents=required_agents,
        )

        self.plans[plan.id] = plan
        return plan

    def approve_plan(self, plan_id: str) -> bool:
        """Aprueba un plan para ejecución."""
        if plan_id in self.plans:
            self.plans[plan_id].status = "approved"
            return True
        return False

    def reject_plan(self, plan_id: str, reason: str = "") -> bool:
        """Rechaza un plan."""
        if plan_id in self.plans:
            self.plans[plan_id].status = "failed"
            return True
        return False

    def get_plan(self, plan_id: str) -> Optional[ExecutionPlan]:
        """Obtiene un plan por ID."""
        return self.plans.get(plan_id)

    def list_plans(self, status: Optional[str] = None) -> list[ExecutionPlan]:
        """Lista planes con filtro de estado."""
        plans = list(self.plans.values())
        if status:
            plans = [p for p in plans if p.status == status]
        return plans

    def update_step_status(self, plan_id: str, step_id: str, status: str) -> bool:
        """Actualiza el estado de un step."""
        plan = self.plans.get(plan_id)
        if plan:
            for step in plan.steps:
                if step.id == step_id:
                    step.status = status
                    return True
        return False

    def get_next_step(self, plan_id: str) -> Optional[PlanStep]:
        """Obtiene el siguiente step a ejecutar."""
        plan = self.plans.get(plan_id)
        if not plan:
            return None

        for step in plan.steps:
            if step.status == "pending":
                # Verificar dependencias
                deps_met = all(
                    self._get_step_by_id(plan, dep_id).status == "completed"
                    for dep_id in step.dependencies
                    if self._get_step_by_id(plan, dep_id)
                )
                if deps_met:
                    return step

        return None

    def _match_pattern(self, content: str):
        """Busca un patrón conocido en el contenido."""
        import re
        content_lower = content.lower()

        for pattern_name, pattern in self.patterns.items():
            if re.search(pattern["trigger"], content_lower, re.IGNORECASE):
                return pattern

        return None

    def _create_steps_from_pattern(self, pattern: dict) -> list[PlanStep]:
        """Crea steps desde un patrón conocido."""
        steps = []
        for i, step_config in enumerate(pattern["steps"]):
            step = PlanStep(
                id=str(uuid4()),
                order=i + 1,
                description=step_config["description"],
                agent=step_config["agent"],
                action=step_config["action"],
                dependencies=[steps[-1].id] if steps else [],
            )
            steps.append(step)
        return steps

    def _create_generic_plan(self, content: str) -> list[PlanStep]:
        """Crea un plan genérico para tareas no conocidas."""
        return [
            PlanStep(
                id=str(uuid4()),
                order=1,
                description="Analizar tarea",
                agent="planner",
                action="analyze",
            ),
            PlanStep(
                id=str(uuid4()),
                order=2,
                description="Implementar solución",
                agent="openhands",
                action="implement",
                dependencies=[],  # Se actualizará con el ID del step 1
            ),
            PlanStep(
                id=str(uuid4()),
                order=3,
                description="Verificar resultado",
                agent="openhands",
                action="verify",
                dependencies=[],  # Se actualizará con el ID del step 2
            ),
        ]

    def _get_step_by_id(self, plan: ExecutionPlan, step_id: str) -> Optional[PlanStep]:
        """Obtiene un step por ID."""
        for step in plan.steps:
            if step.id == step_id:
                return step
        return None

    def get_stats(self) -> dict:
        """Obtiene estadísticas del planner."""
        plans = list(self.plans.values())
        return {
            "total_plans": len(plans),
            "plans_by_status": self._count_by_status(plans),
            "total_steps": sum(len(p.steps) for p in plans),
        }

    def _count_by_status(self, plans: list[ExecutionPlan]) -> dict:
        counts = {}
        for plan in plans:
            counts[plan.status] = counts.get(plan.status, 0) + 1
        return counts
