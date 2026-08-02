"""JARVIS Intent Classifier — Classify user intents and extract actionable params.

Supports 10 intents with Spanish/English keyword matching.
No ML dependencies — pure regex + keyword approach.

Usage:
    from jarvis_intent import classify_intent, extract_params
    intent = classify_intent("abre el dashboard de ventas")
    params = extract_params("abre el dashboard de ventas", intent)
"""

import re
from dataclasses import dataclass, field

# ─── Intent Definitions ──────────────────────────────────────────────────────

INTENTS: dict[str, dict] = {
    "open_page": {
        "keywords_es": [
            "abre", "abrir", "mostrar", "ir a", "navega", "visita",
            "landing", "página", "portal", "sitio", "web",
        ],
        "keywords_en": [
            "open", "show", "go to", "navigate", "visit",
            "landing", "page", "portal", "site", "website",
        ],
        "url_patterns": [
            r"(https?://\S+)",
            r"([\w-]+\.(com|net|org|io|dev|mx))",
        ],
    },
    "query_db": {
        "keywords_es": [
            "consulta", "buscar", "buscar en", "cuántos", "cuántas",
            "métricas", "estadísticas", "datos", "reporte", "leads",
            "conversaciones", "ventas", "ingresos", "base de datos",
        ],
        "keywords_en": [
            "query", "search", "find", "how many", "metrics",
            "statistics", "data", "report", "leads", "conversations",
            "sales", "revenue", "database",
        ],
        "db_tables": [
            "conversations", "leads", "daily_metrics", "messages",
            "users", "tenants", "events",
        ],
    },
    "show_content": {
        "keywords_es": [
            "enseña", "muestra", "ver", "despliega", "lista",
            "artículo", "post", "contenido", "documento", "archivo",
        ],
        "keywords_en": [
            "show", "display", "view", "list", "render",
            "article", "post", "content", "document", "file",
        ],
    },
    "create_dashboard": {
        "keywords_es": [
            "crea", "crear", "genera", "generar", "construye",
            "dashboard", "panel", "gráfico", "chart", "widget",
            "reporte visual", "gráfica",
        ],
        "keywords_en": [
            "create", "build", "generate", "make",
            "dashboard", "panel", "chart", "graph", "widget",
            "visual report",
        ],
    },
    "send_message": {
        "keywords_es": [
            "envía", "enviar", "manda", "mandar", "escribe",
            "mensaje", "whatsapp", "telegram", "correo", "email",
            "notificación", "avisa",
        ],
        "keywords_en": [
            "send", "message", "whatsapp", "telegram",
            "email", "notify", "alert", "tell",
        ],
        "params": ["recipient", "channel", "phone"],
    },
    "take_screenshot": {
        "keywords_es": [
            "captura", "screenshot", "pantallazo", "foto de pantalla",
            "imagen de la página", "snapshot",
        ],
        "keywords_en": [
            "screenshot", "capture", "snapshot", "screen grab",
            "take a picture of",
        ],
    },
    "playwright_action": {
        "keywords_es": [
            "haz click", "click en", "presiona", "escribe en",
            "selecciona", "llena", "completa el formulario",
            "scroll", "desplaza", "interactúa con",
        ],
        "keywords_en": [
            "click on", "press", "type in", "fill in",
            "select", "scroll", "interact with", "fill out",
        ],
        "action_types": ["click", "type", "select", "scroll", "hover", "fill"],
    },
    "system_status": {
        "keywords_es": [
            "estado", "estatus", "cómo está", "cómo van",
            "salud", "health", "status", "problemas",
            "servicios", "docker", "containers", "uptime",
        ],
        "keywords_en": [
            "status", "health", "how are things", "problems",
            "services", "docker", "containers", "uptime",
            "system check",
        ],
    },
    "shutdown_mic": {
        "keywords_es": [
            "apaga", "silencio", "para", "detener", "micrófono",
            "callado", "no escuches", "shut up", "mute",
        ],
        "keywords_en": [
            "shut up", "mute", "stop listening", "silence",
            "turn off mic", "quiet",
        ],
    },
    "general_response": {
        "keywords_es": [],
        "keywords_en": [],
    },
}

# ─── Classification ──────────────────────────────────────────────────────────


