import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from products.mystik.config import config
from products.mystik.crm import CRM
from products.mystik.rag import MystikRAG

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute", "20/minute"])
app = FastAPI(title="Mystik AI", version="1.0.0", docs_url="/api/docs")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

ALLOWED_ORIGINS = [
    "https://mystik.sonoradigitalcorp.com",
    "http://mystik.sonoradigitalcorp.com",
    "http://127.0.0.1:3210",
    "http://localhost:3210",
    "http://127.0.0.1:5200",
    "http://localhost:5200",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Tenant-ID"],
)

if not os.environ.get("TESTING"):
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=[
            "mystik.sonoradigitalcorp.com",
            "*.sonoradigitalcorp.com",
            "127.0.0.1",
            "localhost",
            "testserver",
            "testclient",
        ],
    )

crm = CRM()
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
@limiter.limit("10/minute")
async def chat(req: ChatRequest, request: Request):
    tenant = req.tenant or config.default_tenant
    context = rag.search(req.message, tenant)

    prompt = f"{MYSTIK_PERSONA}\n\nContexto del cliente ({tenant}):\n{context}\n\nMensaje: {req.message}\n\nResponde como Mystik:"

    # Try cloud LLM if API key available
    response_text = ""
    if config.openrouter_key:
        try:
            import httpx
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={"Authorization": f"Bearer {config.openrouter_key}", "Content-Type": "application/json"},
                    json={
                        "model": config.llm_model,
                        "messages": [
                            {"role": "system", "content": MYSTIK_PERSONA},
                            {"role": "user", "content": f"Contexto ({tenant}):\n{context}\n\n{req.message}"},
                        ],
                        "max_tokens": 500,
                    },
                )
                data = resp.json()
                response_text = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        except Exception as e:
            logger.warning("OpenRouter failed: %s", e)

    # Template fallback (no LLM needed)
    if not response_text:
        msg = req.message.lower()
        for p in PRODUCT_CATALOG:
            if p["id"] in msg or p["name"].lower() in msg:
                response_text = f"{p['name']}: {p['description']}. Precio: {p['price']}. ¿Te gustaría saber más o agendar una demo?"
                break
        if not response_text:
            response_text = "Soy Mystik, tu asistente de ventas de Sonora Digital Corp. Tenemos Content Studio, OmniVoice, Open Notebook, ABE Music OS y más. ¿Qué producto te interesa?"

    return {
        "response": response_text,
        "tenant": tenant,
        "products": PRODUCT_CATALOG if any(p["name"].lower() in req.message.lower() for p in PRODUCT_CATALOG) else [],
    }


@app.post("/api/leads")
@limiter.limit("30/minute")
async def create_lead(req: LeadRequest, request: Request):
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

# ── Voice Endpoints ──

@app.get("/api/voice/speak")
async def speak_get(text: str = "Hola, soy Mystik"):
    from products.mystik.voice import voice
    audio = await voice.speak(text)
    if not audio:
        return {"status": "error", "detail": "TTS no disponible"}
    from fastapi.responses import Response
    return Response(content=audio, media_type="audio/wav")

@app.post("/api/voice/speak")
async def speak_post(data: dict):
    text = data.get("text", "Hola, soy Mystik")
    from products.mystik.voice import voice
    audio = await voice.speak(text)
    if not audio:
        return {"status": "error", "detail": "TTS no disponible"}
    from fastapi.responses import Response
    return Response(content=audio, media_type="audio/wav")

@app.get("/api/voice/sample")
async def voice_sample():
    return {"note": "Descarga un sample de voz femenina en español desde:",
            "url": "https://huggingface.co/datasets/GianDiego/latam-spanish-speech-orpheus-tts-24khz",
            "o tambien": "https://huggingface.co/datasets/javi22/high_quality_spanish_speech",
            "instrucciones": "Descarga un clip WAV de 3-10s, luego POST a /api/voice/clone con el archivo"}

@app.post("/api/voice/clone")
async def clone_voice(file: bytes, name: str = "mystik"):
    from products.mystik.voice import voice
    profile_id = await voice.clone_voice(file, name)
    if profile_id:
        return {"status": "ok", "profile_id": profile_id}
    return {"status": "error", "detail": "No se pudo clonar la voz"}

@app.post("/api/voice/transcribe")
async def transcribe(file: bytes):
    from products.mystik.voice import voice
    text = await voice.transcribe(file)
    return {"text": text}

# ── Multi-tenant Config Store ──

import json, sqlite3
TENANT_DB = Path(config.tenant_db_path)

