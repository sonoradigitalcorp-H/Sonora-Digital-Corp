"""Voice API - Endpoint para procesamiento de voz."""

import json
import os
import secrets
import shlex
import subprocess
import tempfile

import httpx
from fastapi import APIRouter, Depends, File, Form, Header, HTTPException, UploadFile
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from ..core.config import settings

router = APIRouter()


class VoiceCommandRequest(BaseModel):
    """Request para comando de voz."""
    text: str


class VoiceCommandResponse(BaseModel):
    """Response para comando de voz."""
    success: bool
    text: str = ""
    command: str = ""
    result: str = ""
    error: str = ""


# API Key de OpenRouter
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
if not OPENROUTER_API_KEY:
    # Buscar en archivos .env
    env_paths = [
        "/home/mystic/.hermes/.env",
        "/home/mystic/Documentos/Sonora Digital Corp/sonora-digital-corp/.env",
    ]
    for env_path in env_paths:
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    if line.startswith("OPENROUTER_API_KEY="):
                        OPENROUTER_API_KEY = line.split("=", 1)[1].strip()
                        break
            if OPENROUTER_API_KEY:
                break


PRIMARY_MODEL = "deepseek/deepseek-v4-flash"
FALLBACK_MODEL = "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free"

# Comandos permitidos para la acción "ejecutar". Sin shell, argv exacto.
ALLOWED_COMMANDS = frozenset({
    ("ls",),
    ("ls", "-l"),
    ("ls", "-la"),
    ("pwd",),
    ("whoami",),
    ("uname", "-a"),
    ("date",),
    ("uptime",),
    ("df", "-h"),
    ("docker", "ps"),
    ("git", "status"),
    ("git", "log", "--oneline", "-5"),
})

ALLOWED_COMMANDS_TEXT = (
    "ls, ls -l, ls -la, pwd, whoami, uname -a, date, uptime, df -h, "
    "docker ps, git status, git log --oneline -5"
)


def require_voice_token(
    x_api_key: str | None = Header(default=None),
    authorization: str | None = Header(default=None),
) -> None:
    """Valida el token de la Voice API. Falla cerrado si no está configurado."""
    token = settings.VOICE_API_TOKEN
    if not token:
        raise HTTPException(
            status_code=503,
            detail="Voice API deshabilitada: configure VOICE_API_TOKEN",
        )

    provided = None
    if x_api_key:
        provided = x_api_key
    elif authorization and authorization.startswith("Bearer "):
        provided = authorization[len("Bearer "):].strip()

    if not provided or not secrets.compare_digest(provided, token):
        raise HTTPException(status_code=401, detail="API key inválida o ausente")


def interpret_command(text: str) -> dict:
    """Interpreta un comando de voz usando LLM."""
    system_prompt = f"""Devuelve SOLO un JSON válido, sin explicaciones ni markdown.

Ejemplos:
- "abre una terminal" → {{"action": "abrir_terminal", "params": {{}}, "confidence": 0.9}}
- "listame los archivos" → {{"action": "listar_archivos", "params": {{"path": "."}}, "confidence": 0.9}}
- "ejecuta ls -la" → {{"action": "ejecutar", "params": {{"command": "ls -la"}}, "confidence": 0.9}}
- "ver estado del sistema" → {{"action": "verificar_estado", "params": {{}}, "confidence": 0.9}}
- "abre google" → {{"action": "abrir_navegador", "params": {{"url": "https://google.com"}}, "confidence": 0.9}}
- "muéstrame los contenedores" → {{"action": "ejecutar", "params": {{"command": "docker ps"}}, "confidence": 0.8}}

Acciones: abrir_terminal, ejecutar (params: command), abrir_navegador (params: url),
crear_archivo (params: path, content), listar_archivos (params: path),
iniciar_servicio (params: service), detener_servicio (params: service),
verificar_estado, deploy, commit (params: message), push, test, ayuda

IMPORTANTE para la acción "ejecutar": SOLO se permiten estos comandos exactos:
{ALLOWED_COMMANDS_TEXT}. Cualquier otro comando será rechazado por el servidor."""

    def _call_model(model: str) -> dict:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": text},
                    ],
                    "max_tokens": 150,
                },
            )
            data = response.json()
            if "error" in data:
                err = data["error"]
                raise RuntimeError(f"{err.get('code', 'unknown')}: {err.get('message', '')}")
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            content = content.strip()
            if content.startswith("```"):
                content = content.split("\n", 1)[1].rsplit("```", 1)[0]
            return json.loads(content)

    try:
        try:
            return _call_model(PRIMARY_MODEL)
        except (RuntimeError, json.JSONDecodeError) as e:
            err_str = str(e)
            if "402" in err_str or "credits" in err_str.lower() or "insufficient" in err_str.lower():
                print(f"[voice] Primary model sin créditos, usando fallback: {err_str}")
                try:
                    return _call_model(FALLBACK_MODEL)
                except (RuntimeError, json.JSONDecodeError) as e2:
                    print(f"[voice] Fallback también falló: {e2}")
                    return {"action": "ayuda", "params": {}, "confidence": 0.5}
            print(f"[voice] Error en interpretación: {err_str}")
            return {"action": "ayuda", "params": {}, "confidence": 0.5}

    except Exception as e:
        print(f"[voice] Error inesperado: {e}")
        return {"action": "ayuda", "params": {}, "confidence": 0.5}


