"""Payments MCP Server — Stripe Checkout + Webhook.

Exposes payment processing as native MCP tools for agents.
"""

import json
import os

import httpx

STRIPE_API_KEY = os.getenv("STRIPE_API_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
HASURA_URL = os.getenv("HASURA_URL", "http://localhost:8082/v1/graphql")
HASURA_ADMIN_SECRET = os.getenv("HASURA_ADMIN_SECRET", "sonora-admin-secret")

STRIPE_API_BASE = "https://api.stripe.com/v1"


async def _stripe_post(path: str, data: dict) -> str:
    if not STRIPE_API_KEY:
        return json.dumps({"error": "Stripe not configured — no API key"})
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{STRIPE_API_BASE}{path}",
            data=data,
            headers={"Authorization": f"Bearer {STRIPE_API_KEY}"},
            timeout=30,
        )
        return json.dumps(resp.json())


async def create_checkout_session(price_id: str, success_url: str, cancel_url: str, customer_email: str | None = None, metadata: dict | None = None) -> str:
    data = {
        "mode": "payment",
        "line_items[0][price]": price_id,
        "line_items[0][quantity]": 1,
        "success_url": success_url,
        "cancel_url": cancel_url,
    }
    if customer_email:
        data["customer_email"] = customer_email
    if metadata:
        for k, v in (metadata or {}).items():
            data[f"metadata[{k}]"] = v
    return await _stripe_post("/checkout/sessions", data)


async def create_payment_intent(amount_cents: int, currency: str = "usd", description: str = "", metadata: dict | None = None) -> str:
    data = {
        "amount": str(amount_cents),
        "currency": currency,
        "description": description,
    }
    if metadata:
        for k, v in (metadata or {}).items():
            data[f"metadata[{k}]"] = v
    return await _stripe_post("/payment_intents", data)


async def create_product(name: str, description: str, unit_amount_cents: int, currency: str = "usd") -> str:
    prod = await _stripe_post("/products", {"name": name, "description": description})
    prod_data = json.loads(prod)
    if "error" in prod_data:
        return prod
    price = await _stripe_post("/prices", {
        "product": prod_data["id"],
        "unit_amount": str(unit_amount_cents),
        "currency": currency,
    })
    return price


async def list_products() -> str:
    result = await _stripe_post("/products", {})
    data = json.loads(result)
    if "error" not in data and "data" in data:
        prices = await _stripe_post("/prices", {})
        prices_data = json.loads(prices)
        price_map = {}
        if "error" not in prices_data and "data" in prices_data:
            for p in prices_data["data"]:
                price_map[p["product"]] = p
        for prod in data["data"]:
            if prod["id"] in price_map:
                prod["price"] = price_map[prod["id"]]
    return json.dumps(data)


async def handle_webhook(payload: str, sig_header: str) -> str:
    if not STRIPE_WEBHOOK_SECRET:
        return json.dumps({"error": "Webhook secret not configured"})
    try:
        import hashlib
        import hmac
        parts = sig_header.split(",")
        sig = None
        for p in parts:
            if p.startswith("v1="):
                sig = p[3:]
        if not sig:
            return json.dumps({"error": "No signature found"})
        expected = hmac.new(STRIPE_WEBHOOK_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, sig):
            return json.dumps({"error": "Invalid signature"})
        event = json.loads(payload)
        event_type = event.get("type", "")
        if event_type == "checkout.session.completed":
            session = event["data"]["object"]
            async with httpx.AsyncClient() as client:
                await client.post(HASURA_URL, json={
                    "query": """
                        mutation ($session_id: String!, $amount: numeric!, $customer: String!, $metadata: jsonb) {
                            insert_transactions_one(object: {
                                provider_transaction_id: $session_id,
                                amount: $amount,
                                description: $customer,
                                metadata: $metadata,
                                status: "completed",
                                provider: "stripe"
                            }) { id }
                        }
                    """,
                    "variables": {
                        "session_id": session["id"],
                        "amount": session["amount_total"] / 100 if session.get("amount_total") else 0,
                        "customer": session.get("customer_details", {}).get("email", ""),
                        "metadata": session.get("metadata", {}),
                    }
                }, headers={"x-hasura-admin-secret": HASURA_ADMIN_SECRET}, timeout=10)
        return json.dumps({"received": True, "type": event_type})
    except Exception as e:
        return json.dumps({"error": str(e)})


MCP_TOOLS = {
    "stripe_create_checkout": {
        "description": "Create a Stripe Checkout session for payment",
        "input_schema": {
            "type": "object",
            "properties": {
                "price_id": {"type": "string", "description": "Stripe Price ID"},
                "success_url": {"type": "string", "description": "Redirect URL on success"},
                "cancel_url": {"type": "string", "description": "Redirect URL on cancel"},
                "customer_email": {"type": "string", "description": "Customer email (optional)"},
                "metadata": {"type": "object", "description": "Metadata key-value pairs"},
            },
            "required": ["price_id", "success_url", "cancel_url"],
        },
        "handler": lambda args: create_checkout_session(
            args["price_id"], args["success_url"], args["cancel_url"],
            args.get("customer_email"), args.get("metadata"),
        ),
    },
    "stripe_create_payment": {
        "description": "Create a direct PaymentIntent",
        "input_schema": {
            "type": "object",
            "properties": {
                "amount_cents": {"type": "integer", "description": "Amount in cents"},
                "currency": {"type": "string", "description": "Currency code (default: usd)"},
                "description": {"type": "string", "description": "Payment description"},
                "metadata": {"type": "object", "description": "Metadata key-value pairs"},
            },
            "required": ["amount_cents"],
        },
        "handler": lambda args: create_payment_intent(
            args["amount_cents"], args.get("currency", "usd"),
            args.get("description", ""), args.get("metadata"),
        ),
    },
    "stripe_create_product": {
        "description": "Create a Stripe product with a price",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Product name"},
                "description": {"type": "string", "description": "Product description"},
                "unit_amount_cents": {"type": "integer", "description": "Price in cents"},
                "currency": {"type": "string", "description": "Currency code"},
            },
            "required": ["name", "description", "unit_amount_cents"],
        },
        "handler": lambda args: create_product(
            args["name"], args["description"], args["unit_amount_cents"], args.get("currency", "usd"),
        ),
    },
    "stripe_list_products": {
        "description": "List all Stripe products with their prices",
        "input_schema": {"type": "object", "properties": {}},
        "handler": lambda _: list_products(),
    },
}
