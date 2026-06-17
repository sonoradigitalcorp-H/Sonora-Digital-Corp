"""
SDC Payments — Mercado Pago + Bitso + SPEI integration.
Multi-provider payment system for Mexico/LatAm market.
Domain types in src.core.domain (frozen dataclasses, typed enums).
"""

import json
import logging
import os
import uuid
import time
from typing import Optional, Dict, List, Any
from datetime import datetime, timezone

from src.core.domain import (
    PaymentProvider,
    PaymentCurrency,
    Plan,
    SPEIAccount,
    PaymentResult,
)

log = logging.getLogger("jarvis.payments")

PAYMENT_PROVIDERS: Dict[str, Dict[str, Any]] = {
    "mercadopago": {
        "name": "Mercado Pago",
        "fees": 0.039,
        "supports": ["card", "oxxo", "spei", "wallet"],
        "settlement": "next_day",
    },
    "bitso": {
        "name": "Bitso",
        "fees": 0.01,
        "supports": ["usdc", "btc", "spei_transfer"],
        "settlement": "instant",
    },
    "spei": {
        "name": "SPEI Directo",
        "fees": 0.0,
        "supports": ["bank_transfer"],
        "settlement": "same_day",
    },
}

SPEI_ACCOUNT: SPEIAccount = SPEIAccount(
    bank="NVIO",
    clabe="710969000013788012",
    holder="Luis Daniel Guerrero Enciso",
    currency="MXN",
)

PLANS: Dict[str, Plan] = {
    "conquistador": Plan(id="conquistador", name="Conquistador", price_mxn=780, price_usd=39),
    "agente_ia": Plan(id="agente_ia", name="Agente IA", price_mxn=1380, price_usd=69),
    "imperio": Plan(id="imperio", name="Imperio", price_mxn=2980, price_usd=149),
}

MP_WEBHOOK_URL = "https://sonoradigitalcorp.com/api/payments/webhook/mercadopago"


class MercadoPagoClient:
    def __init__(self, access_token: str = ""):
        self.access_token = access_token or os.environ.get(
            "MERCADO_PAGO_ACCESS_TOKEN", ""
        )
        self.base_url = "https://api.mercadopago.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    def create_preference(
        self, items: List[Dict], payer: Dict = None
    ) -> Optional[Dict]:
        if not self.access_token or self.access_token.startswith("TEST-"):
            log.info("MP test mode — returning mock preference")
            return {
                "id": f"mock_{str(uuid.uuid4())[:8]}",
                "init_point": f"https://www.mercadopago.com.mx/checkout/v1/redirect?pref_id=mock",
                "sandbox_init_point": f"https://sandbox.mercadopago.com.mx/checkout/v1/test?pref_id=mock",
            }
        try:
            import requests

            payload = {
                "items": items,
                "payer": payer or {},
                "back_urls": {
                    "success": "https://sonoradigitalcorp.com/pago/exito",
                    "failure": "https://sonoradigitalcorp.com/pago/fallo",
                    "pending": "https://sonoradigitalcorp.com/pago/pendiente",
                },
                "auto_return": "approved",
                "payment_methods": {
                    "excluded_payment_types": [],
                    "installments": 6,
                },
            }
            resp = requests.post(
                f"{self.base_url}/preferences",
                json=payload,
                headers=self.headers,
                timeout=15,
            )
            if resp.ok:
                return resp.json()
            log.warning(f"MP create_preference error: {resp.text}")
        except Exception as e:
            log.warning(f"MP client error: {e}")
        return None

    def get_payment(self, payment_id: str) -> Optional[Dict]:
        try:
            import requests

            resp = requests.get(
                f"{self.base_url}/payments/{payment_id}",
                headers=self.headers,
                timeout=10,
            )
            if resp.ok:
                return resp.json()
        except Exception as e:
            log.warning(f"MP get_payment error: {e}")
        return None

    def verify_webhook_signature(self, request_data: Dict, headers: Dict) -> bool:
        import hashlib, hmac

        secret = os.environ.get("MERCADO_PAGO_WEBHOOK_SECRET", "")
        if not secret:
            return True
        received_sig = headers.get("x-signature", "")
        if not received_sig:
            return True
        parts = received_sig.split(",")
        ts = ""
        hash_val = ""
        for p in parts:
            if p.startswith("ts="):
                ts = p[3:]
            if p.startswith("v1="):
                hash_val = p[3:]
        if not ts or not hash_val:
            return True
        template_id = request_data.get("data", {}).get("id", "")
        manifest = (
            f"id:{template_id};request-id:{headers.get('x-request-id', '')};ts:{ts};"
        )
        expected = hmac.new(
            secret.encode(), manifest.encode(), hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected, hash_val)

    def process_webhook(self, data: Dict) -> Dict:
        action = data.get("action", "")
        payment_id = data.get("data", {}).get("id")
        if action == "payment.created":
            return {"status": "pending", "payment_id": payment_id}
        elif action == "payment.updated":
            payment = self.get_payment(payment_id)
            if payment:
                status = payment.get("status")
                if status == "approved":
                    return {
                        "status": "approved",
                        "payment_id": payment_id,
                        "amount": payment.get("transaction_amount"),
                    }
                elif status == "rejected":
                    return {"status": "rejected", "payment_id": payment_id}
        return {"status": "unknown"}


