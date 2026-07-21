"""Engram Memory MCP Server — Per-tenant memory with FTS5.

Exposes memory save, get, and search as native MCP tools for agents.
7-layer memory system: working(0), task(1), project(2), customer(3),
business(4), historical(5), strategic(6).
"""

import json
import os
import sqlite3
import time
from pathlib import Path

ENGRAM_DIR = os.getenv("ENGRAM_DIR", "/home/ubuntu/sonora-digital-corp/state/engram")


def _get_db(tenant_id: str) -> sqlite3.Connection:
    Path(ENGRAM_DIR).mkdir(parents=True, exist_ok=True)
    db_path = os.path.join(ENGRAM_DIR, f"engram_{tenant_id}.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL DEFAULT '',
            key TEXT NOT NULL,
            value TEXT NOT NULL,
            layer INTEGER NOT NULL DEFAULT 0,
            importance INTEGER NOT NULL DEFAULT 1,
            tags TEXT NOT NULL DEFAULT '',
            access_count INTEGER NOT NULL DEFAULT 0,
            created_at REAL NOT NULL,
            accessed_at REAL NOT NULL
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_memories_key ON memories(key)
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_memories_user ON memories(user_id)
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_memories_layer ON memories(layer)
    """)
    try:
        conn.execute("CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts USING fts5(key, value, tags, content='memories', content_rowid='id')")
    except sqlite3.OperationalError:
        pass
    return conn


async def engram_save(tenant_id: str, key: str, value: str, user_id: str = "", layer: int = 0, importance: int = 1, tags: str = "") -> str:
    if not tenant_id or not key:
        return json.dumps({"error": "tenant_id and key are required"})
    try:
        conn = _get_db(tenant_id)
        now = time.time()
        existing = conn.execute("SELECT id FROM memories WHERE key=? AND user_id=?", (key, user_id)).fetchone()
        if existing:
            conn.execute(
                "UPDATE memories SET value=?, layer=?, importance=?, tags=?, accessed_at=? WHERE id=?",
                (value, layer, importance, tags, now, existing["id"]),
            )
            mem_id = existing["id"]
        else:
            cur = conn.execute(
                "INSERT INTO memories (user_id, key, value, layer, importance, tags, created_at, accessed_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (user_id, key, value, layer, importance, tags, now, now),
            )
            mem_id = cur.lastrowid
        try:
            conn.execute("INSERT INTO memories_fts(rowid, key, value, tags) VALUES (?, ?, ?, ?)", (mem_id, key, value, tags))
        except sqlite3.OperationalError:
            pass
        conn.commit()
        conn.close()
        return json.dumps({"saved": True, "id": mem_id, "key": key})
    except Exception as e:
        return json.dumps({"error": str(e)})


async def engram_get(tenant_id: str, key: str, user_id: str = "") -> str:
    if not tenant_id or not key:
        return json.dumps({"error": "tenant_id and key are required"})
    try:
        conn = _get_db(tenant_id)
        if user_id:
            row = conn.execute("SELECT * FROM memories WHERE key=? AND user_id=?", (key, user_id)).fetchone()
        else:
            row = conn.execute("SELECT * FROM memories WHERE key=?", (key,)).fetchone()
        if not row:
            conn.close()
            return json.dumps({"found": False})
        conn.execute("UPDATE memories SET access_count=access_count+1, accessed_at=? WHERE id=?", (time.time(), row["id"]))
        conn.commit()
        conn.close()
        return json.dumps({
            "found": True,
            "id": row["id"],
            "key": row["key"],
            "value": row["value"],
            "user_id": row["user_id"],
            "layer": row["layer"],
            "importance": row["importance"],
            "tags": row["tags"],
            "access_count": row["access_count"] + 1,
            "created_at": row["created_at"],
        })
    except Exception as e:
        return json.dumps({"error": str(e)})


async def engram_search(tenant_id: str, query: str, user_id: str = "", layer: int | None = None, limit: int = 10) -> str:
    if not tenant_id or not query:
        return json.dumps({"error": "tenant_id and query are required"})
    try:
        conn = _get_db(tenant_id)
        try:
            sql = """
                SELECT m.* FROM memories m
                JOIN memories_fts fts ON m.id = fts.rowid
                WHERE memories_fts MATCH ?
            """
            params: list = [query]
            if user_id:
                sql += " AND m.user_id=?"
                params.append(user_id)
            if layer is not None:
                sql += " AND m.layer=?"
                params.append(layer)
            sql += " ORDER BY m.importance DESC, m.accessed_at DESC LIMIT ?"
            params.append(limit)
            rows = conn.execute(sql, params).fetchall()
        except sqlite3.OperationalError:
            rows = conn.execute(
                "SELECT * FROM memories WHERE key LIKE ? OR value LIKE ? OR tags LIKE ? ORDER BY importance DESC, accessed_at DESC LIMIT ?",
                (f"%{query}%", f"%{query}%", f"%{query}%", limit),
            ).fetchall()
        conn.close()
        results = []
        for row in rows:
            results.append({
                "id": row["id"],
                "key": row["key"],
                "value": row["value"][:500],
                "user_id": row["user_id"],
                "layer": row["layer"],
                "importance": row["importance"],
                "tags": row["tags"],
                "access_count": row["access_count"],
                "created_at": row["created_at"],
            })
        return json.dumps({"results": results, "count": len(results)})
    except Exception as e:
        return json.dumps({"error": str(e)})


async def engram_list_layers(tenant_id: str, user_id: str = "") -> str:
    if not tenant_id:
        return json.dumps({"error": "tenant_id is required"})
    layers = {}
    for layer_id, layer_name in [(0, "working"), (1, "task"), (2, "project"), (3, "customer"), (4, "business"), (5, "historical"), (6, "strategic")]:
        layers[layer_name] = {"id": layer_id, "description": _layer_desc(layer_id)}
    return json.dumps({"layers": layers})


def _layer_desc(layer_id: int) -> str:
    return {
        0: "Working memory — current session context",
        1: "Task memory — active tasks and their state",
        2: "Project memory — ongoing projects",
        3: "Customer memory — per-customer knowledge",
        4: "Business memory — business metrics and KPIs",
        5: "Historical memory — past sessions and decisions",
        6: "Strategic memory — long-term goals and patterns",
    }.get(layer_id, "Unknown")


MCP_TOOLS = {
    "engram_save": {
        "description": "Save a memory for a tenant/user with a key-value pair",
        "input_schema": {
            "type": "object",
            "properties": {
                "tenant_id": {"type": "string", "description": "Tenant ID"},
                "key": {"type": "string", "description": "Memory key"},
                "value": {"type": "string", "description": "Memory value/content"},
                "user_id": {"type": "string", "description": "User ID (optional)"},
                "layer": {"type": "integer", "description": "Memory layer 0-6 (default: 0 working)"},
                "importance": {"type": "integer", "description": "Importance 1-3 (default: 1)"},
                "tags": {"type": "string", "description": "Space-separated tags for search (optional)"},
            },
            "required": ["tenant_id", "key", "value"],
        },
        "handler": lambda args: engram_save(
            args["tenant_id"], args["key"], args["value"],
            args.get("user_id", ""), args.get("layer", 0),
            args.get("importance", 1), args.get("tags", ""),
        ),
    },
    "engram_get": {
        "description": "Retrieve a memory by key for a tenant/user",
        "input_schema": {
            "type": "object",
            "properties": {
                "tenant_id": {"type": "string", "description": "Tenant ID"},
                "key": {"type": "string", "description": "Memory key"},
                "user_id": {"type": "string", "description": "User ID (optional)"},
            },
            "required": ["tenant_id", "key"],
        },
        "handler": lambda args: engram_get(args["tenant_id"], args["key"], args.get("user_id", "")),
    },
    "engram_search": {
        "description": "Search memories by text query with FTS5",
        "input_schema": {
            "type": "object",
            "properties": {
                "tenant_id": {"type": "string", "description": "Tenant ID"},
                "query": {"type": "string", "description": "Search query"},
                "user_id": {"type": "string", "description": "Filter by user (optional)"},
                "layer": {"type": "integer", "description": "Filter by layer (optional)"},
                "limit": {"type": "integer", "description": "Max results (default: 10)"},
            },
            "required": ["tenant_id", "query"],
        },
        "handler": lambda args: engram_search(
            args["tenant_id"], args["query"],
            args.get("user_id", ""), args.get("layer"),
            args.get("limit", 10),
        ),
    },
    "engram_list_layers": {
        "description": "List available memory layers with descriptions",
        "input_schema": {
            "type": "object",
            "properties": {
                "tenant_id": {"type": "string", "description": "Tenant ID"},
                "user_id": {"type": "string", "description": "User ID (optional)"},
            },
            "required": ["tenant_id"],
        },
        "handler": lambda args: engram_list_layers(args["tenant_id"], args.get("user_id", "")),
    },
}
