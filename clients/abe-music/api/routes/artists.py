from fastapi import APIRouter
from database import query_db

router = APIRouter(prefix="/api", tags=["artists"])

@router.get("/artists")
def get_artists():
    return query_db("SELECT * FROM artists ORDER BY streams DESC")
