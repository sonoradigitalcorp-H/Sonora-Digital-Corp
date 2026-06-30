import time
from typing import Any

from src.core.agents.agent_base import (
    AgentBase,
    error_response,
    match_keywords,
    success_response,
)


class VoiceAgent(AgentBase):
    name = "voice"
    description = "Procesamiento de voz (STT/TTS)"
    timeout = 30

    def __init__(self):
        super().__init__()
        self._sessions: dict[str, dict] = {}

    async def run(self, task: str, context: dict = None) -> dict[str, Any]:
        self.log.info(f"Voice task: {task[:100]}...")
        if match_keywords(task, ["transcribe", "escucha", "reconocé"]):
            return self._transcribe(task)
        elif match_keywords(task, ["habla", "speak", "decí", "di:"]):
            return self._speak(task)
        elif match_keywords(task, ["sesión", "session", "start"]):
            return self._start_session(task)
        elif match_keywords(task, ["stop", "end", "termina", "corta"]):
            return self._end_session(task)
        else:
            return self._status()

    def _transcribe(self, task: str) -> dict[str, Any]:
        import re

        match = re.search(r'["\']([^"\']+)["\']', task)
        text_to_transcribe = match.group(1) if match else None
        if text_to_transcribe:
            return success_response(
                self.name,
                task,
                action="mock_transcribe",
                transcription=f"[SIMULATED] {text_to_transcribe}",
                note="Real STT needs audio file path or microphone input",
            )
        try:
            from voice.stt import transcribe

            result = transcribe(task)
            return success_response(
                self.name, task, action="transcribe", transcription=result
            )
        except Exception as e:
            return error_response(self.name, task, str(e), action="transcribe")

    def _speak(self, task: str) -> dict[str, Any]:
        import re

        match = re.search(r'(?:habla|speak|decí|di:)\s*["\']?([^"\']*)["\']?', task)
        text = (match.group(1).strip() if match else task).strip()
        if not text or len(text) < 3:
            return error_response(
                self.name, task, "Dame algo que decir, no te hagas el misterioso"
            )
        try:
            from voice.tts import speak as tts_speak

            tts_speak(text, lang="es")
            return success_response(
                self.name,
                task,
                action="speak",
                text=text,
                message=f"Diciendo: {text[:100]}...",
            )
        except Exception as e:
            return success_response(
                self.name,
                task,
                action="speak_offline",
                text=text,
                note=f"TTS no disponible: {e}",
            )

    def _start_session(self, task: str) -> dict[str, Any]:
        import uuid

        session_id = str(uuid.uuid4())[:8]
        self._sessions[session_id] = {
            "id": session_id,
            "created": time.time(),
            "mode": "voice",
            "messages": [],
            "active": True,
        }
        return success_response(
            self.name, task, action="session_start", session_id=session_id
        )

    def _end_session(self, task: str) -> dict[str, Any]:
        import re

        match = re.search(r"([a-f0-9]{8})", task)
        session_id = match.group(1) if match else None
        if session_id and session_id in self._sessions:
            self._sessions[session_id]["active"] = False
            return success_response(
                self.name,
                task,
                action="session_end",
                session_id=session_id,
                duration=time.time() - self._sessions[session_id]["created"],
            )
        ended = []
        for sid in list(self._sessions.keys()):
            self._sessions[sid]["active"] = False
            ended.append(sid)
        return success_response(self.name, task, action="session_end", ended=len(ended))

    def _status(self) -> dict[str, Any]:
        active = sum(1 for s in self._sessions.values() if s.get("active"))
        return success_response(
            self.name,
            task="status",
            action="status",
            active_sessions=active,
            total_sessions=len(self._sessions),
            capabilities=[
                "STT (Whisper)",
                "TTS (edge-tts/gTTS/espeak)",
                "Wake Word (Hey JARVIS)",
                "Web Speech API",
            ],
        )