def _init_tenant_db():
    TENANT_DB.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(TENANT_DB))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tenants (
            id TEXT PRIMARY KEY,
            name TEXT,
            config TEXT DEFAULT '{}',
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.execute("""
        INSERT OR IGNORE INTO tenants (id, name, config)
        VALUES ('sonora', 'Sonora Digital Corp', '{"brand_color":"#FF6B35","llm_model":"cohere/north-mini-code:free","products":"all"}')
    """)
    conn.execute("""
        INSERT OR IGNORE INTO tenants (id, name, config)
        VALUES ('demo', 'Demo Client', '{"brand_color":"#6366f1","llm_model":"cohere/north-mini-code:free","products":"limited"}')
    """)
    conn.commit()
    conn.close()

_init_tenant_db()

@app.get("/api/tenants")
async def list_tenants():
    conn = sqlite3.connect(str(TENANT_DB))
    rows = conn.execute("SELECT id, name, config FROM tenants").fetchall()
    conn.close()
    return {"tenants": [{"id": r[0], "name": r[1], "config": json.loads(r[2])} for r in rows]}

@app.post("/api/tenants")
async def create_tenant(data: dict):
    conn = sqlite3.connect(str(TENANT_DB))
    conn.execute("INSERT OR REPLACE INTO tenants (id, name, config) VALUES (?, ?, ?)",
                 (data["id"], data.get("name", data["id"]), json.dumps(data.get("config", {}))))
    conn.commit()
    conn.close()
    return {"status": "created", "id": data["id"]}

@app.get("/api/tenants/{tenant_id}")
async def get_tenant(tenant_id: str):
    conn = sqlite3.connect(str(TENANT_DB))
    row = conn.execute("SELECT id, name, config FROM tenants WHERE id=?", (tenant_id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return {"id": row[0], "name": row[1], "config": json.loads(row[2])}

# ── Agent Bus — Contexto compartido entre agentes via Redis ──

import asyncio
REDIS_CTX_PREFIX = "agent:ctx:"

def _get_redis():
    try:
        import redis as r
        return r.Redis(host="127.0.0.1", port=6380, decode_responses=True, socket_connect_timeout=2)
    except Exception:
        return None

@app.post("/api/context")
async def set_context(data: dict):
    key = data.get("key")
    value = data.get("value")
    ttl = data.get("ttl", 3600)
    if not key:
        raise HTTPException(status_code=400, detail="key required")
    r = _get_redis()
    if r:
        r.setex(f"{REDIS_CTX_PREFIX}{key}", ttl, json.dumps(value))
        r.publish("agent:context", json.dumps({"key": key, "updated_at": datetime.now(timezone.utc).isoformat()}))
        return {"status": "shared", "key": key}
    return {"status": "stored_local", "key": key}

@app.get("/api/context")
async def list_context():
    r = _get_redis()
    if r:
        keys = r.keys(f"{REDIS_CTX_PREFIX}*")
        result = []
        for k in keys:
            val = r.get(k)
            if val:
                try:
                    result.append({"key": k.replace(REDIS_CTX_PREFIX, ""), "value": json.loads(val)})
                except Exception:
                    result.append({"key": k.replace(REDIS_CTX_PREFIX, ""), "value": val})
        return {"context": result}
    return {"context": [], "note": "Redis unavailable"}

@app.get("/api/context/{key}")
async def get_context(key: str):
    r = _get_redis()
    if r:
        val = r.get(f"{REDIS_CTX_PREFIX}{key}")
        if val:
            try:
                return {"key": key, "value": json.loads(val)}
            except Exception:
                return {"key": key, "value": val}
        raise HTTPException(status_code=404, detail="Context key not found")
    raise HTTPException(status_code=503, detail="Redis unavailable")

# ── Agent Bus — Comunicación entre agentes ──

@app.post("/api/agent-bus/send")
async def agent_send(data: dict):
    target = data.get("target", "all")
    command = data.get("command", "ping")
    payload = data.get("payload", {})
    r = _get_redis()
    if r:
        msg = json.dumps({
            "target": target, "command": command, "payload": payload,
            "sender": "mystik", "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        r.publish("agent:commands", msg)
        r.publish("agent:messages", msg)
        return {"status": "sent", "target": target, "command": command}
    return {"status": "redis_unavailable", "note": "Mensaje no enviado"}

@app.get("/api/agent-bus/status")
async def agent_bus_status():
    r = _get_redis()
    return {
        "redis": r is not None,
        "channels": ["agent:messages", "agent:context", "agent:events", "agent:commands"],
        "context_keys_count": len(r.keys(f"{REDIS_CTX_PREFIX}*")) if r else 0,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
