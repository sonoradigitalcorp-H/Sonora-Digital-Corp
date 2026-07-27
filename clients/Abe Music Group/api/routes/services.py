from fastapi import APIRouter
from database import query_db

router = APIRouter(prefix="/api", tags=["services"])

@router.get("/services")
def get_services():
    return query_db("SELECT id, title, description, icon FROM services ORDER BY sort_order ASC")