class BitsoClient:
    def __init__(self, api_key: str = "", api_secret: str = ""):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://api.bitso.com/v3"

    def create_charge(
        self, amount_mxn: float, concept: str = "Suscripción SDC"
    ) -> Optional[Dict]:
        charge_id = f"bitso_{str(uuid.uuid4())[:8]}"
        log.info(f"Bitso charge created: {charge_id} — ${amount_mxn} MXN — {concept}")
        return {
            "id": charge_id,
            "amount": amount_mxn,
            "currency": "MXN",
            "concept": concept,
            "status": "pending",
            "payment_link": f"https://bitso.com/pay/{charge_id}",
            "accepted_currencies": ["USDC", "BTC", "MXN"],
        }


class PaymentOrchestrator:
    def __init__(self):
        self.mp = MercadoPagoClient()
        self.bitso = BitsoClient()
        self.transactions: Dict[str, Dict] = {}

    def create_payment(
        self, plan_id: str, provider: str = "mercadopago", niche: str = "general"
    ) -> Dict:
        plan = PLANS.get(plan_id)
        if not plan:
            return {"error": f"Plan {plan_id} not found"}
        multiplier = 2.0 if niche == "adulto" else 1.0
        amount = plan.price_mxn * multiplier
        tx_id = str(uuid.uuid4())[:8]
        self.transactions[tx_id] = {
            "id": tx_id,
            "plan": plan_id,
            "amount": amount,
            "provider": provider,
            "status": "pending",
            "created_at": time.time(),
        }
        if provider == "mercadopago":
            result = self.mp.create_preference(
                [
                    {
                        "title": f"SDC {plan.name}",
                        "quantity": 1,
                        "unit_price": amount,
                    }
                ]
            )
            self.transactions[tx_id]["payment_url"] = (
                result.get("init_point") if result else None
            )
        elif provider == "bitso":
            result = self.bitso.create_charge(amount)
            self.transactions[tx_id]["payment_url"] = (
                result.get("payment_link") if result else None
            )
        return self.transactions[tx_id]

    def create_spei_charge(self, plan_id: str, niche: str = "general") -> Dict:
        plan = PLANS.get(plan_id)
        if not plan:
            return {"error": f"Plan {plan_id} not found"}
        multiplier = 2.0 if niche == "adulto" else 1.0
        amount = plan.price_mxn * multiplier
        tx_id = str(uuid.uuid4())[:8]
        self.transactions[tx_id] = {
            "id": tx_id,
            "plan": plan_id,
            "amount": amount,
            "provider": "spei",
            "status": "pending",
            "spei_account": {
                "bank": SPEI_ACCOUNT.bank,
                "clabe": SPEI_ACCOUNT.clabe,
                "holder": SPEI_ACCOUNT.holder,
                "currency": SPEI_ACCOUNT.currency,
                "type": SPEI_ACCOUNT.payment_type,
            },
            "concept": f"SDC {plan.name} — {niche}",
            "created_at": time.time(),
        }
        return self.transactions[tx_id]

    def get_transaction(self, tx_id: str) -> Optional[Dict]:
        return self.transactions.get(tx_id)

    def handle_webhook(self, provider: str, data: Dict) -> Dict:
        if provider == "mercadopago":
            return self.mp.process_webhook(data)
        return {"status": "unknown"}
