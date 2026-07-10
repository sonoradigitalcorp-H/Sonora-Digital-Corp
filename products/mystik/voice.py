import io
import logging
import tempfile
from pathlib import Path

import edge_tts

from products.mystik.config import config

logger = logging.getLogger(__name__)

MYSTIK_VOICE = "es-MX-DaliaNeural"
MYSTIK_VOICE_SPEED = "+10%"


class MystikVoice:
    def __init__(self):
        self.whisper = None
        self._init_whisper()

    def _init_whisper(self):
        try:
            from faster_whisper import WhisperModel
            self.whisper = WhisperModel(config.whisper_model, device="cpu", compute_type="int8")
            logger.info("Whisper loaded: %s", config.whisper_model)
        except Exception as e:
            logger.warning("Whisper not available, STT desactivado: %s", e)

    async def speak(self, text: str, voice: str = MYSTIK_VOICE) -> bytes:
        try:
            communicate = edge_tts.Communicate(text, voice, rate=MYSTIK_VOICE_SPEED)
            audio = io.BytesIO()
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio.write(chunk["data"])
            return audio.getvalue()
        except Exception as e:
            logger.error("TTS error: %s", e)
            return b""

    async def transcribe(self, audio_bytes: bytes) -> str:
        if not self.whisper:
            return ""
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
            logger.error("Voice cloning via OmniVoice failed: %s", e)
            return ""


voice = MystikVoice()
