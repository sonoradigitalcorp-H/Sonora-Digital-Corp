"""Supabase MCP Server — Auth, Storage, Database operations via MCP [FR1].

Exposes Supabase Auth and Storage as native MCP tools for agents.
"""

import json
import os

import httpx

SUPABASE_URL = os.getenv("SUPABASE_URL", "http://localhost:54321")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")


async def _supabase_get(path: str, token: str = "") -> dict:
    headers = {"apikey": SUPABASE_ANON_KEY}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{SUPABASE_URL}{path}", headers=headers, timeout=10)
        return resp.json()


async def _supabase_post(path: str, data: dict, token: str = "") -> dict:
    headers = {"apikey": SUPABASE_ANON_KEY, "Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{SUPABASE_URL}{path}", json=data, headers=headers, timeout=10)
        return resp.json()


async def supabase_signup(email: str, password: str, name: str = "") -> str:
    data = {"email": email, "password": password}
    if name:
        data["data"] = {"full_name": name}
    result = await _supabase_post("/auth/v1/signup", data)
    return json.dumps(result)


async def supabase_login(email: str, password: str) -> str:
    result = await _supabase_post("/auth/v1/token?grant_type=password", {"email": email, "password": password})
    return json.dumps(result)


async def supabase_get_user(token: str) -> str:
    result = await _supabase_get("/auth/v1/user", token=token)
    return json.dumps(result)


async def supabase_list_users() -> str:
    headers = {"apikey": SUPABASE_SERVICE_KEY, "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}"}
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{SUPABASE_URL}/auth/v1/admin/users", headers=headers, timeout=10)
        return json.dumps(resp.json())


MCP_TOOLS = {
    "supabase_signup": {
        "description": "Register a new user with email and password",
        "input_schema": {
            "type": "object",
            "properties": {
                "email": {"type": "string", "description": "User email"},
                "password": {"type": "string", "description": "User password"},
                "name": {"type": "string", "description": "User display name"},
            },
            "required": ["email", "password"],
        },
        "handler": lambda args: supabase_signup(args["email"], args["password"], args.get("name", "")),
    },
    "supabase_login": {
        "description": "Sign in with email and password",
        "input_schema": {
            "type": "object",
            "properties": {
                "email": {"type": "string", "description": "User email"},
                "password": {"type": "string", "description": "User password"},
            },
            "required": ["email", "password"],
        },
        "handler": lambda args: supabase_login(args["email"], args["password"]),
    },
    "supabase_get_user": {
        "description": "Get user info by access token",
        "input_schema": {
            "type": "object",
            "properties": {
                "token": {"type": "string", "description": "Supabase access token"},
            },
            "required": ["token"],
        },
        "handler": lambda args: supabase_get_user(args["token"]),
    },
    "supabase_list_users": {
        "description": "List all users (admin only)",
        "input_schema": {"type": "object", "properties": {}},
        "handler": lambda _: supabase_list_users(),
    },
}
