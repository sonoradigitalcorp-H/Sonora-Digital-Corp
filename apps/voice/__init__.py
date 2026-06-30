"""
JARVIS Voice Module v2.0
Enhanced voice interface with wake word, STT (Whisper), TTS (edge-tts + queue).
"""

from .stt import list_microphones, transcribe, transcribe_bytes
from .tts import TTSEngine, play_audio, speak
from .wake_word import WakeWordDetector

__all__ = [
    "WakeWordDetector",
    "transcribe", "transcribe_bytes", "list_microphones",
    "speak", "play_audio", "TTSEngine",
]
