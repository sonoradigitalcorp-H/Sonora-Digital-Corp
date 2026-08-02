"""Pydantic models for Cross-Canal Identity Resolution."""

from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, EmailStr
from enum import Enum


class Platform(str, Enum):
    WHATSAPP = "whatsapp"
    TELEGRAM = "telegram"
    WEB = "web"


class LeadType(str, Enum):
    COLD = "cold"
    WARM = "warm"
    HOT = "hot"


class IdentityCreate(BaseModel):
    platform: Platform
    platform_id: str
    display_name: Optional[str] = None
    phone_e164: Optional[str] = None
    email: Optional[EmailStr] = None
    locale: str = "es"
    metadata: Dict[str, Any] = Field(default_factory=dict)


class IdentityMerge(BaseModel):
    primary_id: UUID
    secondary_id: UUID
    reason: str  # "phone_match" | "email_match" | "manual"


class InternalUser(BaseModel):
    internal_id: UUID = Field(default_factory=uuid4)
    platform: Platform
    platform_id: str
    display_name: Optional[str] = None
    phone_e164: Optional[str] = None
    email: Optional[EmailStr] = None
    locale: str = "es"
    metadata: Dict[str, Any] = Field(default_factory=dict)
    merged_into: Optional[UUID] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Enriched fields from conversations
    lead_type: Optional[LeadType] = None
    lead_confidence: float = 0.0
    business_name: Optional[str] = None
    business_type: Optional[str] = None
    pain_points: List[str] = Field(default_factory=list)
    budget_range: Optional[str] = None
    timeline: Optional[str] = None
    preferred_contact: Optional[str] = None
    conversation_count: int = 0
    last_interaction: Optional[datetime] = None

    class Config:
        use_enum_values = True


class IdentityResolutionResult(BaseModel):
    user: InternalUser
    is_new: bool
    merged: bool
    merged_from: Optional[UUID] = None


# Database row model (matches Postgres schema)
class IdentityRow(BaseModel):
    internal_id: UUID
    platform: str
    platform_id: str
    display_name: Optional[str]
    phone_e164: Optional[str]
    email: Optional[str]
    locale: str
    metadata: Dict[str, Any]
    merged_into: Optional[UUID]
    created_at: datetime
    updated_at: datetime