"""OrchestratorV2 — Enruta tareas a agentes V2 con Redis + Ollama + HermesClient."""
import logging
from typing import Any

from apps.jarvis.src.core.agents_v2.research_v2 import ResearchAgentV2
from apps.jarvis.src.core.agents_v2.memory_v2 import MemoryAgentV2
from apps.jarvis.src.core.agents_v2.review_v2 import ReviewAgentV2

log = logging.getLogger("jarvis.v2.orchestrator")


class OrchestratorV2:
    """V2 orchestrator that routes tasks to V2 agents."""

    def __init__(self):
        self.agents = {
            "research": ResearchAgentV2(),
            "memory": MemoryAgentV2(),
            "review": ReviewAgentV2(),
        }

    def route(self, task: str) -> str:
        task_lower = task.lower()
        if any(w in task_lower for w in ["recuerda", "guarda", "almacena", "remember", "store", "save", "busca en memoria", "search memory"]):
            return "memory"
        if any(w in task_lower for w in ["revisa", "review", "code review", "valida", "validate"]):
            return "review"
        return "research"

    async def execute(self, task: str, context: dict = None) -> dict[str, Any]:
        agent_name = self.route(task)
        agent = self.agents.get(agent_name)
        if not agent:
            return {"agent": "v2", "task": task, "status": "error", "error": f"No agent for: {task}"}
        log.info(f"V2 Routing: '{task[:60]}' → {agent_name}")
        return await agent.run(task, context)
