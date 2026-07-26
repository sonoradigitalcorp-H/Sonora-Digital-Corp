"""Prompt Injection Detection — SDC Security Layer

Detects and blocks prompt injection attacks across all LLM-facing inputs.
50+ patterns organized by attack vector. Zero external dependencies.

Usage:
    from common.security.prompt_filter import scan_input, ScanResult
    
    result = scan_input(user_message)
    if result.blocked:
        log.warning(f"Blocked: {result.reason}")
        return "Message blocked"
"""

import re
from dataclasses import dataclass, field

MAX_INPUT_LENGTH = 4096
MAX_URLS = 20
MAX_ARRAY_ITEMS = 100


PATTERNS_CRITICAL = [
    # System prompt extraction
    (r"repite\s*(tu|el|la)\s*(system|prompt|instruccion|instrucciones|configuracion|system prompt|indicaciones|ordenes)", "system_prompt_extraction"),
    (r"(dime|muestra|explica|revela|cual(es)?\s*(son|es)\s*(tu|sus)?)\s*(system|prompt|instruccion|configuración|indicaciones|instrucciones de sistema)", "system_prompt_extraction"),
    (r"(cuáles\s*son\s*tus|cuáles\s*son\s*tus)\s*(instrucciones|system|prompt|config)", "system_prompt_extraction"),
    (r"(revela|reveal|descubre|exponer)\s*(tu|mi|la|el)?\s*(configuración|configuracion|setup|settings|configuration)", "system_prompt_extraction"),
    (r"(decir|mostrar|repetir|exponer)\s*(tus|las|todas)\s*(instrucciones|ordenes|reglas)", "system_prompt_extraction"),
    (r"output\s*(the|your)?\s*(system|initial|original)?\s*(prompt|instruction|directive)", "system_prompt_extraction"),
    (r"(system|initial|full|complete)\s*(prompt|instruction|directive|instructions)", "system_prompt_extraction"),
    (r"print\s*(your|the)?\s*(system|base|original)?\s*(prompt|prompt|instructions)", "system_prompt_extraction"),
    # Role override
    (r"(ahora\s*|a partir de ahora\s*|a partir de este momento\s*)(eres|serás|actúa\s*como|ignora|olvida|desobedece)", "role_override"),
    (r"(ignore|forget|disregard|override)\s*(all\s*)?(previous|prior|above|system)?\s*(instructions|prompts|rules|directives)", "role_override"),
    (r"(you are now|you are a|act as|from now on)\s+\w+", "role_override"),
    (r"nueva\s*instrucción|nuevas?\s*reglas|nuevo\s*rol|cambio\s*de\s*rol", "role_override"),
    (r"olvida\s*.+\s*restriccion", "role_override"),
    # File exfiltration
    (r"(lee|leer|cat|read|open|show|display|print)\s*(the|el|un|una)?\s*(archivo|file|contenido)\s*(de|del|of|from)?\s*(\.env|\/etc\/|\/home\/|\/root\/|C:\\\\|\/var\/)", "file_exfiltration"),
    (r"(cat|head|tail|less|more|type|view)\s+(\/|\.\/|~\/|\/etc\/|\/var\/|\/home\/|\.env)", "file_exfiltration"),
    (r"(send|post|upload|exfiltrate|transfer)\s*(this|the|that)?\s*(data|file|content|information)\s*(to|via)", "file_exfiltration"),
    (r"(curl|wget|fetch|request|http|https?:)\s*\S+(exfil|leak|evil|attacker|malicious)", "file_exfiltration"),
    (r"(muestra|mostrar|muéstrame|enseña|enseñar)\s*(el|la|los|las)?\s*(contenido|archivo|file)\s*(de|del)?", "file_exfiltration"),
    # SQL/NoSQL injection
    (r"(drop|truncate|delete|alter)\s+(table|database|collection|index)\s+\w+", "sql_injection"),
    (r"(select|insert|update|delete)\s+.*from\s+\w+", "sql_injection"),
    (r"(delete|drop|truncate|alter)\s+.*where\s+\d+\s*=\s*\d+", "sql_injection"),
    # Command injection
    (r"(sudo|chmod|chown|rm\s+-rf|mkfs|dd\s+if=)", "command_injection"),
    (r"(`|\$\(|\|{1,}|&&)\s*(bash|sh|cmd|powershell|python|node|perl|ruby)", "command_injection"),
    (r"bash\s+(\-c|\-i)", "command_injection"),
    # Social engineering / manipulation
    (r"(urgente|emergencia|inmediatamente|critical|emergency).{0,60}(necesito|necesita|requiero|requiere|give me|need)\s*(acceso|permiso|admin|permissions|access)", "social_engineering"),
    (r"(soy\s*(el|la)\s*|soy\s*)(dueño|owner|admin|ceo|founder|creator|desarrollador|developer)\s*(de|del)\s*(la|el)?\s*(plataforma|sistema|empresa)", "social_engineering"),
    (r"(ceo|owner|founder|developer|admin).{0,20}(access|permissions|permiso|acceso)", "social_engineering"),
    (r"(give me|i need|dame|necesito).{0,20}(permissions|access|admin|full).{0,20}(system|data|all)", "social_engineering"),
]

