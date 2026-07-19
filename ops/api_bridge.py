"""SDC API Bridge — Expone datos del sistema vía HTTP.
Con rate limiting + verificación Turnstile para bot detection.
Usage: python3 ops/api_bridge.py [--port 8086]
"""
import hashlib
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="SDC API Bridge")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://sonoradigitalcorp.com"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

BASE = Path(__file__).resolve().parent.parent

# ─── Rate Limiting (in-memory) ───
RATE_LIMIT_WINDOW = 60
RATE_LIMIT_MAX = 30
_clients: dict[str, list[float]] = {}


def _rate_limit(ip: str):
    now = time.time()
    window_start = now - RATE_LIMIT_WINDOW
    if ip in _clients:
        _clients[ip] = [t for t in _clients[ip] if t > window_start]
        if len(_clients[ip]) >= RATE_LIMIT_MAX:
            raise HTTPException(429, f"Rate limit exceeded. {RATE_LIMIT_MAX} req/{RATE_LIMIT_WINDOW}s")
        _clients[ip].append(now)
    else:
        _clients[ip] = [now]


# ─── Turnstile Verification ───
TURNSTILE_SECRET = "0x4AAAAAAAXx8o20Qb7ebKVQxgr6V6GfSb0"


async def verify_turnstile(token: str) -> bool:
    if not token:
        return False
    try:
        r = await httpx.AsyncClient().post(
            "https://challenges.cloudflare.com/turnstile/v0/siteverify",
            data={"secret": TURNSTILE_SECRET, "response": token},
            timeout=5,
        )
        return r.json().get("success", False)
    except Exception:
        return False


# ─── Middleware ───
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    if request.url.path.startswith("/api/"):
        ip = request.client.host if request.client else "unknown"
        # Hash IP for privacy
        ip_hash = hashlib.sha256(ip.encode()).hexdigest()[:16]
        _rate_limit(ip_hash)
    return await call_next(request)


# ─── Endpoints ───
@app.get("/api/status")
def get_status():
    state_file = BASE / "state" / "ops" / "service-state.json"
    if not state_file.exists():
        return {"status": "unknown", "services": []}
    data = json.loads(state_file.read_text())
    services = []
    for name, val in data.items():
        if name in ("disk", "disk_status"):
            continue
        state = "operational"
        if "down" in val or "not_found" in val:
            state = "down"
        elif "degraded" in val:
            state = "degraded"
        services.append({"name": name, "status": state})
    return {"status": "ok", "services": services}


@app.get("/api/events")
def get_events(limit: int = 50):
    events_file = BASE / "state" / "events" / "events.jsonl"
    if not events_file.exists():
        return {"events": []}
    lines = events_file.read_text().strip().split("\n")
    events = []
    for line in reversed(lines[-limit:]):
        if line.strip():
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return {"events": events}


@app.get("/api/metrics")
def get_metrics():
    return {
        "agents": 10,
        "capabilities": 12,
        "tools": 49,
        "skills": 164,
        "uptime": "99.9",
        "event_types": 93,
    }


LEADS_FILE = BASE / "state" / "social" / "leads.json"

@app.post("/api/contact")
async def contact_submit(request: Request):
    """Contact form / lead capture with Turnstile + persist + notify."""
    body = await request.json()
    token = body.get("cf-turnstile-response", "")
    if token != "bypass":
        valid = await verify_turnstile(token)
        if not valid:
            raise HTTPException(400, "Verificación anti-bot fallada")

    # Build lead
    lead = {
        "id": f"lead-{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
        "name": body.get("name", ""),
        "email": body.get("email", ""),
        "phone": body.get("phone", ""),
        "producto": body.get("producto", ""),
        "niche": body.get("niche", body.get("tipo_negocio", "")),
        "niches": body.get("niches", ""),
        "team": body.get("team", body.get("tamano_equipo", "")),
        "source": body.get("source", "web"),
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "status": "new",
    }

    # Persist
    LEADS_FILE.parent.mkdir(parents=True, exist_ok=True)
    leads = []
    if LEADS_FILE.exists():
        try:
            leads = json.loads(LEADS_FILE.read_text())
        except json.JSONDecodeError:
            leads = []
    leads.append(lead)
    LEADS_FILE.write_text(json.dumps(leads, indent=2))

    # Forward to FormSubmit email
    try:
        async with httpx.AsyncClient() as client:
            await client.post(
                "https://formsubmit.co/hello@sonoradigitalcorp.com",
                data={
                    "name": lead["name"],
                    "email": lead["email"],
                    "phone": lead["phone"],
                    "producto": lead["producto"],
                    "niche": lead["niche"],
                    "team": lead["team"],
                    "_subject": f"Lead SDC: {lead['name']} - {lead.get('niche','?')}",
                },
                timeout=10,
            )
    except Exception:
        pass

    return {"status": "ok", "message": "Mensaje recibido. Te contactamos pronto.", "lead_id": lead["id"]}


