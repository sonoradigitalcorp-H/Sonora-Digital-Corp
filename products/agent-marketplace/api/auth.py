"""OAuth 2.0 + JWT Authentication for Agent Marketplace"""

import os
import jwt
import httpx
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["auth"])

# ─── Config ───
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "change-me-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

# Google OAuth
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REDIRECT_URI = os.environ.get("GOOGLE_REDIRECT_URI", "http://localhost:8701/auth/google/callback")


class UserSession(BaseModel):
    email: str
    name: str
    phone: str = ""
    tenant_id: str = ""
    picture: str = ""
    provider: str = "google"


def create_jwt(user: UserSession) -> str:
    payload = {
        "sub": user.email,
        "name": user.name,
        "phone": user.phone,
        "tenant_id": user.tenant_id,
        "exp": datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_jwt(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Token inválido")


# ─── Google OAuth Flow ───
@router.get("/google/login")
async def google_login():
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
    }
    url = "https://accounts.google.com/o/oauth2/v2/auth?" + "&".join(f"{k}={v}" for k, v in params.items())
    return RedirectResponse(url)


@router.get("/google/callback")
async def google_callback(code: str, request: Request):
    # Exchange code for tokens
    async with httpx.AsyncClient() as client:
        token_resp = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uri": GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            },
        )
        tokens = token_resp.json()
        id_token = tokens.get("id_token")

        # Get user info
        user_resp = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )
        user_data = user_resp.json()

    # Create session
    user = UserSession(
        email=user_data["email"],
        name=user_data.get("name", ""),
        picture=user_data.get("picture", ""),
        provider="google",
    )

    # Generate JWT
    token = create_jwt(user)

    # Redirect to dashboard with token
    frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:8701")
    return RedirectResponse(f"{frontend_url}/dashboard.html?token={token}")


# ─── Phone + Email registration (self-provisioning) ───
class RegisterRequest(BaseModel):
    email: str
    phone: str


@router.post("/register")
async def register(data: RegisterRequest):
    """Register with just email + phone. System auto-discovers your business."""
    domain = data.email.split("@")[1]

    # Auto-discover business data from public APIs
    business_name = domain.split(".")[0].capitalize()
    niche = "Tecnología"

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            whois = await client.get(f"https://domainwhois.com/{domain}")
            if whois.status_code == 200:
                business_name = whois.json().get("org", business_name)
    except Exception:
        pass

    user = UserSession(
        email=data.email,
        name=business_name,
        phone=data.phone,
        tenant_id=data.email.split("@")[0][:8],
    )

    token = create_jwt(user)
    return {
        "status": "registered",
        "token": token,
        "business_name": business_name,
        "niche": niche,
        "next_step": "choose_package",
    }
