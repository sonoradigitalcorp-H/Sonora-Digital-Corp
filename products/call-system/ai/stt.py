import os
import wave
import io
import numpy as np

WHISPER_MODEL = None


def get_whisper():
    global WHISPER_MODEL
    if WHISPER_MODEL is None:
        from faster_whisper import WhisperModel
        WHISPER_MODEL = WhisperModel("base", device="cpu", compute_type="int8")
    return WHISPER_MODEL


def transcribe_bytes(audio_bytes, sample_rate=16000):
    model = get_whisper()
    audio_np = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
    segments, info = model.transcribe(audio_np, beam_size=1, language="es")
    text = " ".join(seg.text for seg in segments)
    return text.strip()
