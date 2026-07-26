import fal_client
import logging
from typing import Optional

logger = logging.getLogger(__name__)

TALKING_HEAD_MODEL = "fal-ai/sync-lipsync/v3/image-to-video"
TALKING_HEAD_FALLBACK = "bytedance/seedance-2.0/reference-to-video"

def generate_talking_head(
    image_url: str,
    audio_url: str,
    face_restoration: bool = True,
    upscale: bool = True,
    model: str = "sync-lipsync-v3",
) -> dict:
    model_id = TALKING_HEAD_MODEL if model == "sync-lipsync-v3" else TALKING_HEAD_FALLBACK

    logger.info(f"Generating talking head with {model_id}")

    arguments = {
        "image_url": image_url,
        "audio_url": audio_url,
        "face_restoration": face_restoration,
        "upscale": upscale,
    }

    if model == "seedance-2":
        arguments["audio_priority"] = "lip_sync"

    result = fal_client.subscribe(model_id, arguments=arguments)
    video_url = result.get("video", result.get("video_url", {})).get("url", "")
    duration_ms = result.get("duration_ms", 0)

    cost = 0.08 if model == "sync-lipsync-v3" else 0.12
    if model == "seedance-2":
        cost = 0.12

    logger.info(f"Video generated: {video_url} (${cost})")

    return {
        "video_url": video_url,
        "duration_ms": duration_ms,
        "cost": cost,
        "model_used": model_id,
    }


def generate_talking_head_async(
    image_url: str,
    audio_url: str,
    webhook_url: Optional[str] = None,
    face_restoration: bool = True,
    upscale: bool = True,
) -> dict:
    model_id = TALKING_HEAD_MODEL

    arguments = {
        "image_url": image_url,
        "audio_url": audio_url,
        "face_restoration": face_restoration,
        "upscale": upscale,
    }

    if webhook_url:
        result = fal_client.subscribe(
            model_id,
            arguments=arguments,
            webhook_url=webhook_url,
        )
    else:
        result = fal_client.subscribe(model_id, arguments=arguments)

    return {
        "request_id": result.get("request_id", ""),
        "status": "queued",
    }
