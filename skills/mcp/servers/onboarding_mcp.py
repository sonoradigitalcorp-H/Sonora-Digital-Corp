"""Onboarding MCP Server — Códigos de activación + routing + flow.

FR-01/FR-02: Generación y validación de códigos únicos.
FR-03: Routing por número de teléfono.
FR-04: Onboarding flow de 5 pasos.
"""

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO))

from scripts.onboarding import detect_tenant, generate, get_flow_step, get_skills, list_codes, validate


async def generate_code(partner_id: str, client_name: str, plan: str = "pro") -> str:
    return generate(partner_id, client_name, plan)


async def validate_code(code: str, phone: str = "") -> str:
    return validate(code, phone)


async def detect(phone: str) -> str:
    return detect_tenant(phone)


async def list_codes_mcp(partner_id: str = "") -> str:
    return list_codes(partner_id)


async def flow_step(step: int, client_name: str = "", partner_name: str = "") -> str:
    return get_flow_step(step, client_name, partner_name)


async def skills_for_type(tenant_type: str = "cliente") -> str:
    return get_skills(tenant_type)


MCP_TOOLS = {
    "onboarding_generate": {
        "description": "Generate a unique onboarding code (SDC-XXXXXX) for a new client",
        "input_schema": {
            "type": "object",
            "properties": {
                "partner_id": {"type": "string", "description": "Partner ID (aztrotech, abe_music)"},
                "client_name": {"type": "string", "description": "Client full name"},
                "plan": {"type": "string", "enum": ["basic", "pro", "enterprise"], "description": "Plan type"},
            },
            "required": ["partner_id", "client_name"],
        },
        "handler": lambda args: generate_code(args["partner_id"], args["client_name"], args.get("plan", "pro")),
    },
    "onboarding_validate": {
        "description": "Validate an onboarding code and activate the client's tenant",
        "input_schema": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Onboarding code (SDC-XXXXXX)"},
                "phone": {"type": "string", "description": "Client phone number (optional for status check)"},
            },
            "required": ["code"],
        },
        "handler": lambda args: validate_code(args["code"], args.get("phone", "")),
    },
    "onboarding_detect": {
        "description": "Detect a client's tenant by their phone number",
        "input_schema": {
            "type": "object",
            "properties": {
                "phone": {"type": "string", "description": "Phone number to look up"},
            },
            "required": ["phone"],
        },
        "handler": lambda args: detect(args["phone"]),
    },
    "onboarding_flow_step": {
        "description": "Get the onboarding flow message for a specific step",
        "input_schema": {
            "type": "object",
            "properties": {
                "step": {"type": "number", "description": "Step number (1-5)"},
                "client_name": {"type": "string", "description": "Client name for personalization"},
                "partner_name": {"type": "string", "description": "Partner name for personalization"},
            },
            "required": ["step"],
        },
        "handler": lambda args: flow_step(args["step"], args.get("client_name", ""), args.get("partner_name", "")),
    },
    "onboarding_skills": {
        "description": "Get agentic skills configuration for a tenant type",
        "input_schema": {
            "type": "object",
            "properties": {
                "tenant_type": {"type": "string", "enum": ["cliente", "partner", "admin"], "description": "Tenant type"},
            },
            "required": [],
        },
        "handler": lambda args: skills_for_type(args.get("tenant_type", "cliente")),
    },
    "onboarding_list_codes": {
        "description": "List onboarding codes, optionally filtered by partner",
        "input_schema": {
            "type": "object",
            "properties": {
                "partner_id": {"type": "string", "description": "Filter by partner ID"},
            },
            "required": [],
        },
        "handler": lambda args: list_codes_mcp(args.get("partner_id", "")),
    },
}
