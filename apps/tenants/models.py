"""Tenant data models — Tenant, EnvVar, Agent, HealthCheck."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


def _now():
    return datetime.now(timezone.utc).isoformat()


class TenantPlan(str, Enum):
    TRIAL = "trial"
    SMALL = "small"
    MEDIUM = "medium"
    ENTERPRISE = "enterprise"


class TenantStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    TRIAL = "trial"


class AgentType(str, Enum):
    VOICE = "voice"
    CRM = "crm"
    SUPPORT = "support"
    SALES = "sales"
    CONTENT = "content"


class HealthStatus(str, Enum):
    OK = "ok"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class Tenant:
    id: str
    name: str
    email: str
    plan: TenantPlan = TenantPlan.TRIAL
    status: TenantStatus = TenantStatus.TRIAL
    created_at: str = field(default_factory=_now)
    last_active: str = field(default_factory=_now)
    api_key: str = ""
    webhook_token: str = ""


@dataclass
class EnvVar:
    id: str
    tenant_id: str
    key: str
    value: str
    is_secret: bool = True


@dataclass
class Agent:
    id: str
    tenant_id: str
    agent_type: AgentType = AgentType.VOICE
    status: TenantStatus = TenantStatus.ACTIVE
    config: dict = field(default_factory=dict)
    clients_count: int = 0
    hours_worked: float = 0.0
    clients_helped: int = 0


@dataclass
class HealthCheck:
    id: str
    tenant_id: str
    timestamp: str = field(default_factory=_now)
    status: HealthStatus = HealthStatus.OK
    message: str = ""
    metrics: dict = field(default_factory=dict)
