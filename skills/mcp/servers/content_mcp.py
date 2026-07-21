"""Content MCP Server — Video generation via FAL.ai.

Pipeline: FLUX (image) → Stable Video (image-to-video) → Supabase Storage.
"""

import hashlib
import json
import os

import httpx

FAL_KEY = os.getenv("FAL_KEY", "")
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")


async def _upload_to_supabase(content: bytes, path: str, content_type: str) -> str:
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        return ""
    headers = {
        "apikey": SUPABASE_SERVICE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "Content-Type": content_type,
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{SUPABASE_URL}/storage/v1/object/sdc-assets/{path}",
            content=content,
            headers=headers,
            timeout=120,
        )
        if resp.status_code in (200, 201):
            return f"{SUPABASE_URL}/storage/v1/object/public/sdc-assets/{path}"
    return ""


async def generate_video(artist_name: str, prompt: str, lora_weight_id: str = "", script_text: str = "", content_type: str = "clase") -> str:
    if not FAL_KEY:
        return json.dumps({"error": "FAL_KEY not configured"})
    if not prompt:
        return json.dumps({"error": "prompt is required"})
    try:
        headers_api = {"Authorization": f"Key {FAL_KEY}", "Content-Type": "application/json"}
        artist_slug = artist_name.lower().replace(" ", "-") if artist_name else "unknown"
        prompt_hash = hashlib.md5(prompt.encode()).hexdigest()[:8]

        enriched = prompt
        if lora_weight_id:
            enriched = f"[lora:{lora_weight_id}] {prompt}"

        # Step 1: Generate image with FLUX
        img_payload = {"prompt": enriched, "image_size": "portrait_4_3"}
        if lora_weight_id:
            img_payload["lora"] = lora_weight_id

        async with httpx.AsyncClient() as client:
            img_resp = await client.post(
                "https://fal.run/fal-ai/flux/schnell",
                json=img_payload,
                headers=headers_api,
                timeout=60,
            )
            img_data = img_resp.json()
            image_url = ""
            if "images" in img_data:
                image_url = img_data["images"][0].get("url", "")
            elif "output" in img_data:
                if isinstance(img_data["output"], dict):
                    image_url = img_data["output"].get("url", "")

            if not image_url:
                return json.dumps({"error": f"FLUX image generation failed: {str(img_data)[:200]}"})

            # Step 2: Animate image with Stable Video
            vid_resp = await client.post(
                "https://fal.run/fal-ai/stable-video",
                json={"image_url": image_url},
                headers=headers_api,
                timeout=120,
            )
            vid_data = vid_resp.json()
            video_url = ""
            if "video" in vid_data:
                video_url = vid_data["video"].get("url", "")
            elif "output" in vid_data:
                if isinstance(vid_data["output"], dict):
                    video_url = vid_data["output"].get("url", "") or vid_data["output"].get("video_url", "")

            if not video_url:
                # Return image URL as fallback (for FFmpeg slideshow)
                return json.dumps({
                    "video_url": "",
                    "image_url": image_url,
                    "artist": artist_name,
                    "content_type": content_type,
                    "fallback": True,
                    "model_used": "flux",
                    "message": "Stable Video failed, returning image for slideshow",
                })

            # Step 3: Upload video to Supabase Storage
            vid_content_resp = await client.get(video_url, timeout=60)
            vid_content = vid_content_resp.content
            storage_path = f"content/{artist_slug}/video_{prompt_hash}.mp4"
            stored_url = await _upload_to_supabase(vid_content, storage_path, "video/mp4")

            return json.dumps({
                "video_url": stored_url or video_url,
                "image_url": image_url,
                "artist": artist_name,
                "content_type": content_type,
                "fallback": False,
                "model_used": "flux+stable-video",
                "duration_seconds": 5,
                "size_bytes": len(vid_content),
            })

    except Exception as e:
        return json.dumps({"error": str(e)})


MCP_TOOLS = {
    "generate_video": {
        "description": "Generate a video using FLUX → Stable Video pipeline on FAL.ai",
        "input_schema": {
            "type": "object",
            "properties": {
                "artist_name": {"type": "string", "description": "Artist name for folder structure"},
                "prompt": {"type": "string", "description": "Visual description prompt for the image"},
                "lora_weight_id": {"type": "string", "description": "LoRA weight ID for consistent artist appearance"},
                "script_text": {"type": "string", "description": "Script text (for metadata)"},
                "content_type": {"type": "string", "description": "Content type: clase, promo, podcast"},
            },
            "required": ["artist_name", "prompt"],
        },
        "handler": lambda args: generate_video(args["artist_name"], args["prompt"], args.get("lora_weight_id", ""), args.get("script_text", ""), args.get("content_type", "clase")),
    },
}
