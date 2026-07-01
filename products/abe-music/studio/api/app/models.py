from pydantic import BaseModel
from typing import Optional

class GenerateRequest(BaseModel):
    model: str = "seedance-2-0"
    callback_url: Optional[str] = None
    input: dict

class GenerateResponse(BaseModel):
    taskId: str
    credits: int

class TaskResponse(BaseModel):
    id: str
    status: str
    created_at: int
    model: str
    billing_status: str
    credits: int
    failed_reason: Optional[str] = None
    data: Optional[dict] = None

class ArtistCharacter(BaseModel):
    artist_id: str
    name: str
    image_urls: list[str]
    genre: Optional[str] = None

class WebhookPayload(BaseModel):
    id: str
    status: str
    created_at: Optional[int] = None
    model: Optional[str] = None
    data: Optional[dict] = None
