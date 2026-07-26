import fal_client
import logging
import requests
from typing import Optional

logger = logging.getLogger(__name__)

TTS_MODEL = "bytedance/seed-audio-1.0"
TTS_FALLBACK = "fal-ai/playaudio/v2"

def get_audio_duration(url: str) -> float:
    try:
        resp = requests.head(url, timeout=5)
        if resp.status_code == 200:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            path = parsed.path
            if "duration" in resp.headers:
                return float(resp.headers["duration"])
    except Exception:
        pass
    return 0.0


def generate_tts(
    text: str,
    reference_audio: Optional[str] = None,
    language: str = "es",
    voice: str = "seed-audio",
) -> dict:
    model_id = TTS_MODEL if voice == "seed-audio" else TTS_FALLBACK
    logger.info(f"Generating TTS with {model_id}")

    arguments = {
        "prompt": text,
        "target_language": language,
        "audio_type": "talk",
    }

    if reference_audio:
        arguments["reference_audio"] = reference_audio

    result = fal_client.subscribe(model_id, arguments=arguments)

    if "audio" in result:
        audio_url = result["audio"]["url"]
    elif "audio_url" in result:
        audio_url = result["audio_url"]
    else:
        audio_url = result.get("output", {}).get("url", "")

    duration_ms = result.get("duration_ms", 0)
    if not duration_ms and audio_url:
        duration_ms = int(get_audio_duration(audio_url) * 1000)

    cost = 0.01 if voice == "seed-audio" else 0.015
    if reference_audio:
        cost += 0.005

    logger.info(f"Audio generated: {audio_url} (${cost})")

    return {
        "audio_url": audio_url,
        "duration_ms": duration_ms,
        "cost": cost,
        "model_used": model_id,
    }
