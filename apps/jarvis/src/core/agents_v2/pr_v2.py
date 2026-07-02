"""PrAgentV2 — GitHub Pull Request management via Git MCP."""
from .agent_base_v2 import AgentBaseV2


class PRAgentV2(AgentBaseV2):
    name = "pr"
    description = "GitHub Pull Request management via Git MCP"
    timeout = 30

    async def run(self, task: str, context: dict = None) -> dict:
        self.publish("pr_task", task=task[:100])
        result = await self.hermes.git_log(max_count=10)
        return self.success(task, result=str(result)[:500])
