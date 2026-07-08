import json
from pathlib import Path
from typing import Any

from memory.base import MemoryResult, MemoryStore

REPO = Path(__file__).resolve().parent.parent.parent
SEMANTIC_DIR = REPO / "state" / "semantic"


class SemanticMemory(MemoryStore):
    name = "semantic"

    def __init__(self, storage_dir: str | Path | None = None):
        self.storage_dir = Path(storage_dir) if storage_dir else SEMANTIC_DIR
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self._qdrant = None
        self._init_qdrant()

    def _init_qdrant(self):
        try:
            from qdrant_client import QdrantClient
            self._qdrant = QdrantClient("localhost", port=6333, prefer_grpc=False)
            self._qdrant.get_collections()
        except Exception:
            self._qdrant = None

    def _path(self, key: str) -> Path:
        safe = key.replace("/", "_").replace("\\", "_")
        return self.storage_dir / f"{safe}.json"

    async def store(self, key: str, data: dict, ttl: int | None = None) -> MemoryResult:
        if self._qdrant:
            try:
                from qdrant_client.http import models
                point_id = hash(key) % (2**63)
                self._qdrant.upsert(
                    collection_name="hermes",
                    points=[models.PointStruct(id=point_id, vector=[0.0]*384, payload={"key": key, "data": data})],
                )
                return MemoryResult(key=key, data=data, found=True, store_type="semantic")
            except Exception:
                pass
        self._path(key).write_text(json.dumps(data, indent=2, default=str))
        return MemoryResult(key=key, data=data, found=True, store_type="semantic")

    async def retrieve(self, key: str) -> MemoryResult:
        if self._qdrant:
            try:
                from qdrant_client.http import models
                hits = self._qdrant.scroll(
                    collection_name="hermes",
                    scroll_filter=models.Filter(
                        must=[models.FieldCondition(key="key", match=models.MatchValue(value=key))]
                    ),
                    limit=1,
                )
                if hits and hits[0]:
                    return MemoryResult(key=key, data=hits[0][0].payload.get("data"), found=True, store_type="semantic")
            except Exception:
                pass
        path = self._path(key)
        if path.exists():
            data = json.loads(path.read_text())
            return MemoryResult(key=key, data=data, found=True, store_type="semantic")
        return MemoryResult(key=key, found=False, store_type="semantic")

    async def search(self, query: str | dict, top_k: int = 5) -> list[MemoryResult]:
        if self._qdrant:
            try:
                hits = self._qdrant.search(
                    collection_name="hermes",
                    query_vector=[0.0]*384,
                    limit=top_k,
                )
                return [
                    MemoryResult(key=h.payload.get("key", ""), data=h.payload.get("data"), found=True, store_type="semantic")
                    for h in hits
                ]
            except Exception:
                pass
        if isinstance(query, dict):
            query = str(query)
        q = query.lower()
        results: list[MemoryResult] = []
        for path in sorted(self.storage_dir.glob("*.json")):
            if len(results) >= top_k:
                break
            try:
                data = json.loads(path.read_text())
                if q in path.stem.lower() or q in json.dumps(data).lower():
                    results.append(MemoryResult(key=path.stem, data=data, found=True, store_type="semantic"))
            except Exception:
                continue
        return results

    async def delete(self, key: str) -> bool:
        if self._qdrant:
            try:
                from qdrant_client.http import models
                self._qdrant.delete(
                    collection_name="hermes",
                    points_selector=models.Filter(
                        must=[models.FieldCondition(key="key", match=models.MatchValue(value=key))]
                    ),
                )
                return True
            except Exception:
                pass
        path = self._path(key)
        if path.exists():
            path.unlink()
            return True
        return False

    async def list_keys(self, prefix: str = "") -> list[str]:
        return [
            p.stem for p in sorted(self.storage_dir.glob("*.json"))
            if p.stem.startswith(prefix)
        ]
