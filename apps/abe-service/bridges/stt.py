import logging

log = logging.getLogger("abe.bridge.stt")


def transcribe(audio_path: str, language: str | None = None) -> str:
    try:
        from voice.stt import transcribe as _transcribe
        return _transcribe(audio_path, language)
    except ImportError:
        log.warning("voice.stt not available")
        return ""
    except Exception as e:
        log.warning(f"STT error: {e}")
        return ""


def transcribe_bytes(audio_bytes: bytes, sample_rate: int = 16000) -> str:
    try:
        from voice.stt import transcribe_bytes as _transcribe_bytes
        return _transcribe_bytes(audio_bytes, sample_rate)
    except ImportError:
        log.warning("voice.stt not available")
        return ""
    except Exception as e:
        log.warning(f"STT bytes error: {e}")
        return ""
