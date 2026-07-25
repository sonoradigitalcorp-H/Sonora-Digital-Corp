"""LLM integration for Agent Galaxy backend.

Primary: DeepSeek V4 Flash via OpenRouter
Fallback: OpenHermes / free tier models
Follows the multi-provider fallback pattern from llm_mcp.py.
"""

import json
import logging
import os
import time
from typing import Optional

import httpx

log = logging.getLogger("galaxy.llm")

LLM_CONFIG = {
    "primary": {
        "provider": "openrouter",
        "model": "deepseek/deepseek-chat-v4-flash",
        "api_key_env": "OPENCODE_GO_API_KEY",
    },
    "fallback": {
        "provider": "openrouter",
        "model": "huggingfaceh4/zephyr-7b-beta",
        "api_key_env": "OPENCODE_GO_API_KEY",
    },
}

OPENROUTER_BASE_URL = os.getenv("OPENROUTER_URL", "https://openrouter.ai/api/v1")

SYSTEM_PROMPT = (
    "Eres un agente de Sonora Digital Corp. Responde en español mexicano, "
    "cálido y profesional. Ayudas a los usuarios a navegar y configurar "
    "su galaxia de agentes inteligentes."
)


def _get_api_key() -> str:
    """Retrieve the OpenRouter API key from environment."""
    return os.getenv("OPENCODE_GO_API_KEY", os.getenv("OPENROUTER_API_KEY", ""))


def _build_headers() -> dict:
    """Build HTTP headers for OpenRouter API."""
    api_key = _get_api_key()
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://sonoradigitalcorp.com",
        "X-Title": "Agent Galaxy Backend",
    }


async def chat_completion(
    messages: list[dict],
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 1024,
    use_fallback: bool = False,
) -> dict:
    """Execute a chat completion with automatic fallback.

    Args:
        messages: List of {role, content} message dicts.
        model: Override model identifier.
        temperature: Sampling temperature (0-2).
        max_tokens: Maximum tokens in the response.
        use_fallback: Force use of the fallback model.

    Returns:
        dict with keys: text, model, provider, usage, cost, elapsed.
        On failure: error key is present.
    """
    configs = [LLM_CONFIG["fallback"]] if use_fallback else [LLM_CONFIG["primary"], LLM_CONFIG["fallback"]]
    api_key = _get_api_key()
    last_error = None

    for cfg in configs:
        model_to_use = model or cfg["model"]
        url = f"{OPENROUTER_BASE_URL}/chat/completions"
        payload = {
            "model": model_to_use,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        headers = _build_headers()

        if not api_key:
            log.warning(f"No API key for {cfg['provider']}, skipping")
            last_error = "No API key configured"
            continue

        try:
            t0 = time.time()
            async with httpx.AsyncClient(timeout=120) as client:
                resp = await client.post(url, json=payload, headers=headers)
                elapsed = time.time() - t0

            if resp.status_code != 200:
                err_body = resp.text[:500]
                log.warning(f"LLM HTTP {resp.status_code} ({cfg['provider']}): {err_body}")
                last_error = f"HTTP {resp.status_code}: {err_body[:200]}"
                continue

            data = resp.json()
            if "error" in data:
                last_error = f"{cfg['provider']}: {data['error']}"
                log.warning(last_error)
                continue

            choice = data.get("choices", [{}])[0]
            msg = choice.get("message", {})
            text = msg.get("content", "") or msg.get("reasoning_content", "")
            usage = data.get("usage", {})
            prompt_tok = usage.get("prompt_tokens", 0) or 0
            completion_tok = usage.get("completion_tokens", 0) or 0

            cost = 0.0
            if "flash" not in model_to_use.lower():
                cost = (prompt_tok + completion_tok) * 0.0001 / 1000

            log.info(
                f"LLM OK | provider={cfg['provider']} model={model_to_use} "
                f"tokens={prompt_tok}+{completion_tok} cost=${cost:.6f} elapsed={elapsed:.1f}s"
            )

            return {
                "text": text,
                "model": model_to_use,
                "provider": cfg["provider"],
                "usage": usage,
                "cost": round(cost, 6),
                "elapsed": round(elapsed, 2),
            }

        except httpx.TimeoutException:
            last_error = f"{cfg['provider']}: timeout"
            log.warning(last_error)
            continue
        except Exception as e:
            last_error = f"{cfg['provider']}: {str(e)}"
            log.warning(last_error)
            continue

    return {
        "error": last_error or "All LLM providers failed",
        "text": "",
        "model": "",
        "provider": "none",
        "usage": {},
        "cost": 0.0,
        "elapsed": 0.0,
    }


async def simple_chat(
    user_message: str,
    system_prompt: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 1024,
) -> dict:
    """Convenience wrapper for single-turn chat.

    Args:
        user_message: The user's message text.
        system_prompt: Optional override system prompt.
        temperature: Sampling temperature.
        max_tokens: Maximum response tokens.

    Returns:
        Same dict structure as chat_completion.
    """
    messages = [
        {"role": "system", "content": system_prompt or SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]
    return await chat_completion(messages, temperature=temperature, max_tokens=max_tokens)
