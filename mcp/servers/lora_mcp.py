"""LoRA MCP Server — Train and manage LoRA models via FAL.ai.

Enables consistent artist appearance across all generated content.
"""

import json
import os

import httpx

FAL_KEY = os.getenv("FAL_KEY", "")
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")
HASURA_URL = os.getenv("HASURA_URL", "http://localhost:8082/v1/graphql")
HASURA_ADMIN_SECRET = os.getenv("HASURA_ADMIN_SECRET", "sonora-admin")


async def train_lora(artist_name: str, photos: list[str], trigger_word: str = "", tenant_id: str = "") -> str:
    if not FAL_KEY:
        return json.dumps({"error": "FAL_KEY not configured"})
    if not photos or len(photos) < 5:
        return json.dumps({"error": "At least 5 photos required"})
    if not artist_name:
        return json.dumps({"error": "artist_name is required"})
    try:
        trigger = trigger_word or artist_name.lower().replace(" ", "_")
        headers = {
            "Authorization": f"Key {FAL_KEY}",
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://fal.run/fal-ai/flux-lora",
                json={
                    "images": photos,
                    "trigger_word": trigger,
                    "name": f"{artist_name}_lora",
                },
                headers=headers,
                timeout=300,
            )
            data = resp.json()
            weight_id = data.get("weight_id") or data.get("id")
            if not weight_id:
                return json.dumps({"error": f"FAL training failed: {data}", "response": data})

            if HASURA_URL and tenant_id:
                query = """
                    mutation ($artist: String!, $weight: String!, $trigger: String!, $photos: Int!, $tenant: String!) {
                        insert_lora_models_one(object: {
                            artist_name: $artist, weight_id: $weight, trigger_word: $trigger,
                            photos_count: $photos, tenant_id: $tenant, status: "active"
                        }) { id }
                    }
                """
                await client.post(
                    HASURA_URL,
                    json={"query": query, "variables": {"artist": artist_name, "weight": weight_id, "trigger": trigger, "photos": len(photos), "tenant": tenant_id}},
                    headers={"x-hasura-admin-secret": HASURA_ADMIN_SECRET, "Content-Type": "application/json"},
                    timeout=10,
                )

            return json.dumps({
                "weight_id": weight_id,
                "artist_name": artist_name,
                "trigger_word": trigger,
                "photos_count": len(photos),
                "status": "trained",
            })
    except Exception as e:
        return json.dumps({"error": str(e)})


async def list_loras(tenant_id: str = "") -> str:
    if HASURA_URL:
        try:
            where = f'{{"tenant_id": {{"_eq": "{tenant_id}"}}}}' if tenant_id else "{}"
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    HASURA_URL,
                    json={"query": f"query {{ lora_models(where: {where}) {{ id artist_name weight_id trigger_word photos_count status created_at }} }}"},
                    headers={"x-hasura-admin-secret": HASURA_ADMIN_SECRET, "Content-Type": "application/json"},
                    timeout=10,
                )
                data = resp.json()
                if "data" in data:
                    return json.dumps({"lora_models": data["data"].get("lora_models", [])})
        except Exception:
            pass
    return json.dumps({"lora_models": []})


MCP_TOOLS = {
    "train_lora": {
        "description": "Train a LoRA model for consistent artist appearance using FAL.ai",
        "input_schema": {
            "type": "object",
            "properties": {
                "artist_name": {"type": "string", "description": "Artist name"},
                "photos": {"type": "array", "items": {"type": "string"}, "description": "List of photo URLs (10-20 recommended)"},
                "trigger_word": {"type": "string", "description": "Trigger word for the LoRA (optional)"},
                "tenant_id": {"type": "string", "description": "Tenant ID for Hasura registration (optional)"},
            },
            "required": ["artist_name", "photos"],
        },
        "handler": lambda args: train_lora(args["artist_name"], args["photos"], args.get("trigger_word", ""), args.get("tenant_id", "")),
    },
    "list_loras": {
        "description": "List trained LoRA models",
        "input_schema": {
            "type": "object",
            "properties": {
                "tenant_id": {"type": "string", "description": "Filter by tenant (optional)"},
            },
            "required": [],
        },
        "handler": lambda args: list_loras(args.get("tenant_id", "")),
    },
}
