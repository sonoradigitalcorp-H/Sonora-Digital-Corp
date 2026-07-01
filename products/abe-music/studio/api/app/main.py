from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from contextlib import asynccontextmanager

from app.db import init_db
from app.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    import os
    Path(settings.storage_path).mkdir(parents=True, exist_ok=True)
    yield

app = FastAPI(title="ABE Studio API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

static_dir = Path(settings.storage_path)
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

from app.routes.generate import router as gen_router
from app.routes.tasks import router as tasks_router
from app.routes.webhook import router as wh_router
from app.routes.poll import router as poll_router

app.include_router(gen_router)
app.include_router(tasks_router)
app.include_router(wh_router)
app.include_router(poll_router)

@app.get("/health")
async def health():
    return {"status": "ok", "service": "abe-studio-api"}
