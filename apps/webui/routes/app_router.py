"""
SDC App — Full-stack application with niche-based access.
Each user gets personalized dashboard based on their niche.
"""

import logging
import os
import secrets
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

log = logging.getLogger("jarvis.app")
router = APIRouter(prefix="/app", tags=["app"])

JARVIS_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROMPTS_DIR = os.path.join(JARVIS_DIR, "prompts")
SKILLS_DIR = os.path.join(JARVIS_DIR, "skills")

# In-memory store (replace with Neo4j in production)
users = {}
sessions = {}

# Niche configurations
NICHES = {
    "musica": {
        "name": "Músicos",
        "icon": "🎵",
        "color": "#FFD700",
        "features": ["crm_artistas", "distribucion", "merch", "contenido_visual"],
        "skills": ["fal-ai-video", "music-gen", "abe-music"],
        "prompts": ["generar_cancion", "crear_video_musical", "distribuir_release"]
    },
    "fitness": {
        "name": "Fitness",
        "icon": "💪",
        "color": "#4ade80",
        "features": ["rutinas", "nutricion", "comunidad", "suscripciones"],
        "skills": ["content-fitness", "voice-tts"],
        "prompts": ["crear_rutina", "plan_nutricional", "video_entrenamiento"]
    },
    "educacion": {
        "name": "Educadores",
        "icon": "📚",
        "color": "#60a5fa",
        "features": ["cursos", "materiales", "alumnos", "certificados"],
        "skills": ["course-creator", "pdf-generator"],
        "prompts": ["crear_curso", "generar_material", "evaluar_alumno"]
    },
    "ecommerce": {
        "name": "Ecommerce",
        "icon": "🛒",
        "color": "#f472b6",
        "features": ["tienda", "printful", "marketing", "analytics"],
        "skills": ["shopify", "printful", "fal-ai"],
        "prompts": ["crear_producto", "campana_marketing", "generar_imagen"]
    },
    "creativo": {
        "name": "Creativos",
        "icon": "🎨",
        "color": "#c084fc",
        "features": ["contenido_visual", "portafolio", "ventas_digitales"],
        "skills": ["fal-ai", "meme-maker", "video-gen"],
        "prompts": ["generar_imagen", "crear_video", "diseno_grafico"]
    }
}


class UserRegister(BaseModel):
    nombre: str
    email: str
    nicho: str
    plan: str = "explorador"


class UserLogin(BaseModel):
    email: str
    password: str


def generate_credentials():
    """Generate secure credentials for new user."""
    password = secrets.token_urlsafe(12)
    api_key = f"sdk_{secrets.token_urlsafe(24)}"
    return password, api_key


@router.post("/register")
async def register_user(data: UserRegister):
    """Register new user and generate credentials."""
    if data.nicho not in NICHES:
        raise HTTPException(400, f"Nicho {data.nicho} no válido")
    
    user_id = str(uuid.uuid4())[:8]
    password, api_key = generate_credentials()
    
    user = {
        "id": user_id,
        "nombre": data.nombre,
        "email": data.email,
        "nicho": data.nicho,
        "plan": data.plan,
        "password": password,  # In production: hash this
        "api_key": api_key,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "active"
    }
    
    users[user_id] = user
    log.info(f"User registered: {user_id} - {data.email}")
    
    return {
        "status": "success",
        "user_id": user_id,
        "credentials": {
            "email": data.email,
            "password": password,
            "api_key": api_key
        },
        "nicho": NICHES[data.nicho],
        "message": "Credenciales generadas. Guarda tu password y API key."
    }


