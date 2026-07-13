"""OmniVoice MCP Server — Text-to-Speech and Voice Cloning.

Exposes OmniVoice TTS and cloning as native MCP tools for agents.
"""

import json
import os

import httpx

OMNIVOICE_URL = os.getenv("OMNIVOICE_URL", "http://localhost:3900")


async def generate_speech(text: str, voice: str = "default", language: str = "es") -> str:
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{OMNIVOICE_URL}/tts",
            json={"text": text, "voice": voice, "language": language},
            timeout=60,
        )
        return json.dumps(resp.json())


async def clone_voice(audio_url: str, name: str) -> str:
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{OMNIVOICE_URL}/clone",
            json={"audio_url": audio_url, "name": name},
            timeout=120,
        )
        return json.dumps(resp.json())


async def list_voices() -> str:
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{OMNIVOICE_URL}/voices", timeout=10)
        return json.dumps(resp.json())


MCP_TOOLS = {
    "omnivoice_speak": {
        "description": "Generate speech audio from text using OmniVoice TTS",
        "input_schema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text to convert to speech"},
                "voice": {"type": "string", "description": "Voice ID or name", "default": "default"},
                "language": {"type": "string", "description": "Language code", "default": "es"},
            },
            "required": ["text"],
        },
        "handler": lambda args: generate_speech(args["text"], args.get("voice", "default"), args.get("language", "es")),
    },
    "omnivoice_clone": {
        "description": "Clone a voice from an audio sample",
        "input_schema": {
            "type": "object",
            "properties": {
                "audio_url": {"type": "string", "description": "URL of audio sample"},
                "name": {"type": "string", "description": "Name for the cloned voice"},
            },
            "required": ["audio_url", "name"],
        },
        "handler": lambda args: clone_voice(args["audio_url"], args["name"]),
    },
    "omnivoice_list_voices": {
        "description": "List available voices",
        "input_schema": {"type": "object", "properties": {}},
        "handler": lambda _: list_voices(),
    },
}
