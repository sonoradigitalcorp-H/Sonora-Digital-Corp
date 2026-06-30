from typing import Any

from src.core.agents.agent_base import AgentBase, success_response


class HermesAgent(AgentBase):
    name = "hermes"
    description = "Comunicación por Telegram, WhatsApp y automatización n8n"
    timeout = 30

    async def run(self, task: str, context: dict = None) -> dict[str, Any]:
        self.log.info(f"Hermes task: {task[:100]}")
        from src.core.unified_bridge import HermesBridge

        bridge = HermesBridge()
        health = bridge.health()
        return success_response(self.name, task, hermes_health=health)
