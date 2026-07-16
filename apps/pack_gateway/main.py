import os
import sys
import logging
from pathlib import Path
from typing import Optional

import yaml
from fastapi import FastAPI, Header, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from apps.pack_gateway.models import (    ChatRequest,    ChatResponse,    ChatHistoryResponse,    ChatHistoryMessage,    ErrorResponse,    HealthResponse,    ProductResponse,    MetricsResponse,    WhatsAppStatusResponse,    WhatsAppRestartResponse,    LeadCreate,    LeadResponse,    PublicPacksResponse,)
from apps.pack_gateway.chat import load_pack, load_agent, get_tenant_config, build_prompt, chat_with_openrouter
from apps.pack_gateway.supabase_client import save_chat_message, get_chat_history, get_products, get_metrics, submit_lead, get_leads, update_lead_status, get_public_packs
from apps.pack_gateway.auth import get_current_user, get_optional_user
from apps.pack_gateway.security import SecurityHeadersMiddleware

log = logging.getLogger("pack-gateway")
logging.basicConfig(level=logging.INFO)

SDC_DIR = Path(os.path.expanduser("~/sonora-digital-corp"))
DASHBOARD_DIR = SDC_DIR / "apps" / "dashboard" / "dist"

app = FastAPI(title="SDC Pack Gateway", version="1.0.0")
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

if DASHBOARD_DIR.exists():
    app.mount("/dashboard/assets", StaticFiles(directory=str(DASHBOARD_DIR / "assets")), name="dashboard-assets")
    log.info("Dashboard static files mounted from %s", DASHBOARD_DIR)
else:
    log.warning("Dashboard dist not found at %s", DASHBOARD_DIR)


def _tenant_to_pack(tenant_id: str):
    parts = tenant_id.split("_", 1)
    if len(parts) != 2:
        return None, None, None
    pack_name = parts[0]
    tc = get_tenant_config(tenant_id)
    if not tc:
        return None, None, None
    return pack_name, tc.get("name", tenant_id), tc.get("pack", pack_name)


@app.get("/health", response_model=HealthResponse)
async def health(user: Optional[dict] = Depends(get_optional_user)):
    key = None
    env_path = Path(os.path.expanduser("~/.hermes/.env"))
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if line.startswith("OPENROUTER_API_KEY="):
                key = "configurada" if line.split("=", 1)[1].strip() else "vacia"
                break
    return HealthResponse(
        status="ok",
        openrouter=key or "no configurada",
        tenant=user.get("sub") if user else None,
    )


@app.get("/dashboard/{full_path:path}")
async def serve_dashboard(full_path: str):
    if not DASHBOARD_DIR.exists():
        return ErrorResponse(error="dashboard_no_disponible", detail="Dashboard no construido")
    file_path = DASHBOARD_DIR / full_path
    if file_path.exists() and file_path.is_file():
        return FileResponse(str(file_path))
    index_html = DASHBOARD_DIR / "index.html"
    if index_html.exists():
        return FileResponse(str(index_html))
    return ErrorResponse(error="dashboard_no_encontrado", detail="index.html no encontrado")


@app.post("/api/v1/chat", response_model=ChatResponse | ErrorResponse)
async def chat(
    req: ChatRequest,
    x_tenant_id: str = Header(..., alias="X-Tenant-ID"),
    user: Optional[dict] = Depends(get_optional_user),
):
    if not req.message.strip():
        return ErrorResponse(error="mensaje_vacio", detail="El mensaje no puede estar vacio")

    pack_name, business_name, actual_pack = _tenant_to_pack(x_tenant_id)
    if not pack_name:
        return ErrorResponse(error="tenant_no_encontrado", detail=f"Tenant {x_tenant_id} no encontrado")

    pack = load_pack(actual_pack or pack_name)
    if not pack:
        return ErrorResponse(error="pack_no_encontrado", detail=f"Pack {actual_pack or pack_name} no encontrado")

    agents = pack.get("agents", [])
    if not agents:
        return ErrorResponse(error="sin_agentes", detail="El pack no tiene agentes")

    agent_name = agents[0] if isinstance(agents[0], str) else list(agents[0].keys())[0]
    agent = load_agent(actual_pack or pack_name, agent_name)
    if not agent:
        return ErrorResponse(error="agente_no_encontrado", detail=f"Agente {agent_name} no encontrado")

    messages = build_prompt(agent, pack, business_name or pack_name, req.message)
    result = await chat_with_openrouter(
        messages,
        tenant_id=x_tenant_id,
        session_id=req.session_id,
        user_id=user.get("sub") if user else None,
    )

    if "error" in result:
        return ErrorResponse(error="openrouter_error", detail=result["error"])

    return ChatResponse(
        response=result["response"],
        agent=agent_name,
        model=result.get("model", "openrouter/free"),
        tenant=x_tenant_id,
    )


