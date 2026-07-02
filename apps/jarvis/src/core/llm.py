"""
JARVIS LLM Client — Conexión a deepseek-v4-flash via opencode-go / OpenRouter.
Soporta streaming SSE y respuestas completas.
"""

import json
import logging
import os
import time
from collections.abc import Generator
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent.parent / ".env")
load_dotenv(Path.home() / "sdcorp" / ".secrets" / "keys.env")

log = logging.getLogger("jarvis.llm")

# LangFuse tracing (importado dinámicamente para evitar path issues con guiones)
import importlib.util

_LF_PATH = Path(__file__).resolve().parent.parent.parent.parent.parent / "sonora-enterprise-os" / "scripts" / "instrument-langfuse.py"
if _LF_PATH.exists():
    _spec = importlib.util.spec_from_file_location("instrument_langfuse", str(_LF_PATH))
    _instr = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_instr)
    _tracker = _instr._tracker
    log.info("LangFuse tracker loaded from %s", _LF_PATH)
else:
    _tracker = None
    log.warning("LangFuse instrument-langfuse.py not found at %s", _LF_PATH)


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
    "ollama": {
        "base_url": "http://localhost:11434",
        "api_key": "ollama",
        "models": {
            "deepseek-r1:7b-64k": {"context": 64000, "cost_per_1k": 0.0},
            "qwen3:4b-64k": {"context": 64000, "cost_per_1k": 0.0},
            "llama3.2:3b-64k": {"context": 64000, "cost_per_1k": 0.0},
            "qwen3:1.7b-32k": {"context": 32000, "cost_per_1k": 0.0},
        },
        "default_model": "deepseek-r1:7b-64k",
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
    model: str | None = None,
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

    _start = time.time()
    _model = body["model"]

    log.info(
        f"LLM request: {len(messages)} messages, model={_model}, stream={stream}"
    )

    def _trace(result: dict, status: str = "success"):
        if not _tracker:
            return
        duration = (time.time() - _start) * 1000
        tok = result.get("usage", {}).get("total_tokens", 0) if isinstance(result.get("usage"), dict) else 0
        _tracker.trace(
            name="llm.chat_completion",
            input={"messages_count": len(messages), "model": _model},
            output={"content_length": len(result.get("content", "")), "finish_reason": result.get("finish_reason", "")},
            tenant="sdc-core", agent="llm",
            duration_ms=duration,
            cost_usd=tok * 0.0001 / 1000,
            metadata={"model": _model, "tokens": tok},
            status=status,
        )

    try:
        resp = requests.post(url, headers=headers, json=body, timeout=60)
        resp.raise_for_status()

        if stream:
            _trace({"content": "", "usage": {}}, "stream")
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

            result = {
                "content": content,
                "reasoning": reasoning,
                "model": data.get("model", model),
                "usage": usage,
                "cost": cost,
                "finish_reason": data["choices"][0].get("finish_reason", "stop"),
            }
            _trace(result)
            return result
        else:
            log.warning(f"LLM unexpected response: {json.dumps(data)[:200]}")
            result = {"content": "", "error": "Respuesta inesperada del LLM"}
            _trace(result, "error")
            return result

    except requests.exceptions.Timeout:
        log.error("LLM request timed out")
        result = {"content": "", "error": "Timeout del LLM"}
        _trace(result, "error")
        return result
    except requests.exceptions.RequestException as e:
        log.error(f"LLM request failed: {e}")
        result = {"content": "", "error": str(e)}
        _trace(result, "error")
        return result


def stream_chat_completion(
    messages: list,
    model: str | None = None,
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


def ollama_chat_completion(
    messages: list,
    model: str = "deepseek-r1:7b-64k",
    max_tokens: int = 2000,
    temperature: float = 0.7,
) -> dict:
    """Send a chat completion request to local Ollama."""
    url = f"{PROVIDERS['ollama']['base_url']}/api/chat"
    body = {
        "model": model,
        "messages": messages,
        "stream": False,
        "options": {
            "num_predict": max_tokens,
            "temperature": temperature,
        },
    }
    _start = time.time()
    log.info(f"Ollama request: {len(messages)} messages, model={model}")

    try:
        resp = requests.post(url, json=body, timeout=120)
        resp.raise_for_status()
        data = resp.json()
        duration = (time.time() - _start) * 1000

        content = data.get("message", {}).get("content", "")
        log.info(f"Ollama response: {len(content)} chars in {duration:.0f}ms")

        return {
            "content": content,
            "model": model,
            "usage": {"total_tokens": data.get("eval_count", 0)},
            "latency_ms": duration,
        }
    except requests.exceptions.Timeout:
        log.error("Ollama request timed out (120s)")
        return {"content": "", "error": "timeout", "model": model}
    except requests.exceptions.ConnectionError:
        log.error("Ollama not available at localhost:11434")
        return {"content": "", "error": "ollama_not_available", "model": model}
    except Exception as e:
        log.error(f"Ollama request failed: {e}")
        return {"content": "", "error": str(e), "model": model}


def ask_local(
    prompt: str,
    system: str | None = None,
    model: str = "deepseek-r1:7b-64k",
) -> str:
    """Send a prompt to local Ollama model, get text response."""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    result = ollama_chat_completion(messages, model=model)
    return result.get("content", "")


def ask(prompt: str, system: str | None = None) -> str:
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
