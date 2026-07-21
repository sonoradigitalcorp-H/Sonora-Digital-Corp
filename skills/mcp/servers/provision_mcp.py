"""Provision MCP Server — Create and manage multi-tenant brains.

FR-07: Provisioning automático de tenants en <5 segundos.
FR-02: Aislamiento de memoria por tenant.
FR-03: Partner branding white-label.
"""

from scripts.provision_tenant import get_stats, list_tenants, provision


async def create_tenant(partner_id: str, client_name: str, plan: str = "pro") -> str:
    return await provision(partner_id, client_name, plan)


async def list_tenant(partner_id: str = "") -> str:
    return await list_tenants(partner_id)


async def stats() -> str:
    return await get_stats()


MCP_TOOLS = {
    "create_tenant": {
        "description": "Create a new digital brain tenant for a client under a partner",
        "input_schema": {
            "type": "object",
            "properties": {
                "partner_id": {"type": "string", "description": "Partner ID (aztrotech, abe_music)"},
                "client_name": {"type": "string", "description": "Client name"},
                "plan": {"type": "string", "enum": ["basic", "pro", "enterprise"], "description": "Plan type"},
            },
            "required": ["partner_id", "client_name"],
        },
        "handler": lambda args: create_tenant(args["partner_id"], args["client_name"], args.get("plan", "pro")),
    },
    "list_tenants": {
        "description": "List tenants, optionally filtered by partner",
        "input_schema": {
            "type": "object",
            "properties": {
                "partner_id": {"type": "string", "description": "Filter by partner ID (optional)"},
            },
            "required": [],
        },
        "handler": lambda args: list_tenant(args.get("partner_id", "")),
    },
    "tenant_stats": {
        "description": "Get provisioning statistics across all tenants",
        "input_schema": {"type": "object", "properties": {}},
        "handler": lambda _: stats(),
    },
}
