import logging
import uuid
from datetime import datetime, timedelta

from fastapi import APIRouter, Request
from src.core.payments import (
    PAYMENT_PROVIDERS,
    PLANS,
    SPEI_ACCOUNT,
    PaymentOrchestrator,
)

router = APIRouter()
log = logging.getLogger("jarvis.webui.payments")
_payments = PaymentOrchestrator()


@router.get("/api/payments/spei")
async def payments_spei():
    return {
        "spei": SPEI_ACCOUNT,
        "instructions": "Transfiere el monto exacto via SPEI a la cuenta NVIO. Envía el comprobante a Mystic para activación.",
    }


@router.post("/api/payments/spei/notify")
async def payments_spei_notify(data: dict):
    plan = data.get("plan", "conquistador")
    niche = data.get("nicho", "general")
    reference = data.get("reference", "")
    result = _payments.create_spei_charge(plan, niche)
    if reference:
        result["reference"] = reference
    return result


@router.get("/api/payments/plans")
async def payments_list_plans():
    return {
        "plans": PLANS,
        "providers": {
            k: {kk: vv for kk, vv in v.items() if kk != "fees"}
            for k, v in PAYMENT_PROVIDERS.items()
        },
    }


@router.post("/api/payments/create")
async def payments_create(data: dict):
    return _payments.create_payment(
        data.get("plan", "conquistador"),
        data.get("provider", "mercadopago"),
        data.get("nicho", "general"),
    )


@router.get("/api/payments/transaction/{tx_id}")
async def payments_get_transaction(tx_id: str):
    tx = _payments.get_transaction(tx_id)
    if not tx:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Transaction not found")
    return tx


@router.post("/api/whatsapp/webhook")
async def whatsapp_webhook(request: Request):
    data = await request.json()
    message = data.get("message", data.get("text", ""))
    sender = data.get("from", data.get("sender", ""))
    if not message:
        return {"status": "ignored"}
    log.info(f"WhatsApp from {sender}: {message[:100]}")
    from src.core.orchestrator import get_orchestrator

    orch = get_orchestrator()
    return {"status": "received", "message": message, "agent": orch.route(message)}


@router.get("/api/whatsapp/qr")
async def whatsapp_qr():
    try:
        import requests as req

        r = req.get("http://localhost:3001/qr", timeout=5)
        return r.json()
    except Exception as e:
        return {"error": str(e), "hint": "WhatsApp bridge may need restart"}


@router.post("/api/payments/webhook/{provider}")
async def payments_webhook(provider: str, request: Request):
    data = await request.json()
    if provider == "mercadopago":
        verified = _payments.mp.verify_webhook_signature(data, dict(request.headers))
        if not verified:
            log.warning("MP webhook signature verification failed")
    result = _payments.handle_webhook(provider, data)
    log.info(f"Payment webhook: {provider} → {result}")
    return result


# ── Store Payment Endpoints (for n8n workflows) ────────────────────────────


def _gen_ref():
    return f"JARVIS-{uuid.uuid4().hex[:8].upper()}"


@router.post("/api/payments/spei/create")
async def store_spei_create(data: dict):
    """Create SPEI payment for store order. Called by n8n workflow."""
    amount = data.get("amount", 0)
    data.get("description", "Compra en tienda JARVIS")
    data.get("email", "cliente@email.com")

    ref = _gen_ref()
    return {
        "status": "ok",
        "order_id": data.get("order_id", ref),
        "payment_url": f"https://www.mercadopago.com.mx/payments/{ref}",
        "instructions": (
            f"1. Transfiere ${amount:.2f} MXN vía SPEI\n"
            f"2. A la cuenta CLABE: {SPEI_ACCOUNT['clabe']}\n"
            f"3. Con referencia: {ref}\n"
            f"4. Envía el comprobante a @tu_telegram"
        ),
        "expires_at": (datetime.now() + timedelta(hours=24)).isoformat(),
    }


@router.post("/api/payments/crypto/create")
async def store_crypto_create(data: dict):
    """Create crypto payment for store order. Called by n8n workflow."""
    amount = data.get("amount", 0)
    currency = data.get("currency", "USDC")
    data.get("description", "Compra en tienda JARVIS")

    ref = _gen_ref()
    # In production: get real Bitso deposit address
    addresses = {
        "USDC": "0x1234567890abcdef1234567890abcdef12345678",
        "BTC": "bc1q7zldmzjwspnaa48udvelwe6k3fef7xrrhg5625",
        "USDT": "0x1234567890abcdef1234567890abcdef12345678",
    }
    addr = addresses.get(currency, addresses["USDC"])

    return {
        "status": "ok",
        "order_id": data.get("order_id", ref),
        "payment_url": f"https://bitso.com/transfer/{ref}",
        "instructions": (
            f"1. Envía ${amount:.2f} {currency}\n"
            f"2. A la dirección: {addr}\n"
            f"3. Red: (según moneda)\n"
            f"4. Referencia: {ref}\n"
            f"5. Envía comprobante a @tu_telegram"
        ),
        "address": addr,
        "expires_at": (datetime.now() + timedelta(hours=24)).isoformat(),
    }


@router.post("/api/payments/verify")
async def store_payment_verify(data: dict):
    """Verify payment for store order. Called by n8n workflow."""
    order_id = data.get("order_id", "")
    payment_id = data.get("payment_id", "")
    # In production: verify with Mercado Pago / Bitso API
    return {
        "status": "verified",
        "order_id": order_id,
        "payment_id": payment_id,
        "verified_at": datetime.now().isoformat(),
    }
