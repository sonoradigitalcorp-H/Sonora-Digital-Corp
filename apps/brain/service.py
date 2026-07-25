"""Unified Brain v2 — Servicio central.

Conecta Engram + Neo4j + Qdrant + eventos + lecciones en un solo
cerebro consultable. Exposición via MCP tool.
"""

import json
import logging
import os
import sqlite3
import time
from datetime import datetime
from typing import Any, Optional

from apps.brain.config import BrainConfig
from apps.brain.models import BrainQuery, BrainResult, KnowledgeNode, SyncStatus

log = logging.getLogger("brain.service")


class BrainService:
    """Cerebro unificado de Sonora Digital Corp.

    Orquesta consultas a través de:
      1. Engram (memoria SQLite + FTS5)
      2. Neo4j (grafos de conocimiento)
      3. Qdrant (búsqueda semántica)
    """

    def __init__(self, config: Optional[BrainConfig] = None):
        self.config = config or BrainConfig()
        self.neo4j = None
        self.qdrant = None
        self._engram_conn: Optional[sqlite3.Connection] = None
        self._status = SyncStatus()
        self._connect()

    def _connect(self):
        """Conectar a stores disponibles."""
        # Neo4j
        try:
            from neo4j import GraphDatabase
            self.neo4j = GraphDatabase.driver(
                self.config.neo4j_uri,
                auth=(self.config.neo4j_user, self.config.neo4j_password),
            )
            log.info(f"✅ Brain → Neo4j: {self.config.neo4j_uri}")
        except Exception as e:
            log.warning(f"⚠️ Brain → Neo4j: {e}")

        # Qdrant
        try:
            from qdrant_client import QdrantClient
            self.qdrant = QdrantClient(
                host=self.config.qdrant_host,
                port=self.config.qdrant_port,
            )
            log.info(f"✅ Brain → Qdrant: {self.config.qdrant_host}:{self.config.qdrant_port}")
        except Exception as e:
            log.warning(f"⚠️ Brain → Qdrant: {e}")

        # Engram (SQLite, conexión lazy)
        self._engram_path = self.config.engram_path
        if os.path.exists(self._engram_path):
            log.info(f"✅ Brain → Engram: {self._engram_path}")
        else:
            log.warning(f"⚠️ Brain → Engram: no encontrado en {self._engram_path}")

    @property
    def engram(self) -> Optional[sqlite3.Connection]:
        """Conexión lazy a Engram SQLite."""
        if self._engram_conn is None and os.path.exists(self._engram_path):
            self._engram_conn = sqlite3.connect(self._engram_path)
            self._engram_conn.row_factory = sqlite3.Row
        return self._engram_conn

    # ─── Health ───────────────────────────────────────────

    def ready(self) -> dict:
        """Health check de todas las conexiones."""
        status = {}
        # Neo4j
        if self.neo4j:
            try:
                with self.neo4j.session() as s:
                    r = s.run("MATCH (n) RETURN count(n) as c").single()
                    status["neo4j"] = f"ok ({r['c']} nodes)"
            except Exception as e:
                status["neo4j"] = f"error: {e}"
        else:
            status["neo4j"] = "not connected"

        # Qdrant
        if self.qdrant:
            try:
                cols = self.qdrant.get_collections()
                status["qdrant"] = f"ok ({len(cols.collections)} collections)"
            except Exception as e:
                status["qdrant"] = f"error: {e}"
        else:
            status["qdrant"] = "not connected"

        # Engram
        if self.engram:
            try:
                cur = self.engram.execute("SELECT count(*) as c FROM memories")
                row = cur.fetchone()
                status["engram"] = f"ok ({row['c']} memories)"
            except Exception as e:
                status["engram"] = f"error: {e}"
        else:
            status["engram"] = "not connected"

        status["sync"] = self._status.last_sync or "never"
        return status

    # ─── Búsqueda Unificada ──────────────────────────────

    async def query(self, q: BrainQuery) -> BrainResult:
        """Consulta unificada: auto-detecta modo o usa el solicitado."""
        t0 = time.time()
        result = BrainResult(query=q.text, mode=q.mode)
        sources = []

        if q.mode in ("auto", "fts"):
            sources.append("engram")
        if q.mode in ("auto", "semantic"):
            sources.append("qdrant")
        if q.mode in ("auto", "graph"):
            sources.append("neo4j")

        # Si es auto, probar FTS primero, luego semántico, luego grafo
        if q.mode == "auto":
            # Engram FTS
            engram_results = self._search_engram(q.text, q.limit)
            result.results.extend(engram_results)
            if len(result.results) >= q.limit:
                result.sources_queried = ["engram"]
                result.elapsed_ms = int((time.time() - t0) * 1000)
                result.total = len(result.results)
                return result

            # Si no hay suficiente, agregar Qdrant
            qdrant_results = self._search_qdrant(q.text, q.limit - len(result.results))
            result.results.extend(qdrant_results)
            result.sources_queried = ["engram", "qdrant"]

        elif q.mode == "fts":
            engram_results = self._search_engram(q.text, q.limit)
            result.results.extend(engram_results)
            result.sources_queried = ["engram"]

        elif q.mode == "semantic":
            qdrant_results = self._search_qdrant(q.text, q.limit)
            result.results.extend(qdrant_results)
            result.sources_queried = ["qdrant"]

        elif q.mode == "graph":
            neo4j_results = self._search_neo4j(q.text, q.limit)
            result.results.extend(neo4j_results)
            result.sources_queried = ["neo4j"]

        result.elapsed_ms = int((time.time() - t0) * 1000)
        result.total = len(result.results)
        return result

    def _search_engram(self, text: str, limit: int = 10) -> list:
        """Buscar en Engram (FTS5)."""
        if not self.engram:
            return []
        try:
            # Intentar FTS5 primero, fallback a LIKE
            try:
                cur = self.engram.execute(
                    """SELECT key, value, layer, importance, created_at
                       FROM memories
                       WHERE key MATCH ? OR value MATCH ?
                       ORDER BY rank
                       LIMIT ?""",
                    (text, text, limit),
                )
            except Exception:
                cur = self.engram.execute(
                    """SELECT key, value, layer, importance, created_at
                       FROM memories
                       WHERE key LIKE ? OR value LIKE ?
                       ORDER BY created_at DESC
                       LIMIT ?""",
                    (f"%{text}%", f"%{text}%", limit),
                )
            results = []
            for row in cur.fetchall():
                r = dict(row)  # sqlite3.Row → dict for .get()
                results.append(KnowledgeNode(
                    id=r.get("key", ""),
                    type="MEMORY",
                    label=r.get("key", ""),
                    content=str(r.get("value", ""))[:500],
                    source="engram",
                    created_at=r.get("created_at", ""),
                    score=r.get("importance", 0),
                ))
            return results
        except Exception as e:
            log.warning(f"Engram search error: {e}")
            return []

    def _search_qdrant(self, text: str, limit: int = 5) -> list:
        """Buscar en Qdrant (semántico). Requiere embed."""
        if not self.qdrant:
            return []
        try:
            # Embed simple con sentence-transformers
            embedding = self._embed(text)
            if not embedding:
                return []

            hits = self.qdrant.search(
                collection_name=self.config.qdrant_collection,
                query_vector=embedding,
                limit=limit,
            )
            results = []
            for hit in hits:
                payload = hit.payload or {}
                results.append(KnowledgeNode(
                    id=str(hit.id),
                    type=payload.get("type", "UNKNOWN"),
                    label=payload.get("label", ""),
                    content=payload.get("content", "")[:500],
                    source="qdrant",
                    score=hit.score or 0,
                    metadata=payload,
                ))
            return results
        except Exception as e:
            log.warning(f"Qdrant search error: {e}")
            return []

    def _search_neo4j(self, text: str, limit: int = 10) -> list:
        """Buscar en Neo4j (grafos)."""
        if not self.neo4j:
            return []
        try:
            with self.neo4j.session() as s:
                # Búsqueda por label/tipo
                result = s.run(
                    """MATCH (n)
                       WHERE n.name CONTAINS $query OR n.description CONTAINS $query
                          OR any(tag IN n.tags WHERE tag CONTAINS $query)
                       RETURN n, labels(n) as types
                       LIMIT $limit""",
                    query=text,
                    limit=limit,
                )
                nodes = []
                for record in result:
                    n = record["n"]
                    nodes.append(KnowledgeNode(
                        id=str(n.element_id),
                        type=str(record["types"][0]) if record["types"] else "NODE",
                        label=n.get("name", n.get("title", "unknown")),
                        content=n.get("description", n.get("summary", ""))[:500],
                        source="neo4j",
                        metadata=dict(n),
                    ))
                return nodes
        except Exception as e:
            log.warning(f"Neo4j search error: {e}")
            return []

    def _embed(self, text: str) -> Optional[list]:
        """Genera embedding para búsqueda semántica."""
        try:
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer("all-MiniLM-L6-v2")
            return model.encode(text).tolist()
        except ImportError:
            log.debug("sentence-transformers no instalado, skip Qdrant search")
            return None
        except Exception as e:
            log.warning(f"Embed error: {e}")
            return None

    # ─── Sync ────────────────────────────────────────────

    def run_sync(self) -> SyncStatus:
        """Ejecuta sync de todos los ingestores."""
        from apps.brain.sync import BrainSyncer
        syncer = BrainSyncer(self)
        self._status = syncer.full_sync()
        self._status.last_sync = datetime.now().isoformat()
        syncer.close()
        return self._status

    def sync_status(self) -> SyncStatus:
        """Retorna estado de la última sync."""
        return self._status

    # ─── Lifecycle ───────────────────────────────────────

    def close(self):
        """Cerrar conexiones."""
        if self.neo4j:
            self.neo4j.close()
        if self._engram_conn:
            self._engram_conn.close()
        log.info("BrainService closed")

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
