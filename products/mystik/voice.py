import logging
import tempfile
from pathlib import Path
from typing import AsyncGenerator

from products.mystik.config import config

logger = logging.getLogger(__name__)


class MystikVoice:
    def __init__(self):
        self.whisper = None
        self.tts = None
        self._init_models()

    def _init_models(self):
        try:
            from faster_whisper import WhisperModel
            self.whisper = WhisperModel(config.whisper_model, device="cpu", compute_type="int8")
            logger.info("Whisper loaded: %s", config.whisper_model)
        except Exception as e:
            logger.warning("Whisper not available: %s", e)

        try:
            from openvoice import VoiceCloner
            self.tts = VoiceCloner()
            logger.info("OpenVoice loaded")
        except Exception as e:
            logger.warning("OpenVoice not available: %s", e)

    async def transcribe(self, audio_bytes: bytes) -> str:
        if not self.whisper:
            return "(whisper no disponible)"
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(audio_bytes)
            tmp_path = f.name
        try:
            segments, _ = self.whisper.transcribe(tmp_path, language="es")
            return " ".join(seg.text for seg in segments)
        except Exception as e:
            logger.error("Transcription error: %s", e)
            return ""
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    async def speak(self, text: str, voice_profile: str = "default") -> bytes:
        if not self.tts:
            return await self._fallback_tts(text)
        try:
            audio = self.tts.clone_voice(text, voice_profile)
            return audio
        except Exception as e:
            logger.error("TTS error: %s", e)
            return await self._fallback_tts(text)

    async def _fallback_tts(self, text: str) -> bytes:
        try:
            import httpx
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    "http://127.0.0.1:8766/tts",
                    json={"text": text, "voice": "es-MX", "format": "wav"},
                )
                return resp.content
        except Exception:
            return b""

    async def clone_voice(self, audio_sample: bytes, name: str = "mystik") -> str:
        try:
            import httpx
            async with httpx.AsyncClient(timeout=60) as client:
                resp = await client.post(
                    f"{config.omnivoice_url}/profiles",
                    files={"audio": audio_sample},
                    data={"name": name},
                )
                data = resp.json()
                profile_id = data.get("profile_id", "")
                logger.info("Voice cloned: %s -> %s", name, profile_id)
                return profile_id
        except Exception as e:
            logger.error("Voice cloning failed: %s", e)
            return ""


voice = MystikVoice()
