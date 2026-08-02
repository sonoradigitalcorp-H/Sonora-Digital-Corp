"""Fal.ai MCP Server — Image, Video and Audio generation via fal.ai cloud API."""

import json
import os
import httpx

FAL_API_KEY = os.getenv("FAL_API_KEY", "")


async def _fal_headers() -> dict:
    return {"Authorization": f"Key {FAL_API_KEY}", "Content-Type": "application/json"}


async def gen_image(prompt: str, model: str = "fal-ai/flux/schnell", image_size: str = "1024x1024") -> str:
    if not FAL_API_KEY:
        return json.dumps({"error": "FAL_API_KEY not configured"})
    if not prompt:
        return json.dumps({"error": "prompt is required"})

    try:
        headers = await _fal_headers()
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"https://fal.run/{model}",
                json={"prompt": prompt, "image_size": image_size},
                headers=headers,
                timeout=60,
            )
            data = resp.json()
            image_url = data.get("images", [{}])[0].get("url", "") if "images" in data else data.get("image_url", "")
            return json.dumps({"image_url": image_url, "model": model, "prompt": prompt})
    except Exception as e:
        return json.dumps({"error": str(e)})


async def gen_video(prompt: str, model: str = "fal-ai/stable-video") -> str:
    if not FAL_API_KEY:
        return json.dumps({"error": "FAL_API_KEY not configured"})

    try:
        headers = await _fal_headers()
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"https://fal.run/{model}",
                json={"prompt": prompt},
                headers=headers,
                timeout=120,
            )
            data = resp.json()
            video_url = data.get("video", {}).get("url", "") or data.get("video_url", "")
            return json.dumps({"video_url": video_url, "model": model})
    except Exception as e:
        return json.dumps({"error": str(e)})


async def list_models() -> str:
    return json.dumps({
        "image_models": [
            "fal-ai/flux/schnell",
            "fal-ai/flux-lora",
            "fal-ai/flux-pro",
            "fal-ai/stable-diffusion-v3",
        ],
        "video_models": [
            "fal-ai/stable-video",
            "fal-ai/runway-gen3",
        ],
        "audio_models": [
            "fal-ai/whisper",
            "fal-ai/playht/tts",
        ],
    })


MCP_TOOLS = {
    "fal_gen_image": {
        "description": "Generate an image using fal.ai models",
        "input_schema": {
            "type": "object",
            "properties": {
                "prompt": {"type": "string", "description": "Image description"},
                "model": {"type": "string", "description": "Model name (default: fal-ai/flux/schnell)"},
                "image_size": {"type": "string", "description": "Size (default: 1024x1024)"},
            },
            "required": ["prompt"],
        },
        "handler": lambda args: gen_image(args["prompt"], args.get("model", "fal-ai/flux/schnell"), args.get("image_size", "1024x1024")),
    },
    "fal_gen_video": {
        "description": "Generate a video using fal.ai models",
        "input_schema": {
            "type": "object",
            "properties": {
                "prompt": {"type": "string", "description": "Video description"},
                "model": {"type": "string", "description": "Model name (default: fal-ai/stable-video)"},
            },
            "required": ["prompt"],
        },
        "handler": lambda args: gen_video(args["prompt"], args.get("model", "fal-ai/stable-video")),
    },
    "fal_list_models": {
        "description": "List available fal.ai models",
        "input_schema": {"type": "object", "properties": {}},
        "handler": lambda _: list_models(),
    },
}
