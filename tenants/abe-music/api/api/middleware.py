import logging
from datetime import datetime, timezone

import jwt
from fastapi import HTTPException, Request

from ..config import config
from ..models import Role, TokenPayload

log = logging.getLogger("abe.auth")


def create_token(payload: dict) -> str:
    payload["iat"] = datetime.now(timezone.utc)
    payload["exp"] = datetime.now(timezone.utc).timestamp() + 3600
    return jwt.encode(payload, config.jwt_secret, algorithm="HS256")


def verify_token(token: str) -> TokenPayload | None:
    try:
        decoded = jwt.decode(token, config.jwt_secret, algorithms=["HS256"])
        return TokenPayload(**decoded)
    except Exception as e:
        log.warning(f"JWT verify error: {e}")
        return None


def require_role(required: Role):
    async def dependency(request: Request):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing token")
        payload = verify_token(auth[7:])
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid token")

        role_hierarchy = {
            Role.CEO: 4,
            Role.DIRECTOR: 3,
            Role.ARTISTA: 2,
            Role.FAN: 1,
        }
        if role_hierarchy.get(payload.role, 0) < role_hierarchy.get(required, 0):
            raise HTTPException(status_code=403, detail="Insufficient role")

        request.state.user = payload
        return payload

    return dependency
