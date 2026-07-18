"""Enterprise Demo Provisioning — Create a 7-day demo tenant for client prospecting.

César (or any partner) creates a demo for a potential client.
The demo is a fully functional digital brain that expires in 7 days.
If client buys, the demo is migrated to a full enterprise tenant.

Usage:
  python3 scripts/demo_provision.py --partner aztrotech --client "Juan Pérez" --email juan@empresa.com
  python3 scripts/demo_provision.py --partner aztrotech --list
"""

import argparse
import json
import os
import sqlite3
import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))


def _get_db() -> sqlite3.Connection:
    db_path = Path(os.environ.get("DEMO_DB_PATH", str(REPO / "data" / "demo.db")))
    os.makedirs(db_path.parent, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def _init_db():
    conn = _get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS demos (
            id TEXT PRIMARY KEY,
            partner_id TEXT NOT NULL,
            client_name TEXT NOT NULL,
            client_email TEXT DEFAULT '',
            status TEXT DEFAULT 'active',
            demo_url TEXT,
            qr_data TEXT,
            viewed INTEGER DEFAULT 0,
            converted INTEGER DEFAULT 0,
            expires_at TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );
    """)
    conn.commit()
    conn.close()


def load_packages() -> dict:
    import yaml
    path = REPO / "config" / "packages.yaml"
    if path.exists():
        with open(path) as f:
            return yaml.safe_load(f) or {}
    return {}


def get_partner_branding(partner_id: str) -> dict:
    """Get partner branding from tenants.yaml for the demo page."""
    import yaml
    path = REPO / "config" / "tenants.yaml"
    if not path.exists():
        return {"name": partner_id.capitalize(), "primary_color": "#7c3aed"}
    with open(path) as f:
        config = yaml.safe_load(f) or {}
    for p in config.get("partners", []):
        if p["id"] == partner_id:
            return p.get("branding", {"name": p["name"], "primary_color": "#7c3aed"})
    return {"name": partner_id.capitalize(), "primary_color": "#7c3aed"}


async def create_demo(partner_id: str, client_name: str, client_email: str = "") -> str:
    if not partner_id or not client_name:
        return json.dumps({"error": "partner_id and client_name are required"})

    _init_db()
    conn = _get_db()

    demo_id = uuid.uuid4().hex[:12]
    branding = get_partner_branding(partner_id)
    expires = (datetime.now() + timedelta(days=7)).isoformat()

    demo_url = f"https://demo.aztrotech.mx/d/{demo_id}" if partner_id == "aztrotech" else f"https://demo.sonoradigitalcorp.com/d/{demo_id}"
    qr_data = f"demo:sdc:{demo_id}"

    conn.execute(
        """INSERT INTO demos
           (id, partner_id, client_name, client_email, status, demo_url, qr_data, expires_at)
           VALUES (?, ?, ?, ?, 'active', ?, ?, ?)""",
        (demo_id, partner_id, client_name, client_email, demo_url, qr_data, expires),
    )
    conn.commit()
    conn.close()

    return json.dumps({
        "demo_id": demo_id,
        "partner_id": partner_id,
        "client_name": client_name,
        "client_email": client_email,
        "demo_url": demo_url,
        "qr_data": qr_data,
        "expires_at": expires,
        "expires_in_days": 7,
        "branding": branding,
        "powered_by_sdc": True,
        "message": f"Demo creada para {client_name}. Expira en 7 días. URL: {demo_url}",
    })


async def list_demos(partner_id: str = "") -> str:
    _init_db()
    conn = _get_db()

    if partner_id:
        rows = conn.execute(
            "SELECT * FROM demos WHERE partner_id = ? ORDER BY created_at DESC", (partner_id,)
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM demos ORDER BY created_at DESC").fetchall()

    conn.close()
    return json.dumps({
        "count": len(rows),
        "demos": [dict(r) for r in rows],
        "partner_filter": partner_id or "all",
    })


async def mark_converted(demo_id: str, deal_id: int = 0) -> str:
    _init_db()
    conn = _get_db()
    conn.execute("UPDATE demos SET converted = 1, status = 'converted' WHERE id = ?", (demo_id,))
    conn.commit()
    conn.close()
    return json.dumps({"demo_id": demo_id, "status": "converted", "deal_id": deal_id})


def main():
    parser = argparse.ArgumentParser(description="SDC Enterprise Demo Provisioning")
    parser.add_argument("--partner", required=True, help="Partner ID (aztrotech)")
    parser.add_argument("--client", default="", help="Client name for demo")
    parser.add_argument("--email", default="", help="Client email (optional)")
    parser.add_argument("--list", action="store_true", help="List demos for partner")
    parser.add_argument("--convert", metavar="DEMO_ID", help="Mark a demo as converted")

    args = parser.parse_args()

    import asyncio

    if args.convert:
        result = asyncio.run(mark_converted(args.convert))
    elif args.list:
        result = asyncio.run(list_demos(args.partner))
    else:
        if not args.client:
            print(json.dumps({"error": "client name required (use --client)"}))
            return
        result = asyncio.run(create_demo(args.partner, args.client, args.email))

    print(result)


if __name__ == "__main__":
    main()
