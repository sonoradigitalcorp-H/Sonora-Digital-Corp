from dataclasses import dataclass, field
from typing import Any


@dataclass
class TenantConfig:
    id: str
    name: str
    isolation: str = "column"
    capabilities: list[str] = field(default_factory=lambda: ["*"])
    constitution_overrides: dict = field(default_factory=dict)
    budget: float = 100.0
    settings: dict = field(default_factory=dict)

    @classmethod
    def default(cls) -> "TenantConfig":
        return cls(
            id="abe-music",
            name="ABE Music OS",
            isolation="column",
            capabilities=["*"],
            budget=500.0,
            settings={"region": "us-east", "timezone": "America/Mexico_City"},
        )


@dataclass
class Tenant:
    config: TenantConfig
    active: bool = True
    warnings: list[str] = field(default_factory=list)
