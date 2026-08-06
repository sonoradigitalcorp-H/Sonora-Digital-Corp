"""OpenCode Agent - Wrapper para OpenCode."""

from .base import BaseAgent, AgentTask, AgentResult


class OpenCodeAgent(BaseAgent):
    """
    OpenCode Agent - IDE interactivo.

    Capacidades:
    - code: Escribir código
    - edit: Editar archivos
    - refactor: Refactorizar código
    """

    def __init__(self):
        super().__init__("opencode", "OpenCode")
        self.max_concurrent = 1
        self.health_endpoint = "http://localhost:3001/health"

    async def execute(self, task: AgentTask) -> AgentResult:
        """Ejecuta una tarea de IDE."""
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
                "result": f"Executed {task.action} in IDE",
            }

            self.end_task(success=True)

            return AgentResult(
                task_id=task.id,
                agent_id=self.agent_id,
                status="success",
                output=output,
                duration=0.5,
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
        return ["code", "edit", "refactor"]
