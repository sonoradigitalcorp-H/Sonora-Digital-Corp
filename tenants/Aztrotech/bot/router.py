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
    r"\b(código|programar|programa|programa\s+un|desarrolla|desarrollar|implementa|implementar|arquitectura)\b",
    r"\b(investiga|research|paper|documentación técnica)\b",
    r"\b(diseño de sistema|scalabilidad|optimiza|optimizar)\b",
]

PACKAGES = {
    "despertar": {"calls_per_month": 100, "calls_per_day": 5, "channels": 1, "concurrent_calls": 1, "outbound": False},
    "elevar": {"calls_per_month": 500, "calls_per_day": 20, "channels": 3, "concurrent_calls": 5, "outbound": True},
    "soberano": {"calls_per_month": -1, "calls_per_day": -1, "channels": -1, "concurrent_calls": 20, "outbound": True},
}


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

    async def call(self, messages: list, model: Optional[str] = None) -> dict:
        model = model or self.default
        api_key = self.config.get("openrouter", {}).get("api_key") or os.getenv("OPENROUTER_API_KEY")
        base_url = self.config["openrouter"]["base_url"]

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://aztrotech.mx",
            "X-Title": "Aztrotech AI",
        }

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
