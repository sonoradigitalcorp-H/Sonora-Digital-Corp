"""
Motor de Text-to-Speech (TTS) con múltiples proveedores.
Primario: Kokoro-82M (CPU, español, ~200-500ms)
Fallback: Edge TTS → OmniVoice → OpenAI

Flujo:
  1. Kokoro (alta calidad, CPU local, voz española em_alex)
  2. Edge TTS (rápido, neural, gratis)
  3. OmniVoice (clonación de voz, si está disponible)
  4. OpenAI TTS (premium, requiere API key)
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
    Motor TTS unificado con Kokoro como primario y fallback progresivo.
    Proveedores: kokoro (CPU, español), edge (rápido), omnivoice (clonación), openai (premium).
    """

    PROVIDERS = ["kokoro", "edge", "omnivoice", "openai"]

    def __init__(self, provider: str = "kokoro", voice: str = "em_alex"):
        self.provider = provider if provider in self.PROVIDERS else "kokoro"
        self.voice = voice
        self._kokoro = None
        self._edge_tts = None
        logger.info(f"TTSEngine initialized: provider={provider}, voice={voice}")

    # ─── Kokoro TTS (primario) ───

    async def _kokoro_synthesize(self, text: str) -> Optional[bytes]:
        """Síntesis con Kokoro-82M (CPU, español, ~200-500ms)."""
        try:
            from kokoro import KPipeline
            import numpy as np
            import soundfile as sf

            if self._kokoro is None:
                logger.info("Cargando Kokoro KPipeline...")
                self._kokoro = KPipeline(lang_code="a")
                logger.info("Kokoro KPipeline cargado ✓")

            voice = self.voice or "em_alex"
            loop = asyncio.get_event_loop()
            audio_segments = []

            def _generate():
                gen = self._kokoro(text, voice=voice, speed=1.0)
                for gs, ps, audio in gen:
                    audio_segments.append(audio)
                if audio_segments:
                    combined = np.concatenate(audio_segments) if len(audio_segments) > 1 else audio_segments[0]
                    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                        tmp = f.name
                    sf.write(tmp, combined, 24000)
                    with open(tmp, "rb") as f:
                        data = f.read()
                    os.unlink(tmp)
                    return data
                return None

            audio_bytes = await loop.run_in_executor(None, _generate)
            if audio_bytes:
                duration = len(audio_bytes) / 48000
                logger.info(f"Kokoro TTS: {len(audio_bytes)} bytes ({duration:.1f}s)")
            return audio_bytes

        except ImportError as e:
            logger.warning(f"Kokoro no disponible ({e}), saltando a fallback")
            return None
        except Exception as e:
            logger.error(f"Kokoro synthesize error: {e}")
            return None

    # ─── Edge TTS (fallback 1) ───

    async def _edge_synthesize(self, text: str) -> Optional[bytes]:
        """Síntesis con Edge TTS (rápido, neural, local)."""
        try:
            import edge_tts
            communicate = edge_tts.Communicate(text, self.voice if self.voice in [
                "es-MX-DaliaNeural", "es-MX-JorgeNeural",
                "es-ES-AlvaroNeural", "es-ES-ElviraNeural"
            ] else "es-MX-DaliaNeural")
            audio_bytes = b""
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_bytes += chunk["data"]
            if audio_bytes:
                logger.info(f"Edge TTS: {len(audio_bytes)} bytes")
                return audio_bytes
            return None
        except Exception as e:
            logger.warning(f"Edge TTS failed: {e}")
            return None

    # ─── OmniVoice (fallback 2) ───

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
                    logger.info(f"OmniVoice: {len(r.content)} bytes")
                    return r.content
                logger.warning(f"OmniVoice {r.status_code}")
        except Exception as e:
            logger.warning(f"OmniVoice failed: {e}")
        return None

    # ─── OpenAI TTS (fallback 3) ───

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
                    logger.info(f"OpenAI TTS: {len(r.content)} bytes")
                    return r.content
        except Exception as e:
            logger.warning(f"OpenAI TTS failed: {e}")
        return None

    # ─── Orquestación principal ───

    async def synthesize(self, text: str) -> Optional[bytes]:
        """Sintetiza texto a audio con fallback progresivo.

        Orden: Kokoro → Edge → OmniVoice → OpenAI
        """
        if self.provider == "kokoro":
            audio = await self._kokoro_synthesize(text)
            if audio:
                return audio
            logger.info("Kokoro no disponible, fallback a Edge TTS")
            audio = await self._edge_synthesize(text)
            if audio:
                return audio
            audio = await self._omnivoice_synthesize(text)
            if audio:
                return audio
            return await self._openai_synthesize(text)

        elif self.provider == "edge":
            audio = await self._edge_synthesize(text)
            if audio:
                return audio
            audio = await self._kokoro_synthesize(text)
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
            audio = await self._kokoro_synthesize(text)
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
            audio = await self._kokoro_synthesize(text)
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
        Yields: bytes (chunks de audio)
        """
        audio = await self.synthesize(text)
        if not audio:
            return
        for i in range(0, len(audio), chunk_size):
            yield audio[i:i + chunk_size]
