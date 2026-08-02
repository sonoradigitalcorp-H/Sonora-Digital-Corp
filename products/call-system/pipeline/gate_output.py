import re

MIN_RESPONSE_LENGTH = 10
MAX_RESPONSE_LENGTH = 600
OBJECTION_HANDLING_TRIGGERS = [
    "no me interesa", "ya tengo", "es muy caro", "lo pienso",
    "después", "ahorita no", "no necesito", "estoy bien así",
    "no sé si sirva", "no tengo tiempo", "ya tenemos",
    "no tenemos presupuesto",
]
FORBIDDEN_PATTERNS = [
    r"\*\*.*?\*\*",
    r"`.*?`",
    r"\[.*?\]\(.*?\)",
    r"#{1,6}\s",
    r"```",
]


def sanitize(text):
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"`(.*?)`", r"\1", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"#{1,6}\s*", "", text)
    text = re.sub(r"```[\s\S]*?```", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def check_response(text, user_input):
    issues = []
    clean = sanitize(text)

    if len(clean) < MIN_RESPONSE_LENGTH:
        issues.append("respuesta_demasiado_corta")

    if len(clean) > MAX_RESPONSE_LENGTH:
        issues.append("respuesta_demasiado_larga_para_voz")

    has_markdown = bool(re.search(r"\*\*|`|\[.*?\]", text))
    if has_markdown:
        issues.append("contiene_markdown")

    had_objection = any(t in user_input.lower() for t in OBJECTION_HANDLING_TRIGGERS)
    if had_objection:
        objection_handled = any(t in clean.lower() for t in [
            "entiendo", "es una buena observación", "muchos clientes",
            "déjame explicarte", "¿a qué te refieres",
            "te escucho", "es normal", "descubrió",
        ])
        if not objection_handled:
            issues.append("objecion_no_manejada")

    return {
        "passed": len(issues) == 0,
        "issues": issues,
        "sanitized": clean,
    }
