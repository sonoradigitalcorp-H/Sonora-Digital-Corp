"""HermesAgentV2 — Bridge to Hermes MCP Gateway."""
from .agent_base_v2 import AgentBaseV2


class HermesAgentV2(AgentBaseV2):
    name = "hermes"
    description = "Bridge to Hermes MCP Gateway"
    timeout = 30

    async def run(self, task: str, context: dict = None) -> dict:
        self.publish("hermes_task", task=task[:100])
        result = await self.hermes.list_tools()
        return self.success(task, result=str(result)[:500])
