#!/usr/bin/env python3
"""Memory API — interfaz unificada para las 3 capas de memoria [FR1-FR4]"""
import json
import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MEMORY_DIR = REPO / "state" / "memory"
POLICIES = MEMORY_DIR / "policies.yaml"


def load_policies():
    """Carga policies de memoria"""
    import yaml
    if POLICIES.exists():
        with open(POLICIES) as f:
            return yaml.safe_load(f)
    return {}


def get_db_path(layer):
    """Retorna path a la DB de una capa"""
    policies = load_policies()
    layers = policies.get("layers", {})
    if layer not in layers:
        raise ValueError(f"Unknown layer: {layer}. Available: {list(layers.keys())}")
    return MEMORY_DIR / layers[layer]["db"]


def get_conn(layer):
    """Retorna conexión a la DB de una capa"""
    db_path = get_db_path(layer)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def store(layer, spec_id, tag, summary, context=None, importance=0):
    """Almacena un recuerdo en la capa especificada"""
    policies = load_policies()
    layer_config = policies.get("layers", {}).get(layer, {})
    ttl = layer_config.get("ttl_seconds", -1)

    expires_at = None
    if ttl > 0:
        expires_at = (datetime.now(timezone.utc) + timedelta(seconds=ttl)).isoformat()

    conn = get_conn(layer)
    conn.execute(
        "INSERT INTO memories (spec_id, tag, summary, context, memory_layer, importance, expires_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (spec_id, tag, summary, context, {"working": 0, "project": 1, "organization": 2}.get(layer, 0),
         importance, expires_at)
    )
    conn.commit()
    row_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    # Sync FTS
    conn.execute("INSERT INTO memory_fts (rowid, summary, context) VALUES (?, ?, ?)",
                 (row_id, summary, context or ""))
    conn.commit()
    conn.close()
    return {"status": "stored", "id": row_id, "layer": layer, "ttl": ttl}


def query(layer, search=None, limit=10):
    """Busca recuerdos en una capa"""
    conn = get_conn(layer)

    if search:
        cursor = conn.execute(
            "SELECT m.id, m.spec_id, m.tag, m.summary, m.context, m.importance, m.timestamp, m.expires_at "
            "FROM memories m JOIN memory_fts fts ON m.id = fts.rowid "
            "WHERE memory_fts MATCH ? ORDER BY rank LIMIT ?",
            (search, limit)
        )
    else:
        cursor = conn.execute(
            "SELECT id, spec_id, tag, summary, context, importance, timestamp, expires_at "
            "FROM memories ORDER BY timestamp DESC LIMIT ?",
            (limit,)
        )

    results = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return results


def promote(memory_id, from_layer, to_layer):
    """Promueve un recuerdo de una capa a otra (ej: project → organization)"""
    conn = get_conn(from_layer)
    row = conn.execute("SELECT * FROM memories WHERE id = ?", (memory_id,)).fetchone()
    conn.close()

    if not row:
        return {"status": "error", "detail": f"Memory {memory_id} not found in {from_layer}"}

    result = store(to_layer, row["spec_id"], row["tag"], row["summary"], row["context"], row["importance"])
    # Delete from source
    conn = get_conn(from_layer)
    conn.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
    conn.execute("DELETE FROM memory_fts WHERE rowid = ?", (memory_id,))
    conn.commit()
    conn.close()

    return {"status": "promoted", "from": from_layer, "to": to_layer, "new_id": result["id"]}


def cleanup(layer):
    """Limpia recuerdos expirados de una capa"""
    policies = load_policies()
    layer_config = policies.get("layers", {}).get(layer, {})
    ttl = layer_config.get("ttl_seconds", -1)

    if ttl <= 0:
        return {"status": "skipped", "reason": "permanent layer"}

    conn = get_conn(layer)
    now = datetime.now(timezone.utc).isoformat()
    deleted = conn.execute("DELETE FROM memories WHERE expires_at IS NOT NULL AND expires_at < ?", (now,))
    count = deleted.rowcount
    conn.commit()
    conn.close()

    return {"status": "cleaned", "deleted": count}


def migrate_from_engram():
    """Migra datos de engram.db legacy a 02-organization.db"""
    old_db = REPO / "state" / "engram.db"
    if not old_db.exists():
        return {"status": "skipped", "reason": "no engram.db found"}

    old_conn = sqlite3.connect(str(old_db))
    rows = old_conn.execute("SELECT spec_id, tag, summary, context, timestamp FROM memories").fetchall()
    old_conn.close()

    migrated = 0
    for row in rows:
        conn = get_db_path("organization")
        c = sqlite3.connect(str(conn))
        c.execute(
            "INSERT INTO memories (spec_id, tag, summary, context, timestamp, memory_layer, importance) "
            "VALUES (?, ?, ?, ?, ?, 2, 1)",
            (row[0], row[1], row[2], row[3], row[4])
        )
        c.commit()
        c.close()
        migrated += 1

    return {"status": "migrated", "from": "engram.db", "to": "organization.db", "rows": migrated}


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Memory API")
    parser.add_argument("action", choices=["store", "query", "promote", "cleanup", "migrate", "status"])
    parser.add_argument("--layer", default="working", help="Memory layer")
    parser.add_argument("--tag", help="Memory tag")
    parser.add_argument("--summary", help="Memory summary")
    parser.add_argument("--context", help="Memory context")
    parser.add_argument("--search", help="FTS search query")
    parser.add_argument("--id", type=int, help="Memory ID")
    parser.add_argument("--to-layer", help="Target layer for promote")
    parser.add_argument("--limit", type=int, default=10)
    args = parser.parse_args()

    if args.action == "store":
        if not args.tag or not args.summary:
            print("ERROR: --tag and --summary required for store", file=sys.stderr)
            sys.exit(1)
        result = store(args.layer, None, args.tag, args.summary, args.context)
        print(json.dumps(result))

    elif args.action == "query":
        results = query(args.layer, args.search, args.limit)
        print(json.dumps(results, indent=2, default=str))

    elif args.action == "promote":
        if not args.id or not args.to_layer:
            print("ERROR: --id and --to-layer required for promote", file=sys.stderr)
            sys.exit(1)
        result = promote(args.id, args.layer, args.to_layer)
        print(json.dumps(result))

    elif args.action == "cleanup":
        result = cleanup(args.layer)
        print(json.dumps(result))

    elif args.action == "migrate":
        result = migrate_from_engram()
        print(json.dumps(result))

    elif args.action == "status":
        policies = load_policies()
        for layer, config in policies.get("layers", {}).items():
            conn = sqlite3.connect(str(MEMORY_DIR / config["db"]))
            count = conn.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
            conn.close()
            ttl_display = f"{config['ttl_seconds']}s" if config['ttl_seconds'] > 0 else "permanent"
            print(f"  {layer}: {count} rows, TTL={ttl_display}, max={config['max_rows']}")
