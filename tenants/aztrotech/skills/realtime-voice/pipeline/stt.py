import logging
from typing import Optional

logger = logging.getLogger("aztrotech.stt")

_whisper_model = None


def _load_model():
    global _whisper_model
    if _whisper_model is not None:
        return
    try:
        from faster_whisper import WhisperModel
        _whisper_model = WhisperModel("base", device="cpu", compute_type="int8")
        logger.info("Whisper model loaded (base, int8)")
    except ImportError:
        import whisper
        _whisper_model = whisper.load_model("base")
        logger.info("Whisper model loaded (openai-whisper base)")


async def transcribe(audio_bytes: bytes, language: str = "es") -> dict:
    _load_model()
    try:
        import io
        import tempfile
        import wave
        import numpy as np
        import soundfile as sf
        import asyncio

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp_path = tmp.name

        data, sr = sf.read(io.BytesIO(audio_bytes))
        sf.write(tmp_path, data, sr)

        loop = asyncio.get_event_loop()

        if hasattr(_whisper_model, "transcribe"):
            result = await loop.run_in_executor(
                None,
                lambda: _whisper_model.transcribe(
                    tmp_path,
                    language=language,
                    temperature=0.0,
                ),
            )
            segments = list(result.get("segments", []))
            text = " ".join(s.text for s in segments) if segments else ""
        else:
            segments, _ = await loop.run_in_executor(
                None,
                lambda: _whisper_model.transcribe(
                    tmp_path,
                    language=language,
                    beam_size=1,
                ),
            )
            text = " ".join(s.text for s in segments)

        import os
        os.unlink(tmp_path)
        return {"text": text.strip(), "language": language}

    except Exception as e:
        logger.error(f"STT error: {e}")
        return {"text": "", "error": str(e), "language": language}
