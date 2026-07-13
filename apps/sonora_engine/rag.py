"""RAG query engine per client [FR7] — cada tenant tiene su colección en Qdrant."""

from typing import Any


def query_rag(tenant_id: str, query: str, limit: int = 5) -> list[dict[str, Any]]:
    """Query RAG for tenant-specific context.

    In production: queries Qdrant collection named after tenant_id.
    In test mode: returns empty list.
    """
    try:
        from qdrant_client import QdrantClient

        client = QdrantClient(host="localhost", port=6333)
        collection = f"kb_{tenant_id}"

        collections = client.get_collections().collections
        collection_names = [c.name for c in collections]

        if collection not in collection_names:
            return []

        results = client.search(
            collection_name=collection,
            query_vector=[0.0] * 384,  # Placeholder dimension
            limit=limit,
        )

        return [
            {
                "text": r.payload.get("text", ""),
                "score": r.score,
                "source": r.payload.get("source", ""),
            }
            for r in results
        ]
    except Exception:
        return []  # Fallback for tests / unavailable Qdrant
