"""
JARVIS Voice Module v2.0
Enhanced voice interface with wake word, STT (Whisper), TTS (edge-tts + queue).
"""

from .wake_word import WakeWordDetector
from .stt import transcribe, transcribe_bytes, list_microphones
from .tts import speak, play_audio, TTSEngine

__all__ = [
    "WakeWordDetector",
    "transcribe", "transcribe_bytes", "list_microphones",
    "speak", "play_audio", "TTSEngine",
]
