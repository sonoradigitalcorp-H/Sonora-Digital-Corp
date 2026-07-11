import logging
from typing import Any

import httpx

from ..bridges import engram as engram_bridge
from ..config import config

log = logging.getLogger("abe.rag")


COLLECTIONS = {
    "contracts": "abe-contracts",
    "business": "abe-business",
}


class RAGEngine:
    def __init__(self):
        self.collection = COLLECTIONS["contracts"]

    async def _ensure_collection(self, collection: str = None):
        target = collection or self.collection
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                r = await client.get(
                    f"{config.qdrant_url}/collections/{target}",
                )
                if r.status_code == 404:
                    await client.put(
                        f"{config.qdrant_url}/collections/{target}",
                        json={
                            "vectors": {"size": 384, "distance": "Cosine"},
                        },
                    )
        except Exception as e:
            log.warning(f"Qdrant collection check: {e}")

    async def index_contract(self, contract_id: str, text: str, metadata: dict = None):
        await self._ensure_collection(COLLECTIONS["contracts"])
        try:
            import hashlib
            vector = self._mock_vector(text)
            point_id = int(hashlib.md5(contract_id.encode()).hexdigest()[:8], 16)
            async with httpx.AsyncClient(timeout=5) as client:
                await client.put(
                    f"{config.qdrant_url}/collections/{COLLECTIONS['contracts']}/points",
                    json={
                        "points": [{
                            "id": point_id,
                            "vector": vector,
                            "payload": {
                                "contract_id": contract_id,
                                "text": text[:2000],
                                "metadata": metadata or {},
                            },
                        }],
                    },
                )
        except Exception as e:
            log.warning(f"Qdrant index error: {e}")

    async def search(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        try:
            vector = self._mock_vector(query)
            results = []
            for coll_name in COLLECTIONS.values():
                async with httpx.AsyncClient(timeout=5) as client:
                    r = await client.post(
                        f"{config.qdrant_url}/collections/{coll_name}/points/search",
                        json={"vector": vector, "limit": limit, "with_payload": True},
                    )
                    if r.status_code == 200:
                        data = r.json()
                        for p in data.get("result", []):
                            results.append({
                                "id": p["id"],
                                "text": p["payload"].get("text", ""),
                                "collection": coll_name,
                                "score": p["score"],
                            })
            results.sort(key=lambda x: -x["score"])
            return results[:limit]
        except Exception as e:
            log.warning(f"Qdrant search error: {e}")

        return engram_bridge.query(query, limit)

    def _mock_vector(self, text: str) -> list[float]:
        import hashlib
        h = hashlib.md5(text.encode()).hexdigest()
        return [(int(h[i:i+2], 16) / 255.0) * 2 - 1 for i in range(0, min(32, len(h)), 2)] + [0.0] * (384 - 16)