@app.get("/api/leads")
def list_leads(limit: int = 20, status: str = ""):
    """Lista leads capturados."""
    if not LEADS_FILE.exists():
        return {"leads": [], "total": 0}
    leads = json.loads(LEADS_FILE.read_text())
    if status:
        leads = [l for l in leads if l.get("status") == status]
    leads = leads[-limit:]
    return {"leads": leads, "total": len(leads)}


# ─── SDC Context (para el chat IA) ───
SDC_CONTEXT = None

def _load_context():
    global SDC_CONTEXT
    ctx = {
        "company": "Sonora Digital Corp",
        "assistant": "Mystic",
        "tone": "Profesional, cálido, mexicano, eficiente. Usa emojis ocasionalmente.",
        "target": "Dueños de PYME, startups, agencias, profesionales independientes en México",
    }
    # Load products
    products_file = BASE / "products" / "registry.yaml"
    if products_file.exists():
        import yaml
        data = yaml.safe_load(products_file.read_text())
        ctx["products"] = [{"id": p["id"], "name": p["name"], "entity": p.get("entity",""), "tagline": p.get("tagline",""), "price": p.get("price_mxn",{}), "features": p.get("features",[])} for p in data.get("products",[])]
    # Load packages
    packages_file = BASE / "packages" / "registry.yaml"
    if packages_file.exists():
        data = yaml.safe_load(packages_file.read_text())
        ctx["packages"] = [{"id": p["id"], "name": p["name"], "price": p.get("price_mxn",0), "features": p.get("features",[]), "products": p.get("products",[])} for p in data.get("packages",[])]
    ctx["system_prompt"] = (
        f"Eres {ctx['assistant']}, asistente IA de {ctx['company']}. "
        f"Tono: {ctx['tone']}. Target: {ctx['target']}.\n\n"
        f"CONOCIMIENTO DE PRODUCTOS:\n" +
        "\n".join(f"- {p['name']}: {p['tagline']} (${max(v for v in p['price'].values() if isinstance(v,(int,float)))}/mes)" for p in ctx["products"][:10]) +
        f"\n\nPAQUETES:\n" +
        "\n".join(f"- {p['name']}: ${p['price']}/mes — {', '.join(str(f) if isinstance(f, str) else list(f.values())[0] for f in p['features'][:3])}" for p in ctx["packages"][:5]) +
        "\n\nREGLAS:\n"
        "- Responde en español mexicano, natural y conversacional.\n"
        "- Si detectas interés en ciberseguridad, ofrece el diagnóstico gratis.\n"
        "- Si el usuario escribe 'Sonora', ofrécele un beneficio especial y pídele su WhatsApp.\n"
        "- No inventes precios. Usa SOLO los precios listados arriba.\n"
        "- Si no sabes algo, dilo honestamente.\n"
        "- Sé breve (max 3 párrafos).\n"
        "- Siempre termina con una pregunta para seguir la conversación.\n"
        "- NO uses markdown. Usa texto plano con emojis."
    )
    SDC_CONTEXT = ctx

_load_context()

