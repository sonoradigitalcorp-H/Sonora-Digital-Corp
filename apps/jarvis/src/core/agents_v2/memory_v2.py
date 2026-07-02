"""MemoryAgentV2 — Gestion de memoria usando Redis Stream + Neo4j + Ollama."""
from datetime import datetime

from .agent_base_v2 import AgentBaseV2


class MemoryAgentV2(AgentBaseV2):
    name = "memory"
    description = "Gestion de memoria y contexto via Redis + Neo4j + Ollama"
    timeout = 10

    async def run(self, task: str, context: dict = None) -> dict:
        self.publish("memory_task", task=task[:100])

        if "store" in task.lower() or "save" in task.lower() or "remember" in task.lower():
            fact = self.think(f"Extrae el hecho a recordar de: {task}")
            neo = await self.neo4j_query(
                f"MERGE (m:Memory {{id: '{datetime.now().timestamp()}'}}) "
                f"SET m.text = '{fact[:200]}', m.source = 'agent'"
            )
            self.publish("memory_stored", fact=fact[:100])
            return self.success(task, action="stored", fact=fact[:100])

        elif "search" in task.lower() or "find" in task.lower() or "recall" in task.lower():
            query = self.think(f"Extrae el termino de busqueda de: {task}")
            neo = await self.neo4j_query(
                f"MATCH (m:Memory) WHERE m.text CONTAINS '{query}' RETURN m LIMIT 5"
            )
            return self.success(task, action="searched", query=query, data=neo)

        return self.success(task, action="noop")
