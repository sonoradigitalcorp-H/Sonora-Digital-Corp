"""OpenHands Agent - Wrapper para OpenHands."""

from .base import BaseAgent, AgentTask, AgentResult


class OpenHandsAgent(BaseAgent):
    """
    OpenHands Agent - Agente autónomo para código.

    Capacidades:
    - code: Escribir código
    - debug: Depurar errores
    - test: Escribir tests
    - deploy: Desplegar aplicaciones
    - browser: Automatización de navegador
    - terminal: Ejecutar comandos
    """

    def __init__(self):
        super().__init__("openhands", "OpenHands")
        self.max_concurrent = 2
        self.health_endpoint = "http://localhost:3000/health"

    async def execute(self, task: AgentTask) -> AgentResult:
        """Ejecuta una tarea de código."""
        if not self.start_task():
            return AgentResult(
                task_id=task.id,
                agent_id=self.agent_id,
                status="error",
                error="Agent busy",
            )

        try:
            # En producción, aquí se integraría con OpenHands real
            # Por ahora, simular ejecución
            output = {
                "action": task.action,
                "result": f"Executed {task.action} successfully",
                "files_modified": [],
                "commands_run": [],
            }

            self.end_task(success=True)

            return AgentResult(
                task_id=task.id,
                agent_id=self.agent_id,
                status="success",
                output=output,
                duration=1.0,
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
        return ["code", "debug", "test", "deploy", "browser", "terminal"]