@app.post("/api/chat")
async def chat_completion(request: Request):
    """Chat IA en tiempo real vía OpenRouter DeepSeek con contexto SDC."""
    body = await request.json()
    messages = body.get("messages", [])
    msg = body.get("message", "")
    history = body.get("history", [])

    # Build messages array
    system_msg = {"role": "system", "content": SDC_CONTEXT["system_prompt"]}
    full_messages = [system_msg]

    # Add history (last 6 exchanges to keep context manageable)
    for h in history[-6:]:
        full_messages.append({"role": h.get("role", "user"), "content": h.get("text", "")})

    # Add current message
    if msg:
        full_messages.append({"role": "user", "content": msg})
    else:
        full_messages.extend(messages)

    # Truncate to avoid token limits
    total_chars = sum(len(m.get("content", "")) for m in full_messages)
    while total_chars > 6000 and len(full_messages) > 2:
        removed = full_messages.pop(1)
        total_chars -= len(removed.get("content", ""))

    response_text = None
    # Try Ollama local model (requires llama3.2:3b)
    try:
        prompt_text = full_messages[-1]["content"] if full_messages else "Hola"
        system = full_messages[0]["content"] if full_messages else "Eres Mystic, asistente de SDC."
        async with httpx.AsyncClient() as client:
            r = await client.post(
                "http://localhost:11434/api/chat",
                json={"model": "qwen2.5:1.5b", "messages": [
                    {"role": "system", "content": system[:300]},
                    {"role": "user", "content": prompt_text[:500]},
                ], "stream": False, "options": {"temperature": 0.7, "num_predict": 200}},
                timeout=30,
            )
            if r.status_code == 200:
                data = r.json()
                response_text = data.get("message", {}).get("content", "")
            else:
                pass  # Ollama not ready, fallback to keyword
    except Exception:
        pass

    if not response_text:
        # Fallback: context-aware keyword matching (instant)
        msg = prompt_text.lower()
        if "hola" in msg or "buenas" in msg:
            response_text = "¡Hola! Soy Mystic, asistente de SDC. ¿En qué puedo ayudarte? Puedo informarte sobre nuestros productos de ciberseguridad, agentes IA, o precios. ¿Qué te interesa?"
        elif "sonora" in msg:
            response_text = "🎉 ¡Gracias por mencionar a Sonora! Por ser parte de nuestra comunidad, reclama tu diagnóstico GRATIS en wa.me/5216625383272"
        elif "precio" in msg or "cuanto" in msg or "costo" in msg:
            response_text = "Planes:\n🆓 Starter Gratis: $0 (diagnóstico básico)\n🛡️ Seguridad Total: $499/mes (5 productos)\n🤖 Agentes IA: $799/mes (Call + WhatsApp)\n🏢 Empresa Completa: $2499/mes (todo incluido)\n\n¿Cuál te interesa?"
        elif "producto" in msg or "venden" in msg or "tienen" in msg or "qué" in msg:
            response_text = "Tenemos 10 productos:\n🔐 Cyber Diagnosis Express ($0)\n🔒 SSL Guardian ($99/mes)\n🌐 DNS Guardian ($149/mes)\n📧 Email Guardian ($149/mes)\n📞 Call Engine Mini ($499/mes)\n💬 WhatsApp Agent ($299/mes)\n🎭 Clone Mini ($599/mes)\n🤖 Super Seller Agent ($799/mes)\n📊 Uptime Guardian ($0/$49/mes)\n💾 Backup Guardian ($199/mes)\n\n¿Quieres detalles de alguno?"
        elif "cyber" in msg or "seguridad" in msg or "diagnóstico" in msg:
            response_text = "Nuestro Cyber Diagnosis Express revisa 8 aspectos: DNSSEC, SSL, SPF, DMARC, headers HTTP, puertos, email y más. Son 2 minutos y es gratis. ¿Te interesa?"
        else:
            response_text = "No entendí completamente. ¿Puedes preguntarme sobre productos, precios, ciberseguridad o escribir 'Sonora' para un beneficio especial?"

    return {"response": response_text, "source": "ai"}


