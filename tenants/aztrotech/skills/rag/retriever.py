import logging

import httpx

from .embeddings import embed_query

logger = logging.getLogger("aztrotech.rag.retriever")

QDRANT_URL = "http://localhost:6333"
COLLECTION = "obsidian-vault"


async def retrieve(query: str, top_k: int = 5) -> str:
    try:
        vec = embed_query(query)
    except Exception as e:
        logger.error(f"embedding error: {e}")
        return ""

    payload = {
        "vector": vec,
        "limit": top_k,
        "with_payload": True,
        "with_vector": False,
    }

    try:
        async with httpx.AsyncClient(timeout=15) as c:
            r = await c.post(
                f"{QDRANT_URL}/collections/{COLLECTION}/points/search",
                json=payload,
            )
            if r.status_code != 200:
                logger.warning(f"Qdrant search: {r.status_code}")
                return ""
            data = r.json()
    except Exception as e:
        logger.error(f"Qdrant error: {e}")
        return ""

    points = data.get("result", [])
    if not points:
        return ""

    sections = []
    for p in points:
        pay = p.get("payload", {})
        content = pay.get("content", "")
        source = pay.get("source", "")
        section = pay.get("section", "")
        header = f"[{source}] {section}" if section else source
        sections.append(f"### {header}\n{content}")

    context = "\n\n".join(sections)
    return context
