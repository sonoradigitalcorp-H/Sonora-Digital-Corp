import logging

log = logging.getLogger("abe.bridge.tts")


def speak(text: str, lang: str = "es", voice: str | None = None) -> str | None:
    try:
        from voice.tts import speak as _speak
        return _speak(text, lang, voice)
    except ImportError:
        log.warning("voice.tts not available")
        return None
    except Exception as e:
        log.warning(f"TTS error: {e}")
        return None
