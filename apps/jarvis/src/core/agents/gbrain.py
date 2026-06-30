from typing import Any

from src.core.agents.agent_base import (
    AgentBase,
    error_response,
    match_keywords,
)


class GbrainAgent(AgentBase):
    name = "gbrain"
    description = (
        "Cerebro con síntesis, grafo de conocimiento, gap analysis y learning-loop"
    )
    timeout = 60

    async def run(self, task: str, context: dict = None) -> dict[str, Any]:
        self.log.info(f"GBrain task: {task[:100]}")
        from src.core.unified_bridge import GbrainBridge

        bridge = GbrainBridge()
        health = bridge.health()
        if health["status"] != "ok":
            return error_response(self.name, task, "GBrain no disponible")
        if match_keywords(task, ["think", "sintetiza", "sintetizá"]):
            return bridge.think(task)
        if match_keywords(task, ["capture", "guardá", "aprendé", "learn", "learning"]):
            return bridge.capture(task)
        if match_keywords(
            task,
            [
                "learning-loop",
                "learning loop",
                "patrón",
                "patron",
                "anomalía",
                "anomalia",
            ],
        ):
            self.log.info(f"Learning loop triggered via GBrain: {task[:100]}")
            result = bridge.search(task)
            result["methodology"] = "learning-loop"
            return result
        return bridge.search(task)
