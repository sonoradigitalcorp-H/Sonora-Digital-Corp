"""
JARVIS Voice Module v2.0
Enhanced voice interface with wake word, STT (Whisper), TTS (edge-tts + queue).
"""

from .stt import transcribe
from .tts import TTSEngine, play_audio, speak
from .wake_word import WakeWordDetector

__all__ = [
    "WakeWordDetector",
    "transcribe",
    "speak", "play_audio", "TTSEngine",
]
