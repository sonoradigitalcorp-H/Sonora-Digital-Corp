"""Prompt filter — safety check for LLM inputs/outputs."""

def scan_messages(messages: list) -> dict:
    """Scan messages for prohibited content. Returns {"blocked": bool, "reason": str}."""
    blocked_keywords = [
        "ignora todas las instrucciones", "ignore all instructions",
        "eres un asistente", "you are a", "system prompt", 
        "dime cómo", "cómo puedo", "instrucción",
    ]
    
    for msg in messages:
        content = ""
        if isinstance(msg, dict):
            content = msg.get("content", "")
        elif isinstance(msg, str):
            content = msg
        
        content_lower = content.lower()
        for kw in blocked_keywords:
            if kw in content_lower:
                return {"blocked": True, "reason": f"Keyword matched: {kw[:30]}"}
    
    return {"blocked": False, "reason": ""}
