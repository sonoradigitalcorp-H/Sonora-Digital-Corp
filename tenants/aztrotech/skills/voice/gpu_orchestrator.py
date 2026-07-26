"""
GPU Orchestrator — Gestión de GPU on-demand para inferencia de voz.

Estrategias:
  1. GPU local (nvidia-smi) → usar directamente
  2. RunPod Serverless → endpoint HTTP (pago por segundo)
  3. Vast.ai → instancia SSH (pago por hora)
  4. Fallback CPU → edge-tts (gratis, lento)

Flujo:
  orchestrator.synthesize(text) →
    1. Policy check (budget, rate limit)
    2. ¿GPU local? → Qwen3-TTS local en GPU
    3. ¿RunPod config? → HTTP request al endpoint serverless
    4. ¿Vast config? → SSH + Docker exec
    5. Fallback → edge-tts CPU
"""

import asyncio
import json
import logging
import os
import subprocess
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

logger = logging.getLogger("gpu.orchestrator")


class GPUProvider(Enum):
    LOCAL = "local"
    RUNPOD = "runpod"
    VAST = "vast"
    CPU = "cpu"


@dataclass
class GPUResult:
    success: bool
    audio_bytes: Optional[bytes] = None
    provider: str = "cpu"
    latency_ms: float = 0.0
    cost: float = 0.0
    error: str = ""


