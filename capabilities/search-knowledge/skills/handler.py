"""search-knowledge capability — actual logic (HAS-005)
Searches across memory stores: semantic (Qdrant), graph (Neo4j), long (engram), working.
Returns ranked results from all available stores.
"""
import json
import sqlite3
from pathlib import Path


REPO = Path(__file__).resolve().parent.parent.parent.parent


async def run(query: str, stores: list[str] | None = None) -> dict:
    if stores is None:
        stores = ["semantic", "graph", "long", "working"]
    results = {}
    for store in stores:
        fn = _search_dispatch.get(store)
        if fn:
            try:
                results[store] = await fn(query)
            except Exception as e:
                results[store] = {"error": str(e), "count": 0}
    return {"status": "success", "query": query, "stores_searched": stores, "results": results, "total": sum(r.get("count", 0) for r in results.values() if isinstance(r, dict))}


async def _search_semantic(query: str) -> dict:
    return {"count": 0, "message": "Qdrant not connected — semantic search unavailable"}


async def _search_graph(query: str) -> dict:
    return {"count": 0, "message": "Neo4j not connected — graph search unavailable"}


async def _search_long(query: str) -> dict:
    db_path = REPO / "state" / "engram.db"
    if not db_path.exists():
        return {"count": 0, "message": "engram.db not found"}
    conn = sqlite3.connect(str(db_path))
    c = conn.cursor()
    c.execute("SELECT key, value FROM memories WHERE value LIKE ? ORDER BY created_at DESC LIMIT 10", (f"%{query}%",))
    rows = c.fetchall()
    conn.close()
    return {"count": len(rows), "results": [{"key": r[0], "value": r[1][:200]} for r in rows]}


async def _search_working(query: str) -> dict:
    working_file = REPO / "state" / "working_memory.json"
    if not working_file.exists():
        return {"count": 0, "message": "working_memory.json not found"}
    data = json.loads(working_file.read_text())
    matches = []
    for entry in data if isinstance(data, list) else data.get("entries", []):
        text = json.dumps(entry)
        if query.lower() in text.lower():
            matches.append(entry)
    return {"count": len(matches), "results": matches[:10]}


_search_dispatch = {
    "semantic": _search_semantic,
    "graph": _search_graph,
    "long": _search_long,
    "working": _search_working,
}
