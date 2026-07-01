from fastapi import APIRouter, HTTPException
from src.core.abe_music import ArtistCRM, KPIDashboard

router = APIRouter()

_crm = ArtistCRM(data_path=ArtistCRM.DEFAULT_DATA_PATH)
_kpi = KPIDashboard(_crm)


@router.post("/api/abe/artists")
async def abe_create_artist(data: dict):
    return _crm.create_artist(data)


@router.get("/api/abe/artists")
async def abe_list_artists(status: str = None):
    return {"artists": _crm.list_artists(status)}


@router.get("/api/abe/artists/{artist_id}")
async def abe_get_artist(artist_id: str):
    artist = _crm.get_artist(artist_id)
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")
    return artist


@router.post("/api/abe/artists/{artist_id}/releases")
async def abe_create_release(artist_id: str, data: dict):
    release = _crm.create_release(artist_id, data)
    if not release:
        raise HTTPException(status_code=404, detail="Artist not found")
    return release


@router.post("/api/abe/releases/{release_id}/stream")
async def abe_record_stream(release_id: str, data: dict = None):
    result = _crm.record_stream(release_id, (data or {}).get("amount", 1))
    if not result:
        raise HTTPException(status_code=404, detail="Release not found")
    return result


@router.post("/api/abe/releases/{release_id}/revenue")
async def abe_record_revenue(release_id: str, data: dict):
    return _crm.record_revenue(
        release_id, data.get("amount", 0), data.get("source", "streaming")
    )


@router.get("/api/abe/dashboard/ceo")
async def abe_ceo_dashboard():
    return _kpi.get_ceo_dashboard()


@router.get("/api/abe/dashboard/artist/{artist_id}")
async def abe_artist_kpi(artist_id: str):
    kpi = _kpi.get_artist_kpi(artist_id)
    if not kpi:
        raise HTTPException(status_code=404, detail="Artist not found")
    return kpi


@router.get("/api/abe/sync/status")
async def abe_sync_status():
    return _kpi.get_sync_status()
