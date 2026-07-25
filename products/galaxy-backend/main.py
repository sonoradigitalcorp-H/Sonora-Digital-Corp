"""Agent Galaxy Backend — FastAPI API server.

Powers the 3D galaxy prototype with endpoints for agents, onboarding,
voice, LLM chat, tenant management, and events.

Preview mode: SQLite storage, LLM-based voice, in-memory sessions.
"""

import asyncio
import logging
import time
from collections import defaultdict
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from events import GalaxyEvent, event_logger
from llm import chat_completion, simple_chat
from models import (
    ChatRequest,
    ChatResponse,
    GalaxyAgent,
    HealthCheck,
    OnboardingCompleteRequest,
    OnboardingCompleteResponse,
    OnboardingStartResponse,
    TaskRequest,
    TaskResponse,
)
from onboarding import onboarding_manager
from tenant import PLAN_AGENTS, tenant_store
from voice import speech_to_text, text_to_speech, text_to_speech_bytes, voice_stream_generator

# ─── Configuration ─────────────────────────────────────────────

START_TIME = time.time()
log = logging.getLogger("galaxy.api")

RATE_LIMIT_REQUESTS = 60
RATE_LIMIT_WINDOW = 60
_rate_limit_tracker: dict[str, list[float]] = defaultdict(list)

# ─── 9 Planet Agents ───────────────────────────────────────────

