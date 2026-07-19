"""
Sonora Order Tracker — Rastreador de Entregas de Servicios

Seguimiento de principio a fin de cada servicio contratado por un cliente:
  queued → processing → completed → delivered

Flujo:
  1. Cliente solicita servicio → se crea order con estado "queued"
  2. Worker asigna agente → estado "processing"
  3. Contenido generado → estado "completed"
  4. Envío al cliente → estado "delivered"

Cada cambio de estado emite eventos al bus y opcionalmente dispara
notificaciones via el notifier.
"""

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

REPO = Path(__file__).resolve().parent.parent.parent

app = FastAPI(
    title="Sonora Order Tracker",
    version="1.0.0",
    docs_url="/tracker/docs",
    redoc_url="/tracker/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ORDERS_FILE = REPO / "state" / "tracker" / "orders.json"
STATUSES = ["queued", "processing", "completed", "delivered", "cancelled"]

# WebSocket connections for real-time updates
ws_clients: dict[str, set[WebSocket]] = {}


class OrderCreate(BaseModel):
    client_id: str
    client_phone: str = ""
    service_type: str = ""  # photo, video, voice, clone, social
    service_id: str = ""
    description: str = ""
    tokens_cost: int = 0
    tenant: str = "default"


class OrderUpdate(BaseModel):
    status: str = ""
    notes: str = ""
    delivery_url: str = ""
    assigned_agent: str = ""


# ─── Data Store ───────────────────────────────────────────────────────

def _load_orders() -> list[dict]:
    if not ORDERS_FILE.exists():
        ORDERS_FILE.parent.mkdir(parents=True, exist_ok=True)
        return []
    try:
        with open(ORDERS_FILE) as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def _save_orders(orders: list[dict]) -> None:
    ORDERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(ORDERS_FILE, "w") as f:
        json.dump(orders, f, indent=2, ensure_ascii=False)


def _emit_tracker_event(event_type: str, payload: dict) -> None:
    events_file = REPO / "state" / "events" / "events.jsonl"
    events_file.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "event": event_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "payload": payload,
    }
    with open(events_file, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


async def _notify_ws(order_id: str, data: dict) -> None:
    clients = ws_clients.get(order_id, set())
    dead = set()
    for ws in clients:
        try:
            await ws.send_json(data)
        except Exception:
            dead.add(ws)
    clients -= dead


# ─── API Routes ───────────────────────────────────────────────────────

@app.get("/tracker/orders")
def list_orders(client_id: str = "", tenant: str = "", status: str = "", limit: int = 50):
    orders = _load_orders()
    if client_id:
        orders = [o for o in orders if o.get("client_id") == client_id]
    if tenant:
        orders = [o for o in orders if o.get("tenant") == tenant]
    if status:
        orders = [o for o in orders if o.get("status") == status]
    orders.sort(key=lambda o: o.get("created_at", ""), reverse=True)
    return {"orders": orders[:limit], "total": len(orders)}


@app.post("/tracker/orders")
def create_order(order: OrderCreate):
    orders = _load_orders()
    new_order = order.model_dump()
    new_order["id"] = f"ORD-{uuid.uuid4().hex[:8].upper()}"
    new_order["status"] = "queued"
    new_order["status_history"] = [
        {"status": "queued", "at": datetime.now(timezone.utc).isoformat(), "note": "Order created"}
    ]
    new_order["notes"] = ""
    new_order["delivery_url"] = ""
    new_order["assigned_agent"] = ""
    new_order["created_at"] = datetime.now(timezone.utc).isoformat()
    new_order["updated_at"] = new_order["created_at"]
    orders.insert(0, new_order)
    _save_orders(orders)
    _emit_tracker_event("tracker:order:created", {
        "order_id": new_order["id"],
        "client_id": new_order["client_id"],
        "service_type": new_order["service_type"],
        "tokens_cost": new_order["tokens_cost"],
    })
    return {"ok": True, "order": new_order}


@app.get("/tracker/orders/{order_id}")
def get_order(order_id: str):
    orders = _load_orders()
    for o in orders:
        if o.get("id") == order_id:
            return {"order": o}
    raise HTTPException(404, f"Order {order_id} not found")


@app.put("/tracker/orders/{order_id}")
async def update_order(order_id: str, update: OrderUpdate):
    orders = _load_orders()
    for i, o in enumerate(orders):
        if o.get("id") == order_id:
            if update.status:
                if update.status not in STATUSES:
                    raise HTTPException(400, f"Invalid status: {update.status}. Valid: {STATUSES}")
                o["status"] = update.status
                history = o.get("status_history", [])
                history.append({
                    "status": update.status,
                    "at": datetime.now(timezone.utc).isoformat(),
                    "note": update.notes or "",
                })
                o["status_history"] = history
            if update.notes:
                o["notes"] = (o.get("notes", "") + "\n" + update.notes).strip()
            if update.delivery_url:
                o["delivery_url"] = update.delivery_url
            if update.assigned_agent:
                o["assigned_agent"] = update.assigned_agent
            o["updated_at"] = datetime.now(timezone.utc).isoformat()
            orders[i] = o
            _save_orders(orders)
            _emit_tracker_event(f"tracker:order:{update.status or 'updated'}", {
                "order_id": order_id,
                "status": o["status"],
                "delivery_url": o.get("delivery_url", ""),
            })
            await _notify_ws(order_id, {"event": "order:updated", "order": o})
            return {"ok": True, "order": o}
    raise HTTPException(404, f"Order {order_id} not found")


@app.post("/tracker/orders/{order_id}/next")
async def next_status(order_id: str, notes: str = ""):
    """Advance order to next status."""
    orders = _load_orders()
    for _i, o in enumerate(orders):
        if o.get("id") == order_id:
            current = o.get("status", "queued")
            idx = STATUSES.index(current) if current in STATUSES else -1
            if idx < 0 or idx >= len(STATUSES) - 1:
                statuses_left = [s for s in STATUSES if STATUSES.index(s) > idx]
                raise HTTPException(400, f"Order is already {current}. Next would be: {statuses_left}")
            next_st = STATUSES[idx + 1]
            update = OrderUpdate(status=next_st, notes=notes)
            return await update_order(order_id, update)
    raise HTTPException(404, f"Order {order_id} not found")


@app.get("/tracker/stats")
def tracker_stats(tenant: str = ""):
    orders = _load_orders()
    if tenant:
        orders = [o for o in orders if o.get("tenant") == tenant]
    total = len(orders)
    by_status = {}
    for o in orders:
        s = o.get("status", "unknown")
        by_status[s] = by_status.get(s, 0) + 1
    return {
        "total": total,
        "by_status": by_status,
        "recent": orders[:5] if orders else [],
    }


# ─── WebSocket ─────────────────────────────────────────────────────────

@app.websocket("/tracker/ws/{order_id}")
async def tracker_ws(websocket: WebSocket, order_id: str):
    await websocket.accept()
    if order_id not in ws_clients:
        ws_clients[order_id] = set()
    ws_clients[order_id].add(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_clients[order_id].discard(websocket)


# ─── Health ────────────────────────────────────────────────────────────

@app.get("/tracker/health")
def health():
    return {
        "status": "ok",
        "orders_file": str(ORDERS_FILE),
        "total_orders": len(_load_orders()),
    }


# ─── Direct launch ───────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("TRACKER_PORT", "6300"))
    uvicorn.run("products.order_tracker.main:app", host="0.0.0.0", port=port, reload=False)
