"""realtime-voice handler — Real-Time Voice Pipeline
STT → LLM → TTS pipeline for voice conversations.
"""
import os
import httpx
from typing import Any

STT_ENDPOINT = os.getenv("STT_ENDPOINT", "http://localhost:8766")
TTS_ENDPOINT = os.getenv("TTS_ENDPOINT", "http://localhost:8765")


async def execute(context: Any) -> dict:
    input_data = context if isinstance(context, dict) else {}
    action = input_data.get("action", "process")

    if action == "process":
        audio_path = input_data.get("audio_path", "")
        if not audio_path:
            return {"action": "process", "error": "audio_path required"}

        async with httpx.AsyncClient(timeout=60) as client:
            with open(audio_path, "rb") as f:
                stt_resp = await client.post(f"{STT_ENDPOINT}/stt", files={"file": f}, data={"language": "es"})
                stt_resp.raise_for_status()
                transcript = stt_resp.json().get("text", "")

        response_text = input_data.get("response", f"Procesando: {transcript}")
        output_path = audio_path.replace(".wav", "-response.wav")

        async with httpx.AsyncClient(timeout=120) as client:
            tts_resp = await client.post(f"{TTS_ENDPOINT}/tts", json={"text": response_text, "voice": "cesar", "output": output_path})
            tts_resp.raise_for_status()

        return {"action": "process", "transcript": transcript, "response": response_text, "audio": output_path}

    return {"action": action, "error": f"Unknown action: {action}"}
