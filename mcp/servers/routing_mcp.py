"""Routing MCP Server — Detección de tenant por número de teléfono.

FR-03: Routing automático para OpenClaw.
Identifica quién es cada cliente por su número y carga su contexto.
"""

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO))

from scripts.onboarding import detect_tenant


async def resolve(phone: str) -> str:
    return detect_tenant(phone)


MCP_TOOLS = {
    "resolve_tenant": {
        "description": "Resolve a phone number to a tenant. Used by OpenClaw for automatic routing.",
        "input_schema": {
            "type": "object",
            "properties": {
                "phone": {"type": "string", "description": "Phone number (with country code, e.g. +5216623538272)"},
            },
            "required": ["phone"],
        },
        "handler": lambda args: resolve(args["phone"]),
    },
}
