"""
Ce-Son Dispatch Engine — Envía pedidos al grupo de repartidores,
espera asignación, maneja timers y alertas.
"""
import json
import os
import sys
import threading
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO))

WACLI = os.path.expanduser("~/.local/bin/wacli")
WACLI_STORE = os.path.expanduser("~/.config/wacli/r1-6623446953")
EVENTS_FILE = REPO / "state" / "events" / "events.jsonl"

# Timeout configs (override via env)
RESPONSE_TIMEOUT = int(os.environ.get("R1_RESPONSE_TIMEOUT", "5"))  # min esperar en grupo
DELIVERY_TIMEOUT = int(os.environ.get("R1_DELIVERY_TIMEOUT", "20"))  # min para entregar
MAX_REDISPATCH = int(os.environ.get("R1_MAX_REDISPATCH", "3"))

# In-memory dispatch tracker
_active_dispatches: dict[str, dict] = {}
_lock = threading.Lock()


def _wacli(args: list, timeout: int = 30) -> dict:
    if not os.path.exists(WACLI):
        return {"success": False, "error": "wacli not found"}
    cmd = [WACLI] + args + ["--store", WACLI_STORE, "--json"]
    try:
        import subprocess
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        out = r.stdout.strip()
        if out:
            return json.loads(out)
        return {"success": False, "error": r.stderr.strip() or "no output"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def send_to_group(group_jid: str, text: str) -> bool:
    jid = group_jid if "@g.us" in group_jid else f"{group_jid}@g.us"
    result = _wacli(["send", "text", "--message", text, "--to", jid, "--post-send-wait", "2s"])
    return result.get("success", False)


def send_text(to: str, text: str) -> bool:
    jid = to if "@s.whatsapp.net" in to else f"{to}@s.whatsapp.net"
    result = _wacli(["send", "text", "--message", text, "--to", jid, "--post-send-wait", "2s"])
    return result.get("success", False)


def _log_event(event: str, payload: dict) -> None:
    EVENTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    entry = {"event": event, "timestamp": datetime.now(timezone.utc).isoformat(), "payload": payload}
    with open(EVENTS_FILE, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


# ─── Dispatch Flow ──────────────────────────────────────────

def dispatch_order(order_id: str) -> dict:
    """Main entry point: dispatch an order to the delivery group."""
    from apps.whatsapp.order_store import get_db, get_order, add_dispatch_event
    conn = get_db()
    order = get_order(conn, order_id)
    if not order:
        conn.close()
        return {"ok": False, "error": "order not found"}

    group_jid = os.environ.get("R1_GROUP_JID", "")
    owner_phone = os.environ.get("R1_OWNER_PHONE", "")

    if not group_jid:
        _log_event("r1:dispatch:no_group", {"order_id": order_id})
        conn.close()
        return {"ok": False, "error": "no group configured"}

    # Format dispatch message
    items_str = ", ".join(f"{i['qty']}x {i['name']} (${i['price']})" for i in order.get("items", []))
    msg = (
        f"🚚 *NUEVO PEDIDO* #{order_id}\n\n"
        f"📦 *Producto:* {items_str}\n"
        f"💰 *Total:* ${order['total']}\n"
        f"📍 *Dirección:* {order.get('client_address', 'Pendiente')}\n"
        f"📱 *Cliente:* {order.get('client_phone', '')}\n"
        f"💳 *Pago:* {order.get('payment_method', 'pendiente').capitalize()}\n\n"
        f"¿Quién lo toma? Responde *Yo* + tu nombre"
    )

    ok = send_to_group(group_jid, msg)
    if not ok:
        conn.close()
        _log_event("r1:dispatch:send_failed", {"order_id": order_id})
        return {"ok": False, "error": "failed to send to group"}

    add_dispatch_event(conn, order_id)
    conn.close()
    _log_event("r1:dispatched", {"order_id": order_id, "group": group_jid})

    # Start background watcher
    dispatch_id = f"{order_id}@{time.time()}"
    with _lock:
        _active_dispatches[dispatch_id] = {
            "order_id": order_id,
            "group_jid": group_jid,
            "owner_phone": owner_phone,
            "dispatched_at": time.time(),
            "attempts": 1,
            "assigned": False,
        }

    threading.Thread(target=_watch_dispatch, args=(dispatch_id,), daemon=True).start()

    return {"ok": True, "dispatch_id": dispatch_id}


def _watch_dispatch(dispatch_id: str) -> None:
    """Background watcher: waits for assignment, handles timeout/redispatch."""
    time.sleep(RESPONSE_TIMEOUT * 60)

    with _lock:
        info = _active_dispatches.get(dispatch_id)
        if not info or info.get("assigned"):
            return

    # Nobody took it — redispatch or alert
    from apps.whatsapp.order_store import get_db, get_order

    conn = get_db()
    order = get_order(conn, info["order_id"])
    if not order:
        conn.close()
        return
    conn.close()

    current_attempts = info["attempts"]
    if current_attempts < MAX_REDISPATCH:
        # Re-dispatch
        msg = (
            f"⚠️ *REENVÍO* — Pedido #{info['order_id']}\n\n"
            f"¡Nadie tomó el pedido! ¿Quién lo atiende?\n\n"
            f"Responde *Yo* + tu nombre"
        )
        send_to_group(info["group_jid"], msg)
        info["attempts"] += 1
        info["dispatched_at"] = time.time()
        _log_event("r1:dispatch:redispatch", {
            "order_id": info["order_id"],
            "attempt": info["attempts"],
        })
        # Start another watcher
        threading.Thread(target=_watch_dispatch, args=(dispatch_id,), daemon=True).start()
    else:
        # Alert owner
        msg = (
            f"🔴 *PEDIDO SIN ASIGNAR* #{info['order_id']}\n\n"
            f"Se intentó {MAX_REDISPATCH} veces y nadie tomó el pedido.\n"
            f"📦 Total: ${order['total']}\n"
            f"📍 {order.get('client_address', '')}\n\n"
            f"Urge asignación manual."
        )
        if info["owner_phone"]:
            send_text(info["owner_phone"], msg)
        _log_event("r1:dispatch:escalated", {
            "order_id": info["order_id"],
            "attempts": current_attempts,
        })
        with _lock:
            _active_dispatches.pop(dispatch_id, None)


# ─── Assignment via WhatsApp ────────────────────────────────

def check_group_responses() -> None:
    """Poll for 'Yo' responses in group and assign orders."""
    group_jid = os.environ.get("R1_GROUP_JID", "")
    if not group_jid:
        return

    jid = group_jid if "@g.us" in group_jid else f"{group_jid}@g.us"
    result = _wacli(["messages", "list", "--chat", jid, "--limit", "10"])
    if not result.get("success"):
        return

    messages = result.get("data", [])
    if isinstance(messages, dict):
        messages = messages.get("messages", [])

    for msg in messages:
        text = (msg.get("text") or msg.get("body") or "").lower().strip()
        sender = msg.get("sender", "")
        if "@" in sender:
            sender = sender.split("@", 1)[0]

        # Detect "Yo" or "Yo [nombre]" or "Yo lo tomo"
        if not re.search(r'\byo\b', text):
            continue

        # Find which dispatch this matches (most recent unassigned)
        with _lock:
            candidates = [
                (did, info) for did, info in _active_dispatches.items()
                if not info["assigned"]
            ]

        if not candidates:
            continue

        # Take the most recent unassigned
        candidates.sort(key=lambda x: x[1]["dispatched_at"], reverse=True)
        dispatch_id, info = candidates[0]

        # Extract assignee name
        name = sender
        # Try to extract name after "Yo"
        import re
        m = re.search(r'yo\s+(.+)$', text)
        if m:
            name = m.group(1).strip().title()
        elif len(text.split()) >= 2:
            name = text.split()[1].title()

        # Assign in DB
        from apps.whatsapp.order_store import get_db, assign_order
        conn = get_db()
        order = assign_order(conn, info["order_id"], name)
        conn.close()

        if not order:
            continue

        info["assigned"] = True
        info["assigned_to"] = name

        # Notify group
        send_to_group(info["group_jid"],
            f"✅ *Pedido #{info['order_id']} asignado a {name}* 🙌")

        # Notify client
        client_phone = order.get("client_phone", "")
        if client_phone:
            send_text(client_phone,
                f"🙌 *Tu pedido #{info['order_id']} está en camino!*\n\n"
                f"Lo atenderá: *{name}*\n"
                f"Tiempo estimado: {DELIVERY_TIMEOUT} min\n"
                f"Te notificaremos cuando esté entregado.")

        _log_event("r1:assigned", {
            "order_id": info["order_id"],
            "assignee": name,
            "phone": sender,
        })

        # Start delivery timer
        threading.Thread(target=_watch_delivery, args=(info["order_id"], name, client_phone, info.get("owner_phone", "")), daemon=True).start()


def _watch_delivery(order_id: str, assignee: str, client_phone: str, owner_phone: str) -> None:
    """Monitor delivery time. Alert if exceeded."""
    time.sleep(DELIVERY_TIMEOUT * 60)

    from apps.whatsapp.order_store import get_db, get_order
    conn = get_db()
    order = get_order(conn, order_id)
    conn.close()

    if not order or order["status"] == "entregado":
        return

    # Time exceeded
    _log_event("r1:delivery:timeout", {
        "order_id": order_id,
        "assignee": assignee,
        "elapsed_min": DELIVERY_TIMEOUT,
    })

    if client_phone:
        send_text(client_phone,
            f"⏰ *Tu pedido #{order_id} está tomando más tiempo del esperado.*\n"
            f"Estamos revisando. Gracias por tu paciencia.")

    if owner_phone:
        send_text(owner_phone,
            f"⚠️ *PEDIDO #{order_id} EXCEDIÓ TIEMPO*\n"
            f"Repartidor: {assignee}\n"
            f"Tiempo límite: {DELIVERY_TIMEOUT} min\n"
            f"Cliente: {client_phone}")


# ─── Mark as Delivered ──────────────────────────────────────

def mark_delivered(order_id: str, by: str = "sistema") -> dict:
    from apps.whatsapp.order_store import get_db, update_order_status, get_order
    conn = get_db()
    order = update_order_status(conn, order_id, "entregado", actor=by)
    conn.close()

    if order:
        _log_event("r1:delivered", {"order_id": order_id, "by": by})
        # Notify client
        client_phone = order.get("client_phone", "")
        if client_phone:
            send_text(client_phone,
                f"✅ *Pedido #{order_id} entregado!*\n"
                f"¡Gracias por tu compra! 🙌")

    return {"ok": bool(order), "order": order}


# ─── Poller ─────────────────────────────────────────────────

def run_dispatch_poller(once: bool = False):
    print(f"[dispatch] Ce-Son Dispatch Poller started", file=sys.stderr)
    while True:
        try:
            check_group_responses()
        except Exception as e:
            print(f"[dispatch] Error: {e}", file=sys.stderr)
        if once:
            break
        time.sleep(5)


# ─── CLI ────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Ce-Son Dispatch Engine")
    parser.add_argument("action", nargs="?", default="poller",
                        choices=["poller", "dispatch", "delivered"],
                        help="Action to run")
    parser.add_argument("--order-id", help="Order ID for dispatch/delivered actions")
    parser.add_argument("--by", default="sistema", help="Who marked delivered")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    args = parser.parse_args()

    if args.action == "poller":
        run_dispatch_poller(once=args.once)
    elif args.action == "dispatch":
        if not args.order_id:
            print("--order-id required")
            sys.exit(1)
        result = dispatch_order(args.order_id)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.action == "delivered":
        if not args.order_id:
            print("--order-id required")
            sys.exit(1)
        result = mark_delivered(args.order_id, by=args.by)
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
