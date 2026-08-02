import json
import os
import sys
import httpx

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "opencode-go/deepseek-v4-flash"

TENANTS_PROFILE = {
    "abe-music": {
        "contact": "Abraham Ortega",
        "phone": "5216623538272",
        "niche": "music",
        "benefit": "Automatizar booking de artistas + marketing WhatsApp para cada músico",
        "offer": "Un bot por artista que reserva eventos, distribuye música y contesta fans 24/7",
    },
    "astrotech": {
        "contact": "César Holguín",
        "phone": "5216623538272",
        "niche": "technology",
        "benefit": "Multiplicar su capacidad de atención con agentes IA",
        "offer": "Clon digital de su voz para llamadas + agente IA en su web",
    },
    "nathy-conta": {
        "contact": "Nathy",
        "phone": "5216622681111",
        "niche": "finance",
        "benefit": "Dejar de contestar las mismas preguntas fiscales todos los días",
        "offer": "Agente WhatsApp que responde dudas CFDI/SAT mientras ella hace declaraciones",
    },
    "el-joyero": {
        "contact": "Dueño",
        "phone": "",
        "niche": "retail",
        "benefit": "Vender 24/7 aunque la tienda esté cerrada",
        "offer": "Catálogo WhatsApp automático + agente de ventas IA",
    },
}


async def generate_message(tenant_id):
    profile = TENANTS_PROFILE.get(tenant_id)
    if not profile:
        return None

    prompt = f"""Eres Mystica, asistente de Sonora Digital Corp.
Genera un mensaje de WhatsApp personalizado para {profile['contact']} de {tenant_id}.

Contexto: Ya son clientes/partners. El objetivo es ofrecerles una NUEVA capacidad.

Su beneficio: {profile['benefit']}
Lo que ofreces: {profile['offer']}

REGLAS:
- Tono cálido, personal, como de colega a colega
- Menciona que ya usan SDC y esto es una evolución natural
- No más de 3 oraciones
- Termina con una pregunta abierta
- Idioma: español MX

Mensaje:"""

    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://sonoradigitalcorp.com",
            "X-Title": "Mystica Outreach",
        }
        payload = {
            "model": DEFAULT_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 200,
        }
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(OPENROUTER_URL, json=payload, headers=headers)
            data = resp.json()
            return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"Hola {profile['contact']}, soy Mystica de SDC. Tenemos una nueva capacidad para {profile['niche']} que creo te puede interesar. ¿Te comparto más información?"


def get_tenant_phone(tenant_id):
    profile = TENANTS_PROFILE.get(tenant_id, {})
    return profile.get("phone", "")


def get_tenant_contact(tenant_id):
    profile = TENANTS_PROFILE.get(tenant_id, {})
    return profile.get("contact", tenant_id)


def get_all_tenant_ids():
    return list(TENANTS_PROFILE.keys())
