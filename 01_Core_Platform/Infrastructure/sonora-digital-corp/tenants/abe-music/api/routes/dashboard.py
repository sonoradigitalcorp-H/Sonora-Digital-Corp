from fastapi import APIRouter, Depends
from database import query_db
from routes.auth import verify_token

router = APIRouter(prefix="/api/portal", tags=["dashboard"])

@router.get("/dashboard")
def get_dashboard(_=Depends(verify_token)):
    artists = query_db("SELECT id, name, streams, revenue, monthly_listeners, top_song, instagram, image FROM artists ORDER BY streams DESC")
    contacts = query_db("SELECT id, name, email, service_interest, status, created_at FROM contacts ORDER BY created_at DESC LIMIT 10")
    total_streams = sum(a.get("streams", 0) or 0 for a in artists)
    total_revenue = sum(a.get("revenue", 0) or 0 for a in artists)
    return {
        "total_streams": total_streams,
        "revenue": round(total_revenue, 2),
        "artist_count": len(artists),
        "lead_count": len(contacts),
        "artists": artists,
        "recent_leads": contacts[:5],
        "engagement": min(round(len(contacts) * 5 + 70, 1), 99.9),
    }

@router.get("/api/portal/dashboard")
def get_dashboard_alt(_=Depends(verify_token)):
    return get_dashboard(_)
