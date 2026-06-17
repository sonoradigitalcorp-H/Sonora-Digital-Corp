import logging
from typing import Any, Dict, List, Optional

from src.core.agents.agent_base import (
    AgentBase,
    match_keywords,
    success_response,
    error_response,
)


class ResearchAgent(AgentBase):
    name = "research"
    description = "Búsqueda y síntesis de información"
    timeout = 60

    async def run(self, task: str, context: dict = None) -> Dict[str, Any]:
        self.log.info(f"Researching: {task[:100]}...")
        results = {
            "agent": self.name,
            "query": task,
            "sources": [],
            "synthesis": "",
            "confidence": 0.0,
        }
        try:
            from src.core.rag import rag

            semantic = rag.search(task, limit=3)
            if semantic["status"] == "success" and semantic["results"]:
                results["sources"].append(
                    {
                        "type": "vector",
                        "data": [
                            {"text": r["text"], "score": r["score"]}
                            for r in semantic["results"]
                        ],
                    }
                )
            from src.core.neo4j_store import search_sessions

            graph_results = search_sessions(task)
            if graph_results:
                results["sources"].append({"type": "graph", "data": graph_results})
            results["synthesis"] = self._synthesize(results["sources"])
            results["confidence"] = self._calc_confidence(results["sources"])
        except Exception as e:
            self.log.error(f"Research error: {e}")
            results["error"] = str(e)
        return results

    def _synthesize(self, sources: List) -> str:
        texts = []
        for src in sources:
            for item in src.get("data", [])[:2]:
                if isinstance(item, dict):
                    texts.append(str(item.get("text", ""))[:300])
        return "\n".join(filter(None, texts))[:2000]

    def _calc_confidence(self, sources: List) -> float:
        if not sources:
            return 0.0
        valid = sum(1 for s in sources if s.get("data"))
        return round(valid / len(sources), 2)