def classify_intent(text: str) -> str:
    """Classify user text into one of 10 intents.

    Returns intent name string. Falls back to 'general_response'.
    """
    if not text or not text.strip():
        return "general_response"

    normalized = text.lower().strip()
    scores: dict[str, int] = {name: 0 for name in INTENTS}

    for intent_name, config in INTENTS.items():
        if intent_name == "general_response":
            continue

        # Score Spanish keywords
        for kw in config.get("keywords_es", []):
            if kw in normalized:
                scores[intent_name] += 2

        # Score English keywords
        for kw in config.get("keywords_en", []):
            if kw in normalized:
                scores[intent_name] += 2

        # Bonus: URL patterns for open_page
        if intent_name == "open_page":
            for pattern in config.get("url_patterns", []):
                if re.search(pattern, normalized):
                    scores[intent_name] += 5

        # Bonus: DB table names for query_db
        if intent_name == "query_db":
            for table in config.get("db_tables", []):
                if table in normalized:
                    scores[intent_name] += 3

    # Find highest scoring intent
    best_intent = max(scores, key=lambda k: scores[k])
    if scores[best_intent] > 0:
        return best_intent

    return "general_response"


# ─── Parameter Extraction ────────────────────────────────────────────────────


def extract_params(text: str, intent: str) -> dict:
    """Extract actionable parameters from text based on intent type."""
    if not text or intent not in INTENTS:
        return {}

    normalized = text.lower().strip()
    params: dict = {}

    if intent == "open_page":
        # Extract URLs
        urls = re.findall(r"(https?://\S+)", normalized)
        if urls:
            params["url"] = urls[0].rstrip(".,;:)")
        else:
            # Try to extract domain-like patterns
            domains = re.findall(r"([\w-]+\.(?:com|net|org|io|dev|mx))", normalized)
            if domains:
                params["url"] = f"https://{domains[0]}"
            else:
                # Extract page name hints
                page_hints = re.findall(
                    r"(dashboard|landing|portal|página|page|sitio|site|web)\s+(\w+)",
                    normalized,
                )
                if page_hints:
                    params["page_name"] = " ".join(page_hints[0])

    elif intent == "query_db":
        # Extract table references
        for table in INTENTS["query_db"].get("db_tables", []):
            if table in normalized:
                params["table"] = table
                break
        # Extract numeric queries
        nums = re.findall(r"(\d+)", text)
        if nums:
            params["limit"] = int(nums[0])
        # Detect aggregation keywords
        for kw in ["cuántos", "cuántas", "how many", "count"]:
            if kw in normalized:
                params["aggregation"] = "count"

    elif intent == "send_message":
        # Extract phone numbers
        phones = re.findall(r"(\+?\d{10,13})", text)
        if phones:
            params["phone"] = phones[0]
        # Detect channel
        for ch in ["whatsapp", "telegram", "email", "correo"]:
            if ch in normalized:
                params["channel"] = ch
                break
        # Extract quoted message
        quoted = re.findall(r'["\u201c\u201d](.+?)["\u201c\u201d]', text)
        if quoted:
            params["message"] = quoted[0]

    elif intent == "take_screenshot":
        # Extract target URL or page
        urls = re.findall(r"(https?://\S+)", normalized)
        if urls:
            params["url"] = urls[0].rstrip(".,;:)")
        else:
            params["target"] = "current_page"

    elif intent == "playwright_action":
        # Detect action type
        for action in INTENTS.get("playwright_action", {}).get("action_types", []):
            if action in normalized:
                params["action"] = action
                break
        # Extract element selectors or text
        selectors = re.findall(r'(?:selector|elemento|element)\s*[:=]\s*(\S+)', normalized)
        if selectors:
            params["selector"] = selectors[0]

    elif intent == "system_status":
        # Detect specific service
        services = ["docker", "postgres", "redis", "qdrant", "neo4j", "n8n", "nginx"]
        for svc in services:
            if svc in normalized:
                params["service"] = svc
                break

    elif intent == "create_dashboard":
        # Detect dashboard type
        types = ["ventas", "sales", "leads", "métricas", "metrics", "overview"]
        for t in types:
            if t in normalized:
                params["dashboard_type"] = t
                break

    return params


# ─── CLI ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    import json

    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: python3 jarvis_intent.py <text>"}))
        sys.exit(1)

    text = " ".join(sys.argv[1:])
    intent = classify_intent(text)
    params = extract_params(text, intent)
    print(json.dumps({"text": text, "intent": intent, "params": params}, ensure_ascii=False, indent=2))
