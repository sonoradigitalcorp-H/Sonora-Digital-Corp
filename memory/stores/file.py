import shutil
from pathlib import Path
from typing import Any

from memory.base import MemoryResult, MemoryStore

REPO = Path(__file__).resolve().parent.parent.parent
FILES_DIR = REPO / "state" / "files"


class FileMemory(MemoryStore):
    name = "file"

    def __init__(self, storage_dir: str | Path | None = None):
        self.storage_dir = Path(storage_dir) if storage_dir else FILES_DIR
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        safe = key.replace("/", "_").replace("\\", "_")
        return self.storage_dir / safe

    async def store(self, key: str, data: dict, ttl: int | None = None) -> MemoryResult:
        path = self._path(key)
        if "content" in data and isinstance(data["content"], str):
            path.write_text(data["content"])
        elif "bytes" in data:
            path.write_bytes(data["bytes"])
        else:
            import json
            path.write_text(json.dumps(data, default=str))
        return MemoryResult(key=key, data={"path": str(path), "size": path.stat().st_size}, found=True, store_type="file")

    async def retrieve(self, key: str) -> MemoryResult:
        path = self._path(key)
        if not path.exists():
            return MemoryResult(key=key, found=False, store_type="file")
        try:
            data = {"path": str(path), "size": path.stat().st_size}
            if path.suffix in (".txt", ".md", ".json", ".yaml", ".yml", ".csv", ".html", ".css", ".js", ".py"):
                data["content"] = path.read_text()
            else:
                data["content"] = f"[binary file: {path.suffix}, {path.stat().st_size} bytes]"
            return MemoryResult(key=key, data=data, found=True, store_type="file")
        except Exception as e:
            return MemoryResult(key=key, found=False, error=str(e), store_type="file")

    async def search(self, query: str | dict, top_k: int = 5) -> list[MemoryResult]:
        if isinstance(query, dict):
            query = str(query)
        q = query.lower()
        results: list[MemoryResult] = []
        for path in sorted(self.storage_dir.iterdir()):
            if len(results) >= top_k:
                break
            if q in path.name.lower():
                data = {"path": str(path), "size": path.stat().st_size}
                results.append(MemoryResult(key=path.name, data=data, found=True, store_type="file"))
        return results

    async def delete(self, key: str) -> bool:
        path = self._path(key)
        if path.exists():
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
            return True
        return False

    async def list_keys(self, prefix: str = "") -> list[str]:
        return [
            p.name for p in sorted(self.storage_dir.iterdir())
            if p.name.startswith(prefix)
        ]
