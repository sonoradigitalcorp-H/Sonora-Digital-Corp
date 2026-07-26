"""Pricing MCP Server — Dynamic pricing tools for the multi-tenant brain platform.

FR-04: Calculate price based on industry, size, volume, partner.
FR-05: Calculate price based on real cost data + target margin.
"""

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO))

from scripts.pricing_engine import calculate_from_cost, calculate_price, list_industries


async def get_price(
    industry: str = "tecnologia",
    size: str = "small",
    volume_multiplier: float = 1.0,
    partner: str = "",
    estimated_revenue: float = 0,
) -> str:
    result = calculate_price(industry, size, volume_multiplier, partner, estimated_revenue)
    return json.dumps(result)


async def get_price_from_cost(
    estimated_monthly_cost: float,
    industry: str = "tecnologia",
    partner: str = "",
    target_margin: float = 0.80,
) -> str:
    result = calculate_from_cost(estimated_monthly_cost, industry, partner, target_margin)
    return json.dumps(result)


async def get_industries() -> str:
    return list_industries()


MCP_TOOLS = {
    "get_price": {
        "description": "Calculate dynamic price for a client based on industry, size, and volume",
        "input_schema": {
            "type": "object",
            "properties": {
                "industry": {"type": "string", "enum": ["musica", "tecnologia", "marketing", "legal", "salud"], "description": "Industry segment"},
                "size": {"type": "string", "enum": ["small", "medium", "enterprise"], "description": "Client size"},
                "volume_multiplier": {"type": "number", "description": "Volume multiplier (default 1.0)"},
                "partner": {"type": "string", "description": "Partner ID for discount (aztrotech, abe_music)"},
                "estimated_revenue": {"type": "number", "description": "Estimated monthly client revenue for rev share calc"},
            },
            "required": ["industry"],
        },
        "handler": lambda args: get_price(
            args["industry"],
            args.get("size", "small"),
            args.get("volume_multiplier", 1.0),
            args.get("partner", ""),
            args.get("estimated_revenue", 0),
        ),
    },
    "get_price_from_cost": {
        "description": "Calculate price based on real cost data + target margin",
        "input_schema": {
            "type": "object",
            "properties": {
                "estimated_monthly_cost": {"type": "number", "description": "Real monthly cost in USD"},
                "industry": {"type": "string", "description": "Industry segment"},
                "partner": {"type": "string", "description": "Partner ID for discount"},
                "target_margin": {"type": "number", "description": "Target margin (0-1, default 0.80)"},
            },
            "required": ["estimated_monthly_cost"],
        },
        "handler": lambda args: get_price_from_cost(
            args["estimated_monthly_cost"],
            args.get("industry", "tecnologia"),
            args.get("partner", ""),
            args.get("target_margin", 0.80),
        ),
    },
    "get_industries": {
        "description": "List available industry segments with pricing ranges",
        "input_schema": {"type": "object", "properties": {}},
        "handler": lambda _: get_industries(),
    },
}
