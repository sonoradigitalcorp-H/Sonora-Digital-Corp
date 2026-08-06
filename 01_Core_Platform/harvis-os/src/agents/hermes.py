"""Hermes Agent - Wrapper para Hermes MCP."""

from .base import BaseAgent, AgentTask, AgentResult


class HermesAgent(BaseAgent):
    """
    Hermes Agent - Orquestador MCP.

    Capacidades:
    - mcp: Model Context Protocol
    - integration: Integraciones
    - workflow: Flujos de trabajo
    """

    def __init__(self):
        super().__init__("hermes", "Hermes")
        self.max_concurrent = 3
        self.health_endpoint = "http://localhost:3002/health"

    async def execute(self, task: AgentTask) -> AgentResult:
        """Ejecuta una tarea MCP."""
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
                "result": f"Executed MCP action: {task.action}",
            }

            self.end_task(success=True)

            return AgentResult(
                task_id=task.id,
                agent_id=self.agent_id,
                status="success",
                output=output,
                duration=0.3,
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
        return ["mcp", "integration", "workflow"]
