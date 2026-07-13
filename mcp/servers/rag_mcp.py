"""RAG MCP Server — Per-tenant knowledge retrieval from Qdrant.

Exposes semantic search over tenant knowledge bases.
"""

import json
import os

import httpx

QDRANT_URL = os.getenv("QDRANT_URL", "http://127.0.0.1:6333")
EMBED_MODEL = os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2")


async def _get_embedding(text: str) -> list[float]:
    """Get embedding vector for a text. Uses a simple approach."""
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer(EMBED_MODEL)
        vec = model.encode(text).tolist()
        return vec
    except ImportError:
        return [0.0] * 384


async def rag_search(tenant_id: str, query: str, limit: int = 5) -> str:
    if not tenant_id or not query:
        return json.dumps({"error": "tenant_id and query are required"})
    try:
        collection = f"kb_{tenant_id}"
        vec = await _get_embedding(query)
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{QDRANT_URL}/collections/{collection}/points/search",
                json={
                    "vector": vec,
                    "limit": limit,
                    "with_payload": True,
                },
                timeout=30,
            )
            data = resp.json()
            results = []
            for point in data.get("result", []):
                results.append({
                    "id": point["id"],
                    "score": point["score"],
                    "payload": point.get("payload", {}),
                })
            return json.dumps({"results": results, "count": len(results)})
    except Exception as e:
        return json.dumps({"error": str(e)})


async def rag_index(tenant_id: str, document_id: str, content: str, metadata: dict | None = None) -> str:
    if not tenant_id or not document_id or not content:
        return json.dumps({"error": "tenant_id, document_id, and content are required"})
    try:
        collection = f"kb_{tenant_id}"
        vec = await _get_embedding(content)
        payload = {"content": content[:1000], "document_id": document_id}
        if metadata:
            payload.update(metadata)
        async with httpx.AsyncClient() as client:
            resp = await client.put(
                f"{QDRANT_URL}/collections/{collection}/points",
                json={
                    "points": [{
                        "id": hash(f"{tenant_id}:{document_id}") % (2**63),
                        "vector": vec,
                        "payload": payload,
                    }],
                },
                timeout=30,
            )
            data = resp.json()
            return json.dumps({"indexed": True, "document_id": document_id, "status": data.get("status", "ok")})
    except Exception as e:
        return json.dumps({"error": str(e)})


async def rag_list_collections() -> str:
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{QDRANT_URL}/collections", timeout=10)
        data = resp.json()
        collections = []
        for c in data.get("result", {}).get("collections", []):
            if isinstance(c, dict):
                name = c.get("name", "")
                if name.startswith("kb_"):
                    collections.append(name[3:])
        return json.dumps({"collections": collections})


MCP_TOOLS = {
    "rag_search": {
        "description": "Search knowledge base for a tenant using semantic search",
        "input_schema": {
            "type": "object",
            "properties": {
                "tenant_id": {"type": "string", "description": "Tenant ID (e.g. abe_music)"},
                "query": {"type": "string", "description": "Search query"},
                "limit": {"type": "integer", "description": "Max results (default: 5)"},
            },
            "required": ["tenant_id", "query"],
        },
        "handler": lambda args: rag_search(args["tenant_id"], args["query"], args.get("limit", 5)),
    },
    "rag_index": {
        "description": "Index a document into tenant knowledge base",
        "input_schema": {
            "type": "object",
            "properties": {
                "tenant_id": {"type": "string", "description": "Tenant ID"},
                "document_id": {"type": "string", "description": "Unique document identifier"},
                "content": {"type": "string", "description": "Document content"},
                "metadata": {"type": "object", "description": "Optional metadata"},
            },
            "required": ["tenant_id", "document_id", "content"],
        },
        "handler": lambda args: rag_index(args["tenant_id"], args["document_id"], args["content"], args.get("metadata")),
    },
    "rag_list_collections": {
        "description": "List all tenant knowledge bases available",
        "input_schema": {"type": "object", "properties": {}},
        "handler": lambda _: rag_list_collections(),
    },
}
