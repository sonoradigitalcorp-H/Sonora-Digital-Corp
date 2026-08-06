"""Harvis OS - Sistema Operativo para Agentes de IA"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Histogram, generate_latest
from prometheus_client.core import REGISTRY
from starlette.responses import Response

from .config import settings
from ..routes import health, tasks, events, agents
from ..voice import routes as voice_routes
from ..dispatcher import Dispatcher
from ..registry import AgentRegistry
from ..events import EventBus
from ..planner import Planner
from ..memory import ContextManager, VectorStore, GraphStore
from ..adapters import TelegramAdapter
from ..connectors import FastEmbedConnector

# Metrics
TASKS_TOTAL = Counter(
    "harvis_tasks_total",
    "Total tasks processed",
    ["status", "category", "agent"]
)

TASK_DURATION = Histogram(
    "harvis_task_duration_seconds",
    "Task processing duration",
    ["category"]
)


# Singleton instances
dispatcher = Dispatcher()
registry = AgentRegistry()
event_bus = EventBus()
planner = Planner()
context_manager = ContextManager()
fastembed = FastEmbedConnector()
vector_store = VectorStore(embedding_connector=fastembed)
graph_store = GraphStore()
telegram_adapter = TelegramAdapter()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    print(f"Starting Harvis OS v{settings.VERSION}")
    print(f"Redis: {settings.REDIS_URL}")
    print(f"PostgreSQL: {settings.POSTGRES_URL}")

    # Publish system started event
    from ..events.bus import Event
    event_bus.publish(Event(
        id="system-started",
        type="system.started",
        source="harvis-core",
        payload={"version": settings.VERSION},
    ))

    yield

    # Shutdown
    print("Shutting down Harvis OS")


app = FastAPI(
    title="Harvis OS",
    description="Sistema Operativo para Agentes de IA",
    version=settings.VERSION,
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(health.router, tags=["health"])
app.include_router(tasks.router, prefix="/api/v1", tags=["tasks"])
app.include_router(events.router, prefix="/api/v1", tags=["events"])
app.include_router(agents.router, prefix="/api/v1", tags=["agents"])
app.include_router(voice_routes.router, tags=["voice"])


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(
        content=generate_latest(REGISTRY),
        media_type="text/plain"
    )


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Harvis OS",
        "version": settings.VERSION,
        "description": "Sistema Operativo para Agentes de IA",
        "docs": "/docs",
        "health": "/health",
        "metrics": "/metrics",
        "components": {
            "dispatcher": dispatcher.get_stats(),
            "registry": registry.get_stats(),
            "event_bus": event_bus.get_stats(),
            "planner": planner.get_stats(),
            "context": context_manager.get_stats(),
            "vector_store": vector_store.get_stats(),
            "graph_store": graph_store.get_stats(),
            "telegram": telegram_adapter.get_stats(),
        }
    }
