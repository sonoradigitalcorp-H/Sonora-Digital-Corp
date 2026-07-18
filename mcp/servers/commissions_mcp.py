"""Commissions MCP Server — Enterprise deal tracking tools for partners.

FR: Track wholesale deals, partner markups, projections.
"""

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO))

from scripts.commissions import add_deal, add_partner, get_all_partners, get_partner_summary, get_projection


async def register_partner(partner_id: str, name: str, contact: str = "") -> str:
    return add_partner(partner_id, name, contact)


async def register_deal(
    partner_id: str, client_name: str, plan_id: str,
    wholesale_setup: float, wholesale_monthly: float,
    resell_setup: float, resell_monthly: float,
    powered_by: str = "hidden",
) -> str:
    return add_deal(partner_id, client_name, plan_id,
                    wholesale_setup, wholesale_monthly,
                    resell_setup, resell_monthly, powered_by)


async def partner_summary(partner_id: str) -> str:
    return get_partner_summary(partner_id)


async def list_partners() -> str:
    return get_all_partners()


async def partner_projection(partner_id: str, months: int = 12) -> str:
    return get_projection(partner_id, months)


MCP_TOOLS = {
    "register_partner": {
        "description": "Register a new enterprise partner (ej: AztroTech)",
        "input_schema": {
            "type": "object",
            "properties": {
                "partner_id": {"type": "string", "description": "Partner ID (aztrotech)"},
                "name": {"type": "string", "description": "Partner full name or company"},
                "contact": {"type": "string", "description": "Contact info (optional)"},
            },
            "required": ["partner_id", "name"],
        },
        "handler": lambda args: register_partner(args["partner_id"], args["name"], args.get("contact", "")),
    },
    "register_deal": {
        "description": "Register a new enterprise deal for a partner",
        "input_schema": {
            "type": "object",
            "properties": {
                "partner_id": {"type": "string", "description": "Partner ID"},
                "client_name": {"type": "string", "description": "Client company name"},
                "plan_id": {"type": "string", "enum": ["starter", "business", "premium"], "description": "Enterprise plan"},
                "wholesale_setup": {"type": "number", "description": "Wholesale setup fee (SDC charges partner)"},
                "wholesale_monthly": {"type": "number", "description": "Wholesale monthly fee"},
                "resell_setup": {"type": "number", "description": "What partner charges client for setup"},
                "resell_monthly": {"type": "number", "description": "What partner charges client monthly"},
                "powered_by": {"type": "string", "enum": ["hidden", "footer_only", "public_mentions", "full_branding"], "description": "Powered by visibility"},
            },
            "required": ["partner_id", "client_name", "plan_id", "wholesale_setup", "wholesale_monthly", "resell_setup", "resell_monthly"],
        },
        "handler": lambda args: register_deal(
            args["partner_id"], args["client_name"], args["plan_id"],
            args["wholesale_setup"], args["wholesale_monthly"],
            args["resell_setup"], args["resell_monthly"],
            args.get("powered_by", "hidden"),
        ),
    },
    "partner_summary": {
        "description": "Get summary of a partner's active deals and commissions",
        "input_schema": {
            "type": "object",
            "properties": {
                "partner_id": {"type": "string", "description": "Partner ID"},
            },
            "required": ["partner_id"],
        },
        "handler": lambda args: partner_summary(args["partner_id"]),
    },
    "list_partners": {
        "description": "List all registered enterprise partners",
        "input_schema": {"type": "object", "properties": {}},
        "handler": lambda _: list_partners(),
    },
    "partner_projection": {
        "description": "Get revenue projection for a partner over N months",
        "input_schema": {
            "type": "object",
            "properties": {
                "partner_id": {"type": "string", "description": "Partner ID"},
                "months": {"type": "number", "description": "Projection months (default 12)"},
            },
            "required": ["partner_id"],
        },
        "handler": lambda args: partner_projection(args["partner_id"], args.get("months", 12)),
    },
}
