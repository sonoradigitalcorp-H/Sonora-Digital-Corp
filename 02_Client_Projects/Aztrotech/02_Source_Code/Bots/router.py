import re
import os
import httpx
import logging
from typing import Optional

logger = logging.getLogger(__name__)

REASONING_PATTERNS = [
    r"\b(analiza|analizar|evalúa|evaluar|compara|diferencias)\b",
    r"\b(estrategia|plan|planeación|roadmap|pros y contras)\b",
    r"\b(por qué|cómo funciona|explícame|detalla|fundamento)\b",
    r"\b(contrato|legal|términos|condiciones|cláusula)\b",
]

PREMIUM_PATTERNS = [
    r"\b(código|programar|desarrolla|implementa|arquitectura)\b",
    r"\b(investiga|research|paper|documentación técnica)\b",
    r"\b(diseño de sistema|scalabilidad|optimiza)\b",
]

PACKAGES = {
    "despertar": {"calls_per_month": 100, "calls_per_day": 5, "channels": 1, "concurrent_calls": 1, "outbound": False},
    "elevar": {"calls_per_month": 500, "calls_per_day": 20, "channels": 3, "concurrent_calls": 5, "outbound": True},
    "soberano": {"calls_per_month": -1, "calls_per_day": -1, "channels": -1, "concurrent_calls": 20, "outbound": True},
}


def _ollama_available() -> bool:
    endpoint = os.getenv("OLLAMA_ENDPOINT", "http://localhost:11434")
    try:
        import asyncio
        async def _check():
            async with httpx.AsyncClient(timeout=3) as client:
                r = await client.get(f"{endpoint}/api/tags")
                return r.status_code == 200
        return asyncio.run(_check())
    except Exception:
        return False


class ModelRouter:
    def __init__(self, config: dict):
        self.config = config
        m = config.get("models", {})
        self.default = m.get("default", "deepseek/deepseek-v4-flash")
        self.reasoning = m.get("reasoning", "z-ai/glm-5.2")
        self.premium = m.get("premium", "moonshotai/kimi-k2.7-code")

    def select_model(self, user_msg: str, context: Optional[dict] = None) -> str:
        msg_lower = user_msg.lower()
        if self._match_patterns(msg_lower, PREMIUM_PATTERNS):
            return self.premium
        if self._match_patterns(msg_lower, REASONING_PATTERNS):
            return self.reasoning
        return self.default

    def _match_patterns(self, text: str, patterns: list) -> bool:
        return any(re.search(p, text) for p in patterns)

    def get_rate_limits(self, package: str = "despertar") -> dict:
        return PACKAGES.get(package, PACKAGES["despertar"])

    def check_rate_limit(self, package: str, current_usage: dict) -> dict:
        limits = self.get_rate_limits(package)
        result = {"allowed": True, "reason": ""}
        if limits["calls_per_month"] > 0 and current_usage.get("monthly", 0) >= limits["calls_per_month"]:
            result["allowed"] = False
            result["reason"] = f"Límite mensual alcanzado ({limits['calls_per_month']}/mes)"
        if limits["calls_per_day"] > 0 and current_usage.get("daily", 0) >= limits["calls_per_day"]:
            result["allowed"] = False
            result["reason"] = f"Límite diario alcanzado ({limits['calls_per_day']}/día)"
        return result

    def is_inbound(self, context: dict = None) -> bool:
        return context.get("direction", "inbound") == "inbound" if context else True

    def _build_params(self, model: str, messages: list) -> dict:
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": self.config.get("max_tokens", 4096),
        }
        if "glm" in model.lower():
            payload["reasoning_effort"] = "max"
            payload["thinking"] = True
        if "kimi" in model.lower():
            payload["reasoning_effort"] = "high"
        return payload

    async def call_ollama(self, model: str, messages: list) -> dict:
        """Call local Ollama LLM (no token cost)."""
        endpoint = os.getenv("OLLAMA_ENDPOINT", "http://localhost:11434")
        system = ""
        user_parts = []
        for m in messages:
            if m["role"] == "system":
                system += m["content"] + "\n"
            elif m["role"] == "user":
                user_parts.append(m["content"])
        user_full = "\n".join(user_parts)
        payload = {
            "model": model,
            "prompt": user_full,
            "system": system.strip() if system.strip() else None,
            "stream": False,
            "options": {"temperature": 0.7, "num_ctx": 4096},
        }
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(f"{endpoint}/api/generate", json=payload)
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "choices": [{
                        "message": {"content": data.get("response", ""), "role": "assistant"}
                    }],
                    "model": model,
                    "usage": {"prompt_tokens": 0, "completion_tokens": 0},
                }
            raise Exception(f"Ollama failed: {resp.status_code} {resp.text[:200]}")

    async def call(self, messages: list, model: Optional[str] = None) -> dict:
        model = model or self.default
        api_key = self.config.get("openrouter", {}).get("api_key") or os.getenv("OPENROUTER_API_KEY")
        base_url = self.config["openrouter"]["base_url"]

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://astrotech.ai",
            "X-Title": "AstroTech AI",
        }

        # Local-first: if OpenRouter key is empty, use Ollama (qwen2.5:3b)
        if not api_key and _ollama_available():
            model_map = {"deepseek/deepseek-v4-flash": "qwen2.5:3b", "z-ai/glm-5.2": "qwen2.5:3b"}
            local_model = model_map.get(model, "qwen2.5:3b")
            logger.info(f"LLM call (LOCAL): {local_model}")
            return await self.call_ollama(local_model, messages)

        fallback_chain = [model]
        if model == self.default:
            fallback_chain.extend([self.reasoning, self.premium])
        elif model == self.reasoning:
            fallback_chain.append(self.premium)

        for fb_model in fallback_chain:
            payload = self._build_params(fb_model, messages)
            logger.info(f"LLM call: {fb_model}")
            async with httpx.AsyncClient(timeout=self.config["openrouter"]["timeout"]) as client:
                resp = await client.post(f"{base_url}/chat/completions", json=payload, headers=headers)
                if resp.status_code == 200:
                    return resp.json()
                logger.warning(f"{fb_model} falló: {resp.status_code}")

        raise Exception("Todos los modelos en la cadena de respaldo fallaron")
