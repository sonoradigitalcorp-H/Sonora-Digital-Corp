import os
import logging

from fastapi import APIRouter, HTTPException

router = APIRouter()
log = logging.getLogger("jarvis.webui.voice")


@router.post("/api/voice/transcribe")
async def voice_transcribe(data: dict):
    import base64

    audio_b64 = data.get("audio", "")
    if not audio_b64:
        raise HTTPException(status_code=400, detail="No audio data")
    try:
        audio_bytes = base64.b64decode(audio_b64)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid base64 audio")
    try:
        from voice.stt import transcribe_bytes

        text = transcribe_bytes(audio_bytes, data.get("sample_rate", 16000))
        return {"text": text, "confidence": 0.8 if text else 0.0}
    except Exception as e:
        log.warning(f"Voice transcribe error: {e}")
        return {"text": "", "confidence": 0.0, "error": str(e)}


@router.post("/api/voice/speak")
async def voice_speak(data: dict):
    text = data.get("text", "")
    lang = data.get("lang", "es")
    if not text:
        raise HTTPException(status_code=400, detail="No text provided")
    try:
        from voice.tts import speak

        path = speak(text, lang=lang)
        if path and os.path.exists(path):
            import mimetypes
            from fastapi.responses import FileResponse

            media_type, _ = mimetypes.guess_type(path)
            return FileResponse(
                path,
                media_type=media_type or "audio/wav",
                filename=os.path.basename(path),
            )
        return {"error": "TTS failed", "text": text}
    except Exception as e:
        log.warning(f"Voice speak error: {e}")
        return {"error": str(e)}


@router.post("/api/voice/detect-wake")
async def voice_detect_wake(data: dict):
    text = data.get("text", "")
    try:
        from voice.wake_word import detect_wake_word

        return {"detected": detect_wake_word(text), "text": text}
    except Exception as e:
        return {"detected": False, "text": text, "error": str(e)}


@router.get("/api/voice/status")
async def voice_status():
    try:
        from voice.stt import _get_whisper_model

        model = _get_whisper_model()
        return {
            "whisper_available": model is not None,
            "wake_word_available": True,
            "tts_available": True,
        }
    except Exception:
        return {
            "whisper_available": False,
            "wake_word_available": True,
            "tts_available": False,
        }
