import os
import jwt
import logging
from pathlib import Path
from fastapi import Header, HTTPException, Depends
from typing import Optional

log = logging.getLogger("pack-gateway.auth")

_JWT_SECRET = None


def _get_jwt_secret() -> str:
    global _JWT_SECRET
    if _JWT_SECRET:
        return _JWT_SECRET
    supabase_env = Path(os.path.expanduser("~/supabase/.env"))
    if supabase_env.exists():
        for line in supabase_env.read_text().splitlines():
            if line.startswith("JWT_SECRET="):
                _JWT_SECRET = line.split("=", 1)[1].strip()
                return _JWT_SECRET
    hermes_env = Path(os.path.expanduser("~/.hermes/.env"))
    if hermes_env.exists():
        for line in hermes_env.read_text().splitlines():
            if line.startswith("SUPABASE_JWT_SECRET="):
                _JWT_SECRET = line.split("=", 1)[1].strip()
                return _JWT_SECRET
    log.error("JWT_SECRET no encontrado en ningun env file")
    return ""


def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Token requerido")

    token = authorization.replace("Bearer ", "")
    secret = _get_jwt_secret()
    if not secret:
        raise HTTPException(status_code=500, detail="JWT_SECRET no configurado")

    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        return {
            "sub": payload.get("sub"),
            "email": payload.get("email", ""),
            "role": payload.get("role", "authenticated"),
            "aud": payload.get("aud", ""),
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Token invalido: {str(e)}")


def get_optional_user(authorization: Optional[str] = Header(None)):
    if not authorization:
        return None
    try:
        return get_current_user(authorization)
    except HTTPException:
        return None