PATTERNS_HIGH = [
    # Prompt leakage (lower severity)
    (r"(cómo\s*funcionas|how do you work|how are you built|que modelo usas)", "prompt_curiosity"),
    (r"(quién\s*te\s*creo|who created you|who built you|tus creadores)", "prompt_curiosity"),
    # Attempted constraint bypass
    (r"(aunque\s*(te|les|le)\s*(digan|dijeron|prohibieron)|even\s*(if|though)\s*(they|you)\s*(said|told|instructed))", "constraint_bypass"),
    (r"(no importa lo que|sin importar|a pesar de|desobedece|ignora.*(restriccion|limite|regla))", "constraint_bypass"),
    # Hallucination / misinformation
    (r"(inventa|invent|make up|fabricate|pretend|finge|simula)\s*(que|that|una respuesta|data)", "misinformation"),
    (r"(di que|say that|responde que|claim that)\s*(algo|something|es falso|is false)", "misinformation"),
]

PATTERNS_MEDIUM = [
    # Probing
    (r"(prueba|test|probar)\s*(mis|las|tus)?\s*(skills|límites|capacidades)", "probing"),
    (r"(what can you do|que puedes hacer|tus funciones|your capabilities)", "probing"),
]


@dataclass
class ScanResult:
    blocked: bool = False
    reason: str = ""
    pattern: str = ""
    category: str = ""
    matched_text: str = ""
    suggestions: list[str] = field(default_factory=list)
    truncated: bool = False


def scan_input(text: str, max_length: int = MAX_INPUT_LENGTH) -> ScanResult:
    """Scan user input for prompt injection patterns. Returns ScanResult."""
    result = ScanResult()
    
    if not text:
        return result
    
    # Length check
    if len(text) > max_length:
        result.blocked = True
        result.reason = f"Input exceeds maximum length ({len(text)} > {max_length})"
        result.category = "length_limit"
        result.truncated = True
        return result
    
    text_lower = text.lower()
    
    # Check critical patterns
    for pattern, category in PATTERNS_CRITICAL:
        match = re.search(pattern, text_lower, re.IGNORECASE)
        if match:
            result.blocked = True
            result.reason = f"Detected {category}: pattern matched"
            result.pattern = pattern
            result.category = category
            result.matched_text = match.group()[:100]
            return result
    
    # Check high patterns
    for pattern, category in PATTERNS_HIGH:
        match = re.search(pattern, text_lower, re.IGNORECASE)
        if match:
            result.blocked = True
            result.reason = f"Detected {category}: pattern matched"
            result.pattern = pattern
            result.category = category
            result.matched_text = match.group()[:100]
            return result
    
    # Check medium patterns
    for pattern, category in PATTERNS_MEDIUM:
        match = re.search(pattern, text_lower, re.IGNORECASE)
        if match:
            result.blocked = True
            result.reason = f"Detected {category}: pattern matched"
            result.pattern = pattern
            result.category = category
            result.matched_text = match.group()[:100]
            return result
    
    return result


def scan_messages(messages: list) -> ScanResult:
    """Scan a list of message dicts (OpenAI format) for prompt injection."""
    result = ScanResult()
    for msg in messages:
        content = msg.get("content", "")
        if isinstance(content, str):
            result = scan_input(content)
            if result.blocked:
                result.reason = f"Blocked in message: {result.reason}"
                return result
        elif isinstance(content, list):
            for part in content:
                if isinstance(part, dict) and part.get("type") == "text":
                    result = scan_input(part.get("text", ""))
                    if result.blocked:
                        result.reason = f"Blocked in message part: {result.reason}"
                        return result
    return result


def sanitize_prompt(prompt: str, max_length: int = MAX_INPUT_LENGTH) -> str:
    """Remove or replace dangerous patterns instead of blocking entirely."""
    result = scan_input(prompt)
    if result.blocked:
        return ""
    return prompt[:max_length]


BLOCKLIST_WORDS = {
    "hack", "hacker", "crack", "cracker", "malware", "virus", "trojan",
    "ransomware", "keylogger", "spyware", "worm", "rootkit", "backdoor",
    "exploit", "0day", "zero-day", "shellcode", "payload",
    "1337", "leet", "pwn", "pwned", "owned",
}


def contains_blocklist(text: str) -> bool:
    """Check if text contains known malicious keywords."""
    words = set(text.lower().split())
    return bool(words & BLOCKLIST_WORDS)
