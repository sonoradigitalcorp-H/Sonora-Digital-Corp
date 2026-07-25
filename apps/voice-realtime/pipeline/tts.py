"""
Motor de Text-to-Speech (TTS) con múltiples proveedores.
Soporta Edge TTS (rápido, voces neurales) y OmniVoice (clonación).
"""
import asyncio
import base64
import json
import logging
import os
import tempfile
from pathlib import Path
from typing import Optional

import httpx

logger = logging.getLogger("voice-realtime.tts")


class TTSEngine:
    """
    Motor TTS unificado con fallback.
    Proveedores: edge (Rápido, neural), omnivoice (Clonación), openai (Premium).
    """

    PROVIDERS = ["edge", "omnivoice", "openai"]

    def __init__(self, provider: str = "edge", voice: str = "es-MX-DaliaNeural"):
        self.provider = provider if provider in self.PROVIDERS else "edge"
        self.voice = voice
        self._edge_tts = None
        logger.info(f"TTSEngine initialized: provider={provider}, voice={voice}")

    async def _edge_synthesize(self, text: str) -> Optional[bytes]:
        """Síntesis con Edge TTS (rápido, neural, local)."""
        try:
            import edge_tts
            communicate = edge_tts.Communicate(text, self.voice)
            audio_bytes = b""
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_bytes += chunk["data"]
            return audio_bytes if audio_bytes else None
        except Exception as e:
            logger.warning(f"Edge TTS failed: {e}")
            return None

    async def _omnivoice_synthesize(self, text: str) -> Optional[bytes]:
        """Síntesis con OmniVoice (voz clonada)."""
        try:
            omnivoice_url = os.environ.get("OMNIVOICE_URL", "http://127.0.0.1:3900")
            voice_name = os.environ.get("OMNIVOICE_VOICE", "mystic")
            async with httpx.AsyncClient(timeout=30) as client:
                r = await client.post(
                    f"{omnivoice_url}/speak",
                    json={"text": text, "voice": voice_name, "language": "es"},
                )
                if r.status_code == 200:
                    return r.content
                logger.warning(f"OmniVoice {r.status_code}")
        except Exception as e:
            logger.warning(f"OmniVoice failed: {e}")
        return None

    async def _openai_synthesize(self, text: str) -> Optional[bytes]:
        """Síntesis con OpenAI TTS (premium, requiere API key)."""
        try:
            api_key = os.environ.get("OPENAI_API_KEY", "")
            if not api_key:
                return None
            async with httpx.AsyncClient(timeout=30) as client:
                r = await client.post(
                    "https://api.openai.com/v1/audio/speech",
                    headers={"Authorization": f"Bearer {api_key}"},
                    json={
                        "model": "tts-1",
                        "input": text,
                        "voice": "nova",
                        "response_format": "mp3",
                    },
                )
                if r.status_code == 200:
                    return r.content
        except Exception as e:
            logger.warning(f"OpenAI TTS failed: {e}")
        return None

    async def synthesize(self, text: str) -> Optional[bytes]:
        """Sintetiza texto a audio con fallback entre proveedores."""
        if self.provider == "edge":
            audio = await self._edge_synthesize(text)
            if audio:
                return audio
            audio = await self._omnivoice_synthesize(text)
            if audio:
                return audio
            return await self._openai_synthesize(text)

        elif self.provider == "omnivoice":
            audio = await self._omnivoice_synthesize(text)
            if audio:
                return audio
            audio = await self._edge_synthesize(text)
            if audio:
                return audio
            return await self._openai_synthesize(text)

        else:  # openai
            audio = await self._openai_synthesize(text)
            if audio:
                return audio
            audio = await self._edge_synthesize(text)
            if audio:
                return audio
            return await self._omnivoice_synthesize(text)

    async def synthesize_stream(self, text: str, chunk_size: int = 4096):
        """
        Sintetiza texto en chunks de audio streaming.
        Útil para enviar audio mientras se genera (menor latencia).
        Yields: bytes (chunks de audio MP3/PCM)
        """
        audio = await self.synthesize(text)
        if not audio:
            return
        # Enviar en chunks para simular streaming
        for i in range(0, len(audio), chunk_size):
            yield audio[i:i + chunk_size]
