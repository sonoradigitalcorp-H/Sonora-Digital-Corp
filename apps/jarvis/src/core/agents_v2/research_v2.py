"""ResearchAgentV2 — Busqueda y sintesis usando Neo4j + Qdrant + Ollama local."""
from .agent_base_v2 import AgentBaseV2


class ResearchAgentV2(AgentBaseV2):
    name = "research"
    description = "Busqueda y sintesis de informacion via Neo4j + Qdrant + Ollama"
    timeout = 60

    async def run(self, task: str, context: dict = None) -> dict:
        self.publish("agent_task_started", task=task[:100])

        # Use Ollama to understand what to search
        query = self.think(f"Extrae SOLO las palabras clave de busqueda de: {task}")
        keywords = query.strip().split()[:5]

        results = []
        for kw in keywords:
            neo = await self.neo4j_query(f"MATCH (n) WHERE n.name CONTAINS '{kw}' RETURN n LIMIT 5")
            if neo.get("success"):
                results.append({"source": "neo4j", "data": neo})

        summary = self.think(
            f"Basado en estos datos del sistema: {str(results)[:500]}\n"
            f"Responde la pregunta: {task}"
        )

        self.publish("agent_task_completed", task=task[:100])
        return self.success(task, result=summary, sources=len(results))
