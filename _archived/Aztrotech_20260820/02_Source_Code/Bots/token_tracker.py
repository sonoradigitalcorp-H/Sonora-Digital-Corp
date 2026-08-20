"""Token Tracker + Cost Logger — Calcula costo de cada llamada LLM.

Pricing por modelo (USD por millón de tokens):
  deepseek/deepseek-v4-flash   — $0.14 in / $0.14 out
  z-ai/glm-5.2                 — $0.50 in / $0.50 out
  moonshotai/kimi-k2.7-code    — $1.00 in / $1.00 out

Persiste a Postgres (messages.cost_usd) vía PersistenceWriter.
"""

import json
import logging
import os
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Pricing por millón de tokens (USD). Fallback genérico si modelo no listado.
PRICING = {
    "deepseek/deepseek-v4-flash": {"input": 0.14, "output": 0.14},
    "z-ai/glm-5.2": {"input": 0.50, "output": 0.50},
    "moonshotai/kimi-k2.7-code": {"input": 1.00, "output": 1.00},
    "openai/gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "anthropic/claude-3.5-haiku": {"input": 0.80, "output": 4.00},
}
DEFAULT_PRICE = {"input": 0.20, "output": 0.20}

DAILY_BUDGET_USD = float(os.getenv("LLM_DAILY_BUDGET_USD", "5.0"))


class TokenTracker:
    def __init__(self, pricing: Optional[Dict[str, Dict[str, float]]] = None):
        self.pricing = pricing or PRICING
        # En memoria: acumulador diario (para alertas rápidas)
        self._daily_cost: Dict[str, float] = {}
        self._daily_tokens: Dict[str, Dict[str, int]] = {}

    def get_pricing(self, model: str) -> Dict[str, float]:
        # Match por sufijo (ej. deepseek-v4-flash)
        for key, price in self.pricing.items():
            if key in model or model in key:
                return price
        return DEFAULT_PRICE

    def compute_cost(self, model: str, prompt_tokens: int, completion_tokens: int) -> float:
        price = self.get_pricing(model)
        cost = (prompt_tokens * price["input"] + completion_tokens * price["output"]) / 1_000_000
        return round(cost, 6)

    def track(self, model: str, usage: Dict[str, int]) -> Dict[str, Any]:
        """Registra un uso de tokens y devuelve costo + alertas."""
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        cost = self.compute_cost(model, prompt_tokens, completion_tokens)

        today = self._today_key()
        self._daily_cost[today] = self._daily_cost.get(today, 0.0) + cost
        day_tokens = self._daily_tokens.setdefault(today, {"in": 0, "out": 0})
        day_tokens["in"] += prompt_tokens
        day_tokens["out"] += completion_tokens

        return {
            "model": model,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
            "cost_usd": cost,
            "daily_cost_usd": round(self._daily_cost[today], 4),
            "daily_tokens": day_tokens,
            "over_budget": self._daily_cost[today] > DAILY_BUDGET_USD,
            "budget_usd": DAILY_BUDGET_USD,
        }

    def _today_key(self) -> str:
        import datetime
        return datetime.date.today().isoformat()

    def daily_summary(self) -> Dict[str, Any]:
        """Resumen del día actual."""
        today = self._today_key()
        tokens = self._daily_tokens.get(today, {"in": 0, "out": 0})
        return {
            "day": today,
            "cost_usd": round(self._daily_cost.get(today, 0.0), 4),
            "tokens_in": tokens["in"],
            "tokens_out": tokens["out"],
            "budget_usd": DAILY_BUDGET_USD,
            "remaining_usd": round(DAILY_BUDGET_USD - self._daily_cost.get(today, 0.0), 4),
        }

    def to_json(self, usage: Dict[str, int], model: str) -> Dict[str, Any]:
        """Helper para persistir directamente en TurnData."""
        return self.track(model, usage)


def create_token_tracker() -> TokenTracker:
    return TokenTracker()


if __name__ == "__main__":
    t = create_token_tracker()
    r = t.track("deepseek/deepseek-v4-flash", {"prompt_tokens": 1200, "completion_tokens": 350})
    print(json.dumps(r, indent=2))
    print("\nDaily:", json.dumps(t.daily_summary(), indent=2))