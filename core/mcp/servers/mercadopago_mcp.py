"""MercadoPago MCP Server — Payment processing via MercadoPago.

Checkout preferences, payment queries, and webhook handling.
"""

import json
import os

import httpx

MP_TOKEN = os.getenv("MERCADO_PAGO_ACCESS_TOKEN", "")
MP_API = "https://api.mercadopago.com"
HASURA_URL = os.getenv("HASURA_URL", "http://localhost:8082/v1/graphql")
HASURA_ADMIN_SECRET = os.getenv("HASURA_ADMIN_SECRET", "sonora-admin")


async def _mp_post(path: str, data: dict) -> str:
    if not MP_TOKEN:
        return json.dumps({"error": "MercadoPago not configured — no Access Token"})
    if MP_TOKEN.startswith("TEST-"):
        mp_base = "https://api.mercadopago.com"
    else:
        mp_base = "https://api.mercadopago.com"
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{mp_base}{path}",
            json=data,
            headers={"Authorization": f"Bearer {MP_TOKEN}", "Content-Type": "application/json"},
            timeout=30,
        )
        return json.dumps(resp.json())


async def _mp_get(path: str) -> str:
    if not MP_TOKEN:
        return json.dumps({"error": "MercadoPago not configured"})
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{MP_API}{path}",
            headers={"Authorization": f"Bearer {MP_TOKEN}"},
            timeout=15,
        )
        return json.dumps(resp.json())


async def mp_create_preference(
    title: str,
    unit_price: float,
    quantity: int = 1,
    currency: str = "MXN",
    external_reference: str = "",
    success_url: str = "",
    failure_url: str = "",
    pending_url: str = "",
    notification_url: str = "",
    metadata: dict | None = None,
) -> str:
    if not MP_TOKEN:
        return json.dumps({"error": "MercadoPago not configured — no Access Token"})
    items = [{"title": title, "quantity": quantity, "unit_price": unit_price, "currency_id": currency}]
    body = {
        "items": items,
        "auto_return": "approved",
        "back_urls": {
            "success": success_url or "https://abe.sonoracorp.com/gracias",
            "failure": failure_url or "https://abe.sonoracorp.com/compra",
            "pending": pending_url or "https://abe.sonoracorp.com/compra",
        },
        "external_reference": external_reference,
    }
    if notification_url:
        body["notification_url"] = notification_url
    if metadata:
        body["metadata"] = metadata
    return await _mp_post("/checkout/preferences", body)


async def mp_get_payment(payment_id: str) -> str:
    if not payment_id:
        return json.dumps({"error": "payment_id is required"})
    return await _mp_get(f"/v1/payments/{payment_id}")


async def mp_handle_webhook(topic: str, id: str) -> str:
    if not topic or not id:
        return json.dumps({"error": "topic and id are required"})
    try:
        if topic == "payment":
            payment_resp = await mp_get_payment(id)
            payment = json.loads(payment_resp)
            status = payment.get("status", "")
            external_ref = payment.get("external_reference", "")
            metadata = payment.get("metadata", {})
            tx_amount = payment.get("transaction_amount", 0)

            if status == "approved":
                parts = external_ref.split(":")
                user_id = parts[0] if len(parts) > 0 else ""
                artist = parts[1] if len(parts) > 1 else ""
                product_type = parts[2] if len(parts) > 2 else "foto"

                async with httpx.AsyncClient() as client:
                    q = """
                        mutation ($amount: numeric!, $ref: String!, $metadata: jsonb, $artist: String) {
                            insert_transactions_one(object: {
                                amount: $amount, provider_transaction_id: $ref,
                                description: $artist, metadata: $metadata,
                                status: "completed", provider: "mercadopago"
                            }) { id }
                        }
                    """
                    await client.post(
                        HASURA_URL,
                        json={"query": q, "variables": {
                            "amount": tx_amount, "ref": str(id),
                            "metadata": {"payment": payment, "user_id": user_id, "artist": artist, "product_type": product_type},
                            "artist": artist,
                        }},
                        headers={"x-hasura-admin-secret": HASURA_ADMIN_SECRET, "Content-Type": "application/json"},
                        timeout=10,
                    )
                return json.dumps({"received": True, "status": "completed", "payment_id": id, "external_reference": external_ref})
            else:
                return json.dumps({"received": True, "status": status or "unknown", "payment_id": id})
        else:
            return json.dumps({"received": True, "topic": topic, "id": id})
    except Exception as e:
        return json.dumps({"error": str(e)})


async def mp_list_products(tenant_id: str = "") -> str:
    where = f'{{"tenant_id": {{"_eq": "{tenant_id}"}}}}' if tenant_id else "{}"
    q = f'query {{ products(where: {where}, where: {{active: {{_eq: true}}}}) {{ id name description price_mxn type requires_lora artist {{ name }} }} }}'
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            HASURA_URL,
            json={"query": q},
            headers={"x-hasura-admin-secret": HASURA_ADMIN_SECRET, "Content-Type": "application/json"},
            timeout=10,
        )
        data = resp.json()
        return json.dumps(data.get("data", {}).get("products", []))


MCP_TOOLS = {
    "mp_create_preference": {
        "description": "Create a MercadoPago checkout preference for payment",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Product title"},
                "unit_price": {"type": "number", "description": "Price in MXN"},
                "quantity": {"type": "integer", "description": "Quantity (default: 1)"},
                "currency": {"type": "string", "description": "Currency code (default: MXN)"},
                "external_reference": {"type": "string", "description": "Reference like user_id:artist:product_type"},
                "success_url": {"type": "string", "description": "Redirect URL on success"},
                "failure_url": {"type": "string", "description": "Redirect URL on failure"},
                "pending_url": {"type": "string", "description": "Redirect URL on pending"},
                "notification_url": {"type": "string", "description": "Webhook URL for IPN"},
            },
            "required": ["title", "unit_price"],
        },
        "handler": lambda args: mp_create_preference(
            args["title"], args["unit_price"],
            args.get("quantity", 1), args.get("currency", "MXN"),
            args.get("external_reference", ""),
            args.get("success_url", ""), args.get("failure_url", ""),
            args.get("pending_url", ""), args.get("notification_url", ""),
        ),
    },
    "mp_get_payment": {
        "description": "Get payment status from MercadoPago by ID",
        "input_schema": {
            "type": "object",
            "properties": {
                "payment_id": {"type": "string", "description": "MercadoPago payment ID"},
            },
            "required": ["payment_id"],
        },
        "handler": lambda args: mp_get_payment(args["payment_id"]),
    },
    "mp_handle_webhook": {
        "description": "Process MercadoPago IPN webhook notification",
        "input_schema": {
            "type": "object",
            "properties": {
                "topic": {"type": "string", "description": "Notification topic (payment, merchant_order, etc)"},
                "id": {"type": "string", "description": "Resource ID"},
            },
            "required": ["topic", "id"],
        },
        "handler": lambda args: mp_handle_webhook(args["topic"], args["id"]),
    },
    "mp_list_products": {
        "description": "List active products for a tenant",
        "input_schema": {
            "type": "object",
            "properties": {
                "tenant_id": {"type": "string", "description": "Tenant ID (optional)"},
            },
            "required": [],
        },
        "handler": lambda args: mp_list_products(args.get("tenant_id", "")),
    },
}
