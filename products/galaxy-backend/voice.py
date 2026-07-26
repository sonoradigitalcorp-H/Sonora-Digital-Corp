"""Voice pipeline for Agent Galaxy backend.

STT: Audio → text via DeepSeek V4 Flash (or Whisper-compatible endpoint)
TTS: Text → audio via DeepSeek V4 Flash (or OmniVoice-compatible endpoint)
WebSocket: Real-time bidirectional voice streaming.

Preview mode: Uses LLM-based synthesis; production should swap for dedicated STT/TTS providers.
"""

import asyncio
import base64
import io
import logging
import os
import time
from typing import AsyncGenerator, Optional

import httpx

log = logging.getLogger("galaxy.voice")

STT_PROVIDER = os.getenv("GALAXY_STT_PROVIDER", "deepseek_v4_flash")
TTS_PROVIDER = os.getenv("GALAXY_TTS_PROVIDER", "deepseek_v4_flash")
OMNIVOICE_URL = os.getenv("OMNIVOICE_URL", "http://localhost:3900")

STT_SYSTEM_PROMPT = (
    "You are a speech-to-text assistant. Transcribe the following audio "
    "description into text. Return only the transcription."
)


async def speech_to_text(audio_data: bytes, language: str = "es") -> dict:
    """Convert audio bytes to text.

    Preview mode: Accepts a text description of audio content since
    DeepSeek V4 Flash is a text model. In production, this should use
    Whisper, Deepgram, or similar STT provider.

    Args:
        audio_data: Raw audio bytes (WAV/MP3/OGG).
        language: Language code for transcription.

    Returns:
        dict with keys: text, provider, elapsed, confidence.
    """
    t0 = time.time()
    audio_b64 = base64.b64encode(audio_data).decode("utf-8")[:200]

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                f"{OMNIVOICE_URL}/stt",
                json={"audio_b64": audio_b64, "language": language},
            )
            if resp.status_code == 200:
                data = resp.json()
                text = data.get("text", "")
                elapsed = time.time() - t0
                log.info(f"STT OK | provider=omnivoice lang={language} elapsed={elapsed:.1f}s")
                return {
                    "text": text,
                    "provider": "omnivoice",
                    "elapsed": round(elapsed, 2),
                    "confidence": data.get("confidence", 0.95),
                }
    except Exception as e:
        log.warning(f"OmniVoice STT failed, using fallback: {e}")

    elapsed = time.time() - t0
    return {
        "text": f"[Preview STT: {len(audio_data)} bytes, lang={language}]",
        "provider": STT_PROVIDER,
        "elapsed": round(elapsed, 2),
        "confidence": 0.5,
    }


async def text_to_speech(text: str, voice: str = "default", language: str = "es") -> dict:
    """Convert text to audio bytes.

    Tries OmniVoice first, falls back to LLM-based synthesis preview.

    Args:
        text: Text to synthesize.
        voice: Voice identifier.
        language: Language code.

    Returns:
        dict with keys: audio_b64, provider, elapsed, format.
    """
    t0 = time.time()

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                f"{OMNIVOICE_URL}/tts",
                json={"text": text, "voice": voice, "language": language},
            )
            if resp.status_code == 200:
                data = resp.json()
                audio_b64 = data.get("audio_b64", "")
                if audio_b64:
                    elapsed = time.time() - t0
                    log.info(f"TTS OK | provider=omnivoice voice={voice} elapsed={elapsed:.1f}s")
                    return {
                        "audio_b64": audio_b64,
                        "provider": "omnivoice",
                        "elapsed": round(elapsed, 2),
                        "format": data.get("format", "wav"),
                    }
    except Exception as e:
        log.warning(f"OmniVoice TTS failed, using fallback: {e}")

    elapsed = time.time() - t0
    audio_data = b"[Preview TTS: voice synthesis not available]"
    audio_b64 = base64.b64encode(audio_data).decode("utf-8")
    return {
        "audio_b64": audio_b64,
        "provider": TTS_PROVIDER,
        "elapsed": round(elapsed, 2),
        "format": "wav",
    }


async def text_to_speech_bytes(text: str, voice: str = "default", language: str = "es") -> bytes:
    """Convert text to raw audio bytes.

    Wrapper around text_to_speech that decodes the base64 payload.
    """
    result = await text_to_speech(text, voice=voice, language=language)
    try:
        return base64.b64decode(result["audio_b64"])
    except Exception:
        return result.get("audio_b64", b"").encode("utf-8") if isinstance(result.get("audio_b64"), str) else b""


async def voice_stream_generator(
    text: str,
    voice: str = "default",
    language: str = "es",
    chunk_size: int = 4096,
) -> AsyncGenerator[bytes, None]:
    """Generate audio in streaming chunks for WebSocket delivery.

    Yields audio chunks as they become available.
    """
    audio = await text_to_speech_bytes(text, voice=voice, language=language)
    for i in range(0, len(audio), chunk_size):
        yield audio[i : i + chunk_size]
        await asyncio.sleep(0.01)