def _run(cmd, **kwargs):
    r = subprocess.run(cmd, capture_output=True, text=True, **kwargs)
    return r.stdout[:500] if r.stdout else r.stderr[:200] or "OK"


def _run_safe_command(params: dict) -> str:
    """Ejecuta únicamente comandos de la allowlist, sin shell."""
    raw = params.get("command", "")
    try:
        argv = shlex.split(raw)
    except ValueError as e:
        raise PermissionError(f"Comando no permitido (sintaxis inválida): {raw}") from e
    if not argv or tuple(argv) not in ALLOWED_COMMANDS:
        raise PermissionError(f"Comando no permitido: {raw}")
    return _run(argv, timeout=30)


def _open_terminal() -> str:
    subprocess.Popen(["gnome-terminal"], start_new_session=True)
    return "Terminal abierta"


def _open_browser(url: str) -> str:
    target = url or "https://google.com"
    subprocess.Popen(["xdg-open", target], start_new_session=True)
    return f"Abriendo {target}"


def _git_commit(message: str) -> str:
    _run(["git", "add", "."])
    _run(["git", "commit", "-m", message or "Update"])
    return "Commit realizado"


def execute_action(action: str, params: dict) -> str:
    """Ejecuta una acción. Lanza excepción si la acción falla o no está permitida."""

    actions = {
        "abrir_terminal": lambda p: _open_terminal(),
        "ejecutar": _run_safe_command,
        "abrir_navegador": lambda p: _open_browser(p.get("url", "")),
        "listar_archivos": lambda p: "\n".join(os.listdir(p.get("path", "."))[:20]),
        "iniciar_servicio": lambda p: _run(["docker", "compose", "up", "-d", p.get("service", "")]),
        "detener_servicio": lambda p: _run(["docker", "compose", "stop", p.get("service", "")]),
        "verificar_estado": lambda p: _run(["docker", "ps", "--format", "{{.Names}} → {{.Status}}"]),
        "commit": lambda p: _git_commit(p.get("message", "")),
        "push": lambda p: _run(["git", "push"]) or "Push realizado",
        "test": lambda p: _run(["python", "-m", "pytest", "tests/", "-q"], timeout=120),
        "ayuda": lambda p: (
            "Comandos: abrir terminal, ejecutar [ls, pwd, whoami, uname -a, date, uptime, "
            "df -h, docker ps, git status, git log], abrir [url], listar archivos, "
            "ver estado, test, commit, deploy"
        ),
    }

    if action not in actions:
        raise ValueError(f"Acción no reconocida: {action}")

    result = actions[action](params)
    return str(result) if result is not None else "OK"


@router.get("/voice")
async def voice_page():
    """Página principal de voice control."""
    template_path = os.path.join(os.path.dirname(__file__), "templates", "index.html")
    with open(template_path) as f:
        return HTMLResponse(content=f.read())


@router.post("/api/voice/process")
async def process_voice(
    audio: UploadFile = File(...),
    duration: int = Form(3),
    _: None = Depends(require_voice_token),
):
    """Procesa audio del micrófono."""
    try:
        # Guardar archivo temporal
        temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        content = await audio.read()
        temp_file.write(content)
        temp_file.close()

        # Transcribir con Whisper (si está disponible)
        try:
            import whisper
            model = whisper.load_model("base")
            result = model.transcribe(temp_file.name)
            text = result["text"]
        except ImportError:
            # Fallback: usar el texto del frontend
            text = ""

        os.unlink(temp_file.name)

        if not text:
            return VoiceCommandResponse(
                success=False,
                error="No se pudo transcribir el audio"
            )

        # Interpretar comando
        cmd = interpret_command(text)
        action = cmd.get("action", "ayuda")
        params = cmd.get("params", {})

        # Ejecutar acción
        result = execute_action(action, params)

        return VoiceCommandResponse(
            success=True,
            text=text,
            command=action,
            result=result,
        )

    except Exception as e:
        return VoiceCommandResponse(
            success=False,
            error=str(e),
        )


@router.post("/api/voice/command")
async def process_command(
    request: VoiceCommandRequest,
    _: None = Depends(require_voice_token),
):
    """Procesa un comando de texto."""
    try:
        # Interpretar comando
        cmd = interpret_command(request.text)
        action = cmd.get("action", "ayuda")
        params = cmd.get("params", {})

        # Ejecutar acción
        result = execute_action(action, params)

        return VoiceCommandResponse(
            success=True,
            text=request.text,
            command=action,
            result=result,
        )

    except Exception as e:
        return VoiceCommandResponse(
            success=False,
            error=str(e),
        )
