"""
Sonora Affiliates — Portal de Afiliados y Referidos

Programa de referidos con tracking de:
  - Links de referido únicos por afiliado
  - Comisiones en tokens y MXN
  - Solicitudes de pago
  - Leaderboard de afiliados

Cada afiliado tiene un código único (REF-XXXXXX) que se usa en
links wa.me y en el portal.
"""

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

REPO = Path(__file__).resolve().parent.parent.parent

app = FastAPI(
    title="Sonora Affiliates",
    version="1.0.0",
    docs_url="/affiliates/docs",
    redoc_url="/affiliates/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

AFFILIATES_FILE = REPO / "state" / "affiliates" / "affiliates.json"
EARNINGS_FILE = REPO / "state" / "affiliates" / "earnings.json"
PAYOUTS_FILE = REPO / "state" / "affiliates" / "payouts.json"


class AffiliateCreate(BaseModel):
    name: str
    email: str = ""
    phone: str = ""
    tenant: str = "default"


class AffiliateUpdate(BaseModel):
    name: str = ""
    email: str = ""
    phone: str = ""
    commission_pct: float = 10.0  # percentage of tokens spent by referrals
    active: bool = True


class EarningRecord(BaseModel):
    affiliate_id: str
    amount_tokens: int = 0
    amount_mxn: float = 0.0
    source: str = ""  # referral, commission, bonus
    referral_id: str = ""
    description: str = ""


class PayoutRequest(BaseModel):
    affiliate_id: str
    amount_mxn: float
    method: str = "transferencia"  # transferencia, stripe, mercadopago
    account_info: str = ""


# ─── Data helpers ─────────────────────────────────────────────────────

def _load_json(path: Path) -> list:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        return []
    try:
        with open(path) as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def _save_json(path: Path, data: list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _emit_event(event_type: str, payload: dict) -> None:
    events_file = REPO / "state" / "events" / "events.jsonl"
    events_file.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "event": event_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "payload": payload,
    }
    with open(events_file, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def _generate_ref_code() -> str:
    return f"REF-{uuid.uuid4().hex[:6].upper()}"


# ─── Affiliates CRUD ──────────────────────────────────────────────────

@app.get("/affiliates/health")
def health():
    return {
        "status": "ok",
        "affiliates_file": str(AFFILIATES_FILE),
        "total_affiliates": len(_load_json(AFFILIATES_FILE)),
    }

@app.get("/affiliates/stats")
def stats():
    affiliates = _load_json(AFFILIATES_FILE)
    earnings = _load_json(EARNINGS_FILE)
    payouts = _load_json(PAYOUTS_FILE)
    return {
        "total_affiliates": len(affiliates),
        "active_affiliates": sum(1 for a in affiliates if a.get("active", True)),
        "total_referrals": sum(a.get("referrals_count", 0) for a in affiliates),
        "total_tokens_earned": sum(e.get("amount_tokens", 0) for e in earnings),
        "total_mxn_earned": sum(e.get("amount_mxn", 0.0) for e in earnings),
        "pending_payouts_mxn": sum(p.get("amount_mxn", 0) for p in payouts if p.get("status") == "pending"),
        "paid_payouts_mxn": sum(p.get("amount_mxn", 0) for p in payouts if p.get("status") == "paid"),
    }

@app.get("/affiliates/leaderboard")
def leaderboard(limit: int = 10):
    affiliates = _load_json(AFFILIATES_FILE)
    active = [a for a in affiliates if a.get("active", True)]
    sorted_affs = sorted(active, key=lambda a: a.get("total_tokens", 0), reverse=True)
    result = []
    for i, a in enumerate(sorted_affs[:limit]):
        result.append({
            "rank": i + 1,
            "id": a["id"],
            "name": a["name"],
            "ref_code": a["ref_code"],
            "total_tokens": a.get("total_tokens", 0),
            "total_mxn": a.get("total_mxn", 0.0),
            "referrals_count": a.get("referrals_count", 0),
        })
    return {"leaderboard": result}

@app.get("/affiliates")
def list_affiliates(tenant: str = "", active_only: bool = False):
    affiliates = _load_json(AFFILIATES_FILE)
    if tenant:
        affiliates = [a for a in affiliates if a.get("tenant") == tenant]
    if active_only:
        affiliates = [a for a in affiliates if a.get("active", True)]
    totals = {
        "total": len(affiliates),
        "active": sum(1 for a in affiliates if a.get("active", True)),
        "total_tokens": sum(a.get("total_tokens", 0) for a in affiliates),
    }
    return {"affiliates": affiliates, "totals": totals}


@app.post("/affiliates")
def create_affiliate(aff: AffiliateCreate):
    affiliates = _load_json(AFFILIATES_FILE)
    ref_code = _generate_ref_code()
    while any(a.get("ref_code") == ref_code for a in affiliates):
        ref_code = _generate_ref_code()
    new_aff = {
        "id": f"AF-{uuid.uuid4().hex[:8].upper()}",
        "ref_code": ref_code,
        "name": aff.name,
        "email": aff.email,
        "phone": aff.phone,
        "tenant": aff.tenant,
        "commission_pct": 10.0,
        "active": True,
        "total_tokens": 0,
        "total_mxn": 0.0,
        "referrals_count": 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    affiliates.append(new_aff)
    _save_json(AFFILIATES_FILE, affiliates)
    _emit_event("affiliate:created", {
        "affiliate_id": new_aff["id"],
        "ref_code": ref_code,
        "name": aff.name,
    })
    return {"ok": True, "affiliate": new_aff}


@app.get("/affiliates/{affiliate_id}")
def get_affiliate(affiliate_id: str):
    affiliates = _load_json(AFFILIATES_FILE)
    for a in affiliates:
        if a.get("id") == affiliate_id:
            return {"affiliate": a}
    raise HTTPException(404, f"Affiliate {affiliate_id} not found")


@app.put("/affiliates/{affiliate_id}")
def update_affiliate(affiliate_id: str, update: AffiliateUpdate):
    affiliates = _load_json(AFFILIATES_FILE)
    for i, a in enumerate(affiliates):
        if a.get("id") == affiliate_id:
            if update.name:
                a["name"] = update.name
            if update.email:
                a["email"] = update.email
            if update.phone:
                a["phone"] = update.phone
            a["commission_pct"] = update.commission_pct
            a["active"] = update.active
            affiliates[i] = a
            _save_json(AFFILIATES_FILE, affiliates)
            return {"ok": True, "affiliate": a}
    raise HTTPException(404, f"Affiliate {affiliate_id} not found")


@app.delete("/affiliates/{affiliate_id}")
def deactivate_affiliate(affiliate_id: str):
    affiliates = _load_json(AFFILIATES_FILE)
    for i, a in enumerate(affiliates):
        if a.get("id") == affiliate_id:
            a["active"] = False
            affiliates[i] = a
            _save_json(AFFILIATES_FILE, affiliates)
            return {"ok": True, "deactivated": affiliate_id}
    raise HTTPException(404, f"Affiliate {affiliate_id} not found")


# ─── Referral codes ──────────────────────────────────────────────────

@app.get("/affiliates/ref/{ref_code}")
def resolve_ref_code(ref_code: str):
    """Resolve a referral code to an affiliate."""
    affiliates = _load_json(AFFILIATES_FILE)
    for a in affiliates:
        if a.get("ref_code") == ref_code.upper():
            return {"affiliate": a}
    raise HTTPException(404, f"Referral code {ref_code} not found")


@app.get("/affiliates/generate-link/{affiliate_id}")
def generate_wa_link(affiliate_id: str):
    """Generate a wa.me link with the affiliate's referral code."""
    affiliates = _load_json(AFFILIATES_FILE)
    for a in affiliates:
        if a.get("id") == affiliate_id:
            ref_code = a["ref_code"]
            link = f"https://wa.me/5216623538272?text={ref_code}"
            return {"link": link, "ref_code": ref_code, "affiliate": a["name"]}
    raise HTTPException(404, f"Affiliate {affiliate_id} not found")


# ─── Earnings ─────────────────────────────────────────────────────────

@app.get("/earnings")
def list_earnings(affiliate_id: str = "", limit: int = 50):
    earnings = _load_json(EARNINGS_FILE)
    if affiliate_id:
        earnings = [e for e in earnings if e.get("affiliate_id") == affiliate_id]
    earnings.sort(key=lambda e: e.get("created_at", ""), reverse=True)
    total_tokens = sum(e.get("amount_tokens", 0) for e in earnings)
    total_mxn = sum(e.get("amount_mxn", 0.0) for e in earnings)
    return {
        "entries": earnings[:limit],
        "total": len(earnings),
        "total_tokens": total_tokens,
        "total_mxn": total_mxn,
    }


@app.post("/earnings")
def add_earning(earning: EarningRecord):
    earnings = _load_json(EARNINGS_FILE)
    entry = earning.model_dump()
    entry["id"] = f"ERN-{uuid.uuid4().hex[:8].upper()}"
    entry["created_at"] = datetime.now(timezone.utc).isoformat()
    earnings.append(entry)
    _save_json(EARNINGS_FILE, earnings)

    # Update affiliate totals
    affiliates = _load_json(AFFILIATES_FILE)
    for i, a in enumerate(affiliates):
        if a.get("id") == earning.affiliate_id:
            a["total_tokens"] = a.get("total_tokens", 0) + entry["amount_tokens"]
            a["total_mxn"] = a.get("total_mxn", 0.0) + entry["amount_mxn"]
            a["referrals_count"] = a.get("referrals_count", 0) + (1 if earning.source == "referral" else 0)
            affiliates[i] = a
            _save_json(AFFILIATES_FILE, affiliates)
            break

    _emit_event("affiliate:earning", {
        "affiliate_id": entry["affiliate_id"],
        "amount_tokens": entry["amount_tokens"],
        "amount_mxn": entry["amount_mxn"],
        "source": entry["source"],
    })
    return {"ok": True, "earning": entry}


# ─── Payouts ──────────────────────────────────────────────────────────

@app.get("/payouts")
def list_payouts(affiliate_id: str = "", status: str = ""):
    payouts = _load_json(PAYOUTS_FILE)
    if affiliate_id:
        payouts = [p for p in payouts if p.get("affiliate_id") == affiliate_id]
    if status:
        payouts = [p for p in payouts if p.get("status") == status]
    payouts.sort(key=lambda p: p.get("created_at", ""), reverse=True)
    pending = sum(p.get("amount_mxn", 0) for p in payouts if p.get("status") == "pending")
    paid = sum(p.get("amount_mxn", 0) for p in payouts if p.get("status") == "paid")
    return {
        "payouts": payouts,
        "total": len(payouts),
        "pending_mxn": pending,
        "paid_mxn": paid,
    }


@app.post("/payouts")
def request_payout(payout: PayoutRequest):
    payouts = _load_json(PAYOUTS_FILE)
    new_payout = payout.model_dump()
    new_payout["id"] = f"PAY-{uuid.uuid4().hex[:8].upper()}"
    new_payout["status"] = "pending"
    new_payout["created_at"] = datetime.now(timezone.utc).isoformat()
    payouts.append(new_payout)
    _save_json(PAYOUTS_FILE, payouts)
    _emit_event("affiliate:payout:requested", {
        "affiliate_id": new_payout["affiliate_id"],
        "amount_mxn": new_payout["amount_mxn"],
        "payout_id": new_payout["id"],
    })
    return {"ok": True, "payout": new_payout}


@app.post("/payouts/{payout_id}/process")
def process_payout(payout_id: str):
    """Mark a payout as processed."""
    payouts = _load_json(PAYOUTS_FILE)
    for i, p in enumerate(payouts):
        if p.get("id") == payout_id:
            if p["status"] != "pending":
                raise HTTPException(400, f"Payout already {p['status']}")
            p["status"] = "paid"
            p["processed_at"] = datetime.now(timezone.utc).isoformat()
            payouts[i] = p
            _save_json(PAYOUTS_FILE, payouts)
            _emit_event("affiliate:payout:paid", {
                "affiliate_id": p["affiliate_id"],
                "amount_mxn": p["amount_mxn"],
                "payout_id": payout_id,
            })
            return {"ok": True, "payout": p}
    raise HTTPException(404, f"Payout {payout_id} not found")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("AFFILIATES_PORT", "6400"))
    uvicorn.run("products.affiliates.main:app", host="0.0.0.0", port=port, reload=False)
