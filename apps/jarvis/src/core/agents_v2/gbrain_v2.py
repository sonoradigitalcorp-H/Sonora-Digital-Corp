"""GbrainAgentV2 — Graph brain with Neo4j + Ollama synthesis."""
from .agent_base_v2 import AgentBaseV2


class GbrainAgentV2(AgentBaseV2):
    name = "gbrain"
    description = "Graph brain with Neo4j + Ollama synthesis"
    timeout = 30

    async def run(self, task: str, context: dict = None) -> dict:
        self.publish("gbrain_task", task=task[:100])
        result = await self.neo4j_query("MATCH (n) RETURN labels(n), count(n) as cnt ORDER BY cnt DESC LIMIT 10")
        return self.success(task, result=str(result)[:500])
