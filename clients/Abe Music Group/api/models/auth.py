from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    token: str
    user: dict

class UserOut(BaseModel):
    email: str
    name: str
    role: str

class UserCreate(BaseModel):
    email: str
    password: str
    name: str = ""
    role: str = "user"
