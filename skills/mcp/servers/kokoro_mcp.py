"""Kokoro MCP Server — Text-to-Speech via ElevenLabs API (no GPU needed)."""

import json
import os
import httpx

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")  # Rachel default
ELEVENLABS_URL = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"


async def generate_speech(text: str, voice_id: str = "", language: str = "es") -> str:
    if not text:
        return json.dumps({"error": "text is required"})
    if not ELEVENLABS_API_KEY:
        return json.dumps({"error": "ELEVENLABS_API_KEY not configured"})

    try:
        vid = voice_id or ELEVENLABS_VOICE_ID
        headers = {
            "xi-api-key": ELEVENLABS_API_KEY,
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"https://api.elevenlabs.io/v1/text-to-speech/{vid}",
                json={
                    "text": text,
                    "model_id": "eleven_multilingual_v2",
                    "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
                },
                headers=headers,
                timeout=60,
            )
            if resp.status_code != 200:
                return json.dumps({"error": f"ElevenLabs API error: {resp.status_code}", "detail": resp.text})

            audio_url = resp.url  # Streaming URL
            import hashlib
            filename = f"tts_{hashlib.md5(text.encode()).hexdigest()[:8]}.mp3"

            return json.dumps({
                "audio_url": audio_url,
                "filename": filename,
                "format": "mp3",
                "text_length": len(text),
            })
    except Exception as e:
        return json.dumps({"error": str(e)})


async def list_voices() -> str:
    if not ELEVENLABS_API_KEY:
        return json.dumps({"error": "ELEVENLABS_API_KEY not configured"})

    try:
        headers = {"xi-api-key": ELEVENLABS_API_KEY}
        async with httpx.AsyncClient() as client:
            resp = await client.get("https://api.elevenlabs.io/v1/voices", headers=headers, timeout=10)
            return json.dumps(resp.json())
    except Exception as e:
        return json.dumps({"error": str(e)})


MCP_TOOLS = {
    "kokoro_tts": {
        "description": "Generate speech audio from text using ElevenLabs TTS",
        "input_schema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text to convert to speech"},
                "voice_id": {"type": "string", "description": "ElevenLabs voice ID (optional)"},
                "language": {"type": "string", "description": "Language code", "default": "es"},
            },
            "required": ["text"],
        },
        "handler": lambda args: generate_speech(args["text"], args.get("voice_id", ""), args.get("language", "es")),
    },
    "kokoro_list_voices": {
        "description": "List available ElevenLabs voices",
        "input_schema": {"type": "object", "properties": {}},
        "handler": lambda _: list_voices(),
    },
}
