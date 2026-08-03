"""RAG Retriever — FastEmbed local embeddings, coherent with sdc_knowledge (384-dim).

Búsqueda RAG-first: vector + filtro por tenant → chunks formateados para prompt.
Sin MCP: se importa directo desde el bot para baja latencia.
"""

import logging
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, FieldCondition, Filter, MatchValue

logger = logging.getLogger(__name__)

# Lazy-loaded FastEmbed model (coherente con scripts/ingest_qdrant_openrouter.py)
EMBED_MODEL = os.getenv(
    "EMBED_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)
EMBED_DIM = 384


@dataclass
class Chunk:
    id: str
    score: float
    text: str
    source: str
    chunk_index: int
    payload: Dict[str, Any] = field(default_factory=dict)


class RAGRetriever:
    def __init__(
        self,
        tenant_id: str,
        qdrant_url: str = "http://localhost:6333",
        collection: str = "sdc_knowledge",
        embed_model: str = EMBED_MODEL,
        min_score: float = 0.50,
        top_k: int = 5,
    ):
        self.tenant_id = tenant_id
        self.qdrant_url = qdrant_url
        self.collection = collection
        self.embed_model = embed_model
        self.min_score = min_score
        self.top_k = top_k
        self._client: Optional[QdrantClient] = None
        self._embed: Any = None

    @property
    def client(self) -> QdrantClient:
        if self._client is None:
            self._client = QdrantClient(url=self.qdrant_url, prefer_grpc=False)
        return self._client

    def _get_embed(self):
        if self._embed is None:
            from fastembed import TextEmbedding
            self._embed = TextEmbedding(model_name=self.embed_model)
        return self._embed

    def _embed_query(self, text: str) -> List[float]:
        model = self._get_embed()
        return list(model.embed([text]))[0].tolist()

    def search(
        self,
        query: str,
        top_k: Optional[int] = None,
        min_score: Optional[float] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Chunk]:
        """Search Qdrant, filtered by tenant + optional extra filters."""
        k = top_k or self.top_k
        threshold = min_score if min_score is not None else self.min_score

        vector = self._embed_query(query)
        conditions = [FieldCondition(key="tenant_id", match=MatchValue(value=self.tenant_id))]
        for key, value in (filters or {}).items():
            conditions.append(FieldCondition(key=key, match=MatchValue(value=value)))

        hits = self.client.search(
            collection_name=self.collection,
            query_vector=vector,
            query_filter=Filter(must=conditions),
            limit=k,
        )

        results = []
        for hit in hits:
            if hit.score >= threshold:
                payload = hit.payload or {}
                results.append(
                    Chunk(
                        id=str(hit.id),
                        score=round(float(hit.score), 4),
                        text=payload.get("text", ""),
                        source=payload.get("source", ""),
                        chunk_index=payload.get("chunk_index", 0),
                        payload=payload,
                    )
                )
        return results

    def get_context_for_prompt(
        self,
        query: str,
        max_chunks: int = 3,
        max_chars: int = 1800,
    ) -> str:
        """Formatea chunks para inyección en el prompt (fuentes + score + texto)."""
        chunks = self.search(query, top_k=max_chunks)
        if not chunks:
            return ""
        parts = []
        total = 0
        for c in chunks:
            block = f"[Fuente: {c.source}] (relevancia {c.score})\n{c.text.strip()}"
            if total + len(block) > max_chars:
                break
            parts.append(block)
            total += len(block)
        return "\n\n".join(parts)

    def health(self) -> Dict[str, Any]:
        """Estado del retriever para diagnóstico."""
        try:
            collections = [c.name for c in self.client.get_collections().collections]
            return {
                "ok": self.collection in collections,
                "qdrant_url": self.qdrant_url,
                "collection": self.collection,
                "collections": collections,
                "embed_model": self.embed_model,
                "dim": EMBED_DIM,
                "tenant_id": self.tenant_id,
            }
        except Exception as e:
            return {"ok": False, "error": str(e)}


def create_retriever(
    tenant_id: str,
    qdrant_url: str = "http://localhost:6333",
    collection: str = "sdc_knowledge",
) -> RAGRetriever:
    """Factory para crear retriever con defaults de MVP."""
    return RAGRetriever(
        tenant_id=tenant_id,
        qdrant_url=qdrant_url,
        collection=collection,
    )


if __name__ == "__main__":
    import sys

    r = create_retriever("aztrotech")
    print("Health:", r.health())
    q = sys.argv[1] if len(sys.argv) > 1 else "¿Qué servicios ofrece Aztrotech?"
    print(f"\nQuery: {q}\n")
    context = r.get_context_for_prompt(q)
    print(context or "(sin resultados sobre el umbral)")