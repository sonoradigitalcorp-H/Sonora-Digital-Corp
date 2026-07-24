import sys
import json
import logging
from pathlib import Path
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

BASE = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE))

from tenants.aztrotech.skills.rag.retriever import retrieve
from tenants.aztrotech.skills.voice.tts import TTS
from tenants.aztrotech.skills.storage.minio_store import save_photo, save_audio, save_document, save_file
from tenants.aztrotech.skills.image.fal_gen import generate_image, generate_character, face_swap
from tenants.aztrotech.skills.whatsapp.wacli_mcp import send_whatsapp, get_messages

mcp = FastMCP("aztrotech-cesar-dt", port=18990)

LLM_API_KEY = "sk-8dX1i04JKc4T4beJwjuPoIESLZPqwyMpupBHLKCunfHF6U7Lq5L2A17J6xAf6Ve8"
CESAR_PHONE = "526621072254"
FAL_KEY = "f8be3dbb-ae16-4562-8f4d-6ae8aa3215ac:f1b8ddaff0bbdda7361ab6a400de27c4"
_tts = None
_persona = None


def load_persona() -> str:
    global _persona
    if _persona is None:
        pf = BASE / "tenants" / "aztrotech" / "prompt-cesar.md"
        if pf.exists():
            _persona = pf.read_text(encoding="utf-8")
        else:
            _persona = "Eres César Holguín, fundador de AztroTech."
    return _persona


@mcp.tool()
async def chat(query: str) -> str:
    persona = load_persona()
    rag_context = await retrieve(query)
    system = f"{persona}\n\n{rag_context}" if rag_context else persona

    headers = {
        "Authorization": f"Bearer {LLM_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "deepseek-v4-flash",
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": query},
        ],
        "max_tokens": 4096,
        "temperature": 0.7,
    }

    async with httpx.AsyncClient(timeout=120) as c:
        r = await c.post("https://opencode.ai/zen/go/v1/chat/completions", headers=headers, json=payload)
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"]
        return f"Error: {r.status_code}"


@mcp.tool()
async def speak(text: str) -> bool:
    global _tts
    if _tts is None:
        _tts = TTS()
    audio = await _tts.synthesize(text)
    return audio is not None


@mcp.tool()
async def whatsapp_send(message: str) -> dict:
    return await send_whatsapp(CESAR_PHONE, message)


@mcp.tool()
async def whatsapp_inbox(limit: int = 10) -> list:
    return await get_messages(limit=limit)


@mcp.tool()
async def rag_search(query: str) -> str:
    return await retrieve(query)


@mcp.tool()
async def image_generate(prompt: str) -> dict:
    return await generate_image(prompt)


@mcp.tool()
async def image_character(prompt: str, reference_url: str) -> dict:
    return await generate_character(prompt, reference_url)


@mcp.tool()
async def image_face_swap(target_url: str, face_url: str) -> str:
    return await face_swap(target_url, face_url)


if __name__ == "__main__":
    mcp.run()
