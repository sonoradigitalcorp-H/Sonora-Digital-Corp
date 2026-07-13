#!/usr/bin/env python3
"""OpenLovable MCP Server — design generation and code export via Lovable [Design].

This server wraps Lovable's capabilities. In production it should call the
Lovable API or use Playwright MCP to drive the Lovable web UI. Until official
API credentials are available, it provides a structured prompt generator and
fallback to Playwright browser automation.
"""

import json
import os

LOVABLE_API_KEY = os.getenv("LOVABLE_API_KEY", "")
LOVABLE_API_URL = os.getenv("LOVABLE_API_URL", "https://api.lovable.dev")

# Tenant-aware design system tokens
TENANT_DESIGN_SYSTEMS = {
    "abe": {
        "brand": "ABE Music Group",
        "colors": {"primary": "#FFD700", "secondary": "#FF3B5C", "background": "#0a0a0f"},
        "font": "Outfit",
        "tone": "premium, artístico, cercano",
        "audience": "artistas y músicos independientes",
    },
    "sonora": {
        "brand": "Sonora Digital Corp",
        "colors": {"primary": "#8b5cf6", "secondary": "#3b82f6", "background": "#0a0a0f"},
        "font": "Outfit",
        "tone": "tecnológico, profesional, innovador",
        "audience": "empresas que quieren adoptar IA",
    },
}


def _get_design_system(tenant: str) -> dict:
    return TENANT_DESIGN_SYSTEMS.get(tenant, TENANT_DESIGN_SYSTEMS["sonora"])


async def openlovable_generate_prompt(tenant: str, page_type: str, description: str) -> str:
    """Generate a structured Lovable prompt for a given tenant and page."""
    ds = _get_design_system(tenant)
    prompt = f"""Create a {page_type} page for {ds['brand']}.

Brand Design System:
- Primary color: {ds['colors']['primary']}
- Secondary/accent color: {ds['colors']['secondary']}
- Background: {ds['colors']['background']}
- Font: {ds['font']}
- Tone: {ds['tone']}
- Target audience: {ds['audience']}

Page requirements:
{description}

Deliverables:
- Responsive Next.js + Tailwind CSS page
- Dark mode by default
- Use the brand colors above
- Include a clear CTA
- Accessible and performant
"""
    return json.dumps({"prompt": prompt, "tenant": tenant, "page_type": page_type})


async def openlovable_create_page(tenant: str, page_type: str, description: str) -> str:
    """Create a page design via Lovable (placeholder for API / Playwright integration)."""
    ds = _get_design_system(tenant)
    if not LOVABLE_API_KEY:
        return json.dumps({
            "status": "placeholder",
            "message": "LOVABLE_API_KEY not configured. Returning structured prompt for manual use or Playwright automation.",
            "tenant": tenant,
            "brand": ds["brand"],
            "page_type": page_type,
            "description": description,
            "next_step": "Set LOVABLE_API_KEY or use playwright_mcp to navigate https://lovable.dev and paste the prompt.",
        })

    # Real API call placeholder
    async with __import__("httpx").AsyncClient() as client:
        resp = await client.post(
            f"{LOVABLE_API_URL}/v1/projects/prompt",
            json={"prompt": (await openlovable_generate_prompt(tenant, page_type, description)),
                  "tenant": tenant},
            headers={"Authorization": f"Bearer {LOVABLE_API_KEY}"},
            timeout=120,
        )
        return json.dumps(resp.json())


async def openlovable_list_components(tenant: str) -> str:
    """List available components for a tenant's design system."""
    ds = _get_design_system(tenant)
    components = {
        "abe": ["Hero3D", "ArtistCard", "RotatingPhrases", "VoiceWidget", "PricingCard", "FOMOSection"],
        "sonora": ["Hero3D", "ServiceCard", "PricingCard", "VoiceWidget", "StatsBar", "CTASection"],
    }
    return json.dumps({
        "tenant": tenant,
        "brand": ds["brand"],
        "components": components.get(tenant, components["sonora"]),
    })


MCP_TOOLS = {
    "openlovable_generate_prompt": {
        "description": "Generate a structured Lovable prompt for a tenant page",
        "input_schema": {
            "type": "object",
            "properties": {
                "tenant": {"type": "string", "description": "Tenant slug (abe or sonora)"},
                "page_type": {"type": "string", "description": "Type of page (landing, pricing, contact, dashboard)"},
                "description": {"type": "string", "description": "Page requirements"},
            },
            "required": ["tenant", "page_type", "description"],
        },
        "handler": lambda args: openlovable_generate_prompt(
            args.get("tenant", "sonora"),
            args["page_type"],
            args["description"],
        ),
    },
    "openlovable_create_page": {
        "description": "Create a page design in Lovable for a tenant",
        "input_schema": {
            "type": "object",
            "properties": {
                "tenant": {"type": "string", "description": "Tenant slug (abe or sonora)"},
                "page_type": {"type": "string", "description": "Type of page"},
                "description": {"type": "string", "description": "Page requirements"},
            },
            "required": ["tenant", "page_type", "description"],
        },
        "handler": lambda args: openlovable_create_page(
            args.get("tenant", "sonora"),
            args["page_type"],
            args["description"],
        ),
    },
    "openlovable_list_components": {
        "description": "List available components for a tenant design system",
        "input_schema": {
            "type": "object",
            "properties": {
                "tenant": {"type": "string", "description": "Tenant slug (abe or sonora)"},
            },
            "required": ["tenant"],
        },
        "handler": lambda args: openlovable_list_components(args.get("tenant", "sonora")),
    },
}
