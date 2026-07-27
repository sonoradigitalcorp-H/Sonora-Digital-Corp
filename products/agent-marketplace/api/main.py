"""Mystic Agent Marketplace — API"""

import os
import json
from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .auth import router as auth_router, decode_jwt
from .routes.marketplace import router as marketplace_router
from .routes.provisioning import router as provisioning_router
from .routes.dashboard import router as dashboard_router

REPO = Path(__file__).resolve().parent.parent.parent.parent

app = FastAPI(
    title="Mystic Agent Marketplace API",
    version="1.0.0",
    docs_url="/api/docs",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(auth_router)
app.include_router(marketplace_router, prefix="/api")
app.include_router(provisioning_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")

# Static frontend
FRONTEND_DIR = REPO / "products" / "agent-marketplace" / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")


@app.get("/api/health")
async def health():
    return {"status": "healthy", "service": "agent-marketplace", "version": "1.0.0"}
