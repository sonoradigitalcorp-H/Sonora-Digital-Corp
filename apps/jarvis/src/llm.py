"""
JARVIS LLM Client — Conexión a deepseek-v4-flash via opencode-go / OpenRouter.
Soporta streaming SSE y respuestas completas.
"""

import json
import logging
import os
from pathlib import Path

import requests
from dotenv import load_dotenv
from typing import Optional, Generator, AsyncGenerator
from datetime import datetime, timezone

load_dotenv(Path(__file__).parent.parent.parent / ".env")
load_dotenv(Path.home() / "sdcorp" / ".secrets" / "keys.env")

log = logging.getLogger("jarvis.llm")


def _get_api_key(key_name: str) -> str:
    key = os.environ.get(key_name)
    if key:
        return key
    log.warning(f"{key_name} no seteada en .env, usando placeholder")
    return "sk-placeholder"


# Provider configs (keys via .env, no hardcodeadas)
PROVIDERS = {
    "opencode-go": {
        "base_url": "https://opencode.ai/zen/go/v1",
        "api_key": _get_api_key("OPENCODE_API_KEY"),
        "models": {
            "deepseek-v4-flash": {"context": 32768, "cost_per_1k": 0.0001},
            "deepseek-v4-flash-free": {"context": 8192, "cost_per_1k": 0.0},
        },
        "default_model": "deepseek-v4-flash",
    },
    "openrouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "api_key": _get_api_key("OPENROUTER_API_KEY"),
        "models": {
            "opencode/deepseek-v4-flash-free": {"context": 8192, "cost_per_1k": 0.0},
        },
        "default_model": "opencode/deepseek-v4-flash-free",
    },
}

# Select best available provider
ACTIVE_PROVIDER = "opencode-go"
ACTIVE_MODEL = "deepseek-v4-flash"
BASE_URL = PROVIDERS[ACTIVE_PROVIDER]["base_url"]
API_KEY = PROVIDERS[ACTIVE_PROVIDER]["api_key"]

SYSTEM_PROMPT = """Eres Mystic, la asistente de IA de Sonora Digital Corp.
Creada por Luis Daniel Guerrero Enciso, un emprendedor de Sonora, México.
Luis Daniel es el fundador y CEO de Sonora Digital Corp.
Respondes en español. Máximo 2 oraciones. Directa y clara."""


def chat_completion(
    messages: list,
    model: Optional[str] = None,
    max_tokens: int = 2000,
    temperature: float = 0.7,
    stream: bool = False,
) -> dict:
    """Send a chat completion request to the LLM."""
    url = f"{BASE_URL}/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    body = {
        "model": model or ACTIVE_MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "stream": stream,
    }

    log.info(
        f"LLM request: {len(messages)} messages, model={body['model']}, stream={stream}"
    )

    try:
        resp = requests.post(url, headers=headers, json=body, timeout=60)
        resp.raise_for_status()

        if stream:
            return resp  # Return raw response for streaming

        data = resp.json()

        if "choices" in data and data["choices"]:
            content = data["choices"][0]["message"].get("content", "")
            reasoning = data["choices"][0]["message"].get("reasoning_content", "")
            usage = data.get("usage", {})
            cost = data.get("cost", "N/A")

            log.info(
                f"LLM response: {len(content)} chars, "
                f"{usage.get('total_tokens', '?')} tokens, cost=${cost}"
            )

            return {
                "content": content,
                "reasoning": reasoning,
                "model": data.get("model", model),
                "usage": usage,
                "cost": cost,
                "finish_reason": data["choices"][0].get("finish_reason", "stop"),
            }
        else:
            log.warning(f"LLM unexpected response: {json.dumps(data)[:200]}")
            return {"content": "", "error": "Respuesta inesperada del LLM"}

    except requests.exceptions.Timeout:
        log.error("LLM request timed out")
        return {"content": "", "error": "Timeout del LLM"}
    except requests.exceptions.RequestException as e:
        log.error(f"LLM request failed: {e}")
        return {"content": "", "error": str(e)}


def stream_chat_completion(
    messages: list,
    model: Optional[str] = None,
    max_tokens: int = 4000,
    temperature: float = 0.7,
) -> Generator[str, None, dict]:
    """
    Stream a chat completion from the LLM.
    Yields tokens as they arrive.
    Returns usage stats when done.
    """
    url = f"{BASE_URL}/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    body = {
        "model": model or ACTIVE_MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "stream": True,
        "stream_options": {"include_usage": True},
    }

    log.info(f"LLM stream request: {len(messages)} messages, model={body['model']}")

    try:
        resp = requests.post(url, headers=headers, json=body, timeout=120, stream=True)
        resp.raise_for_status()

        full_content = ""
        usage = {}

        for line in resp.iter_lines(decode_unicode=True):
            if not line or not line.startswith("data: "):
                continue

            data_str = line[6:]  # Remove "data: " prefix
            if data_str.strip() == "[DONE]":
                break

            try:
                chunk = json.loads(data_str)
            except json.JSONDecodeError:
                continue

            # Usage info (sent in final chunk with stream_options)
            if "usage" in chunk:
                usage = chunk["usage"]
                continue

            if "choices" in chunk and chunk["choices"]:
                delta = chunk["choices"][0].get("delta", {})
                token = delta.get("content", "")
                reasoning_token = delta.get("reasoning_content", "")

                if token:
                    full_content += token
                    yield token

                if reasoning_token:
                    # Send reasoning as a special event
                    yield f"__reasoning__:{reasoning_token}"

        yield full_content  # Final yield with full content

        # Return usage as generator return
        return {
            "content": full_content,
            "usage": usage,
            "model": body["model"],
        }

    except requests.exceptions.Timeout:
        log.error("LLM stream timed out")
        return {"error": "timeout"}
    except requests.exceptions.RequestException as e:
        log.error(f"LLM stream failed: {e}")
        return {"error": str(e)}


def ask(prompt: str, system: Optional[str] = None) -> str:
    """Simple convenience function: send a prompt, get text response."""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    result = chat_completion(messages)
    return result.get("content", "")


def list_models() -> list:
    """List available models."""
    models = []
    for provider_name, provider in PROVIDERS.items():
        for model_name, info in provider["models"].items():
            models.append(
                {
                    "provider": provider_name,
                    "model": model_name,
                    "context": info["context"],
                    "free": info["cost_per_1k"] == 0,
                }
            )
    return models


# Test
if __name__ == "__main__":
    result = chat_completion(
        [
            {"role": "system", "content": "Eres JARVIS. Responde en una línea."},
            {"role": "user", "content": "Quien eres?"},
        ]
    )
    log.info(f"JARVIS: {result.get('content', 'error')}")
    log.info(f"Stats: {result.get('usage', {})}")
