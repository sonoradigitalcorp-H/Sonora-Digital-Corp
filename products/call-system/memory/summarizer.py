import json
import os
import httpx

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "opencode-go/deepseek-v4-flash"

SUMMARY_PROMPT = """Eres un analizador de llamadas. Genera un resumen estructurado de esta conversación.

Formato JSON:
{
  "summary": "Resumen de 2-3 oraciones de lo que pasó",
  "action_items": ["Acción 1", "Acción 2"],
  "sentiment": "positivo|neutral|negativo",
  "topics": ["tema1", "tema2"],
  "resolution": "resuelto|resuelto_parcial|no_resuelto",
  "objections_detected": ["objeción1"] o [],
  "lead_score_change": +5 o -3 o 0 (numérico),
  "key_points": ["punto1", "punto2"]
}

Responde SOLO con el JSON, sin explicaciones adicionales."""


async def generate_summary(transcript, tenant, duration_sec):
    if not OPENROUTER_API_KEY:
        return fallback_summary(tenant, duration_sec)

    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://sonoradigitalcorp.com",
            "X-Title": "Mystica Call Summary",
        }

        payload = {
            "model": DEFAULT_MODEL,
            "messages": [
                {"role": "system", "content": SUMMARY_PROMPT},
                {"role": "user", "content": f"Cliente: {tenant.get('name', 'Desconocido')}\nEmpresa: {tenant.get('company', '')}\nDuración: {duration_sec}s\n\nTranscripción:\n{transcript}"},
            ],
            "temperature": 0.1,
            "max_tokens": 500,
        }

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(OPENROUTER_URL, json=payload, headers=headers)
            data = resp.json()
            content = data["choices"][0]["message"]["content"].strip()
            if content.startswith("```"):
                content = content.split("\n", 1)[1].rsplit("\n", 1)[0]
            return json.loads(content)
    except Exception as e:
        return fallback_summary(tenant, duration_sec, str(e))


def fallback_summary(tenant, duration_sec, error=""):
    return {
        "summary": f"Llamada de {duration_sec}s con {tenant.get('name', 'Desconocido')}. Revisar transcripción para detalles.",
        "action_items": ["Revisar transcripción completa"],
        "sentiment": "neutral",
        "topics": ["general"],
        "resolution": "no_resuelto",
        "objections_detected": [],
        "lead_score_change": 0,
        "key_points": [f"Duración: {duration_sec}s"],
    }
