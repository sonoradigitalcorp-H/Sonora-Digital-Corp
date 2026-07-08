"""Kernel data models — HAS-004"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class HermesContext:
    input: str
    channel: str
    tenant: str = "default"
    user_id: str = ""
    conversation_id: str = ""
    memories: dict[str, list[dict]] = field(default_factory=dict)
    constitution_rules: list[dict] = field(default_factory=list)
    working_memory: list[dict] = field(default_factory=list)
    created_at: str = ""
    memory_router: object | None = None


@dataclass
class KernelTask:
    id: str
    mission: str
    description: str
    agent: str | None = None
    capability: str | None = None
    depends_on: list[str] = field(default_factory=list)
    priority: int = 0
    estimated_cost: float = 0.0
    policies: dict = field(default_factory=dict)


@dataclass
class ExecutionResult:
    task_id: str
    status: str = "pending"
    output: dict = field(default_factory=dict)
    duration_ms: int = 0
    cost: float = 0.0
    model_used: str = ""
    events_emitted: list[str] = field(default_factory=list)
    error: str | None = None
