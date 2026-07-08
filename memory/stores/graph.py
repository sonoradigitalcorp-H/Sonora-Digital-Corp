import json
from pathlib import Path
from typing import Any

from memory.base import MemoryResult, MemoryStore

REPO = Path(__file__).resolve().parent.parent.parent
GRAPH_DIR = REPO / "state" / "graph"


class GraphMemory(MemoryStore):
    name = "graph"

    def __init__(self, storage_dir: str | Path | None = None):
        self.storage_dir = Path(storage_dir) if storage_dir else GRAPH_DIR
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self._neo4j = None
        self._init_neo4j()

    def _init_neo4j(self):
        try:
            from neo4j import GraphDatabase
            self._neo4j = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
            self._neo4j.verify_connectivity()
        except Exception:
            self._neo4j = None

    def _path(self, key: str) -> Path:
        safe = key.replace("/", "_").replace("\\", "_")
        return self.storage_dir / f"{safe}.json"

    async def store(self, key: str, data: dict, ttl: int | None = None) -> MemoryResult:
        if self._neo4j:
            try:
                async with self._neo4j.session() as session:
                    await session.run(
                        "MERGE (n:Entity {id: $key}) SET n.data = $data",
                        key=key, data=json.dumps(data),
                    )
                return MemoryResult(key=key, data=data, found=True, store_type="graph")
            except Exception:
                pass
        self._path(key).write_text(json.dumps(data, indent=2, default=str))
        return MemoryResult(key=key, data=data, found=True, store_type="graph")

    async def retrieve(self, key: str) -> MemoryResult:
        if self._neo4j:
            try:
                async with self._neo4j.session() as session:
                    result = await session.run("MATCH (n:Entity {id: $key}) RETURN n.data as data", key=key)
                    row = await result.single()
                    if row:
                        return MemoryResult(key=key, data=json.loads(row["data"]), found=True, store_type="graph")
                return MemoryResult(key=key, found=False, store_type="graph")
            except Exception:
                pass
        path = self._path(key)
        if path.exists():
            data = json.loads(path.read_text())
            return MemoryResult(key=key, data=data, found=True, store_type="graph")
        return MemoryResult(key=key, found=False, store_type="graph")

    async def search(self, query: str | dict, top_k: int = 5) -> list[MemoryResult]:
        if self._neo4j:
            try:
                async with self._neo4j.session() as session:
                    result = await session.run(
                        "MATCH (n:Entity) WHERE n.id CONTAINS $q RETURN n.id as key, n.data as data LIMIT $limit",
                        q=str(query), limit=top_k,
                    )
                    rows = await result.fetch(top_k)
                    return [
                        MemoryResult(key=row["key"], data=json.loads(row["data"]), found=True, store_type="graph")
                        for row in rows
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
                    results.append(MemoryResult(key=path.stem, data=data, found=True, store_type="graph"))
            except Exception:
                continue
        return results

    async def delete(self, key: str) -> bool:
        if self._neo4j:
            try:
                async with self._neo4j.session() as session:
                    await session.run("MATCH (n:Entity {id: $key}) DETACH DELETE n", key=key)
                return True
            except Exception:
                pass
        path = self._path(key)
        if path.exists():
            path.unlink()
            return True
        return False

    async def list_keys(self, prefix: str = "") -> list[str]:
        if self._neo4j:
            try:
                async with self._neo4j.session() as session:
                    result = await session.run(
                        "MATCH (n:Entity) WHERE n.id STARTS WITH $p RETURN n.id as key",
                        p=prefix,
                    )
                    rows = await result.fetch()
                    return [row["key"] for row in rows]
            except Exception:
                pass
        return [
            p.stem for p in sorted(self.storage_dir.glob("*.json"))
            if p.stem.startswith(prefix)
        ]
