import base64
import logging
import os
from collections.abc import AsyncGenerator

from ..bridges import stt as stt_bridge
from ..bridges import tts as tts_bridge
from .chat_engine import ChatEngine

log = logging.getLogger("abe.voice")


class VoicePipeline:
    def __init__(self, chat_engine: ChatEngine):
        self.chat = chat_engine
        self._buffers: dict[str, bytes] = {}

    async def process_chunk(
        self, audio_b64: str, session_id: str = None, sample_rate: int = 16000, final: bool = False
    ) -> dict:
        audio_bytes = base64.b64decode(audio_b64)
        if session_id not in self._buffers:
            self._buffers[session_id or "_default"] = b""
        buf_id = session_id or "_default"
        self._buffers[buf_id] += audio_bytes

        if not final:
            return {"text": "", "final": False, "session_id": session_id}

        full_audio = self._buffers.pop(buf_id, b"")
        if not full_audio:
            return {"text": "", "final": True, "session_id": session_id}

        transcript = stt_bridge.transcribe_bytes(full_audio, sample_rate)
        if not transcript:
            return {"text": "", "final": True, "session_id": session_id}

        response = await self.chat.process(transcript, session_id=session_id)
        response_text = response.get("text", "")

        audio_path = tts_bridge.speak(response_text, lang="es")
        audio_b64 = ""
        if audio_path and os.path.exists(audio_path):
            with open(audio_path, "rb") as f:
                audio_b64 = base64.b64encode(f.read()).decode()

        return {
            "text": transcript,
            "response": response_text,
            "audio": audio_b64,
            "session_id": response.get("session_id", session_id),
            "final": True,
            "intent": response.get("intent"),
        }

    async def stream_process(self, session_id: str) -> AsyncGenerator[dict, None]:
        pass