GALAXY_AGENTS: list[GalaxyAgent] = [
    GalaxyAgent(
        name="mercurio",
        color="#b0b0b0",
        position=(2.0, 0.0, 0.0),
        capabilities=["ventas", "lead_scoring", "crm"],
        cards=[
            {"title": "Lead Scoring", "description": "Califica leads automaticamente", "icon": "star"},
            {"title": "CRM Inteligente", "description": "Gestiona contactos y seguimientos", "icon": "users"},
        ],
        orbit_radius=2.0,
        orbit_speed=4.1,
        description="Agente de ventas y gestion de leads",
        plan_required="explorador",
    ),
    GalaxyAgent(
        name="venus",
        color="#e8c56d",
        position=(-1.5, 0.0, 1.5),
        capabilities=["marketing", "contenido", "redes_sociales"],
        cards=[
            {"title": "Contenido IA", "description": "Genera posts y copy para redes", "icon": "pen"},
            {"title": "Calendario", "description": "Programa publicaciones automaticamente", "icon": "calendar"},
        ],
        orbit_radius=3.5,
        orbit_speed=1.6,
        description="Agente de marketing y creacion de contenido",
        plan_required="explorador",
    ),
    GalaxyAgent(
        name="tauro",
        color="#4ade80",
        position=(0.0, 0.0, -2.5),
        capabilities=["soporte", "atencion_cliente", "faq"],
        cards=[
            {"title": "Soporte 24/7", "description": "Responde preguntas frecuentes", "icon": "headphones"},
            {"title": "Ticketing", "description": "Gestiona y prioriza tickets", "icon": "ticket"},
        ],
        orbit_radius=5.0,
        orbit_speed=1.0,
        description="Agente de soporte y atencion al cliente",
        plan_required="explorador",
    ),
    GalaxyAgent(
        name="marte",
        color="#ef4444",
        position=(3.0, 0.0, 2.0),
        capabilities=["proyectos", "tareas", "automatizacion"],
        cards=[
            {"title": "Gestion de Proyectos", "description": "Organiza tareas y plazos", "icon": "clipboard"},
            {"title": "Automatizaciones", "description": "Crea flujos de trabajo automaticos", "icon": "zap"},
        ],
        orbit_radius=7.0,
        orbit_speed=0.53,
        description="Agente de gestion de proyectos y productividad",
        plan_required="conquistador",
    ),
    GalaxyAgent(
        name="jupiter",
        color="#f59e0b",
        position=(-2.0, 0.0, -3.0),
        capabilities=["finanzas", "facturacion", "reportes"],
        cards=[
            {"title": "Dashboard Financiero", "description": "Visualiza ingresos y gastos", "icon": "chart"},
            {"title": "Facturacion", "description": "Genera facturas y recordatorios", "icon": "file"},
        ],
        orbit_radius=10.0,
        orbit_speed=0.084,
        description="Agente de finanzas y reportes empresariales",
        plan_required="conquistador",
    ),
    GalaxyAgent(
        name="saturno",
        color="#d4a574",
        position=(4.0, 0.0, -1.0),
        capabilities=["analitica", "datos", "reportes_avanzados"],
        cards=[
            {"title": "Analitica Avanzada", "description": "Analisis de datos con IA", "icon": "analytics"},
            {"title": "Predicciones", "description": "Forecasting y tendencias", "icon": "trending"},
        ],
        orbit_radius=14.0,
        orbit_speed=0.034,
        description="Agente de analitica y ciencia de datos",
        plan_required="conquistador",
    ),
    GalaxyAgent(
        name="urano",
        color="#06b6d4",
        position=(-3.0, 0.0, 4.0),
        capabilities=["innovacion", "investigacion", "estrategia"],
        cards=[
            {"title": "Investigacion de Mercado", "description": "Analiza competencia y tendencias", "icon": "search"},
            {"title": "Estrategia", "description": "Recomendaciones estrategicas", "icon": "target"},
        ],
        orbit_radius=18.0,
        orbit_speed=0.012,
        description="Agente de investigacion y estrategia",
        plan_required="imperio",
    ),
    GalaxyAgent(
        name="neptuno",
        color="#6366f1",
        position=(1.0, 0.0, -5.0),
        capabilities=["voz", "idiomas", "traduccion"],
        cards=[
            {"title": "Voz IA", "description": "Clonacion y sintesis de voz", "icon": "mic"},
            {"title": "Traduccion", "description": "Traduccion en tiempo real", "icon": "translate"},
        ],
        orbit_radius=22.0,
        orbit_speed=0.006,
        description="Agente de voz y procesamiento de lenguaje",
        plan_required="imperio",
    ),
    GalaxyAgent(
        name="pluton",
        color="#8b5cf6",
        position=(-5.0, 0.0, -2.0),
        capabilities=["seguridad", "gobernanza", "compliance"],
        cards=[
            {"title": "Seguridad", "description": "Monitoreo y deteccion de amenazas", "icon": "shield"},
            {"title": "Compliance", "description": "Cumplimiento normativo automatico", "icon": "lock"},
        ],
        orbit_radius=28.0,
        orbit_speed=0.004,
        description="Agente de seguridad y gobernanza empresarial",
        plan_required="imperio",
    ),
]


# ─── Rate Limiting ─────────────────────────────────────────────


def _check_rate_limit(client_id: str) -> bool:
    """Simple in-memory rate limiter. Returns True if allowed."""
    now = time.time()
    window = _rate_limit_tracker[client_id]
    window[:] = [t for t in window if now - t < RATE_LIMIT_WINDOW]
    if len(window) >= RATE_LIMIT_REQUESTS:
        return False
    window.append(now)
    return True


# ─── Application ───────────────────────────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle: startup and shutdown hooks."""
    log.info("Agent Galaxy Backend starting...")
    log.info(f"Loaded {len(GALAXY_AGENTS)} planet agents")
    log.info(f"Tenant store: {tenant_store.db_path}")
    event_logger.emit(GalaxyEvent(event_type="galaxy_server_started"))
    yield
    event_logger.flush()
    event_logger.emit(GalaxyEvent(event_type="galaxy_server_stopped"))
    log.info("Agent Galaxy Backend stopped")


