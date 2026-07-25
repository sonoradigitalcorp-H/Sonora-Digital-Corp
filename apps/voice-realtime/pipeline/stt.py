"""
Pipeline de Transcripción (STT) con Whisper en streaming.
Soporta entrada por chunks para VAD y detección de silencios.
"""
import asyncio
import io
import struct
import time
import logging
from typing import Optional, AsyncGenerator

import numpy as np

logger = logging.getLogger("voice-realtime.stt")

# ─── Configuración ───
SAMPLE_RATE = 16000
CHUNK_MS = 100          # 100ms por chunk para streaming
CHUNK_SIZE = int(SAMPLE_RATE * CHUNK_MS / 1000)  # 1600 samples
SILENCE_THRESHOLD = 0.02  # umbral RMS para silencio
SILENCE_DURATION_MS = 800  # ms de silencio para considerar "fin de frase"

_MODEL = None
_MODEL_LOCK = asyncio.Lock()


def get_model():
    """Carga el modelo Whisper (lazy, singleton)."""
    global _MODEL
    if _MODEL is None:
        import whisper
        _MODEL = whisper.load_model("base")
        logger.info("Whisper model loaded (base)")
    return _MODEL


def transcribe_sync(audio_bytes: bytes, language: str = "es") -> dict:
    """Transcripción síncrona con Whisper."""
    model = get_model()
    samples = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
    if len(samples) < SAMPLE_RATE * 0.3:  # menos de 300ms
        return {"text": "", "segments": [], "language": language}
    result = model.transcribe(samples, language=language, fp16=False)
    return {
        "text": result["text"].strip(),
        "segments": [
            {"start": s["start"], "end": s["end"], "text": s["text"].strip()}
            for s in result["segments"]
        ],
        "language": result.get("language", language),
    }


async def transcribe(audio_bytes: bytes, language: str = "es") -> dict:
    """Transcripción asíncrona con Whisper (usa executor para no bloquear)."""
    async with _MODEL_LOCK:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, transcribe_sync, audio_bytes, language)


# ─── VAD (Voice Activity Detection) Simple ───

def rms(samples: np.ndarray) -> float:
    """Calcula RMS de una señal de audio."""
    if len(samples) == 0:
        return 0.0
    return float(np.sqrt(np.mean(samples.astype(np.float32) ** 2)))


def is_speech(chunk: bytes, threshold: float = SILENCE_THRESHOLD) -> bool:
    """Detecta si un chunk de audio PCM16 contiene voz."""
    samples = np.frombuffer(chunk, dtype=np.int16).astype(np.float32) / 32768.0
    return rms(samples) > threshold


class VoiceActivityDetector:
    """
    Detector de actividad de voz con timeout de silencio.
    Ideal para barge-in y detección de fin de frase.
    """
    def __init__(self, silence_timeout_ms: int = SILENCE_DURATION_MS):
        self.silence_timeout_ms = silence_timeout_ms
        self._last_speech_time = 0.0
        self._speaking = False

    def process_chunk(self, chunk: bytes, timestamp: float) -> dict:
        """
        Procesa un chunk de audio.
        Returns: {"speaking": bool, "utterance_end": bool}
        """
        speaking = is_speech(chunk)

        if speaking:
            self._last_speech_time = timestamp
            if not self._speaking:
                self._speaking = True
                return {"speaking": True, "utterance_end": False, "speech_start": True}
            return {"speaking": True, "utterance_end": False}

        # Silencio
        if self._speaking:
            elapsed_ms = (timestamp - self._last_speech_time) * 1000
            if elapsed_ms > self.silence_timeout_ms:
                self._speaking = False
                return {"speaking": False, "utterance_end": True, "speech_end": True}

        return {"speaking": False, "utterance_end": False}

    def reset(self):
        self._last_speech_time = 0.0
        self._speaking = False
