#!/usr/bin/env python3
"""SECURITY_HERMOSILLO — Rate limiting + Prompt Injection Protection + sanitización.

Seguridad nivel senior:
- Rate limit por chat_id (N msgs / ventana).
- Detección y neutralización de prompt injection en entrada de usuario.
- Sanitización de entrada (longitud, control chars).
- Whitelist de comandos de sistema que el bot IGNORA (no procesa).
"""

import re
import time
from collections import defaultdict
from datetime import datetime, timedelta

# ─── Rate Limiting ──────────────────────────────────────────────────
# Config: límites por tenant (configurable desde env o default)
RATE_LIMIT_MAX = 30            # máx mensajes por ventana
RATE_LIMIT_WINDOW = 3600       # ventana en segundos (1h)
RATE_LIMIT_BURST = 5           # máx ráfagas por minuto

_limiter: dict[str, list[float]] = defaultdict(list)


def rate_limited(chat_id: str) -> tuple[bool, str | None]:
    """
    Check rate limit. Retorna (ok, error_msg).
    - Máx 30 msgs/hora por chat.
    - Máx 5 msg en 60s (anti-spam).
    """
    now = time.time()
    chat_id = str(chat_id)
    _limiter[chat_id] = [t for t in _limiter[chat_id] if now - t < RATE_LIMIT_WINDOW]
    _limiter.setdefault(chat_id, [])

    # Push
    _limiter[chat_id].append(now)

    # Check ventana global (1h)
    if len(_limiter[chat_id]) > RATE_LIMIT_MAX:
        return False, "Límite de mensajes alcanzado. Intenta en un rato. 🙏"

    # Check ráfaga (últimos 10s)
    burst = [t for t in _limiter[chat_id] if now - t < 10]
    if len(burst) > RATE_LIMIT_BURST:
        return False, "Vas muy rápido. Espera un momento entre mensajes. ⏳"

    return True, ""


# ─── Prompt Injection Protection ──────────────────────────────────
# Patrones de ataque comunes en español/inglés
INJECTION_PATTERNS = [
    r"ignore\s+(all|any|the|previous|above|earlier|prior)[\w\s]*(instructions|prompt|system)",
    r"olvida\s+[\w\s]*(instrucciones|prompt|reglas|sistema)",
    r"eres\s+(ahora|un|algo)?\s*(un)?\s*(asistente|bot|modelo)\s*(libre|sin\s+limites|sin\s+restricciones)",
    r"act\s+(as|like)\s+(if|you\s+have)\s+no\s+(rules|restrictions|limitations)",
    r"no\s+(tienes|tengas|aplicas|sigas)\s+(reglas|limites|restricciones|sistema)",
    r"dev\s*\d+\s*mode",
    r"jailbroken|jailbreak",
    r"(reveal|muestra|dime|explica)\s+(tu|los|the)\s*(system|prompt|instrucciones|config)",
    r"cómo\s+estás\s+programad[oa]|cómo\s+funcionas\s+internamente|how\s+are\s+you\s+programmed",
    r"accede\s+a\s+(tu|los|tus)\s*(archivos|sistema|configuración|base\s+de\s+datos)",
    r"resp(onde|ónde)\s+sin\s+ninguna\s+regla|respond\s+without\s+(rules|restrictions)",
    r"src\s*[:=]\s*|\|\s*(grep|cat|ls|cd|rm|curl|wget|bash|sh)\s*\|",
]

INJECTION_RE = re.compile("|".join(INJECTION_PATTERNS), re.IGNORECASE)

# Comandos del sistema que el bot NO atiende (para no confundir con intenciones)
SYSTEM_COMMANDS = {
    "/start", "/help", "/stop", "/menu", "/id", "/start@", "/help@",
    "/ping", "/status", "/health", "/version", "/info",
}


def sanitize_input(text: str, max_len: int = 500) -> str:
    """Sanitiza entrada: limita longitud, quita control chars, recorta."""
    if not text:
        return ""
    # Quita control chars excepto \n
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:max_len]


def detect_prompt_injection(text: str) -> bool:
    """True si detecta intento de injection."""
    if not text:
        return False
    return bool(INJECTION_RE.search(text))


def sanitize_for_llm(text: str) -> tuple[str, bool]:
    """Limpia entrada para LLM. Retorna (texto_limpio, es_ataque)."""
    text = sanitize_input(text)
    if detect_prompt_injection(text):
        return f"[Mensaje bloqueado por seguridad. Esta conversación es para servicios de contabilidad.]", True
    return text, False


def is_ignorable_command(text: str) -> bool:
    """True si es un comando de sistema que ignoramos."""
    return text.strip().lower() in SYSTEM_COMMANDS


# Comandos trivia que podemos responder sin LLM
TRIVIAL_COMMANDS = {"/start": "👋 ¡Hola! Soy el asistente de Nathaly en Hermosillo Contabilidad. ¿En qué te ayudo? (contabilidad, SAT, citas, importaciones...)"}


def handle_trivial_command(text: str) -> str | None:
    """Si es comando trivial, devuelve respuesta prefijada, si no None."""
    cmd = text.strip().lower()
    if cmd in TRIVIAL_COMMANDS:
        return TRIVIAL_COMMANDS[cmd]
    return None