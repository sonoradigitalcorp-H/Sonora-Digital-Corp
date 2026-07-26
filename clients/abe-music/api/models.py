from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class Role(str, Enum):
    CEO = "ceo"
    DIRECTOR = "director"
    ARTISTA = "artista"
    FAN = "fan"


class TokenPayload(BaseModel):
    sub: str
    role: Role
    tenant: str = "abe-fenix"


class Message(BaseModel):
    role: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)


class ChatRequest(BaseModel):
    text: str
    session_id: str | None = None
    context: dict[str, Any] = {}


class ChatResponse(BaseModel):
    text: str
    session_id: str
    tts_path: str | None = None
    visemes: list[dict] | None = None


class AudioChunk(BaseModel):
    audio: str
    sample_rate: int = 16000
    session_id: str | None = None
    final: bool = False


class ContractType(str, Enum):
    EXCLUSIVE = "exclusive"
    NON_EXCLUSIVE = "non_exclusive"
    MANAGEMENT = "management"
    PRODUCTION = "production"
    LICENSING = "licensing"
    JOINT_VENTURE = "joint_venture"
    DISTRIBUTION_ONLY = "distribution_only"


class RevenueSplit(BaseModel):
    artist: float
    label: float
    distributor: float
    manager: float = 0.0
    producer: float = 0.0


class Contract(BaseModel):
    id: str
    artist_id: str
    type: ContractType
    start_date: str
    end_date: str | None = None
    revenue_splits: dict[str, RevenueSplit]
    territories: list[str] = ["worldwide"]
    platforms: list[str] = ["all"]
    status: str = "draft"
    created_at: str = ""


class RevenueEntry(BaseModel):
    id: str
    contract_id: str
    artist_id: str
    release_id: str
    amount: float
    source: str
    split: RevenueSplit
    artist_share: float
    label_share: float
    distributor_share: float
    timestamp: str


class ArtistProfile(BaseModel):
    id: str
    name: str
    genre: str
    country: str
    status: str
    streams: int = 0
    revenue: float = 0.0
    email: str = ""
    phone: str = ""
    social: dict[str, str] = {}
    monthly_listeners: int = 0
    spotify_url: str = ""
    releases_count: int = 0
    contracts_count: int = 0


class CEODashboard(BaseModel):
    total_artists: int
    active_artists: int
    total_streams: int
    total_revenue: float
    total_releases: int
    total_contracts: int
    monthly_revenue: list[dict] = []
    top_artists: list[dict] = []
    revenue_by_source: dict[str, float] = {}
    pending_contracts: int = 0
    upcoming_releases: int = 0
    generated_at: str = ""
