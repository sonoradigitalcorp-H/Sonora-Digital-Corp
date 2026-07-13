"""File Upload MCP Server — Upload files to Supabase Storage.

Exposes file upload and retrieval as native MCP tools for agents.
"""

import base64
import json
import os
import uuid

import httpx

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")


async def upload_file(bucket: str, path: str, content_b64: str, content_type: str = "application/octet-stream") -> str:
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        return json.dumps({"error": "Supabase not configured"})
    headers = {
        "apikey": SUPABASE_SERVICE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "Content-Type": content_type,
    }
    try:
        content = base64.b64decode(content_b64)
    except Exception as e:
        return json.dumps({"error": f"Invalid base64 content: {e}"})
    storage_url = f"{SUPABASE_URL}/storage/v1/object/{bucket}/{path}"
    async with httpx.AsyncClient() as client:
        resp = await client.post(storage_url, content=content, headers=headers, timeout=120)
        if resp.status_code in (200, 201):
            return json.dumps({"url": f"{SUPABASE_URL}/storage/v1/object/public/{bucket}/{path}", "path": path, "bucket": bucket})
        return json.dumps({"error": f"Upload failed: {resp.status_code} {resp.text}"})


async def get_file_url(bucket: str, path: str) -> str:
    if not SUPABASE_URL:
        return json.dumps({"error": "Supabase not configured"})
    return json.dumps({"url": f"{SUPABASE_URL}/storage/v1/object/public/{bucket}/{path}", "path": path, "bucket": bucket})


async def list_files(bucket: str, folder: str = "") -> str:
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        return json.dumps({"error": "Supabase not configured"})
    headers = {"apikey": SUPABASE_SERVICE_KEY, "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}"}
    storage_url = f"{SUPABASE_URL}/storage/v1/object/list/{bucket}"
    async with httpx.AsyncClient() as client:
        resp = await client.post(storage_url, json={"prefix": folder, "limit": 100}, headers=headers, timeout=30)
        if resp.status_code == 200:
            return json.dumps(resp.json())
        return json.dumps({"error": f"List failed: {resp.status_code} {resp.text}"})


async def delete_file(bucket: str, path: str) -> str:
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        return json.dumps({"error": "Supabase not configured"})
    headers = {
        "apikey": SUPABASE_SERVICE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "Content-Type": "application/json",
    }
    storage_url = f"{SUPABASE_URL}/storage/v1/object/{bucket}/{path}"
    async with httpx.AsyncClient() as client:
        resp = await client.delete(storage_url, headers=headers, timeout=30)
        if resp.status_code in (200, 204):
            return json.dumps({"deleted": True, "path": path})
        return json.dumps({"error": f"Delete failed: {resp.status_code} {resp.text}"})


MCP_TOOLS = {
    "upload_file": {
        "description": "Upload a file to Supabase Storage (base64 encoded content)",
        "input_schema": {
            "type": "object",
            "properties": {
                "bucket": {"type": "string", "description": "Storage bucket name (e.g. sdc-assets)"},
                "path": {"type": "string", "description": "File path in bucket (e.g. abe-music/fotos/photo.jpg)"},
                "content_b64": {"type": "string", "description": "Base64-encoded file content"},
                "content_type": {"type": "string", "description": "MIME type (e.g. image/jpeg, image/png, application/pdf)"},
            },
            "required": ["bucket", "path", "content_b64"],
        },
        "handler": lambda args: upload_file(
            args["bucket"], args["path"], args["content_b64"], args.get("content_type", "application/octet-stream"),
        ),
    },
    "get_file_url": {
        "description": "Get public URL for a file in Supabase Storage",
        "input_schema": {
            "type": "object",
            "properties": {
                "bucket": {"type": "string", "description": "Storage bucket name"},
                "path": {"type": "string", "description": "File path in bucket"},
            },
            "required": ["bucket", "path"],
        },
        "handler": lambda args: get_file_url(args["bucket"], args["path"]),
    },
    "list_files": {
        "description": "List files in a Supabase Storage bucket/folder",
        "input_schema": {
            "type": "object",
            "properties": {
                "bucket": {"type": "string", "description": "Storage bucket name"},
                "folder": {"type": "string", "description": "Folder prefix (optional)"},
            },
            "required": ["bucket"],
        },
        "handler": lambda args: list_files(args["bucket"], args.get("folder", "")),
    },
    "delete_file": {
        "description": "Delete a file from Supabase Storage",
        "input_schema": {
            "type": "object",
            "properties": {
                "bucket": {"type": "string", "description": "Storage bucket name"},
                "path": {"type": "string", "description": "File path in bucket"},
            },
            "required": ["bucket", "path"],
        },
        "handler": lambda args: delete_file(args["bucket"], args["path"]),
    },
}
