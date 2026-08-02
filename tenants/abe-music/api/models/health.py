from pydantic import BaseModel
from typing import Dict
from datetime import datetime

class ServiceStatus(BaseModel):
    status: str

class HealthResponse(BaseModel):
    status: str
    services: Dict[str, ServiceStatus]
    timestamp: str
