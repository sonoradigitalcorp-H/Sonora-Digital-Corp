"""
TTS — Motor de texto a voz con orquestación GPU.

Flujo:
  1. GPUOrchestrator intenta: GPU local > RunPod > CPU fallback
  2. Policy Engine controla budget y rate limits
  3. Resultado: bytes WAV listos para enviar por WebSocket/WhatsApp
"""

import asyncio
import logging
import os
import tempfile
from pathlib import Path
from typing import Optional

logger = logging.getLogger("tts")

BASE = Path(__file__).parent
CESAR_REF_AUDIO = str(BASE / "cesar" / "processed" / "cesar-ref-short.wav")
CESAR_REF_TEXT_FILE = str(BASE / "cesar" / "ref_text_short.txt")


class TTS:
    """Motor TTS inteligente con orquestación GPU y fallback CPU (Kokoro)."""

    def __init__(self, engine: str = "auto"):
        self.engine = engine
        self._orchestrator = None
        self._kokoro = None
        self._local_model = None

    async def synthesize(self, text: str, *, voice: Optional[str] = None) -> Optional[bytes]:
        """
        Sintetiza texto a audio.

        Args:
            text: Texto a convertir
            voice: Voz objetivo ("cesar" para clonada)

        Returns:
            bytes WAV (24kHz, mono, PCM16) o None si falla
        """
        if self.engine == "edge":
            return await self._edge_tts(text, "es-MX-DaliaNeural")

        if self.engine == "kokoro":
            return await self._kokoro_tts(text)

        # Modo "auto": GPU Orchestrator → Kokoro → edge-tts
        result = await self._get_orchestrator().synthesize(text, voice)
        if result.success:
            logger.info(f"TTS via {result.provider}: {result.latency_ms:.0f}ms (${result.cost:.5f})")
            return result.audio_bytes

        # Fallback 1: Kokoro (alta calidad, CPU)
        logger.info("Orquestador no disponible, fallback a Kokoro")
        kokoro_audio = await self._kokoro_tts(text)
        if kokoro_audio:
            return kokoro_audio

        # Fallback 2: edge-tts (gratis, calidad media)
        logger.warning("Kokoro no disponible, fallback final a edge-tts")
        return await self._edge_tts(text, "es-MX-DaliaNeural")

    def _get_kokoro(self):
        if self._kokoro is None:
            from tenants.aztrotech.skills.voice.kokoro_tts import KokoroTTS
            self._kokoro = KokoroTTS()
        return self._kokoro

    def _get_orchestrator(self):
        if self._orchestrator is None:
            from tenants.aztrotech.skills.voice.gpu_orchestrator import GPUOrchestrator
            self._orchestrator = GPUOrchestrator()
        return self._orchestrator

    async def _edge_tts(self, text: str, voice: Optional[str] = None) -> Optional[bytes]:
        """edge-tts en CPU (fallback secundario)."""
        try:
            import edge_tts
            import subprocess

            voice = voice or "es-MX-DaliaNeural"
            mp3 = f"/tmp/tts-edge-{abs(hash(text))}.mp3"
            wav = mp3.replace(".mp3", ".wav")

            comm = edge_tts.Communicate(text, voice)
            await comm.save(mp3)

            subprocess.run([
                "ffmpeg", "-y", "-i", mp3,
                "-acodec", "pcm_s16le", "-ar", "24000", "-ac", "1",
                wav,
            ], capture_output=True, check=True)

            with open(wav, "rb") as f:
                data = f.read()

            os.unlink(mp3)
            os.unlink(wav)
            return data

        except Exception as e:
            logger.error(f"edge-tts error: {e}")
            return None

    async def _kokoro_tts(self, text: str) -> Optional[bytes]:
        """Kokoro TTS v1.0 (82M params) — fallback CPU de alta calidad."""
        try:
            kokoro = self._get_kokoro()
            return await kokoro.synthesize(text)
        except Exception as e:
            logger.error(f"Kokoro error: {e}")
            return None

    # === LEGACY: Qwen3-TTS local ===
    async def _qwen_tts(self, text: str) -> Optional[bytes]:
        """Qwen3-TTS en CPU (lento, ~15s por síntesis).
        Se mantiene para compatibilidad. Usar GPUOrchestrator en su lugar.
        """
        try:
            import torch
            import soundfile as sf
            from qwen_tts import Qwen3TTSModel

            if self._local_model is None:
                logger.info("Cargando Qwen3-TTS en CPU (esto puede tomar ~30s)...")
                self._local_model = Qwen3TTSModel.from_pretrained(
                    "Qwen/Qwen3-TTS-12Hz-0.6B-Base",
                    device_map="cpu",
                    dtype=torch.float32,
                )

            with open(CESAR_REF_TEXT_FILE) as f:
                ref_text = f.read().strip()

            loop = asyncio.get_event_loop()
            wavs, sr = await loop.run_in_executor(
                None,
                lambda: self._local_model.generate_voice_clone(
                    text=text,
                    language="Spanish",
                    ref_audio=CESAR_REF_AUDIO,
                    ref_text=ref_text,
                ),
            )

            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                out = f.name
            sf.write(out, wavs[0], sr)
            with open(out, "rb") as f:
                data = f.read()
            os.unlink(out)
            return data

        except Exception as e:
            logger.error(f"Qwen3-TTS error: {e}")
            return None
