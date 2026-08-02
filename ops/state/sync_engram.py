#!/usr/bin/env python3
"""Engram ⇄ Git Sync — Exporta/importa memorias del tenant a JSON versionable.

Uso:
  python3 sync_engram.py export   → vuelca engram → ops/state/memory-snapshots/<tenant>.json
  python3 sync_engram.py import   → lee snapshot → engram (idempotente por key)

Así las memorias quedan versionadas en git y se pueden restaurar en otro entorno.
"""

import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime

ENGram_DB = os.getenv(
    "ENGRAM_DB",
    "/home/mystic/Documentos/Sonora Digital Corp/sonora-digital-corp/ops/state/engram.db",
)
SNAPSHOT_DIR = os.getenv(
    "SNAPSHOT_DIR",
    "/home/mystic/Documentos/Sonora Digital Corp/sonora-digital-corp/ops/state/memory-snapshots",
)


def _db_for_tenant(tenant: str) -> str:
    """Cada tenant tiene su propio engram: engram_<tenant>.db."""
    candidate = os.path.join(os.path.dirname(ENGram_DB), f"engram_{tenant}.db")
    if os.path.exists(candidate):
        return candidate
    return ENGram_DB


def _conn():
    return sqlite3.connect(ENGram_DB)


def export_snapshot(tenant: str) -> str:
    os.makedirs(SNAPSHOT_DIR, exist_ok=True)
    conn = sqlite3.connect(_db_for_tenant(tenant))
    rows = conn.execute(
        "SELECT key, value, user_id, layer, importance, tags, created_at FROM memories ORDER BY layer, key"
    ).fetchall()
    conn.close()
    records = [
        {"key": r[0], "value": r[1], "user_id": r[2], "layer": r[3],
         "importance": r[4], "tags": r[5], "created_at": r[6]}
        for r in rows
    ]
    out = os.path.join(SNAPSHOT_DIR, f"{tenant}.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(
            {"tenant": tenant, "exported_at": datetime.utcnow().isoformat() + "Z",
             "count": len(records), "records": records},
            f, ensure_ascii=False, indent=2,
        )
    print(f"Exportadas {len(records)} memorias → {out}")
    return out


def import_snapshot(tenant: str, path: str | None = None) -> int:
    if path is None:
        path = os.path.join(SNAPSHOT_DIR, f"{tenant}.json")
    if not os.path.exists(path):
        print(f"No existe snapshot: {path}")
        return 0
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    conn = sqlite3.connect(_db_for_tenant(tenant))
    n = 0
    for rec in data.get("records", []):
        conn.execute(
            """INSERT OR REPLACE INTO memories (key, value, user_id, layer, importance, tags, created_at)
               VALUES (?, ?, ?, ?, ?, ?, COALESCE(?, CURRENT_TIMESTAMP))""",
            (rec["key"], rec["value"], rec.get("user_id"), rec.get("layer", 0),
             rec.get("importance", 1), rec.get("tags", ""), rec.get("created_at")),
        )
        n += 1
    conn.commit()
    conn.close()
    print(f"Importadas {n} memorias desde {path}")
    return n


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["export", "import"])
    parser.add_argument("--tenant", default="aztrotech")
    parser.add_argument("--path", help="Snapshot path para import")
    args = parser.parse_args()

    if args.action == "export":
        export_snapshot(args.tenant)
    else:
        import_snapshot(args.tenant, args.path)


if __name__ == "__main__":
    sys.exit(main())
