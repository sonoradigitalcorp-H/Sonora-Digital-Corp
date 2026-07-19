import json
from pathlib import Path
from typing import Any

from memory.base import MemoryResult, MemoryStore

REPO = Path(__file__).resolve().parent.parent.parent
SEMANTIC_DIR = REPO / "state" / "semantic"


_EMBEDDER = None

def _get_embedder():
    global _EMBEDDER
    if _EMBEDDER is None:
        try:
            from sentence_transformers import SentenceTransformer
            _EMBEDDER = SentenceTransformer("all-MiniLM-L6-v2")
        except Exception:
            _EMBEDDER = False
    return _EMBEDDER if _EMBEDDER is not False else None

def _embed(text: str) -> list[float]:
    embedder = _get_embedder()
    if embedder:
        return embedder.encode(text, normalize_embeddings=True).tolist()
    return [0.0] * 384


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

    def _ensure_collection(self):
        if not self._qdrant:
            return
        try:
            cols = self._qdrant.get_collections()
            if not any(c.name == "hermes" for c in cols.collections):
                from qdrant_client.http import models
                self._qdrant.create_collection(
                    collection_name="hermes",
                    vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE),
                )
        except Exception:
            pass

    async def store(self, key: str, data: dict, ttl: int | None = None) -> MemoryResult:
        if self._qdrant:
            try:
                from qdrant_client.http import models
                self._ensure_collection()
                point_id = hash(key) % (2**63)
                text = json.dumps(data, default=str)
                vector = _embed(text)
                self._qdrant.upsert(
                    collection_name="hermes",
                    points=[models.PointStruct(id=point_id, vector=vector, payload={"key": key, "data": data})],
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
        if isinstance(query, dict):
            query = str(query)
        if self._qdrant:
            try:
                vector = _embed(query)
                hits = self._qdrant.search(
                    collection_name="hermes",
                    query_vector=vector,
                    limit=top_k,
                )
                return [
                    MemoryResult(key=h.payload.get("key", ""), data=h.payload.get("data"), found=True, store_type="semantic")
                    for h in hits
                ]
            except Exception:
                pass
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
