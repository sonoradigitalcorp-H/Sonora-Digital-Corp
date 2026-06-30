"""
Zamora Brand Studio — API router.
"""

import logging

from fastapi import APIRouter
from src.core.zamora import ZamoraStudio
from starlette.responses import JSONResponse

log = logging.getLogger("jarvis.zamora_router")
router = APIRouter(prefix="/api/zamora", tags=["zamora"])

_zamora = ZamoraStudio()


@router.get("/services")
async def list_services():
    services = _zamora.list_services()
    return JSONResponse([{"name": s.name, "description": s.description, "icon": s.icon, "price_mxn": s.price_mxn} for s in services])


@router.get("/pricing")
async def get_pricing():
    return JSONResponse(_zamora.get_pricing())


@router.get("/portfolio")
async def list_portfolio():
    items = _zamora.list_portfolio()
    return JSONResponse([{"title": p.title, "description": p.description, "image_url": p.image_url, "category": p.category, "tags": p.tags} for p in items])
