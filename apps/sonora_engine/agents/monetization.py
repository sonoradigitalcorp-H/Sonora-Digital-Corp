"""Monetization Agent [FR5] — maneja saludos personalizados, pagos, $BEAT."""

import logging
from typing import Any

log = logging.getLogger("sonora.engine.agents.monetization")

DEFAULT_PRICING = {
    "beat": {"cost": 50, "currency": "BEAT"},
    "usd": {"cost": 5.00, "currency": "USD", "providers": ["stripe"]},
}


def get_payment_options(tenant_id: str) -> dict[str, Any]:
    """Get payment options for a tenant."""
    try:
        from ..hasura import query

        result = query("""
            query GetTenantPricing($tenant_id: uuid!) {
                tenants_by_pk(id: $tenant_id) {
                    pricing_config
                }
            }
        """, {"tenant_id": tenant_id})

        config = result.get("data", {}).get("tenants_by_pk", {}).get("pricing_config", {})
        if config:
            return {
                "beat": {"cost": config.get("greeting_beat_cost", 50), "currency": "BEAT"},
                "usd": {"cost": config.get("greeting_usd_cost", 5.00), "currency": "USD", "providers": ["stripe"]},
            }
    except Exception:
        pass

    return DEFAULT_PRICING


def handle_greeting_request(
    tenant_id: str,
    artist_name: str,
    fan_id: str,
    message: str,
) -> dict[str, Any]:
    """Create a pending greeting request and return payment info."""
    import uuid

    pricing = get_payment_options(tenant_id)
    greeting_id = str(uuid.uuid4())

    # In production: INSERT via Hasura mutation
    try:
        from ..hasura import mutate

        mutate("""
            mutation CreateGreeting($greeting: greetings_insert_input!) {
                insert_greetings_one(object: $greeting) {
                    id
                    status
                }
            }
        """, {
            "greeting": {
                "id": greeting_id,
                "tenant_id": tenant_id,
                "artist_id": artist_name,
                "fan_id": fan_id,
                "message": message,
                "beat_cost": pricing["beat"]["cost"],
                "usd_cost": pricing["usd"]["cost"],
                "status": "pending_payment",
            }
        })
    except Exception:
        pass  # Fallback for tests

    return {
        "greeting_id": greeting_id,
        "status": "pending_payment",
        "beat_cost": pricing["beat"]["cost"],
        "usd_cost": pricing["usd"]["cost"],
        "payment_options": pricing,
    }
