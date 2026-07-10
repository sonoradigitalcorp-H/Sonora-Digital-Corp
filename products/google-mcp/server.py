"""Google MCP Server — API access + NotebookLM + Credential management.

Auth methods (in priority order):
  1. GOOGLE_CREDENTIALS env var (JSON service account)
  2. GOOGLE_APPLICATION_CREDENTIALS env var (file path)
  3. gcloud ADC (~/.config/gcloud/application_default_credentials.json)
  4. Interactive OAuth (stored in ~/.google_mcp/oauth.json)
"""

import json
import os
import subprocess
import time
from pathlib import Path
from urllib.parse import urlencode

import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("sdc-google-mcp", port=8767)

HOME = Path.home()
MCP_DIR = HOME / ".google_mcp"
MCP_DIR.mkdir(exist_ok=True)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
NOTEBOOKLM_AUTH = HOME / ".notebooklm" / "profiles" / "default" / "auth.json"


# ── Auth helpers ──────────────────────────────────────────────

@mcp.tool()
async def google_auth_status() -> dict:
    """Check what Google auth methods are available."""
    methods = {}
    if GEMINI_API_KEY:
        methods["gemini_api_key"] = True
    if os.getenv("GOOGLE_CREDENTIALS"):
        methods["env_var_credentials"] = True
    if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        methods["adc_file"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    adc_default = HOME / ".config" / "gcloud" / "application_default_credentials.json"
    if adc_default.exists():
        methods["gcloud_adc"] = str(adc_default)
    oauth = MCP_DIR / "oauth.json"
    if oauth.exists():
        methods["stored_oauth"] = str(oauth)
    if NOTEBOOKLM_AUTH.exists():
        methods["notebooklm"] = str(NOTEBOOKLM_AUTH)
    installed = _check_gcloud()
    methods["gcloud_cli"] = installed
    authenticated = any(v for v in methods.values() if isinstance(v, bool)) or \
                    any(isinstance(v, str) and v for v in methods.values())
    return {
        "authenticated": authenticated,
        "methods": methods,
        "advice": (
            "To add auth: run 'python3 apps/google-mcp/auth.py' interactively, "
            "or set GEMINI_API_KEY env var for instant Gemini access."
        ),
    }


def _check_gcloud() -> bool:
    try:
        subprocess.run(["gcloud", "--version"], capture_output=True, timeout=5)
        return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


# ── Gemini Content Generation (replaces NotebookLM) ──────────

@mcp.tool()
async def generate_content(
    prompt: str,
    system_prompt: str = "Eres un experto creador de contenido para músicos.",
    temperature: float = 0.7,
    max_tokens: int = 2048,
) -> dict:
    """Generate content using Google Gemini API.

    Free tier: 60 requests/min, no API key needed for some models.
    Set GEMINI_API_KEY for higher quotas and Gemini 2.5 Pro access.
    """
    key = GEMINI_API_KEY or _try_discover_key()
    if key:
        return await _gemini_api(prompt, system_prompt, key, temperature, max_tokens)
    return await _gemini_free(prompt)


def _try_discover_key() -> str:
    for var in ["GEMINI_API_KEY", "GOOGLE_API_KEY"]:
        val = os.getenv(var, "")
        if val:
            return val
    return ""


async def _gemini_api(prompt: str, system: str, key: str, temp: float, tokens: int) -> dict:
    model = "gemini-2.0-flash"
    url = f"https://generativelanguage.googleapis.com/v1/models/{model}:generateContent?key={key}"
    combined = f"{system}\n\n{prompt}"
    async with httpx.AsyncClient(timeout=60) as cl:
        r = await cl.post(url, json={
            "contents": [{"parts": [{"text": combined}]}],
            "generationConfig": {
                "temperature": temp,
                "maxOutputTokens": tokens,
            },
        })
        data = r.json()
        if "error" in data:
            return {"provider": "gemini", "model": model, "error": data["error"]["message"], "text": ""}
        text = (data.get("candidates", [{}])[0]
                .get("content", {})
                .get("parts", [{}])[0]
                .get("text", ""))
        return {"provider": "gemini", "model": model, "text": text, "cost": 0}


async def _gemini_free(prompt: str) -> dict:
    return {
        "error": "No Gemini API key. Set GEMINI_API_KEY env var, or use the story generator via SDC Content Server.",
        "solution": "export GEMINI_API_KEY=your_key_here",
    }


# ── NotebookLM tools (when auth available) ────────────────────

@mcp.tool()
async def notebooklm_status() -> dict:
    """Check if NotebookLM auth is available and working."""
    if not NOTEBOOKLM_AUTH.exists():
        return {
            "available": False,
            "message": "NotebookLM not authenticated.",
            "setup": (
                "To enable: On your laptop with a browser:\n"
                "  1. pip install notebooklm-py\n"
                "  2. notebooklm login --browser chromium\n"
                "  3. scp ~/.notebooklm/profiles/default/auth.json "
                "ubuntu@149.56.46.173:~/.notebooklm/profiles/default/\n"
                "Or: xvfb-run notebooklm login --browser chromium (opens browser on VPS)"
            ),
        }
    return {"available": True, "auth_file": str(NOTEBOOKLM_AUTH)}


@mcp.tool()
async def notebooklm_generate_story(
    topic: str,
    artist_name: str = "",
    style: str = "narrative",
) -> dict:
    """Generate a story/script using NotebookLM (requires auth).

    Authenticatation: see notebooklm_status() for setup instructions.
    Falls back to Gemini API if NotebookLM auth is unavailable.
    """
    if not NOTEBOOKLM_AUTH.exists():
        return await generate_content(
            f"Write a {style} script about {topic} for musician {artist_name}",
            "Eres un guionista creativo para contenido musical.",
        )
    try:
        import notebooklm  # noqa: F401
        result = await _notebooklm_generate(topic, artist_name, style)
        return result
    except ImportError:
        return {"error": "notebooklm-py not installed", "fallback": True}


async def _notebooklm_generate(topic: str, artist: str, style: str) -> dict:
    auth = json.loads(NOTEBOOKLM_AUTH.read_text())
    headers = {"Authorization": f"Bearer {auth.get('access_token', '')}"}
    async with httpx.AsyncClient(timeout=120) as cl:
        r = await cl.post(
            "https://notebooklm.google.com/_/api/chat",
            headers=headers,
            json={
                "messages": [
                    {
                        "role": "user",
                        "parts": [{
                            "text": f"Write a {style} about {topic}"
                                    f" for artist {artist}. Keep it under 500 words."
                        }]
                    }
                ]
            },
        )
        data = r.json()
        return {
            "provider": "notebooklm",
            "text": data.get("text", str(data)),
            "style": style,
        }


# ── Google Cloud API Keys management ─────────────────────────

@mcp.tool()
async def list_gcp_projects() -> list[dict]:
    """List Google Cloud projects accessible with current credentials."""
    try:
        result = subprocess.run(
            ["gcloud", "projects", "list", "--format=json"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0:
            projects = json.loads(result.stdout)
            return [{"id": p["projectId"], "name": p.get("name", ""), "number": p.get("projectNumber", "")}
                    for p in projects]
        return [{"error": result.stderr.strip()}]
    except FileNotFoundError:
        return [{"error": "gcloud CLI not installed"}]
    except subprocess.TimeoutExpired:
        return [{"error": "gcloud command timed out"}]


@mcp.tool()
async def get_api_keys(project_id: str = "") -> list[dict]:
    """List API keys from Google Cloud project.

    Uses gcloud CLI. Run 'gcloud auth application-default login' first.
    """
    try:
        if project_id:
            result = subprocess.run(
                ["gcloud", "services", "api-keys", "list",
                 f"--project={project_id}", "--format=json"],
                capture_output=True, text=True, timeout=15,
            )
        else:
            result = subprocess.run(
                ["gcloud", "services", "api-keys", "list", "--format=json"],
                capture_output=True, text=True, timeout=15,
            )
        if result.returncode == 0:
            keys = json.loads(result.stdout) if result.stdout.strip() else []
            return [{"name": k.get("name", ""), "displayName": k.get("displayName", ""),
                     "uid": k.get("uid", ""), "restrictions": k.get("restrictions", {})}
                    for k in keys]
        return [{"error": result.stderr.strip()}]
    except FileNotFoundError:
        return [{"error": "gcloud CLI not installed"}]
    except subprocess.TimeoutExpired:
        return [{"error": "gcloud command timed out"}]


# ── Story/Script templates for musicians ─────────────────────

STORY_TEMPLATES = {
    "lanzamiento": (
        "Eres un narrador para el lanzamiento del nuevo sencillo '{song}' de {artist}. "
        "Genera un guion de 60 segundos para un video promocional que incluya:\n"
        "1. Hook inicial (5s): '¡Al fin llegó!'\n"
        "2. La historia detrás de la canción (20s)\n"
        "3. El sonido y la vibra (15s)\n"
        "4. CTA: dónde escucharla, fecha de estreno (20s)\n"
        "Tono: emocionante, auténtico, regional mexicano."
    ),
    "detras_de_camaras": (
        "Eres el documentalista de {artist}. Genera un guion de 60 segundos para "
        "un 'detrás de cámaras' mostrando el proceso creativo de '{song}'.\n"
        "Incluye: cómo nació la idea, anécdota de la grabación, momento favorito.\n"
        "Tono: natural, chido, sin filtros."
    ),
    "saludo_fans": (
        "Eres {artist} saludando a tus fans. Genera un script de 30 segundos para:\n"
        "- Agradecer el apoyo\n"
        "- Anunciar próximos shows/lanzamientos\n"
        "- Invitar a seguir en redes\n"
        "Tono: cálido, agradecido, carismático."
    ),
    "contenido_diario": (
        "Genera 3 ideas de contenido para redes sociales de {artist} para esta semana.\n"
        "Cada idea debe incluir:\n"
        "- Formato (Reel/Story/Post)\n"
        "- Hook (primeros 3 segundos)\n"
        "- Descripción del contenido\n"
        "- Hashtags relevantes\n"
        "Basado en: {context}"
    ),
}


@mcp.tool()
async def generate_story_script(
    template_name: str,
    artist: str = "el artista",
    song: str = "",
    context: str = "",
) -> dict:
    """Generate a story script using predefined templates for musicians.

    Available templates: lanzamiento, detras_de_camaras, saludo_fans, contenido_diario
    Falls back to Gemini API or NotebookLM.
    """
    template = STORY_TEMPLATES.get(template_name)
    if not template:
        available = list(STORY_TEMPLATES.keys())
        return {"error": f"Unknown template. Available: {available}"}

    prompt = template.format(artist=artist, song=song or "su nuevo tema", context=context or "novedades del artista")
    return await generate_content(prompt, "Eres un creativo experto en contenido musical latino.")


app = mcp.sse_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8767, log_level="info")
