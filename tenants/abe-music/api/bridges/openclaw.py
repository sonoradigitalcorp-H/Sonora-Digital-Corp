import logging
from typing import Any

import httpx

log = logging.getLogger("abe.bridge.openclaw")

OC_BASE = "http://127.0.0.1:18789"


async def health() -> dict:
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            r = await client.get(f"{OC_BASE}/health")
            if r.status_code == 200:
                return r.json()
            return {"status": "error", "code": r.status_code}
    except Exception as e:
        return {"status": "unavailable", "error": str(e)}


async def list_skills() -> list[dict]:
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            r = await client.get(f"{OC_BASE}/skills")
            if r.status_code == 200:
                return r.json().get("skills", [])
            return []
    except Exception:
        return []


async def execute_skill(skill: str, params: dict = None) -> dict[str, Any]:
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(
                f"{OC_BASE}/skill/{skill}/execute",
                json=params or {},
            )
            if r.status_code == 200:
                return r.json()
            return {"error": f"skill call failed: {r.status_code}", "detail": r.text}
    except Exception as e:
        return {"error": str(e)}


async def navigate(url: str) -> dict:
    return await execute_skill("browser/navigate", {"url": url})


async def list_agents() -> list[dict]:
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            r = await client.get(f"{OC_BASE}/agents")
            if r.status_code == 200:
                return r.json().get("agents", [])
            return []
    except Exception:
        return []


async def list_tools() -> list[dict]:
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            r = await client.get(f"{OC_BASE}/tools")
            if r.status_code == 200:
                return r.json().get("tools", [])
            return []
    except Exception:
        return []
