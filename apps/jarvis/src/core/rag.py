"""
JARVIS RAG Pipeline — Embed → Search Qdrant → Return Context.
Includes sanitization against prompt injection and hidden instructions.
"""

import logging
import os
import re
from datetime import datetime
from typing import Any

from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse
from qdrant_client.models import FieldCondition, Filter, MatchValue, PointStruct

from src.core.embeddings import EMBED_DIM, embed_text

log = logging.getLogger("jarvis.rag")

QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
COLLECTION = "jarvis_knowledge"

# === SANITIZATION: Anti-prompt-injection filter ===

INJECTION_PATTERNS = [
    # HTML comments with potential instructions
    (r"<!--[\s\S]*?-->", ""),
    # System prompt overrides
    (
        r"(?i)(ignore|olvid(a|e)|desobedece|disregard)\s+(all|todo|previous|lo\s+anterior|instrucciones)",
        "[FILTERED]",
    ),
    # Role injections
    (
        r"(?i)(system|assistant|user):\s*(you\s+are|eres|act\s+as|comporta)",
        "[FILTERED]",
    ),
    # Base64 encoded payloads (common injection vector)
    (r"[A-Za-z0-9+/]{50,}={0,2}", "[FILTERED]"),
    # Zero-width characters
    (r"[\u200b\u200c\u200d\u2060\u2061\u2062\u2063\u2064\uFEFF]", ""),
    # Markdown images with data URIs (potential exfiltration)
    (r"!\[.*?\]\(data:.*?\)", "[FILTERED]"),
    # CSS injection in markdown
    (r"<style[\s\S]*?<\/style>", ""),
    # Script tags
    (r"<script[\s\S]*?<\/script>", ""),
    # on* event handlers in HTML
    (r'\son\w+\s*=\s*["\'].*?["\']', ""),
    # JavaScript URLs
    (r"javascript:\s*", "blocked:"),
    # Data URLs in links
    (r'href=["\']data:.*?["\']', 'href="#"'),
]


def sanitize_text(text: str) -> str:
    """Remove prompt injection vectors from text before RAG indexing."""
    if not text:
        return ""
    sanitized = text
    for pattern, replacement in INJECTION_PATTERNS:
        sanitized = re.sub(pattern, replacement, sanitized)
    log.debug(f"Sanitized text: {len(text)} → {len(sanitized)} chars")
    return sanitized


def is_safe_to_index(text: str) -> bool:
    """Check if text passes safety checks before indexing."""
    if not text or len(text.strip()) < 10:
        return False
    # Check for obvious injection patterns
    suspicious = [
        r"(?i)system\s*(prompt|message|instruction)",
        r"(?i)you\s+are\s+(now|free|released)",
        r"(?i)ignore\s+(above|previous|all)",
    ]
    for pattern in suspicious:
        if re.search(pattern, text):
            log.warning(f"Blocked suspicious content: {text[:80]}...")
            return False
    return True


class RagEngine:
    def __init__(self):
        self._client = None

    @property
    def client(self) -> QdrantClient | None:
        if self._client is None:
            try:
                self._client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
                self._client.get_collections()
            except Exception as e:
                log.warning(f"Qdrant no disponible: {e}")
                return None
        return self._client

    def ensure_collection(self):
        c = self.client
        if c is None:
            return False
        try:
            c.get_collection(COLLECTION)
            # Ensure tenant_id index exists
            try:
                c.create_payload_index(
                    collection_name=COLLECTION,
                    field_name="tenant_id",
                    field_schema="keyword",
                )
            except Exception:
                pass  # Index may already exist
            return True
        except UnexpectedResponse:
            c.create_collection(
                collection_name=COLLECTION,
                vectors_config={"size": EMBED_DIM, "distance": "Cosine"},
            )
            c.create_payload_index(
                collection_name=COLLECTION,
                field_name="tenant_id",
                field_schema="keyword",
            )
            log.info(f"Colección '{COLLECTION}' creada (dims={EMBED_DIM})")
            return True
        except Exception as e:
            log.error(f"Error creando colección: {e}")
            return False

    def store(self, text: str, metadata: dict | None = None, tenant_id: str = "sdc-core") -> dict[str, Any]:
        c = self.client
        if c is None:
            return {"status": "error", "message": "Qdrant no disponible"}

        clean_text = sanitize_text(text)
        if not is_safe_to_index(clean_text):
            return {"status": "error", "message": "Contenido bloqueado por seguridad"}

        self.ensure_collection()
        vector = embed_text(clean_text)
        if vector is None:
            return {"status": "error", "message": "Embedding falló"}

        point = PointStruct(
            id=abs(hash(text + str(datetime.now()))),
            vector=vector,
            payload={
                "text": text[:1000],
                "metadata": metadata or {},
                "timestamp": datetime.now().isoformat(),
                "tenant_id": tenant_id,
            },
        )
        try:
            c.upsert(collection_name=COLLECTION, points=[point])
            log.info(f"Guardado en RAG [{tenant_id}]: {text[:50]}...")
            return {"status": "success", "id": str(point.id)}
        except Exception as e:
            log.error(f"Error guardando en Qdrant: {e}")
            return {"status": "error", "message": str(e)}

    def search(
        self, query: str, limit: int = 5, threshold: float = 0.0, tenant_id: str = "sdc-core"
    ) -> dict[str, Any]:
        c = self.client
        if c is None:
            return {"status": "error", "message": "Qdrant no disponible", "results": []}

        vector = embed_text(query)
        if vector is None:
            return {"status": "error", "message": "Embedding falló", "results": []}

        # Build filter for tenant isolation
        search_filter = None
        if tenant_id:
            search_filter = Filter(
                must=[FieldCondition(key="tenant_id", match=MatchValue(value=tenant_id))]
            )

        try:
            results = c.search(
                collection_name=COLLECTION,
                query_vector=vector,
                query_filter=search_filter,
                limit=limit,
                score_threshold=threshold,
            )
            return {
                "status": "success",
                "query": query,
                "results": [
                    {
                        "id": str(r.id),
                        "score": round(r.score, 4),
                        "text": r.payload.get("text", ""),
                        "metadata": r.payload.get("metadata", {}),
                        "timestamp": r.payload.get("timestamp", ""),
                        "tenant_id": r.payload.get("tenant_id", "unknown"),
                    }
                    for r in results
                ],
                "count": len(results),
            }
        except Exception as e:
            log.error(f"Error en búsqueda RAG: {e}")
            return {"status": "error", "message": str(e), "results": []}

    def get_context(self, query: str, max_chunks: int = 3, tenant_id: str = "sdc-core") -> str:
        result = self.search(query, limit=max_chunks, tenant_id=tenant_id)
        if result["status"] != "success" or not result["results"]:
            return ""
        parts = []
        for r in result["results"]:
            clean = sanitize_text(r["text"])
            if clean:
                parts.append(f"[{r['score']:.2f}] {clean}")
        return "\n\n".join(parts)


rag = RagEngine()
