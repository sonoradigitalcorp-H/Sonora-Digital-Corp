import json
import logging
import uuid
from pathlib import Path

import httpx

from .chunker import chunk_markdown
from .embeddings import embed

logger = logging.getLogger("aztrotech.rag.indexer")

QDRANT_URL = "http://localhost:6333"
COLLECTION = "obsidian-vault"


async def ensure_collection():
    async with httpx.AsyncClient() as c:
        r = await c.get(f"{QDRANT_URL}/collections/{COLLECTION}")
        if r.status_code == 200:
            return
        payload = {
            "name": COLLECTION,
            "vectors": {
                "size": 384,
                "distance": "Cosine",
            },
        }
        r = await c.put(f"{QDRANT_URL}/collections/{COLLECTION}", json=payload)
        if r.status_code != 200:
            logger.error(f"create collection: {r.status_code} {r.text}")


async def index_vault(vault_path: str):
    await ensure_collection()

    root = Path(vault_path).expanduser().resolve()
    files = list(root.rglob("*.md"))
    # exclude Templates
    files = [f for f in files if "Templates" not in f.parts]

    logger.info(f"Found {len(files)} markdown files in {root}")

    points = []
    for fp in files:
        chunks = chunk_markdown(fp)
        texts = [c["content"] for c in chunks]
        if not texts:
            continue

        try:
            vecs = embed(texts)
        except Exception as e:
            logger.error(f"embedding {fp}: {e}")
            continue

        for i, (chunk, vec) in enumerate(zip(chunks, vecs)):
            points.append({
                "id": str(uuid.uuid5(uuid.NAMESPACE_URL, f"{fp}:{i}")),
                "vector": vec,
                "payload": {
                    "content": chunk["content"][:2000],
                    **chunk["metadata"],
                },
            })

        if len(points) >= 100:
            await _upload(points)
            points = []

    if points:
        await _upload(points)

    logger.info(f"Indexed {len(files)} files → {COLLECTION}")


async def _upload(points: list[dict]):
    async with httpx.AsyncClient(timeout=60) as c:
        r = await c.put(
            f"{QDRANT_URL}/collections/{COLLECTION}/points",
            json={"points": points},
        )
        if r.status_code != 200:
            logger.error(f"upload: {r.status_code} {r.text[:200]}")


if __name__ == "__main__":
    import asyncio
    logging.basicConfig(level=logging.INFO)
    asyncio.run(index_vault("~/Documents/sdc-brain-vault"))
