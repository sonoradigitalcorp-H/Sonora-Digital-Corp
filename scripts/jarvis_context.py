"""JARVIS Context Engine — Multi-source context retrieval for conversations.

Aggregates context from Redis (cache), Engram (SQLite FTS), Postgres (DB),
Qdrant (semantic search), with OpenRouter fallback.

Usage:
    from jarvis_context import get_full_context
    ctx = await get_full_context("¿Cómo van las ventas?", user_id="sergio")
"""

import asyncio
import json
import os
import sqlite3
import time
from datetime import datetime
from pathlib import Path

import asyncpg
import httpx

# ─── Config ──────────────────────────────────────────────────────────────────

DB_URL = os.getenv("DATABASE_URL", "postgresql://sdc:sdc_local_dev@localhost:5432/sdc")
ENGRAM_DB = Path(os.getenv(
    "ENGRAM_DB_PATH",
    Path(__file__).resolve().parent.parent.parent / "ops" / "state" / "engram_aztrotech.db",
))
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
CACHE_TTL = 300  # 5 minutes

# ─── Engram Client (SQLite FTS) ─────────────────────────────────────────────


class EngramClient:
    """Search engram memory via SQLite full-text search."""

    def __init__(self, db_path: str | Path = ENGRAM_DB):
        self.db_path = Path(db_path)

    def available(self) -> bool:
        return self.db_path.exists()

    def search(self, query: str, limit: int = 5) -> list[dict]:
        if not self.available():
            return []
        try:
            conn = sqlite3.connect(str(self.db_path), timeout=5)
            conn.row_factory = sqlite3.Row
            # Try FTS5 first, fallback to LIKE
            try:
                rows = conn.execute(
                    "SELECT * FROM engram_fts WHERE engram_fts MATCH ? LIMIT ?",
                    (query, limit),
                ).fetchall()
            except sqlite3.OperationalError:
                rows = conn.execute(
                    "SELECT * FROM memories WHERE value LIKE ? LIMIT ?",
                    (f"%{query}%", limit),
                ).fetchall()
            conn.close()
            return [dict(r) for r in rows]
        except Exception:
            return []

    async def async_search(self, query: str, limit: int = 5) -> list[dict]:
        return await asyncio.get_event_loop().run_in_executor(None, self.search, query, limit)


# ─── Postgres Client ────────────────────────────────────────────────────────


class PostgresClient:
    """Query conversations, leads, and daily_metrics from SDC database."""

    def __init__(self, dsn: str = DB_URL):
        self.dsn = dsn
        self._pool: asyncpg.Pool | None = None

    async def _get_pool(self) -> asyncpg.Pool:
        if self._pool is None:
            self._pool = await asyncpg.create_pool(self.dsn, min_size=1, max_size=3)
        return self._pool

    async def search_conversations(self, query: str, limit: int = 5) -> list[dict]:
        try:
            pool = await self._get_pool()
            rows = await pool.fetch(
                """SELECT c.id, c.lead_type, c.language, c.started_at,
                          m.content, m.role
                   FROM conversations c
                   JOIN messages m ON m.conversation_id = c.id
                   WHERE m.content ILIKE $1
                   ORDER BY c.started_at DESC LIMIT $2""",
                f"%{query}%", limit,
            )
            return [dict(r) for r in rows]
        except Exception:
            return []

    async def search_leads(self, query: str, limit: int = 5) -> list[dict]:
        try:
            pool = await self._get_pool()
            rows = await pool.fetch(
                """SELECT id, name, phone, lead_score, lead_type, created_at
                   FROM leads
                   WHERE name ILIKE $1 OR phone ILIKE $1
                   ORDER BY created_at DESC LIMIT $2""",
                f"%{query}%", limit,
            )
            return [dict(r) for r in rows]
        except Exception:
            return []

    async def get_daily_metrics(self) -> dict:
        try:
            pool = await self._get_pool()
            row = await pool.fetchrow(
                """SELECT
                     COUNT(*) FILTER (WHERE started_at::date = CURRENT_DATE) as today_conversations,
                     COUNT(*) FILTER (WHERE started_at::date = CURRENT_DATE - 1) as yesterday_conversations
                   FROM conversations"""
            )
            return dict(row) if row else {}
        except Exception:
            return {}

    async def close(self):
        if self._pool:
            await self._pool.close()
            self._pool = None


# ─── Qdrant Client ──────────────────────────────────────────────────────────


