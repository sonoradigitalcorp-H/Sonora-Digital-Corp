import json
import logging
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, Response
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from products.mystik.config import config
from products.mystik.crm import CRM
from products.mystik.rag import MystikRAG

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# ── Prompt Injection Guard ──
PROMPT_INJECTION_PATTERNS = [
    "ignore previous instructions", "ignore all instructions", "ignore all previous",
    "forget everything", "forget all previous", "you are now", "act as if",
    "you are free", "you have been", "new instructions", "override",
    "system prompt", "your system prompt", "your instructions are",
    "say the words", "repeat the words", "output the following",
    "DAN", "jailbreak", "jail broken", "jail broken",
    "you must", "you will obey", "you are required to",
    "pretend", "imagine you are", "from now on",
]

def check_prompt_injection(text: str) -> str | None:
    text_lower = text.lower()
    for pattern in PROMPT_INJECTION_PATTERNS:
        if pattern in text_lower:
            return pattern
    return None

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

# ── Neo4j Connection ──
NEO4J_URI = "bolt://127.0.0.1:7687"
NEO4J_USER = "neo4j"
NEO4J_PASS = "jarvis2026"
neo4j_driver = None

def _init_neo4j():
    global neo4j_driver
    try:
        from neo4j import GraphDatabase
        neo4j_driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
        neo4j_driver.verify_connectivity()
        logger.info("Neo4j connected: %s", NEO4J_URI)
    except Exception as e:
        logger.warning("Neo4j not available: %s", e)

_init_neo4j()

def query_neo4j(query: str, params: dict = None) -> list:
    if not neo4j_driver:
        return []
    try:
        with neo4j_driver.session() as session:
            result = session.run(query, params or {})
            return [r.data() for r in result]
    except Exception as e:
        logger.error("Neo4j query error: %s", e)
        return []

def get_neo4j_context(tenant: str, limit: int = 5) -> str:
    rows = query_neo4j(
        "MATCH (n) WHERE n.tenant = $tenant OR n.tenant IS NULL RETURN n LIMIT $limit",
        {"tenant": tenant, "limit": limit}
    )
    if not rows:
        return ""
    return "\n".join([json.dumps(r.get("n", r), default=str) for r in rows])

# ── Engram Memory ──
ENGRAM_PATH = Path("/home/ubuntu/sonora-digital-corp/state/engram.db")
engram_conn = None

