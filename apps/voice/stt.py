import whisper


_model = None


def transcribe(audio_path: str, language: str = "es") -> str:
    global _model
    if _model is None:
        _model = whisper.load_model("base")
    result = _model.transcribe(audio_path, language=language)
    return result["text"].strip()
