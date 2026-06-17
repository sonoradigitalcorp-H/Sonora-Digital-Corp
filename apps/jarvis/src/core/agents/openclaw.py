from typing import Any, Dict

from src.core.agents.agent_base import AgentBase, success_response


class OpenClawAgent(AgentBase):
    name = "openclaw"
    description = "Agentes especializados vía OpenClaw gateway"
    timeout = 60

    async def run(self, task: str, context: dict = None) -> Dict[str, Any]:
        self.log.info(f"OpenClaw task: {task[:100]}")
        from src.core.unified_bridge import OpenClawBridge

        bridge = OpenClawBridge()
        health = bridge.health()
        agents = bridge.list_agents()
        return success_response(
            self.name, task, openclaw_health=health, available_agents=agents
        )
