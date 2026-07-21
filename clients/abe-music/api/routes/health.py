from fastapi import APIRouter
from datetime import datetime, timezone

router = APIRouter(prefix="/api", tags=["health"])

@router.get("/health")
def health():
    return {
        "status": "ok",
        "services": {
            "webui": {"status": "online"},
            "abe_api": {"status": "online"},
            "scrapers": {"status": "idle"},
            "neo4j": {"status": "connected"},
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
