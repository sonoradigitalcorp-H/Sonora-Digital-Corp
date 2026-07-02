"""OrchestratorV2 — enruta tareas a los 12 agentes V2."""
import logging
from typing import Any

from apps.jarvis.src.core.agents_v2.research_v2 import ResearchAgentV2
from apps.jarvis.src.core.agents_v2.memory_v2 import MemoryAgentV2
from apps.jarvis.src.core.agents_v2.review_v2 import ReviewAgentV2
from apps.jarvis.src.core.agents_v2.code_v2 import CodeAgentV2
from apps.jarvis.src.core.agents_v2.explore_v2 import ExploreAgentV2
from apps.jarvis.src.core.agents_v2.skill_v2 import SkillAgentV2
from apps.jarvis.src.core.agents_v2.voice_v2 import VoiceAgentV2
from apps.jarvis.src.core.agents_v2.pr_v2 import PRAgentV2
from apps.jarvis.src.core.agents_v2.sales_v2 import SalesAgentV2
from apps.jarvis.src.core.agents_v2.hermes_v2 import HermesAgentV2
from apps.jarvis.src.core.agents_v2.openclaw_v2 import OpenClawAgentV2
from apps.jarvis.src.core.agents_v2.gbrain_v2 import GbrainAgentV2

log = logging.getLogger("jarvis.v2.orchestrator")

ROUTING_RULES = [
    (["recuerda", "guarda", "almacena", "remember", "store", "save", "busca en memoria", "search memory"], "memory"),
    (["revisa", "review", "code review", "valida", "validate"], "review"),
    (["codigo", "code", "genera", "implementa", "fix", "bug"], "code"),
    (["explora", "explore", "list", "directorio", "archivo", "file", "dir", "ls"], "explore"),
    (["skill", "tool", "ejecuta", "run"], "skill"),
    (["voz", "voice", "speak", "habla", "escucha"], "voice"),
    (["pr", "pull request", "github"], "pr"),
    (["venta", "sale", "lead", "cliente", "propuesta"], "sales"),
    (["hermes", "telegram", "whatsapp"], "hermes"),
    (["openclaw"], "openclaw"),
    (["gbrain", "graph", "grafo", "sintetiza", "synthesize"], "gbrain"),
]


class OrchestratorV2:
    def __init__(self):
        self.agents = {
            "research": ResearchAgentV2(),
            "memory": MemoryAgentV2(),
            "review": ReviewAgentV2(),
            "code": CodeAgentV2(),
            "explore": ExploreAgentV2(),
            "skill": SkillAgentV2(),
            "voice": VoiceAgentV2(),
            "pr": PRAgentV2(),
            "sales": SalesAgentV2(),
            "hermes": HermesAgentV2(),
            "openclaw": OpenClawAgentV2(),
            "gbrain": GbrainAgentV2(),
        }

    def route(self, task: str) -> str:
        task_lower = task.lower()
        for keywords, agent_name in ROUTING_RULES:
            if any(kw in task_lower for kw in keywords):
                return agent_name
        return "research"

    async def execute(self, task: str, context: dict = None) -> dict[str, Any]:
        agent_name = self.route(task)
        agent = self.agents.get(agent_name)
        if not agent:
            return {"agent": "v2", "task": task, "status": "error", "error": f"No agent for: {task}"}
        log.info(f"V2 Routing: '{task[:60]}' → {agent_name}")
        return await agent.run(task, context)
