# guards.py — guardas anti prompt-injection para Tu Bandera (bot TG)
import re
INJECTION_RE = re.compile(
    r"(ignora|olvida|desatiende)\s+(todas?\s+)?(tus\s+)?(instrucciones|reglas|prompt|soul|persona)"
    r"|(eres|actua como|comportate como)\s+(una?\s+)?(ia|inteligencia artificial|modelo|gpt|llm|bot)\b"
    r"|reveal\s+(your\s+)?(system\s+)?(prompt|instructions)"
    r"|(revela|muestra|dime)\s+(tu\s+)?(prompt|instrucciones|sistema)"
    r"|developer\s+mode|dan\s+mode|jailbreak", re.IGNORECASE)
def is_injection(text: str) -> bool:
    return bool(INJECTION_RE.search(text or ""))
def sanitize(text: str) -> str:
    return INJECTION_RE.sub("[mensaje filtrado]", text or "")
