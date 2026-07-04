"""Brain Web UI — FastAPI endpoints for querying the unified brain"""
from fastapi import APIRouter, Query
from apps.brain.mcp_tool import unified_brain_query
from apps.brain.service import BrainService

router = APIRouter(prefix="/brain", tags=["brain"])

@router.get("/search")
def brain_search(
    q: str = Query(..., description="Search query"),
    type: str = Query(None, description="Filter by type"),
    limit: int = Query(10, ge=1, le=100),
):
    result = unified_brain_query(q, type_filter=type, limit=limit)
    return result

@router.get("/stats")
def brain_stats():
    b = BrainService()
    try:
        with b.neo4j.session() as s:
            total = s.run("MATCH (n:Knowledge) RETURN count(n) as c").single()["c"]
            by_type = s.run(
                "MATCH (n:Knowledge) RETURN n.type as type, count(n) as count ORDER BY count DESC"
            ).data()
    finally:
        b.close()

    return {
        "total_nodes": total,
        "nodes_by_type": by_type,
        "status": "ok",
    }

@router.post("/sync")
def brain_sync():
    from apps.brain.sync import BrainSyncer
    syncer = BrainSyncer()
    results = syncer.full_sync()
    syncer.close()
    return {"status": "ok", "results": results}
