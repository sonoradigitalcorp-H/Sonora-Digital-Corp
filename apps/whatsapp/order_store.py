"""
Ce-Son Order Store — SQLite layer for orders, clients, sellers, events.
Full trazabilidad: cada cambio de estado queda registrado como evento.
"""
import json
import os
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

REPO = Path(__file__).resolve().parent.parent.parent
DEFAULT_DB = REPO / "state" / "whatsapp" / "clients" / "r1" / "orders.db"


def get_db(db_path: Optional[str] = None) -> sqlite3.Connection:
    path = db_path or str(DEFAULT_DB)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA busy_timeout=10000")
    _migrate(conn)
    return conn


def _migrate(conn: sqlite3.Connection) -> None:
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS sellers (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            phone TEXT UNIQUE NOT NULL,
            email TEXT,
            level TEXT DEFAULT 'bronce',
            tokens INTEGER DEFAULT 0,
            total_sales INTEGER DEFAULT 0,
            commission_rate REAL DEFAULT 0.05,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            active INTEGER DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS clients (
            id TEXT PRIMARY KEY,
            seller_id TEXT NOT NULL REFERENCES sellers(id),
            name TEXT NOT NULL,
            phone TEXT,
            address TEXT,
            lat REAL,
            lng REAL,
            frequency INTEGER DEFAULT 1,
            last_purchase TEXT,
            total_purchases INTEGER DEFAULT 0,
            total_spent REAL DEFAULT 0,
            favorite_flavor TEXT,
            tags TEXT DEFAULT '[]',
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            notes TEXT
        );

        CREATE TABLE IF NOT EXISTS orders (
            id TEXT PRIMARY KEY,
            seller_id TEXT,
            client_id TEXT,
            client_name TEXT,
            client_phone TEXT,
            client_address TEXT,
            items_json TEXT NOT NULL DEFAULT '[]',
            total REAL NOT NULL,
            payment_method TEXT,
            payment_status TEXT DEFAULT 'pendiente',
            status TEXT NOT NULL DEFAULT 'pendiente',
            assigned_to TEXT,
            assigned_at TEXT,
            delivered_at TEXT,
            dispatch_count INTEGER DEFAULT 0,
            commission_amount REAL DEFAULT 0,
            commission_paid INTEGER DEFAULT 0,
            notes TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT NOT NULL,
            timestamp TEXT NOT NULL DEFAULT (datetime('now')),
            event_type TEXT NOT NULL,
            actor TEXT DEFAULT 'sistema',
            metadata_json TEXT DEFAULT '{}'
        );

        CREATE TABLE IF NOT EXISTS token_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            seller_id TEXT NOT NULL REFERENCES sellers(id),
            amount INTEGER NOT NULL,
            reason TEXT NOT NULL,
            reference_type TEXT,
            reference_id TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS bundles (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            items_json TEXT NOT NULL DEFAULT '[]',
            price REAL NOT NULL,
            original_price REAL,
            discount_pct REAL DEFAULT 0,
            active INTEGER DEFAULT 1,
            valid_until TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS seller_badges (
            seller_id TEXT NOT NULL REFERENCES sellers(id),
            badge_id TEXT NOT NULL,
            earned_at TEXT NOT NULL DEFAULT (datetime('now')),
            PRIMARY KEY (seller_id, badge_id)
        );

        CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
        CREATE INDEX IF NOT EXISTS idx_orders_seller ON orders(seller_id);
        CREATE INDEX IF NOT EXISTS idx_orders_created ON orders(created_at);
        CREATE INDEX IF NOT EXISTS idx_events_order ON events(order_id);
        CREATE INDEX IF NOT EXISTS idx_clients_seller ON clients(seller_id);
    """)


# ─── Orders ──────────────────────────────────────────────────────

def create_order(conn: sqlite3.Connection, data: dict) -> dict:
    oid = f"ORD-{uuid.uuid4().hex[:8].upper()}"
    now = datetime.now(timezone.utc).isoformat()
    conn.execute("""
        INSERT INTO orders (id, seller_id, client_id, client_name, client_phone,
            client_address, items_json, total, payment_method, status, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (oid, data.get("seller_id"), data.get("client_id"),
          data.get("client_name"), data.get("client_phone"),
          data.get("client_address"),
          json.dumps(data.get("items", []), ensure_ascii=False),
          data["total"], data.get("payment_method"), "pendiente", now, now))
    _add_event(conn, oid, "order:created", "sistema", {"total": data["total"]})
    conn.commit()
    return get_order(conn, oid)


def get_order(conn: sqlite3.Connection, order_id: str) -> Optional[dict]:
    row = conn.execute("SELECT * FROM orders WHERE id=?", (order_id,)).fetchone()
    if not row:
        return None
    d = dict(row)
    d["items"] = json.loads(d.pop("items_json", "[]"))
    d["events"] = get_events(conn, order_id)
    return d


def list_orders(conn: sqlite3.Connection, seller_id: str = "", status: str = "",
                limit: int = 50, offset: int = 0) -> list[dict]:
    query = "SELECT * FROM orders WHERE 1=1"
    params = []
    if seller_id:
        query += " AND seller_id=?"
        params.append(seller_id)
    if status:
        query += " AND status=?"
        params.append(status)
    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    rows = conn.execute(query, params).fetchall()
    result = []
    for r in rows:
        d = dict(r)
        d["items"] = json.loads(d.pop("items_json", "[]"))
        result.append(d)
    return result


def update_order_status(conn: sqlite3.Connection, order_id: str,
                        status: str, actor: str = "sistema",
                        metadata: Optional[dict] = None) -> Optional[dict]:
    now = datetime.now(timezone.utc).isoformat()
    extra = ""
    params = [status, now]
    if status == "entregado":
        extra = ", delivered_at=?"
        params.append(now)
    elif status == "asignado":
        extra = ", assigned_at=?"
        params.append(now)
    params.append(order_id)
    conn.execute(f"UPDATE orders SET status=?, updated_at=?{extra} WHERE id=?", params)
    _add_event(conn, order_id, f"order:{status}", actor, metadata or {})
    conn.commit()
    return get_order(conn, order_id)


def add_dispatch_event(conn: sqlite3.Connection, order_id: str) -> None:
    conn.execute("UPDATE orders SET dispatch_count=dispatch_count+1 WHERE id=?", (order_id,))
    _add_event(conn, order_id, "order:dispatched", "sistema", {"count": get_order(conn, order_id).get("dispatch_count", 0) + 1})
    conn.commit()


def assign_order(conn: sqlite3.Connection, order_id: str, seller_name: str) -> Optional[dict]:
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        "UPDATE orders SET assigned_to=?, assigned_at=?, status=?, updated_at=? WHERE id=?",
        (seller_name, now, "asignado", now, order_id)
    )
    _add_event(conn, order_id, "order:assigned", seller_name, {})
    conn.commit()
    return get_order(conn, order_id)


# ─── Events (Trazabilidad) ─────────────────────────────────────

def _add_event(conn: sqlite3.Connection, order_id: str, event_type: str,
               actor: str, metadata: dict) -> None:
    conn.execute(
        "INSERT INTO events (order_id, event_type, actor, metadata_json) VALUES (?, ?, ?, ?)",
        (order_id, event_type, actor, json.dumps(metadata, ensure_ascii=False))
    )


def get_events(conn: sqlite3.Connection, order_id: str) -> list[dict]:
    rows = conn.execute(
        "SELECT * FROM events WHERE order_id=? ORDER BY id", (order_id,)
    ).fetchall()
    return [dict(r) for r in rows]


# ─── Sellers ─────────────────────────────────────────────────────

def register_seller(conn: sqlite3.Connection, name: str, phone: str,
                    email: str = "", commission_rate: float = 0.05) -> dict:
    sid = f"S-{uuid.uuid4().hex[:8].upper()}"
    conn.execute("""
        INSERT INTO sellers (id, name, phone, email, commission_rate)
        VALUES (?, ?, ?, ?, ?)
    """, (sid, name, phone, email, commission_rate))
    conn.commit()
    return get_seller(conn, sid)


def get_seller(conn: sqlite3.Connection, seller_id: str) -> Optional[dict]:
    row = conn.execute("SELECT * FROM sellers WHERE id=?", (seller_id,)).fetchone()
    return dict(row) if row else None


def get_seller_by_phone(conn: sqlite3.Connection, phone: str) -> Optional[dict]:
    row = conn.execute("SELECT * FROM sellers WHERE phone=?", (phone,)).fetchone()
    return dict(row) if row else None


def update_seller_tokens(conn: sqlite3.Connection, seller_id: str, amount: int,
                         reason: str, ref_type: str = "", ref_id: str = "") -> None:
    conn.execute("UPDATE sellers SET tokens=tokens+? WHERE id=?", (amount, seller_id))
    conn.execute("""
        INSERT INTO token_transactions (seller_id, amount, reason, reference_type, reference_id)
        VALUES (?, ?, ?, ?, ?)
    """, (seller_id, amount, reason, ref_type, ref_id))
    conn.commit()


# ─── Clients ─────────────────────────────────────────────────────

def register_client(conn: sqlite3.Connection, seller_id: str, name: str,
                    phone: str = "", address: str = "", lat: float = 0, lng: float = 0) -> dict:
    cid = f"C-{uuid.uuid4().hex[:8].upper()}"
    conn.execute("""
        INSERT INTO clients (id, seller_id, name, phone, address, lat, lng)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (cid, seller_id, name, phone, address, lat, lng))
    conn.commit()
    return get_client(conn, cid)


def get_client(conn: sqlite3.Connection, client_id: str) -> Optional[dict]:
    row = conn.execute("SELECT * FROM clients WHERE id=?", (client_id,)).fetchone()
    if not row:
        return None
    d = dict(row)
    d["tags"] = json.loads(d.get("tags", "[]"))
    return d


def list_seller_clients(conn: sqlite3.Connection, seller_id: str) -> list[dict]:
    rows = conn.execute("SELECT * FROM clients WHERE seller_id=? ORDER BY total_purchases DESC", (seller_id,)).fetchall()
    return [dict(r) for r in rows]


def update_client_purchase(conn: sqlite3.Connection, client_id: str,
                           flavor: str, amount: float) -> None:
    now = datetime.now(timezone.utc).isoformat()
    conn.execute("""
        UPDATE clients SET
            frequency=frequency+1, last_purchase=?, total_purchases=total_purchases+1,
            total_spent=total_spent+?, favorite_flavor=?
        WHERE id=?
    """, (now, amount, flavor, client_id))
    conn.commit()


# ─── Gamification / Badges ──────────────────────────────────────

BADGES = {
    "primera_venta": {"name": "Primera Venta", "icon": "🏆", "desc": "Realiza tu primera venta"},
    "cinco_diarias": {"name": "5 en el Día", "icon": "⚡", "desc": "5 ventas en un solo día"},
    "cliente_recurrente": {"name": "Frecuente", "icon": "🔄", "desc": "Mismo cliente 3+ veces"},
    "sabor_popular": {"name": "Sabor Popular", "icon": "🍇", "desc": "Mayoría de ventas de un sabor"},
    "racha_7": {"name": "Racha 7 Días", "icon": "🔥", "desc": "Ventas 7 días seguidos"},
    "referidor": {"name": "Referidor", "icon": "🤝", "desc": "Trajo a otro vendedor"},
    "10k_club": {"name": "Club 10K", "icon": "💎", "desc": "$10,000 en ventas totales"},
}


def award_badge(conn: sqlite3.Connection, seller_id: str, badge_id: str) -> bool:
    if badge_id not in BADGES:
        return False
    conn.execute("INSERT OR IGNORE INTO seller_badges (seller_id, badge_id) VALUES (?, ?)",
                 (seller_id, badge_id))
    conn.commit()
    return True


def get_seller_badges(conn: sqlite3.Connection, seller_id: str) -> list[dict]:
    rows = conn.execute("""
        SELECT sb.badge_id, sb.earned_at, ? as badge_json
        FROM seller_badges sb WHERE sb.seller_id=?
    """, (json.dumps(BADGES), seller_id)).fetchall()
    result = []
    for r in rows:
        d = dict(r)
        all_badges = json.loads(d.pop("badge_json", "{}"))
        d.update(all_badges.get(d["badge_id"], {}))
        result.append(d)
    return result


# ─── Stats / Reports ────────────────────────────────────────────

def seller_dashboard(conn: sqlite3.Connection, seller_id: str) -> dict:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    seller = get_seller(conn, seller_id)
    if not seller:
        return {}
    orders = list_orders(conn, seller_id=seller_id)
    today_orders = [o for o in orders if o["created_at"][:10] == today]
    total_revenue = sum(o["total"] for o in orders)
    today_revenue = sum(o["total"] for o in today_orders)
    by_flavor = {}
    for o in orders:
        for item in o.get("items", []):
            f = item.get("flavor", "desconocido")
            by_flavor[f] = by_flavor.get(f, 0) + item.get("qty", 1)
    top_flavor = max(by_flavor, key=by_flavor.get) if by_flavor else "N/A"
    pending = len([o for o in orders if o["status"] in ("pendiente", "asignado")])
    badges = get_seller_badges(conn, seller_id)
    return {
        "seller": seller,
        "total_orders": len(orders),
        "total_revenue": total_revenue,
        "today_orders": len(today_orders),
        "today_revenue": today_revenue,
        "pending_orders": pending,
        "top_flavor": top_flavor,
        "sales_by_flavor": by_flavor,
        "badges": badges,
        "tokens": seller.get("tokens", 0),
    }


def owner_report(conn: sqlite3.Connection) -> dict:
    """Reporte global para el dueño de la plataforma."""
    orders = conn.execute("SELECT * FROM orders").fetchall()
    sellers = conn.execute("SELECT * FROM sellers").fetchall()
    total_revenue = sum(dict(o)["total"] for o in orders)
    total_commissions = sum(dict(o).get("commission_amount", 0) for o in orders)
    by_status = {}
    for o in orders:
        s = dict(o)["status"]
        by_status[s] = by_status.get(s, 0) + 1
    return {
        "total_orders": len(orders),
        "total_sellers": len(sellers),
        "total_revenue": total_revenue,
        "total_commissions": total_commissions,
        "orders_by_status": by_status,
    }