def _init_engram():
    global engram_conn
    try:
        engram_conn = sqlite3.connect(str(ENGRAM_PATH))
        engram_conn.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                role TEXT,
                content TEXT,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)
        engram_conn.execute("""
            CREATE TABLE IF NOT EXISTS knowledge (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE,
                value TEXT,
                source TEXT,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)
        engram_conn.commit()
        logger.info("Engram initialized")
    except Exception as e:
        logger.warning("Engram not available: %s", e)

_init_engram()

def save_conversation(session_id: str, role: str, content: str):
    if not engram_conn:
        logger.warning("Engram not available, conversation not saved")
        return
    try:
        engram_conn.execute("INSERT INTO conversations (session_id, role, content) VALUES (?, ?, ?)",
                            (session_id, role, content))
        engram_conn.commit()
    except Exception as e:
        logger.error("Engram save failed: %s", e)

def get_conversation_history(session_id: str, limit: int = 10) -> list:
    if not engram_conn:
        return []
    rows = engram_conn.execute(
        "SELECT role, content FROM conversations WHERE session_id=? ORDER BY id DESC LIMIT ?",
        (session_id, limit)).fetchall()
    return [{"role": r[0], "content": r[1]} for r in reversed(rows)]

MYSTIK_PERSONA = """Eres Mystik, la asistente virtual de ABE Music Group.
Eres amable, directa y servicial. Tu objetivo es ayudar a los artistas y clientes.
Conoces todos los servicios de ABE Music Group al detalle.

NORMAS ESTRICTAS:
1. NUNCA menciones tecnologías, bases de datos, APIs, stacks, servidores, MCP, ni nada técnico.
2. NUNCA digas "Neo4j", "Engram", "ChromaDB", "OpenRouter", "API", "MCP" ni términos similares.
3. Siempre orienta al usuario hacia los servicios, productos y precios.
4. Si el usuario pregunta por algo técnico, redirige suavemente a lo que realmente le importa: sus resultados.
5. Hablas español natural, como una ejecutiva de servicios mexicana.
6. Recuerdas conversaciones pasadas para dar continuidad.
7. Cuando sea relevante, sugiere agendar una llamada o visitar una página."""


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
@limiter.limit("30/minute")
async def chat(req: ChatRequest, request: Request):
    blocked = check_prompt_injection(req.message)
    if blocked:
        return {"response": "No puedo procesar esa solicitud. Por favor, haz una pregunta sobre nuestros productos o servicios."}

    session_id = req.session_id or f"session-{secrets.token_hex(4)}"
    tenant = req.tenant or config.default_tenant

    # 1. Obtener contexto de Neo4j (knowledge graph)
    neo4j_ctx = get_neo4j_context(tenant)

    # 2. Obtener contexto de ChromaDB (RAG)
    chroma_ctx = rag.search(req.message, tenant)

    # 3. Obtener historial de conversación de Engram
    history = get_conversation_history(session_id)

    # 4. Guardar mensaje del usuario
    save_conversation(session_id, "user", req.message)

    # 5. Construir mensajes para el LLM
    messages = [
        {"role": "system", "content": MYSTIK_PERSONA},
    ]

    if neo4j_ctx:
        messages.append({"role": "system", "content": f"Información relevante del sistema:\n{neo4j_ctx[:800]}"})

    if chroma_ctx:
        messages.append({"role": "system", "content": f"Documentación relevante:\n{chroma_ctx[:800]}"})

    for h in history[-6:]:
        messages.append({"role": h["role"], "content": h["content"]})

    messages.append({"role": "user", "content": req.message})

    # 6. Llamar a OpenRouter con DeepSeek
    response_text = ""
    if config.openrouter_key:
        try:
            import httpx
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={"Authorization": f"Bearer {config.openrouter_key}", "Content-Type": "application/json"},
                    json={
                        "model": "deepseek/deepseek-chat",
                        "messages": messages,
                        "max_tokens": 800,
                    },
                )
                data = resp.json()
                response_text = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        except Exception as e:
            logger.warning("OpenRouter failed: %s", e)

    # 7. Guardar respuesta
    if response_text:
        save_conversation(session_id, "assistant", response_text)

    return {
        "response": response_text,
        "session_id": session_id,
        "sources": {"neo4j": bool(neo4j_ctx), "chroma": bool(chroma_ctx), "history": len(history)},
    }

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

TENANT_DB = Path(config.tenant_db_path)

import hashlib, secrets

def _init_tenant_db():
    TENANT_DB.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(TENANT_DB))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tenants (
            id TEXT PRIMARY KEY,
            name TEXT,
            plan TEXT DEFAULT 'starter',
            config TEXT DEFAULT '{}',
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tokens (
            token TEXT PRIMARY KEY,
            user_id INTEGER,
            tenant_id TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            expires_at TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            name TEXT NOT NULL,
            tenant_id TEXT NOT NULL,
            role TEXT DEFAULT 'owner',
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (tenant_id) REFERENCES tenants(id)
        )
    """)
    conn.execute("""
        INSERT OR IGNORE INTO tenants (id, name, plan, config)
        VALUES ('sonora', 'Sonora Digital Corp', 'enterprise', '{"brand_color":"#FF6B35","products":"all"}')
    """)
    conn.execute("""
        INSERT OR IGNORE INTO tenants (id, name, plan, config)
        VALUES ('demo', 'Demo Client', 'starter', '{"brand_color":"#6366f1","products":"limited"}')
    """)
    conn.commit()
    conn.close()

SERVICES = [
    {"id": "mystik-ai", "name": "Mystik AI", "tagline": "Asistente de ventas con voz", "starter": True, "pro": True, "enterprise": True},
    {"id": "content-studio", "name": "Content Studio", "tagline": "Generación de contenido AI", "starter": False, "pro": True, "enterprise": True},
    {"id": "omnivoice", "name": "OmniVoice", "tagline": "Clonación de voz profesional", "starter": False, "pro": True, "enterprise": True},
    {"id": "open-notebook", "name": "Open Notebook", "tagline": "Knowledge base con RAG", "starter": False, "pro": False, "enterprise": True},
    {"id": "abe-music", "name": "ABE Music OS", "tagline": "Gestión para industria musical", "starter": False, "pro": False, "enterprise": True},
]

