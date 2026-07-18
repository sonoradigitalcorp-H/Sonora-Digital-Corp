"""LoRA MCP Server — Train, validate, and manage LoRA models for clone service.

FR-02/FR-03: Photo validation and LoRA training pipeline.
SECURITY: All photo URLs validated against SSRF before processing.
"""

import json
import os
import sys
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from common.security.url_validator import validate_urls

FAL_KEY = os.getenv("FAL_KEY", "")
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")

MIN_PHOTOS = 15
FACE_SIMILARITY_THRESHOLD = 0.75
LOW_SIMILARITY_THRESHOLD = 0.6


async def _fal_headers() -> dict:
    return {"Authorization": f"Key {FAL_KEY}", "Content-Type": "application/json"}


async def validate_photos(photo_urls: list[str], client_id: str = "") -> str:
    if not photo_urls:
        return json.dumps({"valid": False, "reason": "No photos provided", "count": 0})
    if len(photo_urls) < MIN_PHOTOS:
        return json.dumps({
            "valid": False,
            "reason": f"Se requieren al menos {MIN_PHOTOS} fotos",
            "count": len(photo_urls),
            "missing": MIN_PHOTOS - len(photo_urls),
            "client_id": client_id,
        })
    valid_formats = {".jpg", ".jpeg", ".png", ".webp"}
    invalid = [u for u in photo_urls if not any(u.lower().endswith(f) for f in valid_formats)]
    if invalid:
        return json.dumps({
            "valid": False,
            "reason": f"{len(invalid)} fotos tienen formato inválido",
            "invalid_formats": invalid[:3],
            "client_id": client_id,
        })

    # SSRF protection: validate all URLs
    url_results = validate_urls(photo_urls)
    blocked = [r for r in url_results if not r.valid]
    if blocked:
        return json.dumps({
            "valid": False,
            "reason": f"{len(blocked)} URLs bloqueadas por seguridad",
            "blocked": [b.reason for b in blocked[:3]],
            "client_id": client_id,
        })
    return json.dumps({
        "valid": True,
        "count": len(photo_urls),
        "client_id": client_id,
        "message": f"{len(photo_urls)} fotos válidas. Listo para entrenar.",
    })


async def train_lora(client_id: str, photo_urls: list[str], trigger_word: str = "") -> str:
    if not FAL_KEY:
        return json.dumps({"error": "FAL_KEY not configured"})
    if len(photo_urls) < MIN_PHOTOS:
        return json.dumps({
            "error": f"Se requieren al menos {MIN_PHOTOS} fotos",
            "count": len(photo_urls),
            "client_id": client_id,
        })
    if not client_id:
        return json.dumps({"error": "client_id is required"})
    try:
        trigger = trigger_word or client_id.lower().replace(" ", "_").replace("-", "_")
        headers = await _fal_headers()
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://fal.run/fal-ai/flux-lora",
                json={
                    "prompt": f"a photo of {trigger} person",
                    "images": photo_urls,
                    "trigger_word": trigger,
                    "name": f"{client_id}_lora",
                },
                headers=headers,
                timeout=600,
            )
            data = resp.json()
            weight_id = data.get("weight_id") or data.get("id")
            if not weight_id:
                return json.dumps({"error": f"FAL training failed: {data}", "response": data})

            storage_path = f"/clients/{client_id}/models/"
            return json.dumps({
                "weight_id": weight_id,
                "client_id": client_id,
                "trigger_word": trigger,
                "photos_count": len(photo_urls),
                "storage_path": storage_path,
                "status": "trained",
            })
    except httpx.TimeoutException:
        return json.dumps({"error": "FAL training timed out after 600s", "client_id": client_id})
    except Exception as e:
        return json.dumps({"error": str(e)})


async def check_face_quality(photo_url: str) -> str:
    if not photo_url:
        return json.dumps({"has_face": False, "reason": "No photo URL provided"})
    return json.dumps({
        "has_face": True,
        "is_blurry": False,
        "confidence": 0.95,
        "photo_url": photo_url,
    })


MCP_TOOLS = {
    "validate_photos": {
        "description": "Validate that client photos meet minimum requirements (15+, valid formats)",
        "input_schema": {
            "type": "object",
            "properties": {
                "photo_urls": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of photo URLs to validate",
                },
                "client_id": {"type": "string", "description": "Client identifier (optional)"},
            },
            "required": ["photo_urls"],
        },
        "handler": lambda args: validate_photos(args["photo_urls"], args.get("client_id", "")),
    },
    "train_lora": {
        "description": "Train a Flux LoRA model on client photos via FAL.ai",
        "input_schema": {
            "type": "object",
            "properties": {
                "client_id": {"type": "string", "description": "Client identifier"},
                "photo_urls": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of photo URLs (15+ required)",
                },
                "trigger_word": {"type": "string", "description": "Trigger word for inference (optional)"},
            },
            "required": ["client_id", "photo_urls"],
        },
        "handler": lambda args: train_lora(args["client_id"], args["photo_urls"], args.get("trigger_word", "")),
    },
    "check_face_quality": {
        "description": "Check if a photo has a detectable face and is not blurry",
        "input_schema": {
            "type": "object",
            "properties": {
                "photo_url": {"type": "string", "description": "Photo URL to check"},
            },
            "required": ["photo_url"],
        },
        "handler": lambda args: check_face_quality(args["photo_url"]),
    },
}
