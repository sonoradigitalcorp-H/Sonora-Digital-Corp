"""
Ce-Son API — Backend para el dashboard de vendedores.
FastAPI con endpoints de ventas, clientes, gamificación, comisiones.
"""
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO))

from apps.whatsapp.order_store import (
    get_db, get_seller, get_seller_by_phone, register_seller,
    get_order, list_orders, create_order, update_order_status,
    get_client, list_seller_clients, register_client,
    update_seller_tokens, award_badge, get_seller_badges,
    seller_dashboard, owner_report,
)

app = FastAPI(title="Ce-Son v3 API", version="1.0.0", docs_url="/api/docs")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Schemas ────────────────────────────────────────────────

class SellerRegister(BaseModel):
    name: str
    phone: str
    email: str = ""

class OrderCreate(BaseModel):
    seller_id: str = ""
    client_name: str
    client_phone: str = ""
    client_address: str = ""
    items: list[dict]
    total: float
    payment_method: str = "efectivo"

class ClientRegister(BaseModel):
    seller_id: str
    name: str
    phone: str = ""
    address: str = ""
    lat: float = 0
    lng: float = 0


# ─── Auth (simple phone-based) ──────────────────────────────

def _get_seller_from_phone(phone: str):
    conn = get_db()
    seller = get_seller_by_phone(conn, phone)
    conn.close()
    if not seller:
        raise HTTPException(404, "Vendedor no encontrado")
    return seller


# ─── Sellers ────────────────────────────────────────────────

@app.post("/api/sellers/register")
def api_register_seller(data: SellerRegister):
    conn = get_db()
    existing = get_seller_by_phone(conn, data.phone)
    if existing:
        conn.close()
        return {"ok": True, "seller": existing}
    seller = register_seller(conn, data.name, data.phone, data.email)
    conn.close()
    return {"ok": True, "seller": seller}


@app.get("/api/sellers/{seller_id}")
def api_get_seller(seller_id: str):
    conn = get_db()
    seller = get_seller(conn, seller_id)
    conn.close()
    if not seller:
        raise HTTPException(404, "Vendedor no encontrado")
    return {"seller": seller}


@app.get("/api/sellers/by-phone/{phone}")
def api_get_seller_by_phone(phone: str):
    conn = get_db()
    seller = get_seller_by_phone(conn, phone)
    conn.close()
    if not seller:
        raise HTTPException(404, "Vendedor no encontrado")
    return {"seller": seller}


@app.get("/api/sellers/{seller_id}/dashboard")
def api_seller_dashboard(seller_id: str):
    conn = get_db()
    data = seller_dashboard(conn, seller_id)
    conn.close()
    if not data:
        raise HTTPException(404, "Vendedor no encontrado")
    return data


# ─── Orders ─────────────────────────────────────────────────

@app.get("/api/orders")
def api_list_orders(
    seller_id: str = "",
    status: str = "",
    limit: int = 50,
    offset: int = 0,
):
    conn = get_db()
    orders = list_orders(conn, seller_id=seller_id, status=status, limit=limit, offset=offset)
    conn.close()
    return {"orders": orders, "total": len(orders)}


@app.get("/api/orders/{order_id}")
def api_get_order(order_id: str):
    conn = get_db()
    order = get_order(conn, order_id)
    conn.close()
    if not order:
        raise HTTPException(404, "Orden no encontrada")
    return {"order": order}


@app.post("/api/orders")
def api_create_order(data: OrderCreate):
    conn = get_db()
    order = create_order(conn, data.model_dump())
    conn.close()
    return {"ok": True, "order": order}


@app.post("/api/orders/{order_id}/status")
def api_update_status(order_id: str, status: str = Query(...), actor: str = "sistema"):
    conn = get_db()
    order = update_order_status(conn, order_id, status, actor=actor)
    conn.close()
    if not order:
        raise HTTPException(404, "Orden no encontrada")
    return {"ok": True, "order": order}


# ─── Clients ────────────────────────────────────────────────

@app.get("/api/clients")
def api_list_clients(seller_id: str = ""):
    if not seller_id:
        raise HTTPException(400, "seller_id requerido")
    conn = get_db()
    clients = list_seller_clients(conn, seller_id)
    conn.close()
    return {"clients": clients}


@app.get("/api/clients/{client_id}")
def api_get_client(client_id: str):
    conn = get_db()
    client = get_client(conn, client_id)
    conn.close()
    if not client:
        raise HTTPException(404, "Cliente no encontrado")
    return {"client": client}


@app.post("/api/clients")
def api_register_client(data: ClientRegister):
    conn = get_db()
    client = register_client(conn, data.seller_id, data.name, data.phone, data.address, data.lat, data.lng)
    conn.close()
    return {"ok": True, "client": client}


# ─── Gamification ───────────────────────────────────────────

@app.get("/api/sellers/{seller_id}/badges")
def api_get_badges(seller_id: str):
    conn = get_db()
    badges = get_seller_badges(conn, seller_id)
    conn.close()
    return {"badges": badges}


@app.post("/api/sellers/{seller_id}/award-badge")
def api_award_badge(seller_id: str, badge_id: str = Query(...)):
    conn = get_db()
    ok = award_badge(conn, seller_id, badge_id)
    conn.close()
    return {"ok": ok}


@app.post("/api/sellers/{seller_id}/tokens")
def api_add_tokens(seller_id: str, amount: int = Query(...), reason: str = "bonus"):
    conn = get_db()
    update_seller_tokens(conn, seller_id, amount, reason)
    seller = get_seller(conn, seller_id)
    conn.close()
    return {"ok": True, "tokens": seller["tokens"] if seller else 0}


# ─── Owner / Platform Reports ───────────────────────────────

@app.get("/api/owner/report")
def api_owner_report():
    conn = get_db()
    report = owner_report(conn)
    conn.close()
    return report


# ─── Health ─────────────────────────────────────────────────

@app.get("/api/health")
def health():
    return {"status": "ok", "service": "ce-son-v3", "timestamp": datetime.now(timezone.utc).isoformat()}


# ─── Main ───────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("CE_SON_PORT", "6400"))
    uvicorn.run("products.ce_son.main:app", host="0.0.0.0", port=port, reload=False)
