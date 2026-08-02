import os
import json
import httpx

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "deepseek/deepseek-v4-flash"

PROMPTS_DIR = os.path.join(os.path.dirname(__file__), "prompts")
NICHES_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "tests", "promptfoo", "niches")


def _load_prompt(path):
    if os.path.exists(path):
        with open(path, "r") as f:
            return f.read()
    return ""


def _get_niche_prompts(niche, prompt_type):
    base = os.path.join(NICHES_DIR, niche, "prompts")
    if os.path.exists(base):
        return _load_prompt(os.path.join(base, f"{prompt_type}.txt"))
    return ""


def compose_prompt(tenant, lead_type, text, objection, history, variant="A",
                   conversation_history=None, campaign=None, turn_number=1):
    niche = tenant.get("niche", "general")
    name = tenant.get("name", "Usuario")
    company = tenant.get("company", "")
    plan = tenant.get("plan", "trial")

    call_agent = _get_niche_prompts(niche, "call_agent")
    objection_handler = _get_niche_prompts(niche, "objection_handler")
    sys_default = _load_prompt(os.path.join(PROMPTS_DIR, f"system-{lead_type}.txt"))
    if not sys_default:
        sys_default = _load_prompt(os.path.join(PROMPTS_DIR, "system-default.txt"))

    # Build call history from Engram (past calls)
    history_text = "\n".join(
        f"- ({h.get('date', '')[:10]}) {h.get('summary', '')[:200]}"
        for h in (history or [])[-3:]
    ) if history else "Primera interacción con este cliente."

    # Build conversation history (current call turns)
    conv_text = ""
    if conversation_history:
        lines = []
        for c in conversation_history[-6:]:
            lines.append(f"Cliente: {c['user']}")
            lines.append(f"Tú: {c['assistant']}")
        conv_text = "\n".join(lines)

    # Campaign context
    campaign_text = ""
    if campaign:
        src = campaign.get("source", "desconocida")
        obj = campaign.get("objective", "conocer sus necesidades")
        offer = campaign.get("offer", "")
        campaign_text = f"Contactado via: {src} | Objetivo: {obj}"
        if offer:
            campaign_text += f" | Ofrecer: {offer}"

    total_turns = turn_number + (len(conversation_history or []))

    system = sys_default.format(
        name=name,
        company=company,
        plan=plan,
        niche=niche,
        lead_type=lead_type,
        history=history_text,
        variant=variant,
        call_agent=call_agent,
        objection_handler=objection_handler,
        conv_history=conv_text,
        campaign=campaign_text,
        turn=total_turns,
    )

    messages = [{"role": "system", "content": system}]

    # Inject full conversation history as alternating messages
    if conversation_history:
        for c in conversation_history:
            if c.get("user"):
                messages.append({"role": "user", "content": c["user"]})
            if c.get("assistant"):
                messages.append({"role": "assistant", "content": c["assistant"]})

    # Add current user message
    if text:
        messages.append({"role": "user", "content": text})

    # Objection override
    if objection:
        messages.append({"role": "system",
                         "content": f"Objeción detectada: «{objection}». "
                                    f"Usa el método Feel-Felt-Found para responder."})

    return messages


async def generate_response(messages, temperature=0.5):
    if not OPENROUTER_API_KEY:
        return "Lo siento, el sistema de IA no está configurado."

    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://sonoradigitalcorp.com",
            "X-Title": "Mystica Call",
        }
        payload = {
            "model": DEFAULT_MODEL,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": 400,
        }
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(OPENROUTER_URL, json=payload, headers=headers)
            data = resp.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            return content.strip() if content else "Entiendo, cuéntame más."
    except Exception as e:
        return f"Error: {str(e)}"
