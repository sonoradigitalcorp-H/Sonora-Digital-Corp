from fastapi import APIRouter
from webui.routes.app_state import sessions

router = APIRouter()

METHODOLOGY_COMMANDS = {
    "/gsd": {
        "type": "gsd",
        "title": "🚀 GSD — Get Shit Done",
        "description": "Planificación y ejecución full-stack de proyectos.",
        "steps": [
            "1. **Context Gathering**: El asistente hará preguntas para entender el proyecto",
            "2. **Research**: 4 agentes paralelos investigan stack, features, arquitectura",
            "3. **Requirements**: Se define el alcance de la v1",
            "4. **Roadmap**: Se crea un roadmap basado en fases",
            "5. **Execution**: Ejecución por waves con verificación goal-backward",
        ],
        "output": "Se crea el directorio `.planning/` con PROJECT.md, REQUIREMENTS.md, ROADMAP.md",
        "usage": "Escribí `/gsd new-project <nombre>` para iniciar un nuevo proyecto",
    },
    "/wrap-up": {
        "type": "wrap-up",
        "title": "🔄 Close-Loop — Cierre de Sesión",
        "description": "Finaliza la sesión actual: shippea cambios, consolida memoria, aplica mejoras.",
        "steps": [
            "1. **Ship State**: Staggea y commitea cambios pendientes",
            "2. **Memory**: Consolida decisiones en memoria persistente",
            "3. **Self-Improve**: Aplica reglas de mejora pendientes",
            "4. **Report**: Genera reporte de la sesión",
        ],
        "usage": "Ejecutá `/wrap-up` al finalizar tu sesión de trabajo",
    },
    "/reflect": {
        "type": "reflect",
        "title": "🪞 Reflect — Análisis de Conversación",
        "description": "Analiza la conversación para extraer lecciones y mejorar los agentes.",
        "steps": [
            "1. **Scan**: Busca señales de corrección en la conversación",
            "2. **Classify**: Clasifica y mapea a archivos de agente",
            "3. **Propose**: Genera diffs con mejoras propuestas",
            "4. **Apply**: Aplica los cambios aprobados permanentemente",
        ],
        "output": "Los archivos de agente se actualizan con nuevas reglas",
        "usage": "Ejecutá `/reflect` después de una sesión con correcciones importantes",
    },
    "/learn": {
        "type": "learn",
        "title": "🧠 Learning-Loop — Auto-mejora",
        "description": "Detecta patrones de error y oportunidades de mejora continua.",
        "steps": [
            "1. **Analysis**: Analiza tareas recientes en busca de patrones",
            "2. **Confidence**: Evalúa confianza con decay temporal",
            "3. **Cross-agent**: Comparte mejoras entre agentes relevantes",
            "4. **Anomaly**: Detecta anomalías de comportamiento",
        ],
        "usage": "Ejecutá `/learn` para iniciar un ciclo de auto-mejora",
    },
}


def handle_methodology_command(cmd: str):
    info = METHODOLOGY_COMMANDS.get(cmd)
    if not info:
        return {
            "type": "error",
            "content": f"Comando de metodología desconocido: {cmd}",
        }
    steps_text = "\n".join(info["steps"])
    output_text = (
        f"\n\n**Output esperado:** {info['output']}" if info.get("output") else ""
    )
    usage_text = f"\n\n**Uso:** {info['usage']}" if info.get("usage") else ""
    return {
        "type": info["type"],
        "content": f"## {info['title']}\n\n{info['description']}\n\n### Pasos:\n{steps_text}{output_text}{usage_text}\n---\n*Este comando ejecuta una skill de OpenClaw. Necesitás el Gateway en :18789.*",
    }


@router.post("/api/commands")
async def execute_command(data: dict):
    cmd = data.get("command", "").lower()
    session_id = data.get("session_id", "default")
    if cmd == "/help":
        return {
            "type": "help",
            "content": "## Comandos disponibles\n\n| Comando | Descripción |\n|---------|-------------|\n| `/help` | Muestra esta ayuda |\n| `/clear` | Limpia la conversación actual |\n| `/status` | Muestra el estado del sistema |\n| `/memory` | Busca en la memoria de JARVIS |\n| `/skills` | Lista las skills disponibles |\n| `/voice` | Activa/desactiva el modo voz |\n| `/theme` | Cambia el tema (dark/light/cyberpunk) |\n| `/gsd` | GSD: planificar y ejecutar proyecto completo |\n| `/wrap-up` | Close-Loop: cerrar sesión (ship + memory + improve) |\n| `/reflect` | Reflect: analizar sesión y mejorar agentes |\n| `/learn` | Learning-Loop: detectar patrones y auto-mejora |",
        }
    if cmd == "/clear":
        s = sessions.get(session_id)
        if s:
            s["messages"] = []
            s["token_count"] = 0
        return {"type": "clear", "content": "🧹 Conversación limpiada."}
    if cmd == "/status":
        return {
            "type": "status",
            "content": f"## Estado del Sistema\n\n- **Web UI:** v2.0.0 ✅\n- **Sesiones:** {len(sessions)}\n- **Memoria activa:** 3 collections en Qdrant\n- **Servicios:** MCP | Neo4j (pendiente) | Qdrant (activo)\n- **Tema:** Cyberpunk",
        }
    if cmd == "/skills":
        return {
            "type": "skills",
            "content": "## Skills Disponibles\n\n| Skill | Descripción |\n|-------|-------------|\n| `analyze_code` | Análisis estático de código |\n| `search_memory` | Búsqueda en memoria (Neo4j + Qdrant) |\n| `web_fetch` | Fetch de URLs con resumen |\n| `translate` | Traducción de texto |\n| `summarize` | Resumen de contenido |",
        }
    if cmd == "/voice":
        return {
            "type": "voice",
            "content": "🎤 Modo voz activado. Di 'Hey JARVIS' para comenzar.",
        }
    if cmd == "/theme":
        return {"type": "theme", "content": "🎨 Tema cambiado a: cyberpunk"}
    if cmd in ("/gsd", "/wrap-up", "/reflect", "/learn"):
        return handle_methodology_command(cmd)
    return {
        "type": "error",
        "content": f"Comando desconocido: {cmd}. Usa `/help` para ver los comandos disponibles.",
    }
