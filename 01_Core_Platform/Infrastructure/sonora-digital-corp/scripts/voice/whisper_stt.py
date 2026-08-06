"""Whisper STT — Speech to Text via Whisper (transformers).
On-demand: se carga solo cuando hay petición, se libera después.
Usage: python3 -m ops.voice.whisper_stt <audio.wav>
"""
import sys
import json
import time
import tempfile
from pathlib import Path


def transcribe(audio_path: str) -> dict:
    """Transcribe audio file to text using Whisper."""
    t0 = time.time()
    result = {"text": "", "error": None, "elapsed": 0}

    try:
        from transformers import pipeline

        pipe = pipeline(
            "automatic-speech-recognition",
            model="openai/whisper-tiny",
            device=-1,
        )
        output = pipe(audio_path, return_timestamps=True)
        result["text"] = output.get("text", "").strip()
    except Exception as e:
        result["error"] = str(e)

    result["elapsed"] = round(time.time() - t0, 2)
    return result


def transcribe_bytes(audio_bytes: bytes) -> dict:
    """Transcribe from raw bytes."""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        f.write(audio_bytes)
        tmp_path = f.name
    try:
        result = transcribe(tmp_path)
    finally:
        Path(tmp_path).unlink(missing_ok=True)
    return result


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: python3 -m ops.voice.whisper_stt <audio.wav>"}))
        sys.exit(1)

    result = transcribe(sys.argv[1])
    print(json.dumps(result, indent=2))
