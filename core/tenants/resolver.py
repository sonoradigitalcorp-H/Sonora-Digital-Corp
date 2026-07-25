"""TenantContext resolver — loads tenant configuration from tenants/<id>/ directory.

Usage:
    resolver = TenantResolver()
    ctx = resolver.load("sonora-digital")
    print(ctx.prompt)
    print(ctx.allowed_tools)
    print(ctx.mcp_servers)
"""

import os
import yaml
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
TENANTS_DIR = REPO_ROOT / "tenants"


class UnknownTenantError(KeyError):
    pass


@dataclass
class TenantContext:
    tenant_id: str
    display_name: str = ""
    prompt: str = ""
    allowed_tools: list = field(default_factory=list)
    blocked_tools: list = field(default_factory=list)
    mcp_servers: list = field(default_factory=list)
    policies: dict = field(default_factory=dict)
    config: dict = field(default_factory=dict)
    branding: dict = field(default_factory=dict)
    qdrant_collection: str = ""
    neo4j_database: str = ""


class TenantResolver:
    def __init__(self, tenants_dir: Optional[Path] = None):
        self.tenants_dir = Path(tenants_dir) if tenants_dir else TENANTS_DIR
        self._cache: dict[str, TenantContext] = {}

    def list_tenants(self) -> list[str]:
        if not self.tenants_dir.exists():
            return []
        return [
            d.name for d in self.tenants_dir.iterdir()
            if d.is_dir() and not d.name.startswith("_")
        ]

    def load(self, tenant_id: str, use_cache: bool = True) -> TenantContext:
        if use_cache and tenant_id in self._cache:
            return self._cache[tenant_id]

        tenant_dir = self.tenants_dir / tenant_id
        if not tenant_dir.is_dir():
            raise UnknownTenantError(f"Tenant '{tenant_id}' not found in {self.tenants_dir}")

        ctx = TenantContext(tenant_id=tenant_id)

        ctx.prompt = self._read_file(tenant_dir / "prompt.md")

        tools = self._read_yaml(tenant_dir / "tools.yaml")
        if tools:
            ctx.allowed_tools = tools.get("allowed_tools", [])
            ctx.blocked_tools = tools.get("blocked_tools", [])

        mcp = self._read_yaml(tenant_dir / "mcp.yaml")
        if mcp:
            ctx.mcp_servers = mcp.get("mcp_servers", [])

        policies = self._read_yaml(tenant_dir / "policies.yaml")
        if policies:
            ctx.policies = policies

        config = self._read_yaml(tenant_dir / "config.yaml")
        if config:
            ctx.config = config
            ctx.display_name = config.get("display_name", tenant_id)
            ctx.qdrant_collection = config.get("qdrant_collection", f"tenant_{tenant_id}_memory")
            ctx.neo4j_database = config.get("neo4j_database", tenant_id)

        branding = self._read_json(tenant_dir / "branding" / "branding.json")
        if branding:
            ctx.branding = branding

        self._cache[tenant_id] = ctx
        return ctx

    def invalidate(self, tenant_id: str):
        self._cache.pop(tenant_id, None)

    def _read_file(self, path: Path) -> str:
        if path.is_file():
            return path.read_text(encoding="utf-8")
        return ""

    def _read_yaml(self, path: Path) -> Optional[dict]:
        if path.is_file():
            with open(path) as f:
                return yaml.safe_load(f)
        return None

    def _read_json(self, path: Path) -> Optional[dict]:
        if path.is_file():
            import json
            with open(path) as f:
                return json.load(f)
        return None