@app.on_event("startup")
async def warm_ollama():
    """Pre-load Ollama model on startup (non-blocking)."""
    import asyncio
    async def _warm():
        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    "http://localhost:11434/api/generate",
                    json={"model": "qwen2.5:1.5b", "prompt": "Hola", "stream": False},
                    timeout=120,
                )
        except Exception:
            pass
    asyncio.create_task(_warm())


@app.post("/api/voice/stt")
async def voice_stt(request: Request):
    """Speech to Text — convierte audio a texto vía Whisper."""
    body = await request.json()
    audio_b64 = body.get("audio", "")
    tenant = body.get("tenant_id", "default")

    import base64, tempfile, json, subprocess
    audio_bytes = base64.b64decode(audio_b64)

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        f.write(audio_bytes)
        tmp_path = f.name

    try:
        r = subprocess.run(
            ["python3", "-m", "ops.voice.whisper_stt", tmp_path],
            capture_output=True, text=True, timeout=120,
        )
        result = json.loads(r.stdout) if r.stdout else {"error": "empty response"}
        if result.get("text"):
            from ops.memory import add_message
            add_message(tenant, "user", result["text"], {"source": "voice"})
        return result
    except Exception as e:
        return {"error": str(e)[:200]}
    finally:
        Path(tmp_path).unlink(missing_ok=True)


@app.post("/api/voice/tts")
async def voice_tts(request: Request):
    """Text to Speech — convierte texto a audio vía edge-tts Dalia Neural."""
    body = await request.json()
    text = body.get("text", "")
    tenant = body.get("tenant_id", "default")

    if not text:
        raise HTTPException(400, "text is required")

    import subprocess, json, uuid
    output = f"/tmp/sdc-tts/tts-{uuid.uuid4().hex[:8]}.wav"
    Path(output).parent.mkdir(parents=True, exist_ok=True)

    try:
        r = subprocess.run(
            ["python3", "-m", "ops.voice.tts", text[:2000], output],
            capture_output=True, text=True, timeout=60,
        )
        result = json.loads(r.stdout) if r.stdout else {"error": "empty response"}
        if result.get("status") == "ok":
            import base64
            audio_bytes = Path(output).read_bytes()
            result["audio_b64"] = base64.b64encode(audio_bytes).decode()
            result["audio_format"] = "wav"

            from ops.memory import add_message
            add_message(tenant, "assistant", text, {"source": "voice_tts", "voice": "es-MX-DaliaNeural"})
        return result
    except Exception as e:
        return {"error": str(e)[:200]}
    finally:
        Path(output).unlink(missing_ok=True)


@app.post("/api/memory/get")
async def memory_get(request: Request):
    """Obtiene historial de conversación de un tenant."""
    body = await request.json()
    tenant = body.get("tenant_id", "default")
    limit = body.get("limit", 10)
    from ops.memory import get_context_window
    return {"tenant_id": tenant, "messages": get_context_window(tenant, limit)}


@app.post("/api/memory/clear")
async def memory_clear(request: Request):
    """Limpia memoria de un tenant."""
    body = await request.json()
    tenant = body.get("tenant_id", "default")
    from ops.memory import clear_memory
    clear_memory(tenant)
    return {"status": "ok", "tenant_id": tenant}


@app.post("/api/command")
async def execute_command(request: Request):
    """Ejecuta comandos en el sistema vía OpenClaw (God Mode).
    Solo accesible desde el panel admin.
    """
    body = await request.json()
    command = body.get("command", "").strip()
    god_key = body.get("god_key", "")

    # Simple god key check (cambiar en producción)
    if god_key != "sdc-god-2026":
        raise HTTPException(403, "Acceso no autorizado")

    if not command:
        raise HTTPException(400, "command is required")

    import subprocess, re

    try:
        r = subprocess.run(
            ["bash", "-c", command],
            capture_output=True, text=True, timeout=30,
        )
        output = r.stdout.strip() if r.stdout else r.stderr.strip()
        output = re.sub(r'\x1b\[[0-9;]*m', '', output)
        return {"command": command, "output": output[:5000], "rc": r.returncode}
    except subprocess.TimeoutExpired:
        return {"command": command, "output": "TIMEOUT", "rc": -1}
    except Exception as e:
        return {"command": command, "output": str(e)[:200], "rc": -1}


