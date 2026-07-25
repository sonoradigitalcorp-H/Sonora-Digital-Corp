import asyncio
import io
import struct
from typing import Optional

import numpy as np
import whisper

MODEL = None
MODEL_LOCK = asyncio.Lock()

SAMPLE_RATE = 16000

def get_model():
    global MODEL
    if MODEL is None:
        MODEL = whisper.load_model("base")
    return MODEL


def transcribe_sync(audio_bytes: bytes, language: Optional[str] = "es") -> dict:
    model = get_model()
    samples = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
    result = model.transcribe(samples, language=language, fp16=False)
    return {
        "text": result["text"].strip(),
        "segments": [
            {"start": s["start"], "end": s["end"], "text": s["text"].strip()}
            for s in result["segments"]
        ],
        "language": result.get("language", language),
    }


async def transcribe(audio_bytes: bytes, language: Optional[str] = "es") -> dict:
    async with MODEL_LOCK:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, transcribe_sync, audio_bytes, language)
