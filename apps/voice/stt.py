"""
JARVIS Speech-to-Text Module
Whisper-based STT with VAD (Voice Activity Detection) and multiple fallbacks.
"""

import os
import io
import logging
import tempfile
from typing import Optional

log = logging.getLogger("jarvis.voice.stt")

AUDIO_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cache", "voice")
os.makedirs(AUDIO_DIR, exist_ok=True)

# ---------- Whisper STT ----------

_whisper_model = None


def _get_whisper_model(model_size: str = "base"):
    """Lazy-load Whisper model."""
    global _whisper_model
    if _whisper_model is None:
        try:
            from faster_whisper import WhisperModel
            log.info(f"Loading Whisper model '{model_size}'...")
            _whisper_model = WhisperModel(model_size, device="cpu", compute_type="int8")
            log.info("Whisper model loaded")
        except ImportError:
            log.warning("faster-whisper not installed")
            return None
        except Exception as e:
            log.warning(f"Could not load Whisper model: {e}")
            return None
    return _whisper_model


def transcribe(audio_path: str, language: Optional[str] = None) -> str:
    """
    Transcribe audio file to text using Whisper (preferred) or fallback.
    
    Args:
        audio_path: Path to audio file (WAV, MP3, etc.)
        language: Language code (e.g., 'es', 'en'). Auto-detect if None.
    
    Returns:
        Transcribed text
    """
    if not os.path.exists(audio_path):
        log.warning(f"Audio file not found: {audio_path}")
        return ""

    # Try faster-whisper first
    model = _get_whisper_model()
    if model:
        try:
            segments, info = model.transcribe(
                audio_path,
                beam_size=5,
                language=language,
                vad_filter=True,
                vad_parameters=dict(min_silence_duration_ms=500)
            )
            text = " ".join(s.text for s in segments)
            log.info(f"Whisper STT ({info.language}, {info.duration:.1f}s): {text[:60]}...")
            return text
        except Exception as e:
            log.warning(f"Whisper transcription failed: {e}")

    # Fallback: speech_recognition
    return _fallback_stt(audio_path)


def _fallback_stt(audio_path: str) -> str:
    """Fallback using speech_recognition (google/sphinx)."""
    try:
        import speech_recognition as sr
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_path) as source:
            audio = recognizer.record(source)

        # Try Google first (requires internet)
        try:
            text = recognizer.recognize_google(audio, language="es-MX")
            return text
        except (sr.UnknownValueError, sr.RequestError):
            pass

        # Fallback to Sphinx (offline, less accurate)
        try:
            text = recognizer.recognize_sphinx(audio, language="es-MX")
            return text
        except Exception:
            return "[STT no disponible]"

    except ImportError:
        return "[STT no disponible: speech_recognition no instalado]"
    except Exception as e:
        log.warning(f"Fallback STT error: {e}")
        return "[STT error]"


def transcribe_bytes(audio_bytes: bytes, sample_rate: int = 16000) -> str:
    """
    Transcribe from raw PCM bytes (e.g., from browser Web Speech API).
    
    Args:
        audio_bytes: Raw PCM audio data
        sample_rate: Sample rate in Hz
    
    Returns:
        Transcribed text
    """
    tmp_path = os.path.join(AUDIO_DIR, "input_stream.wav")
    try:
        import wave
        import struct
        with wave.open(tmp_path, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(audio_bytes)
        return transcribe(tmp_path)
    except Exception as e:
        log.warning(f"Transcribe bytes error: {e}")
        return ""


def transcribe_stream(audio_generator, language: Optional[str] = None):
    """
    Transcribe a stream of audio chunks.
    Yields interim and final results.
    
    Args:
        audio_generator: Generator yielding audio chunks (bytes)
        language: Language code
    
    Yields:
        dict with {"text": str, "final": bool}
    """
    model = _get_whisper_model()
    if not model:
        yield {"text": "[STT no disponible]", "final": True}
        return

    buffer = b""
    for chunk in audio_generator:
        buffer += chunk
        if len(buffer) >= 16000 * 2 * 2:  # ~2 seconds of audio
            tmp = os.path.join(AUDIO_DIR, "stream_chunk.wav")
            try:
                import wave
                with wave.open(tmp, 'wb') as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(16000)
                    wf.writeframes(buffer)

                segments, _ = model.transcribe(tmp, language=language, vad_filter=True)
                text = " ".join(s.text for s in segments)
                if text.strip():
                    yield {"text": text, "final": False}
            except Exception:
                pass
            buffer = b""

    # Process remaining buffer
    if buffer:
        tmp = os.path.join(AUDIO_DIR, "stream_final.wav")
        try:
            import wave
            with wave.open(tmp, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(16000)
                wf.writeframes(buffer)

            segments, info = model.transcribe(tmp, language=language, vad_filter=True)
            text = " ".join(s.text for s in segments)
            if text.strip():
                yield {"text": text, "final": True}
        except Exception:
            pass


def list_microphones():
    """List available microphones for voice input selection."""
    try:
        import pyaudio
        p = pyaudio.PyAudio()
        devices = []
        for i in range(p.get_device_count()):
            dev = p.get_device_info_by_index(i)
            if dev['maxInputChannels'] > 0:
                devices.append({
                    "index": i,
                    "name": dev['name'],
                    "channels": dev['maxInputChannels'],
                    "sample_rate": int(dev['defaultSampleRate']),
                })
                log.info(f"Mic [{i}] {dev['name']} ({dev['maxInputChannels']}ch, {int(dev['defaultSampleRate'])}Hz)")
        p.terminate()
        return devices
    except ImportError:
        log.warning("PyAudio not installed")
        return []
    except Exception as e:
        log.warning(f"Error listing microphones: {e}")
        return []
