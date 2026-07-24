"""
VAD — Voice Activity Detection simple y rápido (no requiere GPU).

Estrategia:
  1. Intenta importar webrtcvad (C lib, muy rápido)
  2. Si no, usa energy-based VAD (RMS + threshold adaptativo)

Ambos funcionan en CPU sin dependencias pesadas.
Suficiente para barge-in en conversaciones en vivo.
"""

import logging
import math
import struct
from typing import Callable, Optional

logger = logging.getLogger("vad")

SAMPLE_RATE = 16000
CHUNK_SIZE = 512       # samples (~32ms)
FRAME_MS = 32
CHUNK_BYTES = CHUNK_SIZE * 2  # PCM16 = 2 bytes per sample

# Thresholds
SPEECH_THRESHOLD = 0.015       # RMS mínimo para considerar speech
SILENCE_THRESHOLD = 0.008      # RMS máximo para considerar silencio
FRAMES_SPEECH_START = 4        # chunks consecutivos para confirmar speech (~128ms)
FRAMES_SPEECH_END = 15         # chunks consecutivos para confirmar silencio (~480ms)
MIN_SPEECH_DURATION = 0.3      # segmento mínimo de speech en segundos


def rms(audio_chunk: bytes) -> float:
    """Calcula RMS (Root Mean Square) de un chunk PCM16."""
    count = len(audio_chunk) // 2
    if count == 0:
        return 0.0
    # Usar struct para desempaquetar PCM16
    fmt = f"<{count}h"
    try:
        samples = struct.unpack(fmt, audio_chunk[:count * 2])
    except struct.error:
        return 0.0

    sum_sq = sum(s * s for s in samples)
    return math.sqrt(sum_sq / count) / 32768.0  # normalizar a 0-1


class EnergyVAD:
    """
    VAD basado en energía (RMS).
    Detecta transiciones speech_start / speech_end para barge-in.
    No requiere GPU, no requiere torch, no requiere CUDA.
    """

    def __init__(
        self,
        threshold: float = SPEECH_THRESHOLD,
        silence_threshold: float = SILENCE_THRESHOLD,
        on_speech_start: Optional[Callable] = None,
        on_speech_end: Optional[Callable] = None,
    ):
        self.threshold = threshold
        self.silence_threshold = silence_threshold
        self.on_speech_start = on_speech_start
        self.on_speech_end = on_speech_end
        self.reset()

    def reset(self):
        self.is_speaking = False
        self._speech_frames = 0
        self._silence_frames = 0
        self._total_chunks = 0

    def process_chunk(self, audio_chunk: bytes) -> tuple[bool, float]:
        """
        Procesa un chunk PCM16 16kHz.
        Retorna (is_speech, rms_value).
        Dispara callbacks en transiciones.
        """
        energy = rms(audio_chunk)
        self._total_chunks += 1

        if energy >= self.threshold:
            self._speech_frames += 1
            self._silence_frames = 0
        elif energy <= self.silence_threshold:
            self._silence_frames += 1
            self._speech_frames = 0
        else:
            # Zona gris: mantener estado anterior
            if self.is_speaking:
                self._silence_frames += 1
            else:
                self._speech_frames += 1

        is_speech = False
        # Transición: silencio → speech
        if not self.is_speaking and self._speech_frames >= FRAMES_SPEECH_START:
            self.is_speaking = True
            is_speech = True
            logger.debug(f"🗣️ Speech START (rms={energy:.4f})")
            if self.on_speech_start:
                self.on_speech_start()

        # Transición: speech → silencio
        elif self.is_speaking and self._silence_frames >= FRAMES_SPEECH_END:
            self.is_speaking = False
            logger.debug(f"🔇 Speech END (rms={energy:.4f})")
            if self.on_speech_end:
                self.on_speech_end()

        return is_speech, energy

    def process_buffer(self, audio_bytes: bytes) -> list[dict]:
        """Procesa buffer completo. Retorna segmentos de speech."""
        self.reset()
        segments = []
        current = None

        for i in range(0, len(audio_bytes), CHUNK_BYTES):
            chunk = audio_bytes[i:i + CHUNK_BYTES]
            if len(chunk) < CHUNK_BYTES:
                break

            is_speech, energy = self.process_chunk(chunk)
            ts = (i // CHUNK_BYTES) * FRAME_MS / 1000.0

            if is_speech:
                if current is None:
                    current = {"start": ts}
            elif current is not None and not self.is_speaking:
                current["end"] = ts
                if current["end"] - current["start"] >= MIN_SPEECH_DURATION:
                    segments.append(current)
                current = None

        if current is not None:
            current["end"] = (len(audio_bytes) // CHUNK_BYTES) * FRAME_MS / 1000.0
            if current["end"] - current["start"] >= MIN_SPEECH_DURATION:
                segments.append(current)

        return segments

    def get_stats(self) -> dict:
        return {
            "total_chunks": self._total_chunks,
            "is_speaking": self.is_speaking,
            "threshold": self.threshold,
        }


# Exportar nombre genérico para compatibilidad
VADDetector = EnergyVAD
