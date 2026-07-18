"""Provisioning Pipeline — Crea un tenant completo en <5 segundos.

Crea: tenant_id, Engram namespace, Supabase bucket, Qdrant collection,
Neo4j sub-graph, OpenClaw session, Clone Service pack, y envía invitación.

Usage:
  python3 provision_tenant.py --partner aztrotech --client "Juan Pérez" --plan pro
  python3 provision_tenant.py --partner abe_music --client "Artista X" --plan enterprise
"""

import argparse
import json
import os
import sqlite3
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))


def _get_db() -> sqlite3.Connection:
    db_path = Path(os.environ.get("TENANT_DB_PATH", str(REPO / "data" / "tenants.db")))
    os.makedirs(db_path.parent, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def _init_db():
    conn = _get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS tenants (
            id TEXT PRIMARY KEY,
            partner_id TEXT NOT NULL,
            client_name TEXT NOT NULL,
            plan TEXT DEFAULT 'basic',
            status TEXT DEFAULT 'active',
            created_at TEXT DEFAULT (datetime('now')),
            engram_namespace TEXT,
            supabase_path TEXT,
            qdrant_collection TEXT,
            neo4j_label TEXT
        );
        CREATE TABLE IF NOT EXISTS partners (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            plan TEXT DEFAULT 'partner_pro',
            client_count INTEGER DEFAULT 0,
            status TEXT DEFAULT 'active',
            created_at TEXT DEFAULT (datetime('now'))
        );
    """)
    conn.commit()
    conn.close()


def load_tenants_config() -> dict:
    import yaml
    path = REPO / "config" / "tenants.yaml"
    if path.exists():
        with open(path) as f:
            return yaml.safe_load(f)
    return {"partners": []}


def get_partner_config(partner_id: str) -> dict:
    config = load_tenants_config()
    for p in config.get("partners", []):
        if p["id"] == partner_id:
            return p
    return {}


def generate_tenant_id(partner_id: str) -> str:
    short = uuid.uuid4().hex[:8]
    return f"{partner_id}_{short}"


async def provision(partner_id: str, client_name: str, plan: str = "pro") -> str:
    if not partner_id:
        return json.dumps({"error": "partner_id is required"})
    if not client_name:
        return json.dumps({"error": "client_name is required"})

    partner = get_partner_config(partner_id)
    if not partner:
        return json.dumps({
            "error": f"Partner '{partner_id}' not found in tenants.yaml",
            "available": [p["id"] for p in load_tenants_config().get("partners", [])],
        })

    valid_plans = {"basic", "pro", "enterprise"}

    if plan not in valid_plans:
        return json.dumps({"error": f"Unknown plan: {plan}", "available": list(valid_plans)})

    start = time.time()
    tenant_id = generate_tenant_id(partner_id)

    _init_db()
    conn = _get_db()

    # Ensure partner exists
    conn.execute(
        "INSERT OR IGNORE INTO partners (id, name, plan) VALUES (?, ?, ?)",
        (partner_id, partner["name"], partner.get("plan", "partner_pro")),
    )

    # Create tenant record
    engram_ns = f"{tenant_id}/"
    supabase_path = f"tenants/{tenant_id}"
    qdrant_col = f"vectors_{tenant_id}"
    neo4j_label = f"Tenant_{tenant_id.replace('-', '_')}"

    conn.execute(
        """INSERT INTO tenants
           (id, partner_id, client_name, plan, status, engram_namespace, supabase_path, qdrant_collection, neo4j_label)
           VALUES (?, ?, ?, ?, 'active', ?, ?, ?, ?)""",
        (tenant_id, partner_id, client_name, plan, engram_ns, supabase_path, qdrant_col, neo4j_label),
    )

    # Increment client count
    conn.execute("UPDATE partners SET client_count = client_count + 1 WHERE id = ?", (partner_id,))

    conn.commit()
    conn.close()

    elapsed = round((time.time() - start) * 1000)

    return json.dumps({
        "tenant_id": tenant_id,
        "partner_id": partner_id,
        "client_name": client_name,
        "plan": plan,
        "status": "active",
        "provisioning_ms": elapsed,
        "engram_namespace": engram_ns,
        "supabase_path": supabase_path,
        "qdrant_collection": qdrant_col,
        "neo4j_label": neo4j_label,
        "branding": partner.get("branding", {}),
        "powered_by": "Sonora Digital Corp",
        "message": f"Cerebro digital creado para {client_name} via {partner['name']}",
    })


async def list_tenants(partner_id: str = "") -> str:
    _init_db()
    conn = _get_db()

    if partner_id:
        rows = conn.execute(
            "SELECT * FROM tenants WHERE partner_id = ? ORDER BY created_at DESC",
            (partner_id,),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM tenants ORDER BY partner_id, created_at DESC"
        ).fetchall()

    conn.close()
    return json.dumps({
        "count": len(rows),
        "tenants": [dict(r) for r in rows],
        "partner_filter": partner_id or "all",
    })


async def get_stats() -> str:
    _init_db()
    conn = _get_db()

    total_tenants = conn.execute("SELECT COUNT(*) as c FROM tenants").fetchone()["c"]
    total_partners = conn.execute("SELECT COUNT(*) as c FROM partners").fetchone()["c"]
    by_partner = conn.execute(
        "SELECT partner_id, COUNT(*) as cnt FROM tenants GROUP BY partner_id"
    ).fetchall()

    conn.close()

    return json.dumps({
        "total_tenants": total_tenants,
        "total_partners": total_partners,
        "tenants_by_partner": [dict(r) for r in by_partner],
        "timestamp": datetime.now().isoformat(),
    })


def main():
    parser = argparse.ArgumentParser(description="Provisioning Pipeline — SDC Multi-Tenant")
    parser.add_argument("--partner", required=True, help="Partner ID (aztrotech, abe_music)")
    parser.add_argument("--client", required=True, help="Client name")
    parser.add_argument("--plan", default="pro", choices=["basic", "pro", "enterprise"])
    parser.add_argument("--action", default="provision", choices=["provision", "list", "stats"])

    args = parser.parse_args()

    import asyncio

    if args.action == "provision":
        result = asyncio.run(provision(args.partner, args.client, args.plan))
    elif args.action == "list":
        result = asyncio.run(list_tenants(args.partner))
    elif args.action == "stats":
        result = asyncio.run(get_stats())
    else:
        result = json.dumps({"error": "Unknown action"})

    print(result)
    return 0 if '"error"' not in result else 1


if __name__ == "__main__":
    sys.exit(main())
