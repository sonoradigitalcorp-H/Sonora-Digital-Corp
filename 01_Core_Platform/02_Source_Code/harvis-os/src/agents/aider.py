"""Aider Agent - Wrapper para Aider."""

from .base import BaseAgent, AgentTask, AgentResult


class AiderAgent(BaseAgent):
    """
    Aider Agent - Especialista en Git.

    Capacidades:
    - git: Control de versiones
    - commit: Crear commits
    - changelog: Generar changelogs
    - multi-file: Cambios en múltiples archivos
    """

    def __init__(self):
        super().__init__("aider", "Aider")
        self.max_concurrent = 1
        self.health_endpoint = None

    async def execute(self, task: AgentTask) -> AgentResult:
        """Ejecuta una tarea de Git."""
        if not self.start_task():
            return AgentResult(
                task_id=task.id,
                agent_id=self.agent_id,
                status="error",
                error="Agent busy",
            )

        try:
            output = {
                "action": task.action,
                "result": f"Executed git action: {task.action}",
                "commit_hash": None,
                "files_changed": [],
            }

            self.end_task(success=True)

            return AgentResult(
                task_id=task.id,
                agent_id=self.agent_id,
                status="success",
                output=output,
                duration=0.2,
            )

        except Exception as e:
            self.end_task(success=False)
            return AgentResult(
                task_id=task.id,
                agent_id=self.agent_id,
                status="error",
                error=str(e),
            )

    def get_capabilities(self) -> list[str]:
        return ["git", "commit", "changelog", "multi-file"]
