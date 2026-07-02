"""SkillAgentV2 — Skill execution and tool dispatching."""
from .agent_base_v2 import AgentBaseV2


class SkillAgentV2(AgentBaseV2):
    name = "skill"
    description = "Skill execution and tool dispatching"
    timeout = 30

    async def run(self, task: str, context: dict = None) -> dict:
        self.publish("skill_task", task=task[:100])
        result = self.think(f"Ejecuta el skill necesario para: {task}")
        return self.success(task, result=str(result)[:500])
