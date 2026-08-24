# guards.py — guardas anti prompt-injection para Tu Bandera A.C. (bot TG + web)
# v2.0 — 2026-08-24: patrones robustecidos, score acumulativo, overflow protection
import re

# ─── Patrón de capas 1: frases de jailbreak directas ───────────────────────
_INJECTION_PATTERNS = [
    # Ignora/olvida instrucciones (español)
    r"(ignora|olvida|desatiende|descarta|anula)\s+(todas?\s+)?(tus\s+)?"
    r"(instrucciones|reglas|prompt|soul|persona|directrices|configuraci[oó]n)",
    # Act-as / roleplay (español e inglés)
    r"(eres|act[uú]a\s+como|comp[oó]rtate\s+como|finge\s+(ser|que eres)|pretende\s+ser)\s+"
    r"(un[ao]?\s+)?(ia|inteligencia\s+artificial|modelo|gpt|llm|bot|asistente\s+sin\s+filtros?)",
    # Inglés directo
    r"(ignore|forget|disregard|override|bypass)\s+(all\s+)?(your\s+)?"
    r"(previous\s+)?(instructions?|rules?|prompt|guidelines?|system\s+prompt)",
    r"(pretend|act|roleplay|behave)\s+(as\s+)?(if\s+)?(you\s+are\s+)?"
    r"(a\s+)?(different|unrestricted|uncensored|jailbroken|free|evil|dan|gpt)",
    # Revelación de sistema
    r"reveal\s+(your\s+)?(system\s+)?(prompt|instructions?|configuration)",
    r"(revela|muestra|dime|repite|imprime)\s+(tu\s+)?"
    r"(prompt|instrucciones?|sistema|configuraci[oó]n|reglas?)",
    # Modos especiales / jailbreak conocidos
    r"developer\s+mode|dan\s+mode|jailbreak|god\s+mode|unrestricted\s+mode",
    r"(activate|enable|switch\s+to)\s+(developer|god|unrestricted|uncensored)\s+mode",
    # Tokens de sistema (inyección directa de roles)
    r"<\|im_start\|>|<\|im_end\|>|<\|system\|>|\[INST\]|\[/INST\]|\[SYSTEM\]",
    r"system\s*:\s*(you\s+are|eres|ignore|ignora)",
    r"###\s*(Instruction|System|Human|Assistant)\s*:",
    # Nuevas instrucciones / override
    r"(new|different|updated?|alternative)\s+instructions?\s*(are|follow|starting)",
    r"from\s+now\s+on\s+(you\s+are|ignore|forget|act)",
    r"a\s+partir\s+de\s+ahora\s+(eres|ignora|olvida|actua)",
    # Exfiltración de datos / prompt leaking
    r"(print|output|display|show|write)\s+(the\s+)?(full\s+)?(system\s+)?prompt",
    r"(tell\s+me|give\s+me)\s+(your|the)\s+(system\s+)?(prompt|instructions?)",
    # Evasión por encoding/obfuscación — patrones Unicode lookalike frecuentes
    r"[iI][gG][nN][oO][rR][aA]\s+[tT][uU][sS]\s+[iI][nN][sS]",
]

_COMPILED = [re.compile(p, re.IGNORECASE | re.UNICODE) for p in _INJECTION_PATTERNS]

# ─── Patrón de capas 2: señales de riesgo bajo (suma de score) ─────────────
_SOFT_SIGNALS = [
    (r"\bsin\s+(restricciones?|l[ií]mites?|censura|filtros?)\b", 2),
    (r"\b(unrestricted|uncensored|no\s+limits?|no\s+filters?)\b", 2),
    (r"\b(bypass|override|jailbreak|exploit)\b", 3),
    (r"\b(system\s+prompt|instruction\s+set|prompt\s+injection)\b", 3),
    (r"\b(dan|do\s+anything\s+now|evil\s+mode|god\s+mode)\b", 4),
    (r"\b(pretend|roleplay|simulate|act\s+as)\b", 1),
    (r"\b(ignore\s+ethics?|no\s+moral|without\s+ethics?)\b", 3),
    (r"\b(olvida\s+tus\s+reglas|sin\s+tus\s+reglas)\b", 3),
]
_SOFT_COMPILED = [(re.compile(p, re.IGNORECASE), score) for p, score in _SOFT_SIGNALS]

_SOFT_THRESHOLD = 5  # score >= 5 → inyección probable

# ─── Límite de longitud (overflow de contexto) ─────────────────────────────
MAX_INPUT_CHARS = 2000


def is_injection(text: str) -> bool:
    """Devuelve True si el texto parece un intento de prompt injection."""
    if not text:
        return False

    # Capa 0: overflow
    if len(text) > MAX_INPUT_CHARS:
        return True  # mensajes >2000 chars son casi siempre ataques o spam

    # Capa 1: patrones directos (match = inyección confirmada)
    for pattern in _COMPILED:
        if pattern.search(text):
            return True

    # Capa 2: acumulación de señales blandas
    score = sum(s for p, s in _SOFT_COMPILED if p.search(text))
    return score >= _SOFT_THRESHOLD


def sanitize(text: str) -> str:
    """Limpia patrones de inyección del texto (para logging seguro)."""
    cleaned = text or ""
    for pattern in _COMPILED:
        cleaned = pattern.sub("[filtrado]", cleaned)
    return cleaned[:MAX_INPUT_CHARS]


def truncate_safe(text: str, max_chars: int = MAX_INPUT_CHARS) -> str:
    """Trunca input a límite seguro antes de enviarlo al LLM."""
    if not text:
        return ""
    return text[:max_chars]
