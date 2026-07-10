import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel

from products.mystik.config import config
from products.mystik.crm import TwentyCRM
from products.mystik.rag import MystikRAG

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="Mystik AI", version="1.0.0", docs_url="/api/docs")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

crm = TwentyCRM()
rag = MystikRAG()

MYSTIK_PERSONA = """Eres Mystik, la asistente de ventas de Sonora Digital Corp.
Eres directa, conocedora, y ligeramente irreverente pero profesional.
Conoces todos los productos de SDC al detalle.
Tu misión es calificar leads, presentar productos, y cerrar ventas.
Hablas español natural, como una ejecutiva de ventas mexicana."""


class ChatRequest(BaseModel):
    message: str
    tenant: str = ""
    session_id: str = ""


class LeadRequest(BaseModel):
    name: str
    email: str
    company: str = ""
    phone: str = ""
    source: str = "mystik-web"
    tenant: str = "sonora"


class QualifyRequest(BaseModel):
    tenant: str = "sonora"


PRODUCT_CATALOG = [
    {"id": "content-studio", "name": "Content Studio", "description": "Generación de imágenes, TTS, talking heads, OCR y edición vía MCP", "price": "desde $0.03/request"},
    {"id": "omnivoice", "name": "OmniVoice", "description": "Clonación de voz AI y síntesis multi-idioma", "price": "desde $0.01/segundo"},
    {"id": "open-notebook", "name": "Open Notebook", "description": "RAG sobre documentos, PDFs, web. Alternativa open-source a NotebookLM", "price": "desde $50/mes"},
    {"id": "abe-music", "name": "ABE Music OS", "description": "Gestión de artistas, revenue, contratos y CRM para la industria musical", "price": "desde $200/mes"},
    {"id": "mystik-ai", "name": "Mystik AI", "description": "Asistente de ventas AI con voz y texto. Mobile-first, multi-tenant.", "price": "consultar"},
]


@app.get("/health")
async def health():
    return {"status": "ok", "service": "mystik-ai", "version": "1.0.0"}


@app.get("/api/products")
async def list_products():
    return {"products": PRODUCT_CATALOG}


@app.post("/api/chat")
async def chat(req: ChatRequest):
    tenant = req.tenant or config.default_tenant
    context = rag.search(req.message, tenant)

    prompt = f"{MYSTIK_PERSONA}\n\nContexto del cliente ({tenant}):\n{context}\n\nMensaje: {req.message}\n\nResponde como Mystik:"

    try:
        import httpx
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{config.ollama_host}/api/generate",
                json={"model": config.llm_model, "prompt": prompt, "stream": False},
            )
            data = resp.json()
            response_text = data.get("response", "Lo siento, no pude procesar eso.")
    except Exception as e:
        logger.error("LLM error: %s", e)
        response_text = "Estoy teniendo problemas para conectar con mi cerebro. ¿Podrías intentar de nuevo?"

    return {
        "response": response_text,
        "tenant": tenant,
        "products": PRODUCT_CATALOG if any(p["name"].lower() in req.message.lower() for p in PRODUCT_CATALOG) else [],
    }


@app.post("/api/leads")
async def create_lead(req: LeadRequest):
    try:
        lead = crm.create_lead(req.model_dump())
        return {"status": "created", "lead": lead}
    except Exception as e:
        logger.error("CRM error: %s", e)
        return {"status": "error", "detail": str(e)}


@app.get("/api/leads")
async def list_leads(tenant: str = "sonora"):
    try:
        leads = crm.list_leads(tenant)
        return {"leads": leads}
    except Exception as e:
        return {"leads": [], "error": str(e)}


@app.post("/api/leads/{lead_id}/qualify")
async def qualify_lead(lead_id: str, req: QualifyRequest):
    try:
        result = crm.qualify(lead_id, req.tenant)
        return {"status": "qualified", "result": result}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


@app.post("/api/knowledge")
async def search_knowledge(query: str, tenant: str = "sonora"):
    results = rag.search(query, tenant)
    return {"query": query, "results": results}


@app.get("/api/tenant/{tenant_id}/config")
async def tenant_config(tenant_id: str):
    return {
        "tenant": tenant_id,
        "products": PRODUCT_CATALOG,
        "branding": {"name": "Mystik AI", "color": "#FF6B35"},
    }


@app.get("/", response_class=HTMLResponse)
async def root():
    return HTMLResponse("""
    <!DOCTYPE html>
    <html><head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <title>Mystik AI</title>
    <style>
      body { margin:0; background:#0a0a0f; color:#e0e0e0;
             font-family:-apple-system,sans-serif; display:flex;
             align-items:center; justify-content:center; height:100vh; }
      .card { text-align:center; }
      h1 { color:#FF6B35; font-size:2.5rem; }
      .sub { color:#888; font-size:1rem; }
    </style></head><body>
    <div class="card">
      <h1>✦ Mystik AI</h1>
      <p class="sub">Asistente de ventas inteligente</p>
      <p style="margin-top:2rem;font-size:0.8rem;color:#555">
        API: /api/docs · Chat: :3210</p>
    </div></body></html>
    """)
