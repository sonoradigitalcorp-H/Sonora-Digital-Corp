import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import (
    auth_router, stats_router, services_router, artists_router,
    contact_router, dashboard_router, health_router, admin_router, ai_router,
    track_router
)

app = FastAPI(title="ABE Music API", version="3.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(stats_router)
app.include_router(services_router)
app.include_router(artists_router)
app.include_router(contact_router)
app.include_router(dashboard_router)
app.include_router(health_router)
app.include_router(admin_router)
app.include_router(ai_router)
app.include_router(track_router)
