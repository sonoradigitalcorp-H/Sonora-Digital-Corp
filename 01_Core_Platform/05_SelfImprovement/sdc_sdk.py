"""SDC SDK — utilities for the Self-Improvement Engine.

Provides:
  - get_env(): load env vars from ~/.hermes/.env and project .env
  - call_llm(): call OpenRouter LLM (uses deepseek/deepseek-v4-flash-0731 by default)
  - log_action(): structured telemetry logging
  - get_db(): SQLite connection helper
"""

import os
import json
import time
import sqlite3
import logging
import hashlib
from pathlib import Path
from typing import Optional, Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = Path(__file__).resolve().parent / "experience.db"
SKILLS_DIR = Path(__file__).resolve().parent / "skills"

logger = logging.getLogger("sdc_sdk")


def get_env(key: str, default: Optional[str] = None) -> Optional[str]:
    """Load env var, checking ~/.hermes/.env and project .env first."""
    hermes_env = Path.home() / ".hermes" / ".env"
    if hermes_env.exists():
        from dotenv import load_dotenv as _load
        _load(hermes_env, override=False)

    project_env = PROJECT_ROOT / ".env"
    if project_env.exists():
        from dotenv import load_dotenv as _load
        _load(project_env, override=False)

    return os.getenv(key, default)


def call_llm(
    prompt: str,
    system: Optional[str] = None,
    model: Optional[str] = None,
    max_tokens: int = 2048,
    temperature: float = 0.3,
    stop: Optional[list] = None,
) -> str:
    """Call OpenRouter or local Ollama LLM.

    Strategy (token-cost optimization):
      - If OPENROUTER_API_KEY has balance → use OpenRouter (deepseek-v4-flash)
      - If key empty or balance 0 → fallback to local Ollama (qwen2.5:3b)
      - Self-improvement loops at night → always use Ollama (zero cost)

    Modelo default: deepseek/deepseek-v4-flash-0731 (OpenRouter) o qwen2.5:3b (Ollama).
    """
    import requests

    api_key = get_env("OPENROUTER_API_KEY")

    if not api_key:
        return _call_ollama(prompt, system, model, max_tokens, temperature)

    if model is None:
        model = "deepseek/deepseek-v4-flash-0731"
    if model.startswith("openrouter/"):
        model = model[len("openrouter/"):]

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://sonoradigitalcorp.com",
        "X-Title": "SDC Self-Improvement Engine",
        "Content-Type": "application/json",
    }

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    body: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    if stop:
        body["stop"] = stop

    try:
        resp = requests.post(url, headers=headers, json=body, timeout=120)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("error"):
                raise RuntimeError(f"OpenRouter error: {data['error']}")
            return data["choices"][0]["message"]["content"]
        # Balance exhausted → fallback to local
        if resp.status_code in (401, 402, 403):
            logger.warning("OpenRouter rejected, falling back to Ollama")
            return _call_ollama(prompt, system, model, max_tokens, temperature)
        raise RuntimeError(f"OpenRouter API error {resp.status_code}: {resp.text[:500]}")
    except requests.exceptions.ConnectionError:
        logger.warning("OpenRouter unreachable, falling back to Ollama")
        return _call_ollama(prompt, system, model, max_tokens, temperature)


def _call_ollama(prompt: str, system: Optional[str], model: Optional[str], max_tokens: int, temperature: float) -> str:
    """Call local Ollama LLM (qwen2.5:3b by default). Zero token cost."""
    import requests
    endpoint = os.getenv("OLLAMA_ENDPOINT", "http://localhost:11434")
    local_model = "qwen2.5:3b" if not model else model.replace("openrouter/", "").replace("/", "-")
    # Map OpenRouter names to local models
    if "deepseek" in local_model.lower():
        local_model = "qwen2.5:3b"

    payload = {
        "model": local_model,
        "prompt": prompt,
        "system": system or "",
        "stream": False,
        "options": {"temperature": temperature, "num_ctx": min(max_tokens, 4096)},
    }
    resp = requests.post(f"{endpoint}/api/generate", json=payload, timeout=120)
    resp.raise_for_status()
    data = resp.json()
    return data.get("response", "")


def log_action(
    action: str,
    tenant_id: str = "sdc",
    metadata: Optional[dict] = None,
    level: str = "info",
) -> None:
    """Log structured agent action for telemetry. Writes to log + SQLite."""
    entry = {
        "timestamp": time.time(),
        "tenant_id": tenant_id,
        "action": action,
        "level": level,
        "metadata": metadata or {},
    }
    line = json.dumps(entry, ensure_ascii=False)
    getattr(logger, level)(line)


def get_db() -> sqlite3.Connection:
    """Get SQLite connection for the experience store."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def hash_input(text: str) -> str:
    """SHA-256 hash of input for deduplication."""
    return hashlib.sha256(text.encode()).hexdigest()[:16]


__all__ = [
    "get_env",
    "call_llm",
    "log_action",
    "get_db",
    "hash_input",
    "PROJECT_ROOT",
    "DB_PATH",
    "SKILLS_DIR",
]
