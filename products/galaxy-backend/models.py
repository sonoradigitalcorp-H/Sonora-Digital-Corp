"""Pydantic data models for Agent Galaxy backend.

Defines all data structures for agents, tenants, voice config,
onboarding sessions, and LLM interactions.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ─── Galaxy Agent ──────────────────────────────────────────────


class AgentCard(BaseModel):
    """Capability card displayed in the 3D galaxy UI."""

    title: str
    description: str
    icon: str = "star"
    action: str = ""


class GalaxyAgent(BaseModel):
    """A planet agent in the galaxy visualization.

    Each agent represents a capability sphere: sales, support, content, etc.
    Position (x, y, z) determines orbit placement in the 3D scene.
    """

    name: str = Field(..., description="Planet name: mercurio, venus, tauro, marte, jupiter, saturno, urano, neptuno, pluton")
    color: str = Field(..., description="Hex color for the planet sphere")
    position: tuple[float, float, float] = Field(..., description="3D position (x, y, z)")
    capabilities: list[str] = Field(default_factory=list, description="List of capability names")
    cards: list[AgentCard] = Field(default_factory=list, description="UI capability cards")
    orbit_radius: float = Field(..., description="Distance from galactic center")
    orbit_speed: float = Field(1.0, description="Relative orbit speed multiplier")
    description: str = Field("", description="Short description in Spanish")
    plan_required: str = Field("explorador", description="Minimum plan to access: explorador, conquistador, imperio")


# ─── Voice Configuration ──────────────────────────────────────


class VoiceConfig(BaseModel):
    """Voice pipeline configuration per tenant."""

    stt_provider: str = Field("deepseek_v4_flash", description="Speech-to-text provider")
    tts_provider: str = Field("deepseek_v4_flash", description="Text-to-speech provider")
    channels: list[str] = Field(default_factory=lambda: ["whatsapp"], description="Active voice channels")
    language: str = Field("es", description="Primary language code")


# ─── Tenant ────────────────────────────────────────────────────


class Tenant(BaseModel):
    """Multi-tenant customer record.

    Each tenant has an isolated configuration, assigned agents,
    and channel preferences.
    """

    id: str = Field(..., description="UUID tenant identifier")
    phone: str = Field(..., description="WhatsApp phone number")
    plan: str = Field("explorador", description="Plan: explorador, conquistador, imperio")
    agents: list[str] = Field(default_factory=list, description="Assigned agent names")
    voice_config: VoiceConfig = Field(default_factory=VoiceConfig)
    channels: list[str] = Field(default_factory=lambda: ["whatsapp"], description="Active communication channels")
    status: str = Field("active", description="Tenant status: active, trial, suspended")
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    name: str = Field("", description="Display name")


# ─── Onboarding ────────────────────────────────────────────────


class OnboardingStartResponse(BaseModel):
    """Response when starting an onboarding session."""

    session_id: str
    qr_data: str = Field(..., description="QR code payload for WhatsApp connection")
    expires_at: str = Field(..., description="Session expiration timestamp")
    status: str = "pending"


class OnboardingCompleteRequest(BaseModel):
    """Request to complete onboarding with phone number."""

    phone: str
    name: str = Field("", description="Customer display name")
    plan: str = Field("explorador", description="Selected plan")


class OnboardingCompleteResponse(BaseModel):
    """Response after successful onboarding completion."""

    tenant_id: str
    status: str = "active"
    agents: list[str] = Field(default_factory=list, description="Assigned agents")
    message: str = ""


# ─── LLM ───────────────────────────────────────────────────────


class ChatMessage(BaseModel):
    """A single message in a conversation."""

    role: str = Field(..., description="Message role: system, user, assistant")
    content: str = Field(..., description="Message text content")


class ChatRequest(BaseModel):
    """Request body for LLM chat endpoint."""

    messages: list[ChatMessage] = Field(..., description="Conversation history")
    tenant_id: str = Field("", description="Optional tenant for tracking")
    temperature: float = Field(0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(1024, ge=1, le=4096)
    model: str = Field("", description="Override model (empty = primary)")


class ChatResponse(BaseModel):
    """Response from LLM chat endpoint."""

    text: str
    model: str
    provider: str
    usage: dict = Field(default_factory=dict)
    cost: float = 0.0
    elapsed: float = 0.0


class TaskRequest(BaseModel):
    """Request to assign a task to the LLM via OpenClaw."""

    task: str = Field(..., description="Task description")
    tenant_id: str = Field("", description="Tenant identifier")
    context: dict = Field(default_factory=dict, description="Additional context")


class TaskResponse(BaseModel):
    """Response after LLM task execution."""

    result: str
    task_id: str = ""
    status: str = "completed"
    elapsed: float = 0.0


# ─── Events ────────────────────────────────────────────────────


class GalaxyEvent(BaseModel):
    """An event in the galaxy system event log."""

    event_type: str = Field(..., description="Event type identifier")
    tenant_id: str = Field("", description="Tenant that triggered the event")
    data: dict = Field(default_factory=dict, description="Event payload")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


# ─── Health ────────────────────────────────────────────────────


class HealthCheck(BaseModel):
    """Health check response with dependency status."""

    status: str = "healthy"
    version: str = "0.1.0-preview"
    services: dict = Field(default_factory=dict, description="Dependency health status")
    uptime_seconds: float = 0.0
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
