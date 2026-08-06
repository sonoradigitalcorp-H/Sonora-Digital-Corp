from fastapi import APIRouter
from database import query_db

router = APIRouter(prefix="/api", tags=["stats"])

@router.get("/stats")
def get_stats():
    artists = query_db("SELECT COUNT(*) as count, COALESCE(SUM(streams),0) as total_streams FROM artists")
    services = query_db("SELECT COUNT(*) as count FROM services")
    a = artists[0] if artists else {}
    s = services[0] if services else {}
    return {
        "artists": a.get("count", 0),
        "total_streams": a.get("total_streams", 0),
        "services": s.get("count", 0)
    }