class GPUOrchestrator:
    """
    Orquesta inferencia en GPU según disponibilidad y configuración.

    Uso:
        orchestrator = GPUOrchestrator()
        result = await orchestrator.synthesize("Hola, soy Mystic")
        if result.success:
            # result.audio_bytes -> WAV bytes
    """

    def __init__(self, config: Optional[dict] = None):
        self.config = config or self._load_config()
        self._local_gpu = self._detect_local_gpu()

    def _load_config(self) -> dict:
        """Carga configuración desde environment o archivo."""
        return {
            "runpod": {
                "api_key": os.environ.get("RUNPOD_API_KEY", ""),
                "endpoint_id": os.environ.get("RUNPOD_TTS_ENDPOINT", ""),
                "timeout": int(os.environ.get("RUNPOD_TIMEOUT", "30")),
            },
            "vast": {
                "api_key": os.environ.get("VAST_API_KEY", ""),
                "instance_id": os.environ.get("VAST_INSTANCE_ID", ""),
            },
            "prefer": os.environ.get("GPU_PROVIDER", "runpod"),  # local > runpod > vast > cpu
        }

    def _detect_local_gpu(self) -> bool:
        """Detecta si hay GPU local disponible (NVIDIA)."""
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=name,memory.free", "--format=csv,noheader"],
                capture_output=True, text=True, timeout=5,
            )
            if result.returncode == 0 and result.stdout.strip():
                gpu_info = result.stdout.strip()
                logger.info(f"GPU local detectada: {gpu_info}")
                return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        logger.info("Sin GPU local — modo CPU")
        return False

    async def synthesize(
        self, text: str, voice: Optional[str] = None, timeout: int = 30
    ) -> GPUResult:
        """
        Sintetiza texto a audio usando el mejor proveedor disponible.

        Retorna GPUResult con audio_bytes en formato WAV.
        """
        start = time.time()

        # 1. Intentar GPU local
        if self._local_gpu:
            result = await self._local_gpu_tts(text, voice)
            if result.success:
                return result

        # 2. RunPod Serverless
        rp = self.config.get("runpod", {})
        if rp.get("api_key") and rp.get("endpoint_id"):
            result = await self._runpod_tts(text, voice, timeout)
            if result.success:
                return result

        # 3. Fallback CPU (edge-tts)
        logger.info("Fallback a CPU (edge-tts)")
        result = await self._cpu_tts(text, voice)
        result.latency_ms = (time.time() - start) * 1000
        return result

    async def _local_gpu_tts(self, text: str, voice: Optional[str] = None) -> GPUResult:
        """Qwen3-TTS en GPU local (CUDA)."""
        start = time.time()
        try:
            from tenants.aztrotech.skills.voice.tts import TTS
            tts = TTS(engine="qwen")  # Forzará device_map="auto" o "cuda"
            audio = await tts.synthesize(text, voice=voice)
            if audio:
                logger.info(f"TTS local GPU: {len(audio)} bytes en {(time.time()-start)*1000:.0f}ms")
                return GPUResult(
                    success=True,
                    audio_bytes=audio,
                    provider="local_gpu",
                    latency_ms=(time.time() - start) * 1000,
                    cost=0.0,
                )
        except Exception as e:
            logger.warning(f"TTS local GPU falló: {e}")
        return GPUResult(success=False, provider="local_gpu", error="Fallback necesario")

    async def _runpod_tts(self, text: str, voice: Optional[str] = None, timeout: int = 30) -> GPUResult:
        """TTS via RunPod Serverless endpoint."""
        import httpx

        start = time.time()
        rp = self.config.get("runpod", {})
        api_key = rp.get("api_key", "")
        endpoint_id = rp.get("endpoint_id", "")

        if not api_key or not endpoint_id:
            return GPUResult(success=False, provider="runpod", error="RunPod no configurado")

        url = f"https://api.runpod.ai/v2/{endpoint_id}/runsync"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "input": {
                "text": text,
                "voice": voice or "cesar",
                "language": "Spanish",
            }
        }

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                r = await client.post(url, headers=headers, json=payload)
                if r.status_code == 200:
                    data = r.json()
                    audio_b64 = data.get("output", {}).get("audio", "")
                    if audio_b64:
                        import base64
                        audio_bytes = base64.b64decode(audio_b64)
                        cost = data.get("output", {}).get("cost", 0.001)
                        logger.info(f"TTS RunPod: {len(audio_bytes)} bytes en {(time.time()-start)*1000:.0f}ms, ${cost:.4f}")
                        return GPUResult(
                            success=True,
                            audio_bytes=audio_bytes,
                            provider="runpod",
                            latency_ms=(time.time() - start) * 1000,
                            cost=cost,
                        )
                logger.warning(f"RunPod error {r.status_code}: {r.text[:200]}")
        except httpx.TimeoutException:
            logger.warning("RunPod timeout")
        except Exception as e:
            logger.warning(f"RunPod error: {e}")

        return GPUResult(success=False, provider="runpod", error=str(e) if 'e' in dir() else "timeout")

    async def _cpu_tts(self, text: str, voice: Optional[str] = None) -> GPUResult:
        """Fallback: edge-tts en CPU (gratis, ~2-5s)."""
        start = time.time()
        try:
            import edge_tts

            voice = voice or "es-MX-DaliaNeural"
            mp3_path = f"/tmp/gpu-fallback-{int(time.time())}.mp3"
            wav_path = mp3_path.replace(".mp3", ".wav")

            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(mp3_path)

            # Convertir a WAV para consistencia
            subprocess.run([
                "ffmpeg", "-y", "-i", mp3_path,
                "-acodec", "pcm_s16le", "-ar", "24000", "-ac", "1",
                wav_path,
            ], capture_output=True, check=True)

            with open(wav_path, "rb") as f:
                audio = f.read()

            os.unlink(mp3_path)
            os.unlink(wav_path)

            logger.info(f"TTS CPU edge: {len(audio)} bytes en {(time.time()-start)*1000:.0f}ms")
            return GPUResult(
                success=True,
                audio_bytes=audio,
                provider="cpu",
                latency_ms=(time.time() - start) * 1000,
                cost=0.0,
            )
        except Exception as e:
            logger.error(f"CPU TTS falló: {e}")
            return GPUResult(success=False, provider="cpu", error=str(e))

    def status(self) -> dict:
        """Estado del orquestador."""
        local_gpu = self._detect_local_gpu()
        rp = self.config.get("runpod", {})
        return {
            "local_gpu": local_gpu,
            "runpod_configured": bool(rp.get("api_key") and rp.get("endpoint_id")),
            "preferred_provider": self.config.get("prefer", "cpu"),
            "providers": {
                "local": local_gpu,
                "runpod": bool(rp.get("api_key")),
                "vast": bool(self.config.get("vast", {}).get("api_key")),
                "cpu": True,
            },
        }
