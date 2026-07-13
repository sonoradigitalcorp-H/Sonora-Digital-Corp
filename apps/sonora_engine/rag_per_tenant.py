"""Per-tenant RAG engine [FR7] — cada cliente tiene su colección Qdrant aislada.

Crea y consulta colecciones vectoriales por tenant_id.
Integra con Open Notebook para gestión documental.
"""

import hashlib
import json
import logging
import os
from typing import Any

log = logging.getLogger("sonora.engine.rag")

QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
EMBEDDING_DIM = 384  # all-MiniLM-L6-v2 compatible


def _get_client():
    from qdrant_client import QdrantClient
    return QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)


def _collection_name(tenant_id: str) -> str:
    return f"kb_{tenant_id.replace('-', '_')}"


def ensure_collection(tenant_id: str) -> bool:
    """Ensure a Qdrant collection exists for the given tenant.

    Returns True if collection was created, False if already exists.
    """
    try:
        client = _get_client()
        collections = client.get_collections().collections
        names = [c.name for c in collections]

        if _collection_name(tenant_id) in names:
            return False

        from qdrant_client.models import Distance, VectorParams

        client.create_collection(
            collection_name=_collection_name(tenant_id),
            vectors_config=VectorParams(size=EMBEDDING_DIM, distance=Distance.COSINE),
        )
        log.info(f"Created Qdrant collection for tenant {tenant_id}")
        return True
    except Exception as e:
        log.error(f"Failed to create collection for {tenant_id}: {e}")
        return False


def index_document(tenant_id: str, doc_id: str, text: str, metadata: dict | None = None) -> bool:
    """Index a document in the tenant's collection.

    Args:
        tenant_id: Tenant identifier
        doc_id: Unique document ID
        text: Document text content
        metadata: Optional metadata (source, type, etc.)

    Returns:
        True if indexed successfully
    """
    try:
        client = _get_client()
        ensure_collection(tenant_id)

        from qdrant_client.models import PointStruct

        # Mock embedding (in production: use an embedding model)
        mock_vector = [
            float(int(hashlib.md5(f"{tenant_id}:{doc_id}:{i}".encode()).hexdigest(), 16) % 1000) / 1000.0
            for i in range(EMBEDDING_DIM)
        ]

        client.upsert(
            collection_name=_collection_name(tenant_id),
            points=[PointStruct(
                id=abs(hash(doc_id)) % (2**63),
                vector=mock_vector,
                payload={
                    "doc_id": doc_id,
                    "text": text[:5000],
                    "tenant_id": tenant_id,
                    **(metadata or {}),
                },
            )],
        )
        return True
    except Exception as e:
        log.error(f"Index failed for {tenant_id}/{doc_id}: {e}")
        return False


def query_rag(tenant_id: str, query: str, limit: int = 5) -> list[dict[str, Any]]:
    """Query the tenant's RAG collection.

    Args:
        tenant_id: Tenant identifier
        query: Search query text
        limit: Max results

    Returns:
        List of {text, score, source} dicts
    """
    try:
        client = _get_client()
        ensure_collection(tenant_id)

        from qdrant_client.models import Filter, FieldCondition, MatchValue

        # Mock query vector
        mock_vector = [
            float(int(hashlib.md5(f"{tenant_id}:query:{i}".encode()).hexdigest(), 16) % 1000) / 1000.0
            for i in range(EMBEDDING_DIM)
        ]

        results = client.search(
            collection_name=_collection_name(tenant_id),
            query_vector=mock_vector,
            limit=limit,
            query_filter=Filter(
                must=[FieldCondition(key="tenant_id", match=MatchValue(value=tenant_id))]
            ),
        )

        return [
            {
                "text": r.payload.get("text", ""),
                "score": r.score,
                "source": r.payload.get("source", ""),
                "doc_id": r.payload.get("doc_id", ""),
            }
            for r in results
        ]
    except Exception as e:
        log.error(f"RAG query failed for {tenant_id}: {e}")
        return []


def delete_collection(tenant_id: str) -> bool:
    """Delete a tenant's collection (used when tenant is removed)."""
    try:
        client = _get_client()
        client.delete_collection(collection_name=_collection_name(tenant_id))
        log.info(f"Deleted Qdrant collection for tenant {tenant_id}")
        return True
    except Exception as e:
        log.error(f"Failed to delete collection for {tenant_id}: {e}")
        return False


def list_collections() -> list[dict]:
    """List all tenant RAG collections."""
    try:
        client = _get_client()
        collections = client.get_collections().collections
        return [
            {
                "name": c.name,
                "tenant_id": c.name.replace("kb_", "").replace("_", "-"),
                "vectors_count": getattr(c, "vectors_count", 0),
            }
            for c in collections
            if c.name.startswith("kb_")
        ]
    except Exception as e:
        log.error(f"Failed to list collections: {e}")
        return []


def index_artist_knowledge(tenant_id: str, artist_id: str, artist_data: dict) -> bool:
    """Index artist knowledge base from ABE data into RAG.

    Creates rich text chunks from artist profile for semantic search.
    """
    chunks = []
    name = artist_data.get("name", artist_data.get("nombre", "Unknown"))

    # Artist bio chunk
    bio = (
        f"{name} es un artista de {artist_data.get('genero', 'música')} "
        f"de {artist_data.get('pais', 'México')}. "
        f"Tiene {artist_data.get('streams', 0):,} streams "
        f"y {artist_data.get('monthly_listeners', 0):,} oyentes mensuales."
    )
    chunks.append(("bio", bio, {"type": "artist_bio"}))

    # Top song chunk
    top_song = artist_data.get("top_song", "")
    if top_song:
        chunks.append((
            "top_song",
            f"La canción más popular de {name} es '{top_song}' "
            f"con {artist_data.get('top_song_streams', 0):,} streams.",
            {"type": "top_song"},
        ))

    # Revenue chunk
    revenue = artist_data.get("revenue", 0)
    if revenue:
        chunks.append((
            "revenue",
            f"{name} ha generado ${revenue:,.2f} en ingresos.",
            {"type": "revenue"},
        ))

    # Social chunk
    social = artist_data.get("social", {})
    if social:
        social_str = " | ".join(f"{k}: {v}" for k, v in social.items() if v)
        if social_str:
            chunks.append((
                "social",
                f"Redes sociales de {name}: {social_str}",
                {"type": "social"},
            ))

    success = True
    for chunk_id, text, meta in chunks:
        doc_id = f"{artist_id}_{chunk_id}"
        ok = index_document(tenant_id, doc_id, text, {
            "source": "abe_music",
            "artist_id": artist_id,
            "type": meta["type"],
        })
        if not ok:
            success = False

    return success
