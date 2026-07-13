"""Supabase MCP Server — Auth, Storage via MCP.

Connects to Supabase Cloud (sonoradigitalcorp project).
Requires SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_KEY in env.
"""

import json
import os
from typing import Optional

import httpx

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://jibalggzudkflwzdndqz.supabase.co")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")


async def _supabase_get(path: str, token: str = "", use_service: bool = False) -> dict:
    headers = {"apikey": SUPABASE_ANON_KEY}
    if use_service:
        headers["apikey"] = SUPABASE_SERVICE_KEY
        headers["Authorization"] = f"Bearer {SUPABASE_SERVICE_KEY}"
    elif token:
        headers["Authorization"] = f"Bearer {token}"
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{SUPABASE_URL}{path}", headers=headers, timeout=15)
        return resp.json()


async def _supabase_post(path: str, data: dict, token: str = "", use_service: bool = False) -> dict:
    headers = {"apikey": SUPABASE_ANON_KEY, "Content-Type": "application/json"}
    if use_service:
        headers["apikey"] = SUPABASE_SERVICE_KEY
        headers["Authorization"] = f"Bearer {SUPABASE_SERVICE_KEY}"
    elif token:
        headers["Authorization"] = f"Bearer {token}"
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{SUPABASE_URL}{path}", json=data, headers=headers, timeout=15)
        return resp.json()


async def _supabase_delete(path: str, use_service: bool = True) -> dict:
    headers = {"apikey": SUPABASE_SERVICE_KEY, "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}"}
    async with httpx.AsyncClient() as client:
        resp = await client.delete(f"{SUPABASE_URL}{path}", headers=headers, timeout=15)
        return resp.json()


# ─── Auth Tools ───

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
    result = await _supabase_get("/auth/v1/admin/users", use_service=True)
    return json.dumps(result)


# ─── Storage Tools ───

async def supabase_list_buckets() -> str:
    result = await _supabase_get("/storage/v1/bucket", use_service=True)
    return json.dumps(result)


async def supabase_create_bucket(name: str, public: bool = False) -> str:
    result = await _supabase_post("/storage/v1/bucket", {"name": name, "public": public}, use_service=True)
    return json.dumps(result)


async def supabase_list_files(bucket: str, folder: str = "", token: str = "") -> str:
    path = "/storage/v1/object/list/" + bucket
    body = {"prefix": folder}
    if token:
        body["search"] = token
    result = await _supabase_post(path, body, use_service=True)
    return json.dumps(result)


async def supabase_upload_file(bucket: str, path: str, content_b64: str, content_type: str = "application/octet-stream") -> str:
    """Upload a file to Supabase Storage. content_b64 is base64-encoded content."""
    import base64
    headers = {
        "apikey": SUPABASE_SERVICE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "Content-Type": content_type,
    }
    raw = base64.b64decode(content_b64)
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{SUPABASE_URL}/storage/v1/object/{bucket}/{path}",
            content=raw,
            headers=headers,
            timeout=30,
        )
        return json.dumps({"status": resp.status_code, "body": resp.text})


async def supabase_delete_file(bucket: str, path: str) -> str:
    result = await _supabase_delete(f"/storage/v1/object/{bucket}/{path}")
    return json.dumps(result)


async def supabase_get_public_url(bucket: str, path: str) -> str:
    return json.dumps({"url": f"{SUPABASE_URL}/storage/v1/object/public/{bucket}/{path}"})


MCP_TOOLS = {
    # ── Auth ──
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
    # ── Storage ──
    "supabase_list_buckets": {
        "description": "List all storage buckets",
        "input_schema": {"type": "object", "properties": {}},
        "handler": lambda _: supabase_list_buckets(),
    },
    "supabase_create_bucket": {
        "description": "Create a new storage bucket",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Bucket name"},
                "public": {"type": "boolean", "description": "Make bucket public"},
            },
            "required": ["name"],
        },
        "handler": lambda args: supabase_create_bucket(args["name"], args.get("public", False)),
    },
    "supabase_list_files": {
        "description": "List files in a storage bucket/folder",
        "input_schema": {
            "type": "object",
            "properties": {
                "bucket": {"type": "string", "description": "Bucket name"},
                "folder": {"type": "string", "description": "Optional folder prefix"},
            },
            "required": ["bucket"],
        },
        "handler": lambda args: supabase_list_files(args["bucket"], args.get("folder", "")),
    },
    "supabase_upload_file": {
        "description": "Upload a file to Supabase Storage (base64 content)",
        "input_schema": {
            "type": "object",
            "properties": {
                "bucket": {"type": "string", "description": "Bucket name"},
                "path": {"type": "string", "description": "Storage path (e.g. images/photo.jpg)"},
                "content_b64": {"type": "string", "description": "Base64-encoded file content"},
                "content_type": {"type": "string", "description": "MIME type"},
            },
            "required": ["bucket", "path", "content_b64"],
        },
        "handler": lambda args: supabase_upload_file(
            args["bucket"], args["path"], args["content_b64"], args.get("content_type", "application/octet-stream")
        ),
    },
    "supabase_delete_file": {
        "description": "Delete a file from Supabase Storage",
        "input_schema": {
            "type": "object",
            "properties": {
                "bucket": {"type": "string", "description": "Bucket name"},
                "path": {"type": "string", "description": "Storage path to delete"},
            },
            "required": ["bucket", "path"],
        },
        "handler": lambda args: supabase_delete_file(args["bucket"], args["path"]),
    },
    "supabase_get_public_url": {
        "description": "Get public URL for a file in a public bucket",
        "input_schema": {
            "type": "object",
            "properties": {
                "bucket": {"type": "string", "description": "Bucket name"},
                "path": {"type": "string", "description": "File path"},
            },
            "required": ["bucket", "path"],
        },
        "handler": lambda args: supabase_get_public_url(args["bucket"], args["path"]),
    },
}