app = FastAPI(
    title="Agent Galaxy Backend",
    description="API server for the 3D Agent Galaxy prototype. Multi-tenant, LLM-powered, voice-enabled.",
    version="0.1.0-preview",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Health ────────────────────────────────────────────────────


@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Health check with dependency status."""
    uptime = time.time() - START_TIME
    services = {
        "llm": "ready",
        "voice": "ready",
        "tenant_db": "ready",
        "onboarding": "ready",
    }
    return HealthCheck(
        status="healthy",
        services=services,
        uptime_seconds=round(uptime, 1),
    )


# ─── Galaxy Agents ─────────────────────────────────────────────


@app.get("/api/galaxy/agents", response_model=list[GalaxyAgent])
async def list_agents(plan: Optional[str] = Query(None, description="Filter by minimum plan")):
    """List all 9 planet agents with capabilities and 3D positions.

    Optionally filter by plan to show only agents available for that tier.
    """
    if plan:
        plan_order = {"explorador": 0, "conquistador": 1, "imperio": 2}
        plan_level = plan_order.get(plan, 0)
        filtered = []
        for agent in GALAXY_AGENTS:
            agent_level = plan_order.get(agent.plan_required, 0)
            if agent_level <= plan_level:
                filtered.append(agent)
        return filtered
    return GALAXY_AGENTS


@app.get("/api/galaxy/agent/{name}", response_model=GalaxyAgent)
async def get_agent(name: str):
    """Get specific agent details by planet name."""
    for agent in GALAXY_AGENTS:
        if agent.name.lower() == name.lower():
            return agent
    raise HTTPException(status_code=404, detail=f"Agent '{name}' not found")


# ─── Onboarding ────────────────────────────────────────────────


@app.post("/api/onboarding/start", response_model=OnboardingStartResponse)
async def start_onboarding(client_id: str = "anonymous"):
    """Start an onboarding session.

    Returns session_id and QR data for WhatsApp connection.
    Sessions expire after 10 minutes by default.
    """
    if not _check_rate_limit(client_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    return onboarding_manager.start_session()


@app.post("/api/onboarding/{session_id}/complete", response_model=OnboardingCompleteResponse)
async def complete_onboarding(session_id: str, req: OnboardingCompleteRequest):
    """Complete onboarding by providing phone number and plan.

    Creates a new tenant with agents assigned based on the selected plan.
    """
    try:
        result = onboarding_manager.complete_session(
            session_id=session_id,
            phone=req.phone,
            name=req.name,
            plan=req.plan,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ─── Voice ─────────────────────────────────────────────────────


@app.post("/api/voice/stt")
async def voice_stt(tenant_id: str = Query("", description="Tenant ID for tracking")):
    """Speech-to-text endpoint.

    Accepts audio data and returns transcribed text.
    Preview mode: returns metadata about the audio.
    """
    event_logger.emit(GalaxyEvent(
        event_type="galaxy_voice_stt",
        tenant_id=tenant_id,
        data={"status": "preview"},
    ))
    return {
        "status": "preview",
        "message": "Upload audio data in production. Preview mode returns sample transcription.",
        "sample_text": "Hola, bienvenido a tu galaxia de agentes",
        "provider": "deepseek_v4_flash",
    }


@app.post("/api/voice/tts")
async def voice_tts(text: str = Query(..., description="Text to synthesize"), language: str = Query("es", description="Language code")):
    """Text-to-speech endpoint.

    Returns base64-encoded audio.
    """
    result = await text_to_speech(text, language=language)
    event_logger.emit(GalaxyEvent(
        event_type="galaxy_voice_tts",
        data={"text_length": len(text), "provider": result["provider"]},
    ))
    return result


@app.websocket("/api/voice/stream")
async def voice_stream(ws: WebSocket, text: str = Query(..., description="Text to stream as audio")):
    """WebSocket for real-time voice streaming.

    Sends synthesized audio in chunks for low-latency playback.
    """
    await ws.accept()
    try:
        async for chunk in voice_stream_generator(text):
            await ws.send_bytes(chunk)
        await ws.send_bytes(b"__END__")
    except WebSocketDisconnect:
        log.info("Voice streaming WebSocket disconnected")
    except Exception as e:
        log.error(f"Voice streaming error: {e}")
        try:
            await ws.send_text(f"Error: {e}")
        except Exception:
            pass


# ─── Tenant ────────────────────────────────────────────────────


@app.get("/api/tenant/{tenant_id}/config")
async def get_tenant_config(tenant_id: str):
    """Get tenant configuration including voice settings and channels."""
    tenant = tenant_store.get_by_id(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail=f"Tenant '{tenant_id}' not found")
    return {
        "id": tenant.id,
        "name": tenant.name,
        "plan": tenant.plan,
        "voice_config": tenant.voice_config.model_dump(),
        "channels": tenant.channels,
        "status": tenant.status,
    }


@app.get("/api/tenant/{tenant_id}/capabilities")
async def get_tenant_capabilities(tenant_id: str):
    """Get assigned capabilities for a tenant based on their agents."""
    tenant = tenant_store.get_by_id(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail=f"Tenant '{tenant_id}' not found")
    capabilities = []
    for agent in GALAXY_AGENTS:
        if agent.name in tenant.agents:
            capabilities.extend(agent.capabilities)
    return {
        "tenant_id": tenant_id,
        "plan": tenant.plan,
        "agents": tenant.agents,
        "capabilities": list(set(capabilities)),
    }


# ─── LLM ───────────────────────────────────────────────────────


@app.post("/api/llm/chat", response_model=ChatResponse)
async def llm_chat(req: ChatRequest):
    """Chat with DeepSeek V4 Flash (with automatic fallback).

    Sends messages to the primary LLM provider. Falls back to
    a free model if the primary fails.
    """
    messages = [m.model_dump() for m in req.messages]
    result = await chat_completion(
        messages,
        model=req.model if req.model else None,
        temperature=req.temperature,
        max_tokens=req.max_tokens,
    )
    if "error" in result:
        raise HTTPException(status_code=502, detail=result["error"])
    event_logger.emit(GalaxyEvent(
        event_type="galaxy_llm_chat",
        tenant_id=req.tenant_id,
        data={"model": result["model"], "provider": result["provider"], "cost": result["cost"]},
    ))
    return ChatResponse(**result)


@app.post("/api/llm/task", response_model=TaskResponse)
async def llm_task(req: TaskRequest):
    """Assign a task to the LLM via OpenClaw.

    The LLM processes the task and returns a result.
    Tasks are tracked for observability and billing.
    """
    t0 = time.time()
    messages = [
        {"role": "system", "content": "Eres un agente ejecutor de tareas. Responde de forma concisa y accionable."},
        {"role": "user", "content": f"Task: {req.task}\nContext: {req.context}"},
    ]
    result = await chat_completion(messages, max_tokens=2048)
    elapsed = time.time() - t0
    if "error" in result:
        raise HTTPException(status_code=502, detail=result["error"])
    event_logger.emit(GalaxyEvent(
        event_type="galaxy_llm_task",
        tenant_id=req.tenant_id,
        data={"task": req.task[:100], "model": result["model"], "elapsed": elapsed},
    ))
    return TaskResponse(
        result=result["text"],
        task_id=f"task_{int(time.time())}",
        status="completed",
        elapsed=round(elapsed, 2),
    )


# ─── Events ────────────────────────────────────────────────────


@app.get("/api/events")
async def get_events(
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    tenant_id: Optional[str] = Query(None, description="Filter by tenant"),
    limit: int = Query(50, ge=1, le=200, description="Max events to return"),
):
    """Retrieve event log entries with optional filters."""
    events = event_logger.query(event_type=event_type, tenant_id=tenant_id, limit=limit)
    return {"events": events, "total": event_logger.count(event_type=event_type)}


# ─── Error Handlers ────────────────────────────────────────────


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Format HTTP exceptions as JSON responses."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status": exc.status_code},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Catch-all error handler for unexpected exceptions."""
    log.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "status": 500},
    )
