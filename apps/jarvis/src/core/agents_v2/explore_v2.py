"""ExploreAgentV2 — filesystem navigation using HermesClient."""
from .agent_base_v2 import AgentBaseV2


class ExploreAgentV2(AgentBaseV2):
    name = "explore"
    description = "Filesystem navigation and search"
    timeout = 15

    async def run(self, task: str, context: dict = None) -> dict:
        self.publish("explore_task", task=task[:100])

        path = task.replace("explore ", "").replace("list ", "").strip() or "."
        result = self.think(f"Lista los archivos en {path}. Describe que encontraste.")

        return self.success(task, path=path, result=result)