@app.get("/api/v1/chat/history", response_model=ChatHistoryResponse | ErrorResponse)
async def chat_history(
    session_id: str = Query(...),
    user: Optional[dict] = Depends(get_optional_user),
):
    if not session_id:
        return ErrorResponse(error="session_requerida", detail="session_id es requerido")
    data = await get_chat_history(session_id)
    if data is None:
        return ErrorResponse(error="error_bd", detail="Error al consultar historial")
    messages = [
        ChatHistoryMessage(
            id=str(i),
            role=m.get("role", "user"),
            content=m.get("content", ""),
            created_at=m.get("created_at", ""),
            session_id=m.get("session_id"),
            tenant_id=m.get("tenant_id"),
        )
        for i, m in enumerate(data)
    ]
    return ChatHistoryResponse(messages=messages)


@app.get("/rest/v1/joyeria_productos", response_model=list[ProductResponse] | ErrorResponse)
async def products(
    search: str = Query(None),
    categoria: str = Query(None),
    limit: int = Query(100),
    user: Optional[dict] = Depends(get_optional_user),
):
    data = await get_products(search=search, categoria=categoria, limit=limit)
    if data is None:
        return []
    products_list = []
    for item in data:
        products_list.append(
            ProductResponse(
                id=item.get("id", ""),
                codigo=item.get("codigo", ""),
                nombre=item.get("nombre", ""),
                categoria=item.get("categoria", ""),
                material=item.get("material", ""),
                peso_gramos=float(item.get("peso_gramos", 0)),
                precio=float(item.get("precio", 0)),
                stock=int(item.get("stock", 0)),
                descripcion=item.get("descripcion"),
                imagen_url=item.get("imagen_url"),
            )
        )
    return products_list


@app.get("/api/v1/metrics", response_model=MetricsResponse | ErrorResponse)
async def metrics(user: Optional[dict] = Depends(get_optional_user)):
    data = await get_metrics()
    if data is None:
        return ErrorResponse(error="error_metrics", detail="No se pudieron obtener metricas")
    return MetricsResponse(**data)


@app.get("/api/v1/whatsapp/status", response_model=WhatsAppStatusResponse)
async def whatsapp_status(user: Optional[dict] = Depends(get_optional_user)):
    return WhatsAppStatusResponse(
        connected=False,
        status="disconnected",
        messages_today=0,
        messages_this_week=0,
        qr_code=None,
    )


@app.post("/api/v1/whatsapp/restart", response_model=WhatsAppRestartResponse)
async def whatsapp_restart(user: Optional[dict] = Depends(get_optional_user)):
    return WhatsAppRestartResponse(
        success=True,
        message="Comando de reinicio enviado. El bot se reconectara en segundos.",
    )

LANDING_DIR = SDC_DIR / "apps" / "landing"


@app.get("/")
@app.get("/architecture.html")
async def serve_architecture():
    arch_html = LANDING_DIR / "architecture.html"
    if arch_html.exists():
        return FileResponse(str(arch_html))
    return ErrorResponse(error="not_found", detail="Diagrama no encontrado")


async def serve_landing():
    index_html = LANDING_DIR / "index.html"
    if index_html.exists():
        return FileResponse(str(index_html))
    return {"status": "SDC Pack Gateway", "docs": "/docs"}


# ─── Public API ───────────────────────────────────────────────

@app.get("/api/public/packs", response_model=PublicPacksResponse | ErrorResponse)
async def public_packs():
    data = await get_public_packs()
    if data is None:
        return ErrorResponse(error="error_db", detail="Error al cargar catalogo")
    return data


@app.post("/api/public/leads")
async def public_lead(lead: LeadCreate):
    if not lead.name or not lead.email:
        return ErrorResponse(error="campos_requeridos", detail="Nombre y email son requeridos")
    result = await submit_lead(lead.model_dump())
    if result is None:
        return ErrorResponse(error="error_guardar", detail="Error al guardar el lead")
    return {"success": True, "message": "Lead recibido correctamente"}


@app.get("/api/admin/leads")
async def admin_leads(
    status: str = Query(None),
    limit: int = Query(100),
    offset: int = Query(0),
    user: dict = Depends(get_current_user),
):
    data = await get_leads(limit=limit, offset=offset, status=status)
    if data is None:
        return []
    return data


@app.put("/api/admin/leads/{lead_id}/status")
async def admin_update_lead_status(
    lead_id: str,
    status: str = Query(...),
    user: dict = Depends(get_current_user),
):
    valid = ["nuevo", "contactado", "negociacion", "cerrado", "descartado"]
    if status not in valid:
        return ErrorResponse(error="status_invalido", detail="Status invalido")
    result = await update_lead_status(lead_id, status)
    if result is None:
        return ErrorResponse(error="error_actualizar", detail="Error al actualizar lead")
    return {"success": True, "status": status}
