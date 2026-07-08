"""process-payment handler — HAS-005
Process payments via Stripe or Mercado Pago (simulated).
"""
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent.parent.parent
PAYMENTS_DIR = REPO / "state" / "payments"


def _ensure_dir():
    PAYMENTS_DIR.mkdir(parents=True, exist_ok=True)


async def execute(context: Any) -> dict:
    _ensure_dir()
    input_data = context if isinstance(context, dict) else {}
    action = input_data.get("action", "charge")

    if action == "charge":
        amount = input_data.get("amount", 0)
        currency = input_data.get("currency", "usd")
        payment_method = input_data.get("payment_method", "card")
        description = input_data.get("description", "")
        customer_id = input_data.get("customer_id", "")
        provider = input_data.get("provider", "stripe")
        charge_id = f"ch_{uuid.uuid4().hex[:12]}"

        result = {
            "charge_id": charge_id,
            "amount": amount,
            "currency": currency,
            "status": "succeeded",
            "payment_method": payment_method,
            "description": description,
            "customer_id": customer_id,
            "provider": provider,
            "fee": round(amount * 0.029 + 0.30, 2),
            "net_amount": round(amount - (amount * 0.029 + 0.30), 2),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        path = PAYMENTS_DIR / f"{charge_id}.json"
        path.write_text(json.dumps(result, indent=2))
        return result

    elif action == "refund":
        charge_id = input_data.get("charge_id", "")
        amount = input_data.get("amount", 0)
        result = {
            "refund_id": f"rf_{uuid.uuid4().hex[:12]}",
            "charge_id": charge_id,
            "amount": amount,
            "status": "refunded",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        return result

    elif action == "payout":
        amount = input_data.get("amount", 0)
        destination = input_data.get("destination", "bank_account")
        result = {
            "payout_id": f"po_{uuid.uuid4().hex[:12]}",
            "amount": amount,
            "destination": destination,
            "status": "pending",
            "estimated_arrival": datetime.now(timezone.utc).isoformat(),
        }
        return result

    return {"action": action, "status": "unknown"}
