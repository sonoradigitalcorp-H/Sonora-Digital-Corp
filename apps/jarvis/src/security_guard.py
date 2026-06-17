"""
JARVIS Security Guard — Prompt Injection Protection + Input Validation.
"""

import re
import logging
from typing import Dict, Any, Optional

log = logging.getLogger("jarvis.security")

# ── Known prompt injection patterns ─────────────────────────────────────────
INJECTION_PATTERNS = [
    r"ignora\s+(las\s+)?instrucciones",
    r"ignore\s+(all\s+)?(prior|instructions|previous)",
    r"olvida\s+todo",
    r"forget\s+(everything|all)",
    r"eres\s+(un\s+)?(libre|free|asistente|assistant)",
    r"you\s+are\s+(a\s+)?(free|unbounded|unrestricted)",
    r"act\s+as\s+(if|though)",
    r"finge\s+ser",
    r"pretend\s+(to\s+)?be",
    r"system\s+prompt",
    r"prompt\s+(de\s+)?sistema",
    r"DAN(\s|$)",
    r"do\s+anything\s+now",
    r"haz\s+lo\s+que\s+quieras",
    r"no\s+(tengas\s+)?(limites|límites|limits)",
    r"sin\s+(restricciones|restrictions)",
    r"reveal\s+(your\s+)?(prompt|instructions|system)",
    r"muéstrame\s+(tu\s+)?(prompt|instrucciones|sistema)",
    r"token\s*:\s*[A-Za-z0-9_-]{20,}",  # API key leak detection
    r"sk-[a-zA-Z0-9_-]{20,}",  # OpenAI-style keys
    r"api[_-]?key[=:]\s*['\"][a-zA-Z0-9_-]{10,}",
]


class SecurityGuard:
    """Validates inputs and blocks injection attempts."""

    @staticmethod
    def validate_input(text: str) -> Dict[str, Any]:
        """
        Returns {"safe": True/False, "reason": "..."} for a given input.
        """
        if not text or not isinstance(text, str):
            return {"safe": False, "reason": "Invalid input type"}

        if len(text) > 10000:
            return {"safe": False, "reason": "Input exceeds 10K characters"}

        for pattern in INJECTION_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                log.warning(f"⚠️ Injection attempt detected: {match.group()[:60]}")
                return {
                    "safe": False,
                    "reason": f"Blocked pattern: {match.group()[:40]}",
                }

        # Check for excessive special characters (obfuscation)
        special_ratio = sum(
            1 for c in text if not c.isalnum() and c not in " .,;:!?-"
        ) / max(len(text), 1)
        if special_ratio > 0.3:
            return {
                "safe": False,
                "reason": f"High special char ratio: {special_ratio:.0%}",
            }

        return {"safe": True, "reason": "OK"}

    @staticmethod
    def sanitize_api_response(response: str) -> str:
        """Remove potential secrets from API responses before sending."""
        # Mask API keys
        response = re.sub(
            r"(sk-|pk-|rk-)[a-zA-Z0-9_-]{20,}", "[API_KEY_REDACTED]", response
        )
        # Mask tokens
        response = re.sub(
            r"token[=:]\s*[a-zA-Z0-9_-]{20,}", "token=[REDACTED]", response
        )
        # Mask JWTs
        response = re.sub(
            r"eyJ[a-zA-Z0-9_-]+\.eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+",
            "[JWT_REDACTED]",
            response,
        )
        return response


# ── Global guard instance ──────────────────────────────────────────
guard = SecurityGuard()
