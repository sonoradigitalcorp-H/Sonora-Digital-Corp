"""Tenant integration layer — bridges resolver with orchestrator, MCP, and databases.

Usage:
    from core.tenants.integration import TenantIntegration
    ti = TenantIntegration()
    
    # Before processing a request for a tenant:
    ctx = ti.resolve("astrotech")
    system_prompt = ti.build_system_prompt(ctx, user_message="...")
    
    # Before calling an MCP tool:
    if not ti.is_tool_allowed("astrotech", "github_push"):
        raise PermissionError("Tool not allowed for this tenant")
"""

import json
import os
import subprocess
from pathlib import Path
from typing import Optional

from .resolver import TenantResolver, TenantContext, UnknownTenantError


REPO_ROOT = Path(__file__).resolve().parent.parent.parent


class TenantIntegration:
    def __init__(self):
        self.resolver = TenantResolver()

    def resolve(self, tenant_id: str) -> TenantContext:
        return self.resolver.load(tenant_id)

    def build_system_prompt(self, tenant_id: str, user_message: str = "", extra_context: str = "") -> str:
        ctx = self.resolve(tenant_id)
        prompt = ctx.prompt
        if extra_context:
            prompt += f"\n\nContexto adicional: {extra_context}"
        if user_message:
            prompt += f"\n\nMensaje del usuario: {user_message}"
        return prompt

    def is_tool_allowed(self, tenant_id: str, tool_name: str) -> bool:
        ctx = self.resolver.load(tenant_id)
        if ctx.allowed_tools and tool_name not in ctx.allowed_tools:
            return False
        if tool_name in ctx.blocked_tools:
            return False
        return True

    def filter_mcp_servers(self, tenant_id: str, all_servers: list[dict]) -> list[dict]:
        ctx = self.resolver.load(tenant_id)
        allowed_names = {m["name"] for m in ctx.mcp_servers}
        return [s for s in all_servers if s.get("name") in allowed_names]

    def get_allowed_llms(self, tenant_id: str) -> list[str]:
        ctx = self.resolver.load(tenant_id)
        models = []
        if ctx.config.get("default_model"):
            models.append(ctx.config["default_model"])
        if ctx.config.get("fallback_model"):
            models.append(ctx.config["fallback_model"])
        return models

    def list_tenants(self) -> list[dict]:
        tenants = []
        for tid in self.resolver.list_tenants():
            ctx = self.resolver.load(tid)
            tenants.append({
                "id": tid,
                "display_name": ctx.display_name,
                "qdrant_collection": ctx.qdrant_collection,
                "neo4j_database": ctx.neo4j_database,
                "tool_count": len(ctx.allowed_tools),
                "mcp_count": len(ctx.mcp_servers),
            })
        return tenants


def build_orchestrator_config(tenant_id: str, lead_name: str = "", objective: str = "", lead_context: str = "") -> dict:
    """Build orchestrator config dict from tenant context.

    Returns a dict compatible with the Go orchestrator Config struct.
    """
    from core.tenants.integration import TenantIntegration
    ti = TenantIntegration()
    ctx = ti.resolve(tenant_id)

    system_prompt = ctx.prompt
    if objective:
        system_prompt += f"\n\nOBJETIVO: {objective}"
    if lead_context:
        system_prompt += f"\n\nCONTEXTO: {lead_context}"

    return {
        "tenant_id": tenant_id,
        "model": ctx.config.get("default_model", ""),
        "system_prompt": system_prompt,
        "lead_name": lead_name,
        "lead_id": tenant_id,
        "objective": objective,
        "lead_context": lead_context,
        "tone": ctx.branding.get("tone", "professional"),
        "tmp_dir": str(REPO_ROOT / "tmp"),
    }
