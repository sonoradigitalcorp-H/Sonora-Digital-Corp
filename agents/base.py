from abc import ABC, abstractmethod

from agents.types import AgentContext, AgentResult


class HermesAgent(ABC):
    """An agent reasons and delegates. It does not execute directly — that is done by Skills (HAS-005)."""

    agent_id: str = ""
    name: str = ""
    capabilities: list[str] = []
    model: str = "ollama/qwen3:4b-64k"
    status: str = "active"

    @abstractmethod
    async def think(self, context: AgentContext) -> AgentResult:
        """Receive context, reason, return result."""
