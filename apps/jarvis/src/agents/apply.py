from typing import Any, Dict

from src.core.agents.agent_base import AgentBase, success_response, error_response


class ApplyAgent(AgentBase):
    name = "apply"
    description = "Ejecuta tareas de implementación usando habilidades del registro"
    timeout = 120

    async def run(self, task: str, context: dict = None) -> Dict[str, Any]:
        self.log.info(f"Apply phase: {task[:100]}...")

        # Extract tasks from context
        tasks_content = context.get("design_result", {}).get("tasks_content", "")
        if not tasks_content:
            return error_response(self.name, task, "No tasks found in context")

        # In real implementation, this would:
        # 1. Parse tasks from tasks_content
        # 2. Match each task to skills in registry
        # 3. Execute tasks using appropriate agents/skills
        # 4. Track progress and results

        # For now, simulate execution
        executed_tasks = [
            {
                "task": "Implementar componente A",
                "status": "completed",
                "skill": "code",
            },
            {
                "task": "Implementar componente B",
                "status": "completed",
                "skill": "code",
            },
            {
                "task": "Integrar con sistema existente",
                "status": "completed",
                "skill": "code",
            },
        ]

        return success_response(
            self.name,
            task,
            action="execute_tasks",
            executed_tasks=executed_tasks,
            total_tasks=len(executed_tasks),
            completed_tasks=len(
                [t for t in executed_tasks if t["status"] == "completed"]
            ),
            failed_tasks=len([t for t in executed_tasks if t["status"] == "failed"]),
        )
