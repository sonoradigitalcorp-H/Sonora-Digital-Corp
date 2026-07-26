"""
Kokoro TTS wrapper — fallback CPU de alta calidad.
Usa el modelo Kokoro-82M (82M params, MIT license).
Corre en CPU con latencia ~200-500ms.
"""

import asyncio
import logging
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional

logger = logging.getLogger("kokoro")


class KokoroTTS:
    """
    Wrapper ligero para Kokoro-82M.
    Usa el pipeline oficial pero con manejo de dependencias controlado.
    """

    def __init__(self):
        self._pipeline = None
        self._voice_name = "em_alex"  # Spanish male voice

    def _load(self):
        if self._pipeline is not None:
            return

        # Configurar entorno para evitar PIP errors
        env = os.environ.copy()
        env["PIP_REQUIRE_VIRTUALENV"] = "false"

        # El import puede trigger subprocess calls para espeak
        # Las interceptamos y silenciamos
        try:
            from kokoro import KPipeline
            self._pipeline = KPipeline(lang_code="a")
            logger.info("Kokoro KPipeline cargado ✓")
        except Exception as e:
            logger.error(f"Error cargando Kokoro: {e}")
            raise

    async def synthesize(self, text: str, voice: Optional[str] = None) -> Optional[bytes]:
        """
        Sintetiza texto a audio WAV (24kHz, mono, PCM16).
        Retorna bytes o None si falla.
        """
        import numpy as np
        import soundfile as sf
        import torch

        self._load()
        voice_name = voice or self._voice_name

        loop = asyncio.get_event_loop()
        audio_segments = []

        def _generate():
            gen = self._pipeline(text, voice=voice_name, speed=1.0)
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

        try:
            audio_bytes = await loop.run_in_executor(None, _generate)
            if audio_bytes:
                logger.info(f"Kokoro TTS: {len(audio_bytes)} bytes ({len(audio_bytes)/48000:.1f}s)")
            return audio_bytes
        except Exception as e:
            logger.error(f"Kokoro synthesize error: {e}")
            return None

    def available_voices(self) -> list[str]:
        """Lista voces disponibles para español."""
        return ["em_alex", "em_santa", "ef_dora"]  # voces españolas
