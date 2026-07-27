"""Planner — Module 2 of Kernel (HAS-004)
Decomposes a mission into discrete tasks. Supports 4 strategies:
Direct, Delegation, Research, Emergency.
"""
from datetime import datetime
from uuid import uuid4

from kernel.models import HermesContext, KernelTask


class Planner:
    STRATEGY_DIRECT = "direct"
    STRATEGY_DELEGATION = "delegation"
    STRATEGY_RESEARCH = "research"
    STRATEGY_EMERGENCY = "emergency"

    def __init__(self):
        self._patterns: dict[str, str] = {
            "sync": self.STRATEGY_DIRECT,
            "analyze": self.STRATEGY_DELEGATION,
            "search": self.STRATEGY_DIRECT,
            "publish": self.STRATEGY_DELEGATION,
            "generate": self.STRATEGY_DELEGATION,
            "score": self.STRATEGY_DELEGATION,
        }
        self._capability_map: dict[str, str] = {
            "sync": "sync-artist-data",
            "analyze": "analyze-artist",
            "search": "search-knowledge",
            "publish": "publish-track",
            "generate": "generate-video",
            "score": "score-artist",
        }

    async def plan(self, ctx: HermesContext) -> list[KernelTask]:
        strategy = self._detect_strategy(ctx.input)
        if strategy == self.STRATEGY_EMERGENCY:
            return [self._make_task(ctx, "execute immediate action", priority=2)]
        if strategy == self.STRATEGY_RESEARCH:
            return [self._make_task(ctx, "research: " + ctx.input, agent="researcher")]
        if strategy == self.STRATEGY_DIRECT:
            return [self._direct_task(ctx)]
        return [self._delegation_task(ctx)]

    def _detect_strategy(self, user_input: str) -> str:
        lowered = user_input.lower()
        if any(kw in lowered for kw in ["emergency", "urgent", "critical", "fix now"]):
            return self.STRATEGY_EMERGENCY
        if any(kw in lowered for kw in ["research", "investigate", "find out", "explore"]):
            return self.STRATEGY_RESEARCH
        for keyword, strategy in self._patterns.items():
            if keyword in lowered:
                return strategy
        return self.STRATEGY_DELEGATION

    def _direct_task(self, ctx: HermesContext) -> KernelTask:
        lowered = ctx.input.lower()
        capability = None
        for keyword, cap in self._capability_map.items():
            if keyword in lowered:
                capability = cap
                break
        return KernelTask(
            id=self._new_id(),
            mission=ctx.input[:200],
            description=f"Execute: {ctx.input[:200]}",
            capability=capability,
            priority=0,
        )

    def _delegation_task(self, ctx: HermesContext) -> KernelTask:
        return KernelTask(
            id=self._new_id(),
            mission=ctx.input[:200],
            description=f"Delegate: {ctx.input[:200]}",
            priority=0,
        )

    def _make_task(self, ctx: HermesContext, description: str, agent: str | None = None, priority: int = 0) -> KernelTask:
        return KernelTask(
            id=self._new_id(),
            mission=ctx.input[:200],
            description=description,
            agent=agent,
            priority=priority,
        )

    @staticmethod
    def _new_id() -> str:
        return f"task_{uuid4().hex[:12]}"
