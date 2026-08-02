from pydantic import BaseModel
from typing import Optional

class ContactRequest(BaseModel):
    name: str
    email: str
    service: str = ""
    message: str = ""

class ContactOut(BaseModel):
    id: str
    name: str
    email: str
    service: str
    message: str
    created: str
