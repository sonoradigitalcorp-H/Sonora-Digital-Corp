#!/usr/bin/env python3
"""LLM MCP Server — OpenRouter chat completions as MCP tools [FR5].

Exposes LLM calls as native MCP tools for agents and the ABE assistant.
"""

import json
import os

import httpx

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_URL = os.getenv("OPENROUTER_URL", "https://openrouter.ai/api/v1")
DEFAULT_MODEL = os.getenv("LLM_DEFAULT_MODEL", "openai/gpt-4o-mini")

SYSTEM_PROMPT = """Eres un asistente útil de Sonora Digital Corp. Responde en español, de forma clara y concisa. Cuando no sepas algo, dilo honestamente."""


async def llm_chat(messages: list, model: str = None, temperature: float = 0.7) -> str:
    """Call OpenRouter chat completions API."""
    if not OPENROUTER_API_KEY:
        return json.dumps({"error": "OPENROUTER_API_KEY not configured"})

    payload = {
        "model": model or DEFAULT_MODEL,
        "messages": messages,
        "temperature": temperature,
    }

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{OPENROUTER_URL}/chat/completions",
            json=payload,
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://sonoradigitalcorp.com",
                "X-Title": "Sonora OS Assistant",
            },
            timeout=60,
        )
        data = resp.json()
        if "error" in data:
            return json.dumps({"error": data["error"]})
        choice = data.get("choices", [{}])[0]
        return json.dumps({
            "text": choice.get("message", {}).get("content", ""),
            "model": model or DEFAULT_MODEL,
            "usage": data.get("usage", {}),
        })


async def llm_complete(prompt: str, system: str = None, model: str = None, temperature: float = 0.7) -> str:
    """Single-prompt completion."""
    messages = [
        {"role": "system", "content": system or SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ]
    return await llm_chat(messages, model=model, temperature=temperature)


MCP_TOOLS = {
    "llm_chat": {
        "description": "Call OpenRouter chat completions with a message history",
        "input_schema": {
            "type": "object",
            "properties": {
                "messages": {
                    "type": "array",
                    "description": "List of {role, content} messages",
                },
                "model": {"type": "string", "description": "Model ID (default: openai/gpt-4o-mini)"},
                "temperature": {"type": "number", "description": "Sampling temperature"},
            },
            "required": ["messages"],
        },
        "handler": lambda args: llm_chat(
            args["messages"],
            args.get("model"),
            args.get("temperature", 0.7),
        ),
    },
    "llm_complete": {
        "description": "Generate a completion from a single prompt",
        "input_schema": {
            "type": "object",
            "properties": {
                "prompt": {"type": "string", "description": "User prompt"},
                "system": {"type": "string", "description": "Optional system prompt"},
                "model": {"type": "string", "description": "Model ID"},
                "temperature": {"type": "number", "description": "Sampling temperature"},
            },
            "required": ["prompt"],
        },
        "handler": lambda args: llm_complete(
            args["prompt"],
            args.get("system"),
            args.get("model"),
            args.get("temperature", 0.7),
        ),
    },
}
