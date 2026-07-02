"""SalesAgentV2 — Sales pipeline with Ollama decisions."""
from .agent_base_v2 import AgentBaseV2


class SalesAgentV2(AgentBaseV2):
    name = "sales"
    description = "Sales pipeline with Ollama decisions"
    timeout = 30

    async def run(self, task: str, context: dict = None) -> dict:
        self.publish("sales_task", task=task[:100])
        result = self.think(f"Eres un agente de ventas. Procesa: {task}")
        return self.success(task, result=str(result)[:500])