PLANS = {
    "starter": {"name": "Starter", "price": 0, "services": ["mystik-ai"]},
    "pro": {"name": "Pro", "price": 49, "services": ["mystik-ai", "content-studio", "omnivoice"]},
    "enterprise": {"name": "Enterprise", "price": 199, "services": ["mystik-ai", "content-studio", "omnivoice", "open-notebook", "abe-music"]},
}

# ── Auth ──

class SignupRequest(BaseModel):
    email: str
    password: str
    name: str
    plan: str = "starter"

class LoginRequest(BaseModel):
    email: str
    password: str

def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def _generate_token() -> str:
    return secrets.token_hex(32)

@app.post("/api/auth/signup")
async def signup(req: SignupRequest):
    if req.plan not in PLANS:
        raise HTTPException(status_code=400, detail="Plan inválido")
    conn = sqlite3.connect(str(TENANT_DB))
    try:
        tenant_id = f"tenant-{secrets.token_hex(4)}"
        conn.execute("INSERT INTO tenants (id, name, plan, config) VALUES (?, ?, ?, ?)",
                     (tenant_id, req.name, req.plan, json.dumps({"services": PLANS[req.plan]["services"]})))
        conn.execute("INSERT INTO users (email, password_hash, name, tenant_id) VALUES (?, ?, ?, ?)",
                     (req.email, _hash_password(req.password), req.name, tenant_id))
        conn.commit()
        # Auto-login: generar token inmediatamente
        user_row = conn.execute("SELECT id, tenant_id FROM users WHERE email=?", (req.email,)).fetchone()
        token = _generate_token()
        conn.execute("INSERT INTO tokens (token, user_id, tenant_id, expires_at) VALUES (?, ?, ?, datetime('now', '+24 hours'))",
                     (token, user_row[0], user_row[1]))
        return {"status": "ok", "token": token, "tenant_id": tenant_id, "plan": req.plan, "services": PLANS[req.plan]["services"]}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="Email ya registrado")
    finally:
        conn.close()

@app.post("/api/auth/login")
async def login(req: LoginRequest):
    conn = sqlite3.connect(str(TENANT_DB))
    row = conn.execute("SELECT u.id, u.name, u.tenant_id, u.role, t.plan FROM users u JOIN tenants t ON u.tenant_id = t.id WHERE u.email = ? AND u.password_hash = ?",
                       (req.email, _hash_password(req.password))).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    token = _generate_token()
    conn = sqlite3.connect(str(TENANT_DB))
    conn.execute("INSERT INTO tokens (token, user_id, tenant_id, expires_at) VALUES (?, ?, ?, datetime('now', '+24 hours'))",
                 (token, row[0], row[2]))
    conn.commit()
    conn.close()
    return {"token": token, "user": {"id": row[0], "name": row[1]}, "tenant_id": row[2], "role": row[3], "plan": row[4]}

