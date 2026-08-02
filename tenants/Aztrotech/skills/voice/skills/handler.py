"""voice handler — Voice Clone
Síntesis de voz con Qwen3-TTS.
"""
import os
import httpx
from typing import Any

TTS_ENDPOINT = os.getenv("TTS_ENDPOINT", "http://localhost:8765")


async def execute(context: Any) -> dict:
    input_data = context if isinstance(context, dict) else {}
    action = input_data.get("action", "synthesize")

    if action == "synthesize":
        text = input_data.get("text", "")
        if not text:
            return {"action": "synthesize", "error": "Text required"}
        output = input_data.get("output", f"/tmp/tts-{hash(text)}.wav")
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(f"{TTS_ENDPOINT}/tts", json={"text": text, "voice": "cesar", "output": output})
            resp.raise_for_status()
        return {"action": "synthesize", "text": text, "output": output}

    return {"action": action, "error": f"Unknown action: {action}"}
