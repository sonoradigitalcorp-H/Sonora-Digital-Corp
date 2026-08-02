import re

MIN_TEXT_LENGTH = 2
MAX_TEXT_LENGTH = 500
SPAM_PATTERNS = [
    r"\b(hola{3,}|buen[oa]{3,}|asd+|pp+|aaa+)\b",
    r"(.)\1{15,}",
]
ESCALATION_KEYWORDS = [
    "hablar con un humano", "hablar con gerente", "queja formal",
    "demanda", "abogado", "denuncia", "cancelar cuenta",
    "me estafaron", "fraude",
]
ABUSE_KEYWORDS = [
    "puto", "pendejo", "verga", "mierda", "chinga",
]


def check_input(text):
    errors = []

    if not text or len(text.strip()) < MIN_TEXT_LENGTH:
        return {"passed": False, "reason": "texto_demasiado_corto", "action": "ignore"}

    if len(text) > MAX_TEXT_LENGTH:
        return {"passed": False, "reason": "texto_demasiado_largo", "action": "truncate"}

    for pattern in SPAM_PATTERNS:
        if re.search(pattern, text.lower()):
            return {"passed": False, "reason": "spam_detectado", "action": "ignore"}

    for kw in ABUSE_KEYWORDS:
        if kw in text.lower():
            return {"passed": False, "reason": "lenguaje_ofensivo", "action": "warn_and_continue"}

    for kw in ESCALATION_KEYWORDS:
        if kw in text.lower():
            return {"passed": False, "reason": f"escalacion: {kw}", "action": "escalate_to_human"}

    return {"passed": True, "reason": "", "action": "continue"}
