import uuid
from fastapi import APIRouter, Depends, HTTPException
from models import ServiceCreate, ArtistCreate
from database import query_db
from routes.auth import admin_required

router = APIRouter(prefix="/api/admin", tags=["admin"])

@router.post("/services")
def create_service(svc: ServiceCreate, _=Depends(admin_required)):
    query_db(
        "INSERT INTO services (title, description, icon) VALUES (:title, :desc, :icon)",
        {"title": svc.title, "desc": svc.description, "icon": svc.icon}
    )
    return {"ok": True}

@router.put("/services/{svc_id}")
def update_service(svc_id: str, svc: ServiceCreate, _=Depends(admin_required)):
    query_db(
        "UPDATE services SET title = :title, description = :desc, icon = :icon WHERE id = :id",
        {"title": svc.title, "desc": svc.description, "icon": svc.icon, "id": svc_id}
    )
    return {"ok": True}

@router.delete("/services/{svc_id}")
def delete_service(svc_id: str, _=Depends(admin_required)):
    query_db("DELETE FROM services WHERE id = :id", {"id": svc_id})
    return {"ok": True}

@router.post("/artists")
def create_artist(art: ArtistCreate, _=Depends(admin_required)):
    query_db(
        "INSERT INTO artists (name, streams, label, image) VALUES (:name, :streams, :label, :image)",
        {"name": art.name, "streams": art.streams, "label": "ABE Music Group", "image": art.image}
    )
    return {"ok": True}

@router.put("/artists/{art_id}")
def update_artist(art_id: str, art: ArtistCreate, _=Depends(admin_required)):
    query_db(
        "UPDATE artists SET name = :name, streams = :streams, label = :label, image = :image WHERE id = :id",
        {"name": art.name, "streams": art.streams, "label": "ABE Music Group", "image": art.image, "id": art_id}
    )
    return {"ok": True}

@router.delete("/artists/{art_id}")
def delete_artist(art_id: str, _=Depends(admin_required)):
    query_db("DELETE FROM artists WHERE id = :id", {"id": art_id})
    return {"ok": True}

@router.get("/analytics")
def get_analytics(_=Depends(admin_required)):
    artists = query_db("SELECT COUNT(*) as count, COALESCE(SUM(streams),0) as total_streams, COALESCE(SUM(revenue),0) as total_revenue FROM artists")
    a = artists[0] if artists else {}
    return {
        "artist_count": a.get("count", 0),
        "total_streams": a.get("total_streams", 0),
        "total_revenue": round(float(a.get("total_revenue", 0)), 2),
    }
