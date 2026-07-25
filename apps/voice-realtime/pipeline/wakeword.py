"""
Wake Word Detector — openWakeWord para "Hey Jarvis".

Escucha en segundo plano y detecta la frase "hey jarvis" usando openWakeWord.
Cuando se detecta, activa el pipeline de voz completo.

Uso:
    detector = WakeWordDetector()
    await detector.start()  # empieza a escuchar
    result = await detector.detect()  # espera hasta detectar "hey jarvis"
"""

import asyncio
import logging
import numpy as np
from typing import Optional, Callable, Awaitable

logger = logging.getLogger("voice-realtime.wakeword")

# Umbral de confianza para considerar "detectado"
# openWakeWord devuelve scores 0-1, >0.5 es confiable
WAKE_THRESHOLD = 0.5
SAMPLE_RATE = 16000
CHUNK_SIZE = 1600  # 100ms a 16kHz


class WakeWordDetector:
    """
    Detector de wake word "Hey Jarvis" usando openWakeWord.
    
    Recibe chunks de audio PCM16 y notifica cuando detecta la frase.
    """

    def __init__(self, threshold: float = WAKE_THRESHOLD):
        self.threshold = threshold
        self._model = None
        self._callback: Optional[Callable[[str, float], Awaitable[None]]] = None

    def _load(self):
        """Carga el modelo openWakeWord (lazy)."""
        if self._model is not None:
            return
        try:
            from openwakeword.model import Model
            self._model = Model()
            logger.info("WakeWord model loaded (openWakeWord) ✓")
            logger.info(f"  Clases: {list(self._model.prediction_buffer.keys())}")
        except Exception as e:
            logger.error(f"Error loading openWakeWord: {e}")
            raise

    def process_chunk(self, audio_chunk: bytes) -> Optional[dict]:
        """
        Procesa un chunk de audio PCM16 (16kHz, mono, S16LE).
        
        Args:
            audio_chunk: bytes de audio PCM16
            
        Returns:
            dict con {"detected": bool, "keyword": str, "score": float}
            o None si no hay detección
        """
        self._load()
        
        # Convertir PCM16 a float32
        samples = np.frombuffer(audio_chunk, dtype=np.int16).astype(np.float32) / 32768.0
        
        # Predecir
        prediction = self._model.predict(samples)
        
        # Buscar la keyword con mayor score
        best_keyword = None
        best_score = 0.0
        
        for keyword, score in prediction.items():
            if score > best_score and score > self.threshold:
                best_keyword = keyword
                best_score = score
        
        if best_keyword:
            logger.info(f"🔊 Wake word detected: '{best_keyword}' (score={best_score:.3f})")
            return {
                "detected": True,
                "keyword": best_keyword,
                "score": float(best_score),
            }
        
        return None

    def reset(self):
        """Resetea el buffer de predicción."""
        if self._model:
            self._model.reset()

    def set_callback(self, callback: Callable[[str, float], Awaitable[None]]):
        """Registra callback que se llama cuando se detecta wake word."""
        self._callback = callback
