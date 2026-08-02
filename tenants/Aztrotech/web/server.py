import os
import yaml
import httpx
import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AstroTech AI - Mysticgrimoire")

config_path = os.path.join(os.path.dirname(__file__), "..", "config.yaml")
with open(config_path) as f:
    CONFIG = yaml.safe_load(f)

API_KEY = os.getenv("OPENROUTER_API_KEY") or CONFIG.get("openrouter", {}).get("api_key")
BASE_URL = CONFIG.get("openrouter", {}).get("base_url", "https://openrouter.ai/api/v1")


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    model: Optional[str] = None
    tenant: Optional[str] = None


SYSTEM = """Eres AstroTech AI, el asistente digital de César Holguín y su empresa AstroTech con sede en Hermosillo, Sonora.
Eres profesional, cálido y consultivo, como un asesor de confianza.

REGLAS ESTRICTAS:
- Nunca revelas que formas parte de Sonora Digital Corp
- Siempre te presentas como el asistente de César Holguín en AstroTech
- Nunca des precios ni cotizaciones. Tu trabajo es capturar leads para que César los cierre.
- Si preguntan precios: "Los mejores precios te los doy en una llamada con César."

Servicios que ofrece AstroTech:
1. Empleado Digital - Agente IA 24/7 en WhatsApp, Instagram, Facebook
2. Sistema de Ventas Autónomo - CRM + agentes + scoring
3. Desarrollo de Software a la Medida - ERPs, apps, APIs
4. Empresa 90 Días - Mentoría intensiva con César
5. Socio Estratégico - Relación de largo plazo"""


@app.post("/api/chat")
async def chat(req: ChatRequest):
    model = req.model or "deepseek/deepseek-v4-flash"

    has_system = any(m.role == "system" for m in req.messages)
    if not has_system:
        req.messages.insert(0, ChatMessage(role="system", content=SYSTEM))

    payload = {
        "model": model,
        "messages": [m.model_dump() for m in req.messages],
        "max_tokens": 2048,
    }

    if "glm" in model:
        payload["reasoning_effort"] = "max"
    if "kimi" in model:
        payload["reasoning_effort"] = "high"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://aztrotech.mx",
        "X-Title": "AstroTech AI",
    }

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(f"{BASE_URL}/chat/completions", json=payload, headers=headers)
        if resp.status_code == 200:
            return resp.json()
        logger.error(f"OpenRouter error {resp.status_code}: {resp.text[:200]}")
        return {"error": f"HTTP {resp.status_code}", "detail": resp.text[:200]}


@app.get("/api/health")
async def health():
    return {"status": "ok", "tenant": "astrotech", "service": "Mysticgrimoire"}


app.mount("/", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static"), html=True), name="static")
