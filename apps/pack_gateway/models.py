from pydantic import BaseModel
from typing import Any


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


class ChatResponse(BaseModel):
    response: str
    agent: str
    model: str
    tenant: str


class ChatHistoryMessage(BaseModel):
    id: str | None = None
    tenant_id: str | None = None
    session_id: str | None = None
    role: str
    content: str
    created_at: str | None = None


class ChatHistoryResponse(BaseModel):
    messages: list[ChatHistoryMessage]


class ErrorResponse(BaseModel):
    error: str
    detail: str | None = None


class HealthResponse(BaseModel):
    status: str
    tenant: str | None = None
    openrouter: str | None = None


class ProductResponse(BaseModel):
    id: str
    codigo: str
    nombre: str
    categoria: str
    material: str
    peso_gramos: float
    precio: float
    stock: int
    descripcion: str | None = None
    imagen_url: str | None = None


class MetricsResponse(BaseModel):
    ventas_mes: float
    leads_nuevos: int
    conversion: float
    ticket_promedio: float
    ventas_por_dia: list[dict[str, Any]]
    conversion_por_semana: list[dict[str, Any]]
    actividad_chat: list[dict[str, Any]]


class WhatsAppStatusResponse(BaseModel):
    connected: bool
    status: str
    messages_today: int
    messages_this_week: int
    qr_code: str | None = None


class WhatsAppRestartResponse(BaseModel):
    success: bool
    message: str


class LeadCreate(BaseModel):
    name: str
    email: str
    company: str | None = None
    phone: str | None = None
    message: str | None = None


class LeadResponse(BaseModel):
    id: str
    name: str
    email: str
    company: str | None = None
    phone: str | None = None
    message: str | None = None
    status: str
    source: str
    created_at: str


class PublicPacksResponse(BaseModel):
    niches: list[dict]
    packs: list[dict]
