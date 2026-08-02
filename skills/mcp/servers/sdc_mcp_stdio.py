#!/usr/bin/env python3
"""SDC MCP Server (stdio) — Local tools for engram, rag, and LLM.

Exposes memory, knowledge retrieval, and chat as native MCP tools.
Uses OpenRouter for embeddings and chat (no Ollama needed).
"""

import json
import os
import sys
import time
from pathlib import Path

from fastmcp import FastMCP

ENGRAM_DIR = os.getenv("ENGRAM_DIR", str(Path(__file__).resolve().parent.parent.parent / "ops" / "state"))
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_URL = os.getenv("OPENROUTER_URL", "https://openrouter.ai/api/v1")
EMBED_MODEL = os.getenv("EMBED_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
LLM_MODEL = os.getenv("LLM_MODEL", "deepseek/deepseek-v4-flash")

mcp = FastMCP("sdc-mcp-local")

_embed_model = None


def _get_embedding(text: str) -> list[float]:
    """Embedding local FastEmbed (ONNX) — coincide con la colección Qdrant de 384 dims."""
    global _embed_model
    try:
        from fastembed import TextEmbedding
        if _embed_model is None:
            _embed_model = TextEmbedding(model_name=EMBED_MODEL)
        return list(_embed_model.embed([text]))[0].tolist()
    except Exception:
        return [0.0] * 384


def _get_db(tenant_id: str):
    import sqlite3
    Path(ENGRAM_DIR).mkdir(parents=True, exist_ok=True)
    db_path = os.path.join(ENGRAM_DIR, f"engram_{tenant_id}.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute(
        """
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
        """
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_memories_key ON memories(key)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_memories_user ON memories(user_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_memories_layer ON memories(layer)")
    try:
        conn.execute(
            "CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts USING fts5(key, value, tags, content='memories', content_rowid='id')"
        )
    except sqlite3.OperationalError:
        pass
    return conn


@mcp.tool(description="Estado del servidor SDC MCP local")
def sdc_status() -> dict:
    return {
        "status": "running",
        "engram_dir": ENGRAM_DIR,
        "qdrant_url": QDRANT_URL,
        "openrouter_configured": bool(OPENROUTER_API_KEY),
        "embed_model": EMBED_MODEL,
        "llm_model": LLM_MODEL,
    }


@mcp.tool(description="Guarda un recuerdo en la memoria engram del tenant")
def engram_save(tenant_id: str, key: str, value: str, user_id: str = "", layer: int = 0, importance: int = 1, tags: str = "") -> str:
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


@mcp.tool(description="Recupera un recuerdo de la memoria engram del tenant por clave")
def engram_get(tenant_id: str, key: str, user_id: str = "") -> str:
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


@mcp.tool(description="Busca recuerdos en la memoria engram del tenant por texto")
def engram_search(tenant_id: str, query: str, user_id: str = "", layer: int | None = None, limit: int = 10) -> str:
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


@mcp.tool(description="Lista las capas de memoria disponibles del engram")
def engram_list_layers(tenant_id: str, user_id: str = "") -> str:
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


@mcp.tool(description="Busca conocimiento en Qdrant por similitud semántica usando embeddings locales FastEmbed")
async def rag_search(tenant_id: str, query: str, collection: str = "sdc_knowledge", limit: int = 5, min_score: float = 0.65) -> str:
    if not tenant_id or not query:
        return json.dumps({"error": "tenant_id and query are required"})
    try:
        import httpx
        from qdrant_client import QdrantClient
        from qdrant_client.models import Filter, FieldCondition, MatchValue, Distance
        vector = _get_embedding(query)
        client = QdrantClient(url=QDRANT_URL, prefer_grpc=False)
        collections = [c.name for c in client.get_collections().collections]
        if collection not in collections:
            return json.dumps({"error": f"Collection '{collection}' not found. Available: {collections}"})
        hits = client.search(
            collection_name=collection,
            query_vector=vector,
            query_filter=Filter(must=[FieldCondition(key="tenant_id", match=MatchValue(value=tenant_id))]) if tenant_id else None,
            limit=limit,
        )
        results = []
        for hit in hits:
            if hit.score >= min_score:
                results.append({
                    "id": str(hit.id),
                    "score": round(hit.score, 4),
                    "payload": hit.payload,
                })
        return json.dumps({"results": results, "count": len(results), "collection": collection})
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool(description="Chat con OpenRouter para generar respuestas usando LLM")
async def llm_chat(messages: list, model: str = None, temperature: float = 0.7, max_tokens: int = 4096) -> str:
    if not OPENROUTER_API_KEY:
        return json.dumps({"error": "OPENROUTER_API_KEY not configured"})
    try:
        import httpx
        use_model = model or LLM_MODEL
        resp = httpx.post(
            f"{OPENROUTER_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "HTTP-Referer": "http://localhost",
                "X-Title": "SDC MCP",
            },
            json={
                "model": use_model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            },
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        choice = data.get("choices", [{}])[0]
        content = choice.get("message", {}).get("content", "")
        return json.dumps({"content": content, "model": use_model, "usage": data.get("usage", {})})
    except Exception as e:
        return json.dumps({"error": str(e)})


if __name__ == "__main__":
    mcp.run(transport="stdio")