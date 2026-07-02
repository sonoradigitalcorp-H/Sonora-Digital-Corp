"""OpenclawAgentV2 — Bridge to OpenClaw Gateway."""
from .agent_base_v2 import AgentBaseV2


class OpenClawAgentV2(AgentBaseV2):
    name = "openclaw"
    description = "Bridge to OpenClaw Gateway"
    timeout = 30

    async def run(self, task: str, context: dict = None) -> dict:
        self.publish("openclaw_task", task=task[:100])
        result = await self.hermes.health_status()
        return self.success(task, result=str(result)[:500])
