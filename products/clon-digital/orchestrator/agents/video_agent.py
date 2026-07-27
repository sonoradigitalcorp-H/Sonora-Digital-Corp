import httpx
import logging
from typing import Optional

from apps.core.config import settings

logger = logging.getLogger(__name__)

FAL_API = settings.fal_api_url


class VideoAgent:
    async def generate_talking_head(
        self,
        image_url: str,
        audio_url: str,
        model: str = "sync-lipsync-v3",
        face_restoration: bool = True,
        upscale: bool = True,
    ) -> dict:
        async with httpx.AsyncClient(timeout=120.0) as client:
            payload = {
                "image_url": image_url,
                "audio_url": audio_url,
                "model": model,
                "face_restoration": face_restoration,
                "upscale": upscale,
            }
            resp = await client.post(f"{FAL_API}/v1/talking-head", json=payload)
            resp.raise_for_status()
            return resp.json()

    async def generate_tts(
        self,
        text: str,
        reference_audio: Optional[str] = None,
        language: str = "es",
        voice: str = "seed-audio",
    ) -> dict:
        async with httpx.AsyncClient(timeout=60.0) as client:
            payload = {
                "text": text,
                "language": language,
                "voice": voice,
            }
            if reference_audio:
                payload["reference_audio"] = reference_audio
            resp = await client.post(f"{FAL_API}/v1/tts", json=payload)
            resp.raise_for_status()
            return resp.json()

    async def train_lora(self, image_urls: list[str], trigger_word: str = "person") -> dict:
        async with httpx.AsyncClient(timeout=300.0) as client:
            resp = await client.post(f"{FAL_API}/v1/train-lora", json={
                "image_urls": image_urls,
                "trigger_word": trigger_word,
            })
            resp.raise_for_status()
            return resp.json()
