import json
import time
from pathlib import Path
from typing import Any

from memory.base import MemoryResult, MemoryStore

REPO = Path(__file__).resolve().parent.parent.parent
WORKING_DIR = REPO / "state" / "memory"


class WorkingMemory(MemoryStore):
    name = "working"

    def __init__(self, storage_dir: str | Path | None = None):
        self.storage_dir = Path(storage_dir) if storage_dir else WORKING_DIR
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        safe = key.replace("/", "_").replace("\\", "_")
        return self.storage_dir / f"{safe}.json"

    async def store(self, key: str, data: dict, ttl: int | None = None) -> MemoryResult:
        payload = {
            "key": key,
            "data": data,
            "stored_at": time.time(),
            "ttl": ttl,
        }
        self._path(key).write_text(json.dumps(payload, indent=2))
        return MemoryResult(key=key, data=data, found=True, store_type="working")

    async def retrieve(self, key: str) -> MemoryResult:
        path = self._path(key)
        if not path.exists():
            return MemoryResult(key=key, found=False, store_type="working")
        try:
            payload = json.loads(path.read_text())
            if payload.get("ttl"):
                elapsed = time.time() - payload.get("stored_at", 0)
                if elapsed > payload["ttl"]:
                    path.unlink(missing_ok=True)
                    return MemoryResult(key=key, found=False, error="TTL expired", store_type="working")
            return MemoryResult(key=key, data=payload.get("data"), found=True, store_type="working")
        except Exception as e:
            return MemoryResult(key=key, found=False, error=str(e), store_type="working")

    async def search(self, query: str | dict, top_k: int = 5) -> list[MemoryResult]:
        if isinstance(query, dict):
            query = str(query)
        q = query.lower()
        results: list[MemoryResult] = []
        for path in sorted(self.storage_dir.glob("*.json")):
            if len(results) >= top_k:
                break
            try:
                payload = json.loads(path.read_text())
                data_str = json.dumps(payload.get("data", {}))
                if q in path.stem.lower() or q in data_str.lower():
                    results.append(MemoryResult(key=payload["key"], data=payload.get("data"), found=True, store_type="working"))
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
