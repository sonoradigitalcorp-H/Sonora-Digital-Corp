"""Demo Auth & Platform API — para testear la plataforma SDC.

Endpoints:
  POST /api/demo/login       → { token, user }
  POST /api/demo/register    → { token, user }
  GET  /api/demo/agents      → { agents: [...] }
  POST /api/demo/buy         → { license }
  GET  /api/demo/me          → { user }
"""

import json
import hashlib
import hmac
import time
import uuid
from typing import Optional

USERS = {}  # email -> { name, email, phone, company, created_at, tokens }
AGENTS_DB = [
    {
        "id": "voice-agent",
        "name": "Voice Agent",
        "icon": "🎙️",
        "price": 149,
        "price_label": "/licencia/mes",
        "description": "Asistente telefónico IA 24/7. Recibe llamadas, agenda citas, califica leads.",
        "features": [
            "STT → Intent Router → TTS en tiempo real",
            "Detección de emociones por voz",
            "Soundscapes ambientales dinámicos",
            "Routing inteligente por departamento",
            "Agenda automatizada de citas",
            "Reportes semanales de llamadas"
        ],
        "status": "live",
        "tech_stack": ["Mystic Voice Engine", "Whisper STT", "DeepSeek V4 Flash", "Custom TTS"],
        "documentation": "/docs/voice-agent",
    },
    {
        "id": "crm-agent",
        "name": "CRM Agent",
        "icon": "📊",
        "price": 99,
        "price_label": "/licencia/mes",
        "description": "Pipeline de ventas inteligente con scoring y automatización.",
        "features": [
            "Captura automática de leads multi-canal",
            "Lead scoring por plan de interés y fuente",
            "Generación de propuestas personalizadas",
            "Pipeline Neo4j: lead → qualified → proposal → won/lost",
            "Gamificación con XP y badges",
            "Dashboard de ventas en tiempo real"
        ],
        "status": "live",
        "tech_stack": ["Neo4j Graph DB", "Lead Scorer", "Proposal Generator", "Sales Pipeline"],
        "documentation": "/docs/crm-agent",
    },
    {
        "id": "x-agent",
        "name": "X Agent",
        "icon": "🐦",
        "price": 79,
        "price_label": "/licencia/mes",
        "description": "Automatización de redes sociales con IA generativa.",
        "features": [
            "Programación inteligente de contenido",
            "Generación de posts con IA",
            "Análisis de tendencias en tiempo real",
            "Respuestas automáticas contextuales",
            "Métricas de engagement",
            "Multi-cuenta y programación visual"
        ],
        "status": "coming",
        "tech_stack": ["Content Engine", "Trend Analyzer", "Scheduler", "Analytics API"],
        "documentation": "/docs/x-agent",
    },
    {
        "id": "bundle",
        "name": "Bundle Completo",
        "icon": "📦",
        "price": 299,
        "price_label": "/licencia/mes (ahorra 40%)",
        "description": "Todos los agentes + white-label API + soporte prioritario.",
        "features": [
            "Voice Agent incluido",
            "CRM Agent incluido",
            "X Agent incluido",
            "API White-label completa",
            "Soporte prioritario 24/7",
            "Onboarding dedicado",
            "Webhooks y customizaciones"
        ],
        "status": "live",
        "tech_stack": ["Full Stack MCP", "White-label API", "Multi-tenant DB"],
        "documentation": "/docs/bundle",
    }
]

SECRET = "sdc-demo-secret-2026"


def _make_token(email: str) -> str:
    ts = int(time.time())
    payload = f"{email}:{ts}"
    sig = hmac.new(SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()[:16]
    return f"{payload}:{sig}"


def _verify_token(token: str) -> Optional[str]:
    try:
        parts = token.split(":")
        email = parts[0]
        ts = int(parts[1])
        sig_check = hmac.new(SECRET.encode(), f"{email}:{ts}".encode(), hashlib.sha256).hexdigest()[:16]
        if sig_check == parts[2] and time.time() - ts < 86400:  # 24h expiry
            return email
    except:
        pass
    return None


async def demo_login(email: str, password: str) -> str:
    # Check registered users
    if email in USERS:
        u = USERS[email]
        if u.get("password") == password:
            token = _make_token(email)
            return json.dumps({
                "token": token,
                "user": {
                    "name": u["name"],
                    "email": email,
                    "company": u.get("company", ""),
                    "phone": u.get("phone", ""),
                    "licenses": u.get("licenses", []),
                    "demo": False
                }
            })
        return json.dumps({"error": "Contraseña incorrecta"})
    
    return json.dumps({"error": "Usuario no encontrado. Crea una cuenta primero."})


async def demo_register(name: str, email: str, password: str, phone: str = "", company: str = "") -> str:
    if not email or not password:
        return json.dumps({"error": "Email y password requeridos"})
    if "@" not in email:
        return json.dumps({"error": "Email inválido"})
    
    token = _make_token(email)
    USERS[email] = {
        "name": name or email.split("@")[0],
        "email": email,
        "password": password,
        "phone": phone,
        "company": company or "Mi Empresa",
        "created_at": time.time(),
        "licenses": [],
    }
    
    return json.dumps({
        "token": token,
        "user": {
            "name": USERS[email]["name"],
            "email": email,
            "company": USERS[email]["company"],
            "phone": phone,
            "licenses": [],
            "demo": False,
        }
    })


async def demo_agents() -> str:
    return json.dumps({"agents": AGENTS_DB})


async def demo_buy(token: str, agent_id: str) -> str:
    email = _verify_token(token)
    if not email:
        return json.dumps({"error": "Token inválido o expirado"})
    
    agent = next((a for a in AGENTS_DB if a["id"] == agent_id), None)
    if not agent:
        return json.dumps({"error": "Agente no encontrado"})
    
    if agent["status"] == "coming":
        return json.dumps({"error": "Agente próximamente", "agent_id": agent_id})
    
    # "Comprar" licencia
    license_id = f"LIC-{uuid.uuid4().hex[:8].upper()}"
    
    if email in USERS:
        USERS[email].setdefault("licenses", []).append({
            "agent_id": agent_id,
            "status": "active",
            "clients": 1,
            "revenue": agent["price"],
            "license_id": license_id
        })
    
    return json.dumps({
        "success": True,
        "license": {
            "id": license_id,
            "agent_id": agent_id,
            "agent_name": agent["name"],
            "price": agent["price"],
            "status": "active",
            "purchased_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        },
        "message": f"✅ Licencia {agent['name']} adquirida"
    })


async def demo_me(token: str) -> str:
    email = _verify_token(token)
    if not email:
        return json.dumps({"error": "Token inválido"})
    
    if email in USERS:
        u = USERS[email]
        return json.dumps({
            "user": {
                "name": u["name"],
                "email": email,
                "company": u["company"],
                "phone": u["phone"],
                "licenses": u["licenses"],
                "demo": False
            }
        })
    
    return json.dumps({"error": "Usuario no encontrado"})
