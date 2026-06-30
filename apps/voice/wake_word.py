"""
JARVIS Wake Word Detection
"Hey JARVIS" / "Oye JARVIS" detection using browser Web Speech API
and Python fallback with keyword spotting.
"""

import logging
import re
import threading
import time
from collections.abc import Callable

log = logging.getLogger("jarvis.voice.wake")


class WakeWordDetector:
    """
    Wake word detector for JARVIS.
    
    In browser mode, the Web Speech API handles detection.
    In Python mode, uses simple keyword spotting with regex.
    """

    WAKE_WORDS = [
        r"\bhey\s+jarvis\b",
        r"\bhey\s+jarv\b",
        r"\boye\s+jarvis\b",
        r"\boye\s+jarv\b",
        r"\bjarvis\b",
    ]

    def __init__(self, sensitivity: float = 0.5):
        self.sensitivity = sensitivity
        self._listening = False
        self._thread: threading.Thread | None = None
        self._on_wake: Callable | None = None
        self._last_trigger: float = 0
        self._cooldown = 2.0  # seconds between triggers

    @property
    def listening(self) -> bool:
        return self._listening

    def on_wake(self, callback: Callable):
        """Register callback for when wake word is detected."""
        self._on_wake = callback

    def detect(self, text: str) -> bool:
        """Check if wake word is present in text. Returns True if detected."""
        text_lower = text.lower().strip()

        for pattern in self.WAKE_WORDS:
            if re.search(pattern, text_lower):
                now = time.time()
                if now - self._last_trigger >= self._cooldown:
                    self._last_trigger = now
                    log.info(f"Wake word detected: '{text}' (matched: {pattern})")
                    if self._on_wake:
                        self._on_wake()
                    return True
        return False

    def start_background_listening(self):
        """
        Start background audio capture for wake word detection.
        Uses PyAudio + simple VAD to detect speech, then checks for wake word.
        Note: For production, use browser-based detection via Web Speech API.
        """
        if self._listening:
            return

        self._listening = True
        self._thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._thread.start()
        log.info("Wake word detector started (background mode)")

    def stop(self):
        """Stop wake word detection."""
        self._listening = False
        if self._thread:
            self._thread.join(timeout=2)
        log.info("Wake word detector stopped")

    def _listen_loop(self):
        """Background loop for audio capture and wake word detection."""
        try:
            
            import speech_recognition as sr

            recognizer = sr.Recognizer()
            mic = sr.Microphone()

            with mic as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)

            while self._listening:
                try:
                    with mic as source:
                        audio = recognizer.listen(source, timeout=1, phrase_time_limit=3)
                    
                    try:
                        text = recognizer.recognize_google(audio, language="es-MX")
                        if self.detect(text):
                            log.info(f"Heard: '{text}'")
                    except sr.UnknownValueError:
                        pass
                    except sr.RequestError:
                        pass
                except sr.WaitTimeoutError:
                    pass
                except Exception as e:
                    log.warning(f"Audio capture error: {e}")
                    time.sleep(0.5)

        except ImportError:
            log.warning("PyAudio/SpeechRecognition not available. Wake word background mode disabled.")
        except Exception as e:
            log.warning(f"Wake word listener error: {e}")
        finally:
            self._listening = False


# Singleton instance
_detector: WakeWordDetector | None = None


def get_detector() -> WakeWordDetector:
    """Get or create the global wake word detector."""
    global _detector
    if _detector is None:
        _detector = WakeWordDetector()
    return _detector


def detect_wake_word(text: str) -> bool:
    """Check if text contains wake word. Convenience function."""
    return get_detector().detect(text)
