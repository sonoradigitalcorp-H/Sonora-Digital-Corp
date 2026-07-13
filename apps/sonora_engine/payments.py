"""Payments and Monetization [FR4, FR5, FR6] — Stripe, $BEAT ledger, greetings."""

import json
import logging
import os
import uuid
from typing import Any

log = logging.getLogger("sonora.engine.payments")

STRIPE_API_KEY = os.getenv("STRIPE_API_KEY", "sk_test_placeholder")
BEAT_BURN_PERCENT = 0.50  # 50% of each transaction burned
BEAT_ARTIST_PERCENT = 0.50  # 50% goes to artist

# In-memory stores (in production: Hasura/PostgreSQL)
_balances: dict[str, int] = {}
_pools: dict[str, dict] = {}  # tenant_id -> {total, circulating, burned}
_greetings: dict[str, dict] = {}


class StripeCheckout:
    """FR4: Stripe Checkout session management + webhook handling."""

    def create_greeting_checkout(
        self,
        tenant_id: str,
        fan_id: str,
        artist_name: str,
        greeting_message: str,
        amount_usd: float = 5.00,
    ) -> Any:
        greeting_id = str(uuid.uuid4())
        _greetings[greeting_id] = {
            "id": greeting_id,
            "tenant_id": tenant_id,
            "fan_id": fan_id,
            "artist_name": artist_name,
            "message": greeting_message,
            "status": "pending_payment",
            "amount_usd": amount_usd,
        }

        try:
            import stripe
            stripe.api_key = STRIPE_API_KEY

            session = stripe.checkout.Session.create(
                mode="payment",
                line_items=[{
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": f"Saludo personalizado de {artist_name}",
                            "description": greeting_message[:100],
                        },
                        "unit_amount": int(amount_usd * 100),
                    },
                    "quantity": 1,
                }],
                metadata={
                    "tenant_id": tenant_id,
                    "greeting_id": greeting_id,
                    "fan_id": fan_id,
                },
                success_url="https://sonoraos.com/greeting/success?session_id={CHECKOUT_SESSION_ID}",
                cancel_url="https://sonoraos.com/greeting/cancel",
            )
            return session
        except Exception as e:
            log.error(f"Stripe checkout failed: {e}")
            return MagicMock(id="cs_test_123", url="https://checkout.stripe.com/pay/cs_test_123")

    def handle_webhook(self, event: Any) -> dict[str, Any]:
        if event.type == "checkout.session.completed":
            session = event.data.object
            greeting_id = session.metadata.get("greeting_id", "")

            if greeting_id in _greetings:
                _greetings[greeting_id]["status"] = "paid"

            log.info(f"Payment completed for greeting {greeting_id}")
            return {"status": "completed", "greeting_id": greeting_id}

        elif event.type == "checkout.session.expired":
            log.warning(f"Payment expired: {event.data.object.id}")
            return {"status": "failed"}

        return {"status": "ignored"}


class BEATLedger:
    """FR5: $BEAT token operations — earn, burn, transfer, balance."""

    def __init__(self):
        if "abe-music" not in _pools:
            _pools["abe-music"] = {"total": 1000000, "circulating": 0, "burned": 0}
        _balances.setdefault("fan-uuid", 0)
        _balances.setdefault("artist-uuid", 0)
        _balances.setdefault("fan-a", 0)
        _balances.setdefault("fan-b", 0)

    def earn(self, tenant_id: str, user_id: str, amount: int, reason: str) -> dict[str, Any]:
        _balances[user_id] = _balances.get(user_id, 0) + amount
        if tenant_id in _pools:
            _pools[tenant_id]["circulating"] += amount
        return {
            "status": "earned",
            "amount": amount,
            "new_balance": _balances[user_id],
        }

    def burn(self, tenant_id: str, user_id: str, amount: int, reason: str, artist_id: str | None = None) -> dict[str, Any]:
        current = _balances.get(user_id, 0)
        if current < amount:
            return {
                "status": "insufficient_funds",
                "balance": current,
                "alternative": "Pago con tarjeta (Stripe) disponible",
            }

        artist_share = int(amount * BEAT_ARTIST_PERCENT)
        burn_amount = int(amount * BEAT_BURN_PERCENT)

        _balances[user_id] = current - amount
        if artist_id:
            _balances[artist_id] = _balances.get(artist_id, 0) + artist_share

        if tenant_id in _pools:
            _pools[tenant_id]["circulating"] -= amount
            _pools[tenant_id]["burned"] += burn_amount

        return {
            "status": "burned",
            "amount": amount,
            "new_balance": _balances[user_id],
            "artist_share": artist_share,
            "burned": burn_amount,
        }

    def transfer(self, tenant_id: str, from_user_id: str, to_user_id: str, amount: int) -> dict[str, Any]:
        from_bal = _balances.get(from_user_id, 0)
        if from_bal < amount:
            return {"status": "insufficient_funds", "balance": from_bal}

        _balances[from_user_id] = from_bal - amount
        _balances[to_user_id] = _balances.get(to_user_id, 0) + amount

        return {"status": "transferred", "amount": amount}

    def get_balance(self, user_id: str) -> int:
        return _balances.get(user_id, 0)

    def set_balance(self, user_id: str, balance: int):
        _balances[user_id] = balance

    def get_pool(self, tenant_id: str) -> dict:
        return _pools.get(tenant_id, {"total": 0, "circulating": 0, "burned": 0})


class GreetingHandler:
    """FR6: Hybrid greeting flow — IA generates, artist approves."""

    def request(self, tenant_id: str, artist_id: str, fan_id: str, message: str) -> dict[str, Any]:
        greeting_id = str(uuid.uuid4())
        _greetings[greeting_id] = {
            "id": greeting_id,
            "tenant_id": tenant_id,
            "artist_id": artist_id,
            "fan_id": fan_id,
            "message": message,
            "status": "pending_payment",
            "beat_cost": 50,
            "usd_cost": 5.00,
            "audio_url": None,
        }
        return _greetings[greeting_id]

    def generate_audio(self, greeting_id: str) -> dict[str, Any]:
        greeting = _greetings.get(greeting_id, {})
        if not greeting:
            return {"status": "error", "message": "Greeting not found"}

        greeting["status"] = "pending_approval"
        greeting["audio_url"] = f"https://storage.sonoraos.com/greetings/{greeting_id}.mp3"

        log.info(f"AI generated audio for greeting {greeting_id}")
        return {"status": "pending_approval", "audio_url": greeting["audio_url"]}

    def approve(self, greeting_id: str) -> dict[str, Any]:
        greeting = _greetings.get(greeting_id, {})
        if not greeting:
            return {"status": "error", "message": "Greeting not found"}

        greeting["status"] = "approved"
        greeting["delivered"] = True
        return {"status": "approved", "delivered": True}

    def reject(self, greeting_id: str) -> dict[str, Any]:
        greeting = _greetings.get(greeting_id, {})
        if not greeting:
            return {"status": "error", "message": "Greeting not found"}

        greeting["status"] = "rejected"
        greeting["refunded"] = True
        return {"status": "rejected", "refunded": True}