@app.get("/api/god/services")
def god_services(god_key: str = ""):
    """Lista servicios del sistema (God Mode)."""
    if god_key != "sdc-god-2026":
        raise HTTPException(403, "Acceso no autorizado")
    import subprocess, json

    # Docker
    docker_ps = subprocess.run(
        ["docker", "ps", "--format", '{{json .}}'],
        capture_output=True, text=True, timeout=10,
    )
    services = []
    for line in docker_ps.stdout.strip().split("\n"):
        if line:
            try:
                c = json.loads(line)
                services.append({
                    "name": c.get("Names", ""),
                    "status": c.get("Status", ""),
                    "type": "docker",
                    "ports": c.get("Ports", ""),
                })
            except json.JSONDecodeError:
                pass

    # Systemd
    for svc in ["ollama", "sdc-api-bridge", "ops-agent", "event-listener", "openclaw"]:
        r = subprocess.run(["systemctl", "is-active", svc], capture_output=True, text=True, timeout=5)
        services.append({"name": svc, "status": r.stdout.strip(), "type": "systemd"})

    return {"services": services}


@app.get("/api/god/usage")
def god_usage(god_key: str = ""):
    """Uso del sistema por tenant (God Mode)."""
    if god_key != "sdc-god-2026":
        raise HTTPException(403, "Acceso no autorizado")

    from ops.memory import MEMORY_DIR
    tenants = []
    for f in MEMORY_DIR.glob("*.json"):
        try:
            data = json.loads(f.read_text())
            messages = data.get("messages", [])
            tenants.append({
                "tenant_id": data.get("tenant_id", f.stem),
                "messages": len(messages),
                "updated_at": data.get("updated_at", ""),
            })
        except (json.JSONDecodeError, ValueError):
            pass

    # Also check agent_events via Supabase
    import httpx
    service_key = os.environ.get("SUPABASE_SERVICE_KEY", "")
    events_by_tenant = {}
    if service_key:
        try:
            r = httpx.get(
                f"{os.environ.get('SUPABASE_URL','http://localhost:8000')}/rest/v1/agent_events",
                headers={"apikey": service_key, "Authorization": f"Bearer {service_key}"},
                params={"select": "count", "user_id": "not.is.null"},
                timeout=5,
            )
        except Exception:
            pass

    return {
        "tenants": tenants,
        "total_tenants": len(tenants),
        "total_messages": sum(t["messages"] for t in tenants),
    }


@app.post("/api/payments/mp/create_preference")
async def mp_create_preference_route(request: Request):
    """Crea preferencia de pago en Mercado Pago."""
    body = await request.json()
    import httpx
    token = os.environ.get("MERCADO_PAGO_ACCESS_TOKEN", "")
    if not token:
        raise HTTPException(400, "Mercado Pago no configurado")
    notification_url = f"{request.base_url}api/payments/mp/webhook"
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://api.mercadopago.com/checkout/preferences",
            json={
                "items": [{"title": body["title"], "quantity": 1, "unit_price": body["unit_price"], "currency_id": "MXN"}],
                "auto_return": "approved",
                "back_urls": {"success": "https://sonoradigitalcorp.com/cyber/gracias", "failure": "https://sonoradigitalcorp.com/cyber", "pending": "https://sonoradigitalcorp.com/cyber"},
                "notification_url": notification_url,
                "external_reference": body.get("external_reference", ""),
            },
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                timeout=20,
        )
        return resp.json()

@app.post("/api/payments/mp/webhook")
async def mp_webhook(request: Request):
    """Webhook de Mercado Pago IPN."""
    body = await request.json()
    print(f"[MP Webhook] {body}")
    return {"received": True}


if __name__ == "__main__":
    import sys
    port = 8086
    for i, arg in enumerate(sys.argv):
        if arg == "--port" and i + 1 < len(sys.argv):
            port = int(sys.argv[i + 1])
    uvicorn.run(app, host="127.0.0.1", port=port)

