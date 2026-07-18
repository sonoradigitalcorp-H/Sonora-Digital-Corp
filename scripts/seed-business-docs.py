#!/usr/bin/env python3
"""Seed business docs into Qdrant + Engram for ABE Service RAG."""
import hashlib
from pathlib import Path

import httpx

QDRANT_URL = "http://127.0.0.1:6333"
COLLECTION = "abe-business"
BUSINESS_DIR = Path(__file__).resolve().parent.parent / "business"


def mock_vector(text: str) -> list[float]:
    h = hashlib.md5(text.encode()).hexdigest()
    return [(int(h[i:i+2], 16) / 255.0) * 2 - 1 for i in range(0, min(32, len(h)), 2)] + [0.0] * (384 - 16)


async def ensure_collection():
    async with httpx.AsyncClient(timeout=5) as client:
        r = await client.get(f"{QDRANT_URL}/collections/{COLLECTION}")
        if r.status_code == 404:
            await client.put(
                f"{QDRANT_URL}/collections/{COLLECTION}",
                json={"vectors": {"size": 384, "distance": "Cosine"}},
            )
            print(f"Created collection '{COLLECTION}'")
        else:
            print(f"Collection '{COLLECTION}' exists")


async def index_doc(doc_id: str, text: str, metadata: dict = None):
    point_id = int(hashlib.md5(doc_id.encode()).hexdigest()[:8], 16)
    vector = mock_vector(text)
    async with httpx.AsyncClient(timeout=5) as client:
        r = await client.put(
            f"{QDRANT_URL}/collections/{COLLECTION}/points",
            json={
                "points": [{
                    "id": point_id,
                    "vector": vector,
                    "payload": {
                        "doc_id": doc_id,
                        "text": text[:2000],
                        "metadata": metadata or {},
                    },
                }],
            },
        )
        return r.status_code == 200


def collect_docs():
    docs = []
    for product_dir in sorted(BUSINESS_DIR.iterdir()):
        if not product_dir.is_dir():
            continue
        docs_dir = product_dir / "docs"
        if not docs_dir.exists():
            continue
        product_name = product_dir.name.replace("abe-", "").replace("-", " ").title()
        for md_file in docs_dir.glob("*.md"):
            text = md_file.read_text(encoding="utf-8")
            doc_id = f"business/{product_dir.name}/{md_file.name}"
            docs.append((doc_id, text, {
                "product": product_dir.name,
                "product_name": product_name,
                "file": md_file.name,
                "type": "business_doc",
            }))
    return docs


async def main():
    print("=" * 50)
    print("ABE Business Docs Seeder")
    print("=" * 50)

    await ensure_collection()
    docs = collect_docs()
    print(f"Found {len(docs)} documents\n")

    for i, (doc_id, text, metadata) in enumerate(docs, 1):
        ok = await index_doc(doc_id, text, metadata)
        status = "✓" if ok else "✗"
        title = text.split("\n")[0] if text.split("\n") else doc_id
        print(f"  [{i}/{len(docs)}] {status} {metadata['product']}: {title[:60]}")

    print(f"\nDone! {len(docs)} documents indexed in Qdrant collection '{COLLECTION}'")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
