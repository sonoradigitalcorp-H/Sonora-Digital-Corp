from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid


class OrderCreate(BaseModel):
    client_name: str = Field(..., min_length=1, max_length=100)
    client_phone: str = Field(..., pattern=r"^\+?\d{7,15}$")
    script: str = Field(..., min_length=1, max_length=1000)
    style: str = "realistic"
    duration_seconds: int = Field(default=30, ge=15, le=60)
    source: str = "api"
    product_type: str = "avatar_mensual"
    reference_audio_url: Optional[str] = None


class OrderResponse(BaseModel):
    order_id: str
    status: str
    client_name: str
    client_phone: str
    product_type: str
    created_at: str
    video_url: Optional[str] = None
    estimated_cost_usd: float = 0.0
    timeline: list = []


class Order:
    def __init__(self, data: OrderCreate):
        self.id = f"ord_{uuid.uuid4().hex[:8]}"
        self.client_name = data.client_name
        self.client_phone = data.client_phone
        self.script = data.script
        self.style = data.style
        self.duration = data.duration_seconds
        self.source = data.source
        self.product_type = data.product_type
        self.reference_audio_url = data.reference_audio_url
        self.status = "created"
        self.created_at = datetime.utcnow().isoformat()
        self.photo_url = None
        self.audio_url = None
        self.video_url = None
        self.face_model_id = None
        self.total_cost = 0.0
        self.approved_by = None
        self.rejection_reason = None
        self.timeline = [{"event": "created", "at": self.created_at}]

    def to_dict(self):
        return {
            "id": self.id,
            "client_name": self.client_name,
            "client_phone": self.client_phone,
            "script": self.script,
            "style": self.style,
            "duration": self.duration,
            "source": self.source,
            "product_type": self.product_type,
            "status": self.status,
            "created_at": self.created_at,
            "photo_url": self.photo_url,
            "audio_url": self.audio_url,
            "video_url": self.video_url,
            "total_cost": self.total_cost,
            "timeline": self.timeline,
        }


class Client:
    def __init__(self, phone: str, name: str):
        self.phone = phone
        self.name = name
        self.photo_url = None
        self.voice_ref_url = None
        self.lora_id = None
        self.total_orders = 0
        self.created_at = datetime.utcnow().isoformat()
        self.last_order_at = None

    def to_dict(self):
        return {
            "phone": self.phone,
            "name": self.name,
            "photo_url": self.photo_url,
            "voice_ref_url": self.voice_ref_url,
            "lora_id": self.lora_id,
            "total_orders": self.total_orders,
            "created_at": self.created_at,
            "last_order_at": self.last_order_at,
        }