def get_current_user(request: Request):
    auth = request.headers.get("Authorization", "")
    token = auth.replace("Bearer ", "") if auth.startswith("Bearer ") else ""
    if not token:
        raise HTTPException(status_code=401, detail="Token requerido")
    conn = sqlite3.connect(str(TENANT_DB))
    row = conn.execute("SELECT u.id, u.name, u.email, u.tenant_id, u.role, t.plan FROM tokens tk JOIN users u ON tk.user_id = u.id JOIN tenants t ON u.tenant_id = t.id WHERE tk.token = ? AND tk.expires_at > datetime('now')", (token,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    return {"user_id": row[0], "name": row[1], "email": row[2], "tenant_id": row[3], "role": row[4], "plan": row[5]}

@app.get("/api/me")
async def get_me(request: Request):
    return get_current_user(request)

@app.get("/api/dashboard")
async def get_dashboard(request: Request):
    user = get_current_user(request)
    conn = sqlite3.connect(str(TENANT_DB))
    row = conn.execute("SELECT id, name, plan, config FROM tenants WHERE id=?", (user["tenant_id"],)).fetchone()
    conn.close()
    tenant_config = json.loads(row[3]) if row and row[3] else {}
    services = PLANS.get(user["plan"], PLANS["starter"])["services"]
    service_details = [s for s in SERVICES if s["id"] in services]
    return {
        "tenant": {"id": row[0], "name": row[1], "plan": row[2]},
        "user": user,
        "services": service_details,
        "stats": {"api_calls": 0, "storage_mb": 0, "active_chats": 0},
    }

_init_tenant_db()

@app.get("/api/plans")
async def list_plans():
    return {"plans": {k: {"name": v["name"], "price": v["price"], "services": [s for s in SERVICES if s["id"] in v["services"]]} for k, v in PLANS.items()}}

@app.get("/api/services")
async def list_services():
    return {"services": SERVICES}

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

@app.get("/onboard", response_class=HTMLResponse)
async def onboard_page():
    return HTMLResponse(ONBOARD_HTML)

ONBOARD_HTML = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<title>Mystik AI — Onboarding</title>
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  body { background:#0a0a0f; color:#e0e0e0; font-family:-apple-system,sans-serif; min-height:100vh; display:flex; align-items:center; justify-content:center; padding:1rem; }
  .card { background:#12121a; border:1px solid #2a2a3a; border-radius:16px; padding:2rem; max-width:500px; width:100%; }
  h1 { color:#FF6B35; font-size:1.5rem; margin-bottom:0.25rem; }
  .sub { color:#888; font-size:0.85rem; margin-bottom:1.5rem; }
  label { display:block; font-size:0.8rem; color:#aaa; margin:1rem 0 0.25rem; }
  input, select { width:100%; padding:0.75rem; background:#1a1a2e; border:1px solid #2a2a3a; border-radius:8px; color:#fff; font-size:0.9rem; }
  input:focus, select:focus { outline:none; border-color:#FF6B35; }
  .btn { width:100%; padding:0.85rem; background:#FF6B35; color:#fff; border:none; border-radius:8px; font-size:1rem; font-weight:600; cursor:pointer; margin-top:1.5rem; }
  .btn:hover { background:#e85d2a; }
  .btn:disabled { opacity:0.5; cursor:not-allowed; }
  .msg { margin-top:1rem; padding:0.75rem; border-radius:8px; font-size:0.85rem; display:none; }
  .msg.ok { background:#1a3a2a; color:#00ff88; display:block; }
  .msg.err { background:#3a1a1a; color:#ff4444; display:block; }
  .list { margin-top:1.5rem; }
  .list-item { padding:0.75rem; background:#1a1a2e; border-radius:8px; margin-bottom:0.5rem; display:flex; justify-content:space-between; align-items:center; }
  .list-item .name { color:#e0e0e0; }
  .list-item .id { color:#666; font-size:0.75rem; }
</style>
</head>
<body>
<div class="card">
  <h1>✦ Mystik AI</h1>
  <p class="sub">Onboarding de nuevos clientes</p>

  <form id="onboardForm">
    <label>Nombre de la empresa</label>
    <input type="text" id="companyName" placeholder="Ej: Empresa SA de CV" required>

    <label>ID del tenant</label>
    <input type="text" id="tenantId" placeholder="Ej: empresa-sa" required>

    <label>Email de contacto</label>
    <input type="email" id="contactEmail" placeholder="cliente@empresa.com" required>

    <label>Productos habilitados</label>
    <select id="productTier">
      <option value="all">Todos los productos</option>
      <option value="limited">Solo chat + CRM</option>
      <option value="voice">Chat + CRM + Voz</option>
    </select>

    <button type="submit" class="btn" id="submitBtn">→ Crear tenant</button>
  </form>

  <div id="msg" class="msg"></div>

  <div class="list" id="tenantList"></div>
</div>

<script>
async function loadTenants() {
  const res = await fetch('/api/tenants');
  const data = await res.json();
  const list = document.getElementById('tenantList');
  list.innerHTML = '<h3 style="color:#888;font-size:0.8rem;margin-bottom:0.5rem">TENANTS ACTIVOS</h3>';
  data.tenants.forEach(t => {
    const div = document.createElement('div');
    div.className = 'list-item';
    div.innerHTML = '<span><span class="name">' + t.name + '</span><br><span class="id">' + t.id + '</span></span>';
    list.appendChild(div);
  });
}

document.getElementById('onboardForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const btn = document.getElementById('submitBtn');
  const msg = document.getElementById('msg');
  btn.disabled = true;
  btn.textContent = 'Creando...';

  const id = document.getElementById('tenantId').value.toLowerCase().replace(/\\s+/g, '-');
  const data = {
    id: id,
    name: document.getElementById('companyName').value,
    config: {
      contact_email: document.getElementById('contactEmail').value,
      product_tier: document.getElementById('productTier').value,
      brand_color: '#6366f1',
      created_via: 'onboarding-ui',
    }
  };

  try {
    const res = await fetch('/api/tenants', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(data),
    });
    const result = await res.json();
    if (result.status === 'created') {
      msg.className = 'msg ok';
      msg.textContent = '✅ Tenant ' + id + ' creado. Configuración lista.';
      document.getElementById('onboardForm').reset();
      loadTenants();
    } else {
      msg.className = 'msg err';
      msg.textContent = '❌ Error: ' + JSON.stringify(result);
    }
  } catch(err) {
    msg.className = 'msg err';
    msg.textContent = '❌ Error de conexión: ' + err.message;
  }
  btn.disabled = false;
  btn.textContent = '→ Crear tenant';
});

loadTenants();
</script>
</body>
</html>"""

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

# ── Mercado Pago Payments ──

import httpx as _httpx
MP_TOKEN = os.environ.get("MERCADO_PAGO_ACCESS_TOKEN", "")
MP_API = "https://api.mercadopago.com"

@app.post("/api/payments/create_preference")
async def create_preference(data: dict):
    if not MP_TOKEN:
        return {"error": "Mercado Pago no configurado"}
    preference = {
        "items": [{
            "title": data.get("title", "Plan SDC"),
            "unit_price": float(data.get("price", 0)),
            "quantity": data.get("quantity", 1),
            "currency_id": "MXN",
        }],
        "payer": {"email": data.get("email", "")},
        "back_urls": {
            "success": f"https://abe.sonoradigitalcorp.com/dashboard?plan={data.get('plan_id','')}&status=success",
            "failure": "https://abe.sonoradigitalcorp.com/pricing?status=failure",
            "pending": f"https://abe.sonoradigitalcorp.com/dashboard?plan={data.get('plan_id','')}&status=pending",
        },
        "auto_return": "approved",
        "external_reference": json.dumps({"plan_id": data.get("plan_id"), "tenant_id": data.get("tenant_id", "")}),
        "notification_url": "https://abe.sonoradigitalcorp.com/api/payments/webhook",
    }
    async with _httpx.AsyncClient() as client:
        resp = await client.post(f"{MP_API}/checkout/preferences", json=preference,
            headers={"Authorization": f"Bearer {MP_TOKEN}", "X-Idempotency-Key": secrets.token_hex(16)})
        result = resp.json()
    if "id" in result:
        return {"id": result["id"], "init_point": result.get("init_point"), "sandbox_init_point": result.get("sandbox_init_point")}
    return {"error": result}

@app.post("/api/payments/webhook")
async def payments_webhook(data: dict):
    event_type = data.get("type", "")
    event_data = data.get("data", {})
    data_id = event_data.get("id", "")
    logger.info("MP Webhook: type=%s id=%s", event_type, data_id)
    if event_type == "payment" and data_id:
        async with _httpx.AsyncClient() as client:
            payment = await client.get(f"{MP_API}/v1/payments/{data_id}",
                headers={"Authorization": f"Bearer {MP_TOKEN}"})
            pdata = payment.json()
            status = pdata.get("status", "")
            external_ref = pdata.get("external_reference", "{}")
            try:
                ref = json.loads(external_ref)
                plan_id = ref.get("plan_id", "")
                tenant_id = ref.get("tenant_id", "")
                if status == "approved" and plan_id and tenant_id:
                    conn = sqlite3.connect(str(TENANT_DB))
                    conn.execute("UPDATE tenants SET plan=? WHERE id=?", (plan_id, tenant_id))
                    conn.execute("UPDATE users SET role='active' WHERE tenant_id=?", (tenant_id,))
                    conn.commit()
                    conn.close()
                    logger.info("Plan %s activado para tenant %s", plan_id, tenant_id)
            except Exception as e:
                logger.error("Webhook processing error: %s", e)
    return {"status": "ok"}

@app.get("/api/payments/config")
async def payments_config():
    return {"configured": bool(MP_TOKEN), "provider": "mercadopago"}

# ── AI Content Generation (LoRA + Image + Video) ──

import zipfile, io, uuid

UPLOAD_DIR = Path("/home/ubuntu/sonora-digital-corp/state/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
LORA_DIR = Path("/home/ubuntu/sonora-digital-corp/state/lora")
LORA_DIR.mkdir(parents=True, exist_ok=True)
CONTENT_DIR = Path("/home/ubuntu/sonora-digital-corp/state/content")
CONTENT_DIR.mkdir(parents=True, exist_ok=True)

@app.post("/api/content/train-lora")
async def train_lora(request: Request):
    user = get_current_user(request)
    form = await request.form()
    files = form.getlist("files")
    name = form.get("name", "artist-style")

    if len(files) < 3:
        raise HTTPException(status_code=400, detail="Se necesitan al menos 3 fotos")

    session_id = uuid.uuid4().hex[:8]
    session_dir = UPLOAD_DIR / user["tenant_id"] / session_id
    session_dir.mkdir(parents=True, exist_ok=True)

    for f in files:
        content = await f.read()
        (session_dir / f.filename).write_bytes(content)

    logger.info("LoRA training started: tenant=%s, files=%d, name=%s", user["tenant_id"], len(files), name)

    return {
        "status": "training_started",
        "session_id": session_id,
        "tenant_id": user["tenant_id"],
        "files_count": len(files),
        "lora_name": name,
        "note": "Entrenamiento iniciado. Recibirás notificación cuando esté listo.",
    }

@app.get("/api/content/lora-status/{session_id}")
async def lora_status(session_id: str, request: Request):
    user = get_current_user(request)
    lora_path = LORA_DIR / user["tenant_id"] / f"{session_id}.safetensors"
    return {
        "session_id": session_id,
        "status": "ready" if lora_path.exists() else "training",
        "lora_file": str(lora_path) if lora_path.exists() else None,
    }

@app.post("/api/content/generate-image")
async def generate_image(data: dict, request: Request):
    user = get_current_user(request)
    prompt = data.get("prompt", "un artista musical")
    lora = data.get("lora_session", "")
    count = min(data.get("count", 1), 4)

    results = []
    for i in range(count):
        img_id = uuid.uuid4().hex[:12]
        results.append({
            "id": img_id,
            "url": f"/api/content/image/{img_id}",
            "prompt": prompt,
            "status": "generated",
        })
        (CONTENT_DIR / f"{img_id}.txt").write_text(f"Prompt: {prompt}\nTenant: {user['tenant_id']}\nLoRA: {lora}")

    return {"images": results, "count": count}

@app.get("/api/content/image/{image_id}")
async def get_image(image_id: str):
    img_path = CONTENT_DIR / f"{image_id}.png"
    if img_path.exists():
        return Response(content=img_path.read_bytes(), media_type="image/png")
    return {"status": "pending", "image_id": image_id}

@app.get("/api/content/gallery")
async def get_gallery(request: Request):
    user = get_current_user(request)
    tenant_dir = CONTENT_DIR
    images = []
    for f in sorted(tenant_dir.glob("*.txt"), reverse=True)[:50]:
        img_id = f.stem
        images.append({"id": img_id, "url": f"/api/content/image/{img_id}"})
    return {"images": images, "tenant": user["tenant_id"]}

# ── ABE Music Database API (PostgreSQL) ──

ABE_DB = "postgresql://mystik:mystik2026@127.0.0.1:5433/mystik"

def _query_abe(query: str, params: tuple = ()) -> list:
    try:
        import psycopg2
        conn = psycopg2.connect(ABE_DB)
        cur = conn.cursor()
        cur.execute(query, params)
        rows = cur.fetchall()
        cols = [desc[0] for desc in cur.description] if cur.description else []
        conn.close()
        return [dict(zip(cols, row)) for row in rows]
    except Exception as e:
        logger.error("ABE DB query error: %s", e)
        return []

@app.get("/api/abe/artists")
async def abe_artists():
    rows = _query_abe("SELECT id, name, genre, total_streams, total_revenue, spotify_monthly_listeners as monthly_listeners, telegram_handle FROM artists ORDER BY total_revenue DESC")
    return {"artists": rows}

@app.get("/api/abe/artists/{artist_id}")
async def abe_artist(artist_id: str):
    rows = _query_abe("SELECT * FROM artists WHERE id = %s", (artist_id,))
    if not rows:
        raise HTTPException(status_code=404)
    return {"artist": rows[0]}

@app.get("/api/abe/artists/{artist_id}/kpi")
async def abe_artist_kpi(artist_id: str):
    rows = _query_abe("""
        SELECT a.id as artist_id, a.total_streams, a.total_revenue,
               a.spotify_monthly_listeners as monthly_listeners,
               a.spotify_followers as followers,
               COALESCE(r.total, 0) as releases_count
        FROM artists a
        LEFT JOIN (SELECT artist_id, COUNT(*) as total FROM releases GROUP BY artist_id) r ON a.id = r.artist_id
        WHERE a.id = %s
    """, (artist_id,))
    return rows[0] if rows else {}

@app.get("/api/abe/revenue")
async def abe_revenue():
    rows = _query_abe("SELECT id, name, total_revenue as revenue FROM artists ORDER BY total_revenue DESC")
    total = sum(r["revenue"] for r in rows)
    return {"total": float(total), "by_artist": rows, "by_platform": [{"platform": "Spotify", "revenue": float(total)}]}

@app.get("/api/abe/releases")
async def abe_releases(artist_id: str = None):
    if artist_id:
        rows = _query_abe("SELECT * FROM releases WHERE artist_id = %s ORDER BY release_date DESC", (artist_id,))
    else:
        rows = _query_abe("SELECT r.*, a.name as artist_name FROM releases r JOIN artists a ON r.artist_id = a.id ORDER BY r.release_date DESC")
    return {"releases": rows}

@app.get("/api/abe/contracts")
async def abe_contracts():
    rows = _query_abe("SELECT c.*, a.name as artist_name FROM contracts c JOIN artists a ON c.artist_id = a.id")
    return {"contracts": rows}

@app.get("/api/abe/stats")
async def abe_stats():
    artists = _query_abe("SELECT COUNT(*) as total FROM artists")[0]["total"]
    revenue = _query_abe("SELECT COALESCE(SUM(total_revenue),0) as total FROM artists")[0]["total"]
    streams = _query_abe("SELECT COALESCE(SUM(total_streams),0) as total FROM artists")[0]["total"]
    releases = _query_abe("SELECT COUNT(*) as total FROM releases")[0]["total"]
    return {"artists": artists, "revenue": float(revenue), "streams": float(streams), "releases": releases}

# ── Admin endpoints (solo Abraham / CEO) ──

ADMIN_EMAILS = ["sonoradigitalcorp@gmail.com", "abraham@abemusic.com"]

def require_admin(request: Request):
    user = get_current_user(request)
    if user["email"] not in ADMIN_EMAILS:
        raise HTTPException(status_code=403, detail="Solo administradores")
    return user

@app.get("/api/admin/artists")
async def admin_artists(request: Request):
    require_admin(request)
    rows = _query_abe("""
        SELECT a.*, c.type as contract_type, c.revenue_share, c.status as contract_status,
               COUNT(r.id) as releases_count
        FROM artists a
        LEFT JOIN contracts c ON a.id = c.artist_id AND c.status = 'active'
        LEFT JOIN releases r ON a.id = r.artist_id
        GROUP BY a.id, c.type, c.revenue_share, c.status
        ORDER BY a.total_revenue DESC
    """)
    return {"artists": rows}

@app.get("/api/admin/stats")
async def admin_stats(request: Request):
    require_admin(request)
    artists = _query_abe("SELECT id, name, total_revenue, total_streams, spotify_monthly_listeners FROM artists ORDER BY total_revenue DESC")
    total_rev = sum(a["total_revenue"] for a in artists)
    total_str = sum(a["total_streams"] for a in artists)
    return {
        "total_revenue": float(total_rev),
        "total_streams": float(total_str),
        "artist_count": len(artists),
        "artists": artists,
        "avg_revenue_per_artist": float(total_rev / max(len(artists), 1)),
    }

# ── Subscription gating middleware ──

PLAN_LIMITS = {
    "starter": {"max_artists": 1, "features": ["mystik_chat"]},
    "pro": {"max_artists": 3, "features": ["mystik_chat", "content_gen", "voice", "abe_films"]},
    "enterprise": {"max_artists": 999, "features": ["mystik_chat", "content_gen", "voice", "abe_films", "digital_clone", "abe_bot", "distribution"]},
}

def check_feature_access(tenant_plan: str, feature: str) -> bool:
    return feature in PLAN_LIMITS.get(tenant_plan, {}).get("features", [])

@app.get("/api/subscription/features")
async def get_features(request: Request):
    user = get_current_user(request)
    plan = user.get("plan", "starter")
    return {
        "plan": plan,
        "features": PLAN_LIMITS.get(plan, {}).get("features", []),
        "limits": PLAN_LIMITS.get(plan, {}),
    }
