import json
from pathlib import Path
from typing import Any

from memory.base import MemoryResult, MemoryStore

REPO = Path(__file__).resolve().parent.parent.parent
ENGRAM_DB = REPO / "engram.db"


class LongMemory(MemoryStore):
    name = "long"

    def __init__(self, db_path: str | Path | None = None):
        self.db_path = Path(db_path) if db_path else ENGRAM_DB
        self._use_sqlite = self.db_path.exists()
        self._data: dict[str, dict] = {}

    async def store(self, key: str, data: dict, ttl: int | None = None) -> MemoryResult:
        if self._use_sqlite:
            try:
                import sqlite3
                conn = sqlite3.connect(str(self.db_path))
                conn.execute(
                    "INSERT OR REPLACE INTO engrams (key, data, updated_at) VALUES (?, ?, datetime('now'))",
                    (key, json.dumps(data)),
                )
                conn.commit()
                conn.close()
                return MemoryResult(key=key, data=data, found=True, store_type="long")
            except Exception as e:
                return MemoryResult(key=key, found=False, error=str(e), store_type="long")
        self._data[key] = data
        return MemoryResult(key=key, data=data, found=True, store_type="long")

    async def retrieve(self, key: str) -> MemoryResult:
        if self._use_sqlite:
            try:
                import sqlite3
                conn = sqlite3.connect(str(self.db_path))
                row = conn.execute("SELECT data FROM engrams WHERE key = ?", (key,)).fetchone()
                conn.close()
                if row:
                    return MemoryResult(key=key, data=json.loads(row[0]), found=True, store_type="long")
                return MemoryResult(key=key, found=False, store_type="long")
            except Exception:
                pass
        data = self._data.get(key)
        if data:
            return MemoryResult(key=key, data=data, found=True, store_type="long")
        return MemoryResult(key=key, found=False, store_type="long")

    async def search(self, query: str | dict, top_k: int = 5) -> list[MemoryResult]:
        if isinstance(query, dict):
            query = str(query)
        results: list[MemoryResult] = []
        q = query.lower()
        for key, data in self._data.items():
            if len(results) >= top_k:
                break
            if q in key.lower() or q in str(data).lower():
                results.append(MemoryResult(key=key, data=data, found=True, store_type="long"))
        return results

    async def delete(self, key: str) -> bool:
        if self._use_sqlite:
            try:
                import sqlite3
                conn = sqlite3.connect(str(self.db_path))
                conn.execute("DELETE FROM engrams WHERE key = ?", (key,))
                conn.commit()
                conn.close()
                return True
            except Exception:
                return False
        if key in self._data:
            del self._data[key]
            return True
        return False

    async def list_keys(self, prefix: str = "") -> list[str]:
        if self._use_sqlite:
            try:
                import sqlite3
                conn = sqlite3.connect(str(self.db_path))
                rows = conn.execute(
                    "SELECT key FROM engrams WHERE key LIKE ?", (f"{prefix}%",)
                ).fetchall()
                conn.close()
                return [r[0] for r in rows]
            except Exception:
                pass
        return [k for k in self._data if k.startswith(prefix)]
