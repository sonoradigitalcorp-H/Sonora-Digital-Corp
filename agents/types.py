from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentContext:
    mission: str
    tenant: str = "default"
    user_id: str = ""
    conversation_id: str = ""
    memories: dict[str, Any] = field(default_factory=dict)
    capabilities: list[str] = field(default_factory=list)
    constitution: list[dict] = field(default_factory=list)
    working_memory: list[dict] = field(default_factory=list)


@dataclass
class AgentResult:
    status: str = "success"
    output: Any = None
    reasoning: str = ""
    events_emitted: list[str] = field(default_factory=list)
    score: int = 90
    lessons: list[str] = field(default_factory=list)
    capabilities_used: list[str] = field(default_factory=list)
