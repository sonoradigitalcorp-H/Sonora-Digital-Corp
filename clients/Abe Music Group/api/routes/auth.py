from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from models import LoginRequest, UserCreate
from services.auth import AuthService
from database import query_db

router = APIRouter(prefix="/api", tags=["auth"])
security = HTTPBearer()

def verify_token(cred: HTTPAuthorizationCredentials = Depends(security)):
    try:
        return AuthService.decode_token(cred.credentials)
    except Exception:
        raise HTTPException(status_code=401, detail="Token invalido")

def admin_required(payload: dict = Depends(verify_token)):
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin required")
    return payload

@router.post("/auth/login")
def login(req: LoginRequest):
    user = AuthService.find_user(req.email)
    if not user:
        raise HTTPException(status_code=401, detail="Credenciales invalidas")
    stored_hash = user["password_hash"]
    if not AuthService.verify_password(req.password, stored_hash):
        raise HTTPException(status_code=401, detail="Credenciales invalidas")
    token = AuthService.create_token(user["email"], user["role"], user["name"])
    return {
        "token": token,
        "user": {"email": user["email"], "name": user["name"], "role": user["role"]}
    }

@router.post("/auth/register")
def register(req: UserCreate):
    existing = AuthService.find_user(req.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email ya registrado")
    user = AuthService.create_user(req.name or req.email, req.email, req.password, req.role)
    token = AuthService.create_token(user["email"], user["role"], user["name"])
    return {
        "token": token,
        "user": {"email": user["email"], "name": user["name"], "role": user["role"]}
    }

@router.get("/api/me")
def get_me(payload: dict = Depends(verify_token)):
    return {"email": payload["email"], "role": payload["role"], "name": payload["name"]}

@router.get("/me")
def get_me_alt(payload: dict = Depends(verify_token)):
    return {"email": payload["email"], "role": payload["role"], "name": payload["name"]}
