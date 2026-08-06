from pydantic import BaseModel
from typing import Optional

class ServiceCreate(BaseModel):
    title: str
    description: str
    icon: str = "📦"

class ServiceUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None

class ServiceOut(BaseModel):
    id: str
    title: str
    description: str
    icon: str
