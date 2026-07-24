import json
import logging
import os
from pathlib import Path
from typing import Optional

import httpx

logger = logging.getLogger("aztrotech.llm")

OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY", "")
LLM_MODEL = os.environ.get("LLM_MODEL", "nvidia/nemotron-3-nano-30b-a3b:free")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

PERSONA_FILE = Path(__file__).resolve().parent.parent.parent.parent / "prompt.md"


def _load_persona() -> str:
    if PERSONA_FILE.exists():
        with open(PERSONA_FILE) as f:
            return f.read().strip()
    return "Eres Mystic, asistente de AztroTech. Responde en español, directa y profesional."


PERSONA = _load_persona()

SYSTEM_PROMPT = (
    PERSONA
    + "\n\nEres Mystic, asesora de AztroTech. Respondes en español, máximo 3 oraciones, directa y cálida."
)


async def ask_llm(messages: list[dict], model: Optional[str] = None) -> Optional[str]:
    if not OPENROUTER_KEY:
        logger.warning("OPENROUTER_API_KEY not set")
        return None

    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model or LLM_MODEL,
        "messages": messages,
        "max_tokens": 300,
        "temperature": 0.7,
    }
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(OPENROUTER_URL, headers=headers, json=payload)
            if r.status_code == 200:
                return r.json()["choices"][0]["message"]["content"]
            logger.warning(f"LLM {r.status_code}: {r.text[:100]}")
    except Exception as e:
        logger.error(f"LLM error: {e}")
    return None


def build_conversation(history: list[dict], new_text: str) -> list[dict]:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for entry in history[-8:]:
        messages.append(entry)
    messages.append({"role": "user", "content": new_text})
    return messages
