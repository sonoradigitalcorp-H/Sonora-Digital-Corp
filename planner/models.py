"""Pydantic models for Capability Registry and Decision Engine."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator


class ProviderRef(BaseModel):
    id: str
    contract_type: Literal["mcp", "cli", "sdk", "browser", "http"]
    weight: int = Field(default=1, ge=1)
    enabled: bool = True
    health_url: str | None = None
    rate_limit: int = Field(default=10, ge=0)
    cost_per_call: float = Field(default=0.0, ge=0.0)
    config: dict[str, Any] = {}


class Capability(BaseModel):
    id: str
    name: str
    description: str = ""
    input_schema: dict[str, Any] = {}
    output_schema: dict[str, Any] = {}
    providers: list[ProviderRef] = Field(min_length=1)
    tags: list[str] = []
    timeout_seconds: int = Field(default=30, ge=1)

    @model_validator(mode="after")
    def check_unique_provider_ids(self):
        ids = [p.id for p in self.providers]
        if len(ids) != len(set(ids)):
            raise ValueError(f"Duplicate provider IDs in capability '{self.id}': {ids}")
        return self

    @model_validator(mode="after")
    def check_sequential_weights(self):
        weights = sorted([p.weight for p in self.providers])
        expected = list(range(1, len(weights) + 1))
        if weights != expected:
            raise ValueError(
                f"Provider weights in capability '{self.id}' must be sequential 1,2,3... "
                f"got {weights}"
            )
        return self


class RegistrySchema(BaseModel):
    version: str = "2.0.0"
    capabilities: dict[str, Capability] = {}
    skills: dict[str, Any] = {}


class ProviderHealth(BaseModel):
    provider_id: str
    status: Literal["healthy", "degraded", "down"]
    last_checked: datetime
    latency_ms: float = 0.0
    error: str | None = None


class CapabilityResult(BaseModel):
    capability_id: str
    provider_id: str
    success: bool
    data: dict[str, Any] | None = None
    error: str | None = None
    latency_ms: float = 0.0
    cost_estimate: float = 0.0
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