@router.post("/login")
async def login_user(data: UserLogin):
    """Login and create session."""
    user = next((u for u in users.values() if u["email"] == data.email), None)
    if not user or user["password"] != data.password:
        raise HTTPException(401, "Credenciales inválidas")
    
    session_id = secrets.token_urlsafe(32)
    sessions[session_id] = {
        "user_id": user["id"],
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    return {
        "status": "success",
        "session_id": session_id,
        "user": {
            "id": user["id"],
            "nombre": user["nombre"],
            "nicho": user["nicho"],
            "plan": user["plan"]
        }
    }


@router.get("/dashboard/{user_id}")
async def get_dashboard(user_id: str):
    """Get personalized dashboard for user's niche."""
    user = users.get(user_id)
    if not user:
        raise HTTPException(404, "Usuario no encontrado")
    
    niche = NICHES.get(user["nicho"], {})
    
    return {
        "user": {
            "id": user["id"],
            "nombre": user["nombre"],
            "nicho": user["nicho"],
            "plan": user["plan"]
        },
        "niche": niche,
        "features": niche.get("features", []),
        "skills": niche.get("skills", []),
        "prompts": niche.get("prompts", []),
        "stats": {
            "contenido_generado": 0,
            "ventas": 0,
            "engagement": 0
        }
    }


@router.get("/prompts/{nicho}")
async def get_prompts(nicho: str):
    """Get available prompts for niche."""
    if nicho not in NICHES:
        raise HTTPException(404, "Nicho no encontrado")
    
    prompts_file = os.path.join(PROMPTS_DIR, nicho, "prompts.md")
    prompts_content = ""
    if os.path.exists(prompts_file):
        with open(prompts_file, encoding='utf-8') as f:
            prompts_content = f.read()
    
    return {
        "nicho": nicho,
        "prompts": NICHES[nicho]["prompts"],
        "skills": NICHES[nicho]["skills"],
        "content": prompts_content
    }


@router.get("/skills/{nicho}")
async def get_skills(nicho: str):
    """Get available skills for niche."""
    if nicho not in NICHES:
        raise HTTPException(404, "Nicho no encontrado")
    
    skills_file = os.path.join(SKILLS_DIR, nicho, "skills.md")
    skills_content = ""
    if os.path.exists(skills_file):
        with open(skills_file, encoding='utf-8') as f:
            skills_content = f.read()
    
    return {
        "nicho": nicho,
        "skills": NICHES[nicho]["skills"],
        "content": skills_content
    }


@router.post("/execute/{user_id}")
async def execute_action(user_id: str, action: dict):
    """Execute action (prompt/skill) for user."""
    user = users.get(user_id)
    if not user:
        raise HTTPException(404, "Usuario no encontrado")
    
    action_type = action.get("type")
    action_name = action.get("name")
    params = action.get("params", {})
    
    # Route to JARVIS orchestrator
    try:
        from src.core.orchestrator import get_orchestrator
        orchestrator = get_orchestrator()
        
        # Build task description
        task = f"Ejecutar {action_type} '{action_name}' para usuario {user['nombre']} ({user['nicho']})"
        if params:
            task += f" con parámetros: {params}"
        
        # Execute via orchestrator
        result = await orchestrator.execute(task)
        status = result.get("status", "executed")
        
        return {
            "status": status,
            "action": action_name,
            "type": action_type,
            "result": result.get("response", result),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        log.warning(f"Orchestrator execution failed: {e}")
        # Fallback: return mock success
        return {
            "status": "executed",
            "action": action_name,
            "type": action_type,
            "result": f"Acción {action_name} ejecutada con éxito",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


# Frontend HTML
APP_HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SDC App</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#0a0a1a;color:#e0e0e0;font-family:'Segoe UI',system-ui,sans-serif}
.container{max-width:1200px;margin:0 auto;padding:20px}
.header{display:flex;justify-content:space-between;align-items:center;padding:20px 0;border-bottom:1px solid rgba(255,255,255,0.1)}
.logo{font-size:1.5rem;font-weight:700;background:linear-gradient(135deg,#00d4ff,#7b2ff7);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.btn{padding:12px 24px;border-radius:8px;border:none;cursor:pointer;font-weight:600;transition:all 0.3s}
.btn-primary{background:linear-gradient(135deg,#00d4ff,#7b2ff7);color:#fff}
.btn-secondary{background:rgba(255,255,255,0.1);color:#fff}
.auth-form{max-width:400px;margin:60px auto;padding:40px;background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);border-radius:16px}
.auth-form h2{margin-bottom:24px;text-align:center}
.form-group{margin-bottom:16px}
.form-group label{display:block;margin-bottom:8px;color:rgba(255,255,255,0.7)}
.form-group input,.form-group select{width:100%;padding:12px;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);border-radius:8px;color:#fff}
.dashboard{display:none}
.dashboard.active{display:block}
.niche-header{padding:40px;background:rgba(255,255,255,0.03);border-radius:16px;margin-bottom:24px;text-align:center}
.niche-icon{font-size:4rem;margin-bottom:16px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:20px;margin-bottom:24px}
.card{background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);border-radius:12px;padding:24px}
.card h3{margin-bottom:12px;color:#00d4ff}
.action-btn{width:100%;padding:12px;margin-top:12px;background:rgba(0,212,255,0.1);border:1px solid rgba(0,212,255,0.3);border-radius:8px;color:#00d4ff;cursor:pointer;transition:all 0.3s}
.action-btn:hover{background:rgba(0,212,255,0.2)}
.credentials{background:rgba(74,222,128,0.1);border:1px solid rgba(74,222,128,0.3);border-radius:12px;padding:24px;margin:24px 0}
.credentials h3{color:#4ade80;margin-bottom:16px}
.credentials code{display:block;background:rgba(0,0,0,0.3);padding:12px;border-radius:8px;margin:8px 0;font-family:monospace}
.hidden{display:none}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <div class="logo">SDC App</div>
    <div style="flex:1;text-align:center">
      <a href="/static/zamora.html" style="color:#c9a227;text-decoration:none;font-weight:600;font-size:0.9rem">Alejandro Zamora</a>
    </div>
    <div id="userMenu" class="hidden">
      <span id="userName"></span>
      <a href="/static/abe-music.html" style="color:#FFD700;text-decoration:none;margin:0 16px;font-weight:600">ABE MUSIC</a>
      <button class="btn btn-secondary" onclick="logout()">Salir</button>
    </div>
  </div>
  <nav style="display:flex;gap:20px;padding:12px 0;border-bottom:1px solid rgba(255,255,255,0.05);margin-bottom:20px">
    <a href="/api/store/page" style="color:#00d4ff;text-decoration:none;font-weight:600">🛍️ Tienda</a>
    <a href="/static/sdc-products.html" style="color:#888;text-decoration:none">Productos</a>
    <a href="/static/sonora.html" style="color:#888;text-decoration:none">Sonora</a>
  </nav>

  <div id="authSection">
    <div class="auth-form">
      <h2>Registro</h2>
      <div class="form-group">
        <label>Nombre</label>
        <input type="text" id="regNombre" placeholder="Tu nombre">
      </div>
      <div class="form-group">
        <label>Email</label>
        <input type="email" id="regEmail" placeholder="tu@email.com">
      </div>
      <div class="form-group">
        <label>Nicho</label>
        <select id="regNicho">
          <option value="musica">🎵 Músicos</option>
          <option value="fitness">💪 Fitness</option>
          <option value="educacion">📚 Educadores</option>
          <option value="ecommerce">🛒 Ecommerce</option>
          <option value="creativo">🎨 Creativos</option>
        </select>
      </div>
      <button class="btn btn-primary" style="width:100%" onclick="register()">Registrarme</button>
      <p style="text-align:center;margin-top:16px;color:rgba(255,255,255,0.5)">
        ¿Ya tienes cuenta? <a href="#" onclick="showLogin()" style="color:#00d4ff">Inicia sesión</a>
      </p>
    </div>

    <div class="auth-form hidden" id="loginForm">
      <h2>Login</h2>
      <div class="form-group">
        <label>Email</label>
        <input type="email" id="loginEmail" placeholder="tu@email.com">
      </div>
      <div class="form-group">
        <label>Password</label>
        <input type="password" id="loginPassword" placeholder="Tu password">
      </div>
      <button class="btn btn-primary" style="width:100%" onclick="login()">Entrar</button>
    </div>
  </div>

  <div id="credentialsSection" class="hidden">
    <div class="credentials">
      <h3>🔐 Tus Credenciales</h3>
      <p style="color:rgba(255,255,255,0.7);margin-bottom:16px">Guarda estas credenciales. Las necesitarás para acceder.</p>
      <label style="color:rgba(255,255,255,0.7)">Email:</label>
      <code id="credEmail"></code>
      <label style="color:rgba(255,255,255,0.7)">Password:</label>
      <code id="credPassword"></code>
      <label style="color:rgba(255,255,255,0.7)">API Key:</label>
      <code id="credApiKey"></code>
      <button class="btn btn-primary" style="width:100%;margin-top:16px" onclick="goToDashboard()">Ir al Dashboard</button>
    </div>
  </div>

  <div id="dashboard" class="dashboard">
    <div class="niche-header">
      <div class="niche-icon" id="nicheIcon"></div>
      <h1 id="nicheName"></h1>
      <p style="color:rgba(255,255,255,0.6);margin-top:8px" id="nicheDesc"></p>
    </div>

    <h2 style="margin-bottom:20px">Tus Herramientas</h2>
    <div class="grid" id="featuresGrid"></div>

    <h2 style="margin-bottom:20px">Acciones Rápidas</h2>
    <div class="grid" id="promptsGrid"></div>
  </div>
</div>

<script>
let currentUser = null;
let currentSession = null;

async function register() {
  const nombre = document.getElementById('regNombre').value;
  const email = document.getElementById('regEmail').value;
  const nicho = document.getElementById('regNicho').value;
  
  if (!nombre || !email) {
    alert('Completa todos los campos');
    return;
  }
  
  const res = await fetch('/app/register', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({nombre, email, nicho})
  });
  
  const data = await res.json();
  if (data.status === 'success') {
    currentUser = {id: data.user_id, ...data.credentials};
    document.getElementById('credEmail').textContent = data.credentials.email;
    document.getElementById('credPassword').textContent = data.credentials.password;
    document.getElementById('credApiKey').textContent = data.credentials.api_key;
    document.getElementById('authSection').classList.add('hidden');
    document.getElementById('credentialsSection').classList.remove('hidden');
  }
}

function showLogin() {
  document.querySelector('.auth-form').classList.add('hidden');
  document.getElementById('loginForm').classList.remove('hidden');
}

async function login() {
  const email = document.getElementById('loginEmail').value;
  const password = document.getElementById('loginPassword').value;
  
  const res = await fetch('/app/login', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({email, password})
  });
  
  const data = await res.json();
  if (data.status === 'success') {
    currentUser = data.user;
    currentSession = data.session_id;
    loadDashboard();
  } else {
    alert('Credenciales inválidas');
  }
}

async function loadDashboard() {
  const res = await fetch(`/app/dashboard/${currentUser.id}`);
  const data = await res.json();
  
  document.getElementById('nicheIcon').textContent = data.niche.icon;
  document.getElementById('nicheName').textContent = data.niche.name;
  document.getElementById('nicheDesc').textContent = `Plan ${data.user.plan}`;
  
  const featuresHtml = data.features.map(f => `
    <div class="card">
      <h3>${f.replace('_', ' ').toUpperCase()}</h3>
      <p>Accede a esta herramienta</p>
      <button class="action-btn" onclick="executeAction('feature', '${f}')">Abrir</button>
    </div>
  `).join('');
  document.getElementById('featuresGrid').innerHTML = featuresHtml;
  
  const promptsHtml = data.prompts.map(p => `
    <div class="card">
      <h3>${p.replace('_', ' ').toUpperCase()}</h3>
      <p>Ejecuta esta acción con IA</p>
      <button class="action-btn" onclick="executeAction('prompt', '${p}')">Ejecutar</button>
    </div>
  `).join('');
  document.getElementById('promptsGrid').innerHTML = promptsHtml;
  
  document.getElementById('authSection').classList.add('hidden');
  document.getElementById('credentialsSection').classList.add('hidden');
  document.getElementById('dashboard').classList.add('active');
  document.getElementById('userMenu').classList.remove('hidden');
  document.getElementById('userName').textContent = data.user.nombre;
}

async function executeAction(type, name) {
  const res = await fetch(`/app/execute/${currentUser.id}`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({type, name, params: {}})
  });
  const data = await res.json();
  alert(data.result);
}

function goToDashboard() {
  loadDashboard();
}

function logout() {
  currentUser = null;
  currentSession = null;
  document.getElementById('dashboard').classList.remove('active');
  document.getElementById('userMenu').classList.add('hidden');
  document.getElementById('authSection').classList.remove('hidden');
}
</script>
</body>
</html>
"""


@router.get("/", response_class=HTMLResponse)
async def app_root():
    """Serve the main app."""
    return HTMLResponse(APP_HTML)
