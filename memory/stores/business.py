import json
from pathlib import Path
from typing import Any

from memory.base import MemoryResult, MemoryStore

REPO = Path(__file__).resolve().parent.parent.parent
BUSINESS_DIR = REPO / "state" / "business"


class BusinessMemory(MemoryStore):
    name = "business"

    def __init__(self, storage_dir: str | Path | None = None):
        self.storage_dir = Path(storage_dir) if storage_dir else BUSINESS_DIR
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        safe = key.replace("/", "_").replace("\\", "_")
        return self.storage_dir / f"{safe}.json"

    async def store(self, key: str, data: dict, ttl: int | None = None) -> MemoryResult:
        self._path(key).write_text(json.dumps(data, indent=2, default=str))
        return MemoryResult(key=key, data=data, found=True, store_type="business")

    async def retrieve(self, key: str) -> MemoryResult:
        path = self._path(key)
        if not path.exists():
            return MemoryResult(key=key, found=False, store_type="business")
        try:
            data = json.loads(path.read_text())
            return MemoryResult(key=key, data=data, found=True, store_type="business")
        except Exception as e:
            return MemoryResult(key=key, found=False, error=str(e), store_type="business")

    async def search(self, query: str | dict, top_k: int = 5) -> list[MemoryResult]:
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
                    results.append(MemoryResult(key=path.stem, data=data, found=True, store_type="business"))
            except Exception:
                continue
        return results

    async def delete(self, key: str) -> bool:
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