class QdrantSearch:
    """Semantic search on sdc_knowledge collection via Qdrant REST API."""

    def __init__(self, base_url: str = QDRANT_URL):
        self.base_url = base_url.rstrip("/")
        self.collection = "sdc_knowledge"

    async def search(self, query: str, limit: int = 5, min_score: float = 0.6) -> list[dict]:
        try:
            # Use local FastEmbed for embedding (sync, run in executor)
            payload = {
                "vector": await self._embed(query),
                "limit": limit,
                "score_threshold": min_score,
                "with_payload": True,
            }
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.post(
                    f"{self.base_url}/collections/{self.collection}/points/search",
                    json=payload,
                )
                if resp.status_code == 200:
                    results = resp.json().get("result", [])
                    return [
                        {"content": r.get("payload", {}).get("text", ""), "score": r.get("score", 0)}
                        for r in results
                    ]
        except Exception:
            pass
        return []

    async def _embed(self, text: str) -> list[float]:
        """Generate embedding using FastEmbed (local) or zeros."""
        try:
            from fastembed import TextEmbedding
            model = TextEmbedding("BAAI/bge-small-en-v1.5")
            embeddings = list(model.embed([text]))
            return embeddings[0].tolist() if embeddings else [0.0] * 384
        except ImportError:
            return [0.0] * 384


# ─── Redis Client (cache) ───────────────────────────────────────────────────


class RedisCache:
    """Simple async Redis cache with TTL."""

    def __init__(self, url: str = REDIS_URL):
        self.url = url
        self._pool = None

    async def _get_pool(self):
        if self._pool is None:
            try:
                import redis.asyncio as aioredis
                self._pool = await aioredis.from_url(self.url, decode_responses=True)
            except ImportError:
                return None
        return self._pool

    async def get(self, key: str) -> str | None:
        pool = await self._get_pool()
        if pool is None:
            return None
        try:
            return await pool.get(key)
        except Exception:
            return None

    async def set(self, key: str, value: str, ttl: int = CACHE_TTL):
        pool = await self._get_pool()
        if pool is None:
            return
        try:
            await pool.set(key, value, ex=ttl)
        except Exception:
            pass

    async def close(self):
        if self._pool:
            await self._pool.close()
            self._pool = None


# ─── OpenRouter Fallback ────────────────────────────────────────────────────


async def openrouter_fallback(query: str, partial_context: dict) -> dict:
    """Use OpenRouter LLM as last resort for context enrichment."""
    if not OPENROUTER_KEY:
        return {}

    try:
        context_summary = json.dumps(partial_context, default=str, ensure_ascii=False)[:2000]
        messages = [
            {"role": "system", "content": "Eres el asistente JARVIS de Sonora Digital Corp. Resume el contexto relevante para la query del usuario."},
            {"role": "user", "content": f"Contexto parcial:\n{context_summary}\n\nQuery: {query}\n\nProporciona un resumen conciso del contexto relevante."},
        ]
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {OPENROUTER_KEY}"},
                json={"model": OPENROUTER_MODEL, "messages": messages, "max_tokens": 300},
            )
            if resp.status_code == 200:
                data = resp.json()
                return {"openrouter_summary": data["choices"][0]["message"]["content"]}
    except Exception:
        pass
    return {}


# ─── Main Context Aggregator ────────────────────────────────────────────────


async def get_full_context(query: str, user_id: str = "") -> dict:
    """Aggregate context from all sources with priority chain.

    Priority: Redis cache -> Engram -> Postgres -> Qdrant -> OpenRouter fallback.
    """
    cache_key = f"jarvis:ctx:{user_id}:{query[:64].lower().replace(' ', '_')}"
    engram = EngramClient()
    postgres = PostgresClient()
    qdrant = QdrantSearch()
    cache = RedisCache()

    result = {
        "query": query,
        "user_id": user_id,
        "sources": {},
        "cached": False,
        "timestamp": datetime.now().isoformat(),
    }

    # 1. Check Redis cache
    cached = await cache.get(cache_key)
    if cached:
        result["sources"]["cache"] = json.loads(cached)
        result["cached"] = True
        await cache.close()
        return result

    # 2. Engram (local memory)
    engram_results = await engram.async_search(query)
    if engram_results:
        result["sources"]["engram"] = engram_results

    # 3. Postgres (conversations + leads)
    convos, leads, metrics = await asyncio.gather(
        postgres.search_conversations(query),
        postgres.search_leads(query),
        postgres.get_daily_metrics(),
        return_exceptions=True,
    )
    if not isinstance(convos, Exception) and convos:
        result["sources"]["conversations"] = convos
    if not isinstance(leads, Exception) and leads:
        result["sources"]["leads"] = leads
    if not isinstance(metrics, Exception) and metrics:
        result["sources"]["metrics"] = metrics

    # 4. Qdrant (semantic knowledge)
    qdrant_results = await qdrant.search(query)
    if qdrant_results:
        result["sources"]["knowledge"] = qdrant_results

    # 5. OpenRouter fallback if no meaningful results
    if not result["sources"]:
        fallback = await openrouter_fallback(query, result)
        if fallback:
            result["sources"]["openrouter"] = fallback

    # Cache result
    await cache.set(cache_key, json.dumps(result, default=str, ensure_ascii=False))

    # Cleanup
    await postgres.close()
    await cache.close()

    return result
