#!/usr/bin/env python3
"""Hermes Agent Factory - Sonora Digital Corp.
Convierte una ORDEN en lenguaje natural en un agente OpenClaw autónomo y enlazado a un canal.
La idea: NO crear bots manuales por cliente. Hermes decide, la factory materializa el agente,
y OpenClaw lo opera 24/7 en el canal indicado.

Flujo:
  1. Recibe: {"orden": "...", "id": "cesar", "canal": "telegram", "nombre": "César"}
  2. Hero (LLM) genera el prompt/identidad del agente desde la orden
  3. La factory crea/actualiza el agente OpenClaw via `openclaw agents add`
  4. Enlaza routing del canal al agente
"""
import os, sys, json, subprocess, argparse

OPENCLAW = "openclaw"
OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY")
MODEL = os.environ.get("OPENAI_MODEL", "deepseek/deepseek-v4-flash-0731")

FACTORY_DIR = os.path.dirname(os.path.abspath(__file__))
SDK_DIR = os.path.join(FACTORY_DIR, "..", "..", "..", "05_Shared_Libraries", "SDK_Python")
if SDK_DIR not in sys.path:
    sys.path.insert(0, SDK_DIR)

# Prompt que escribe la IDENTIDAD de un agente a partir de una orden de negocio
IDENTITY_WRITER = """Eres el diseñador de agentes de Sonora Digital Corp (Hermes Factory).
Dada una ORDEN de negocio del dueño, escribe la identidad de un agente autónomo.

Devuelve SOLO JSON con este esquema:
{
  "nombre": "Nombre corto del agente (ej: cesar-vendedor)",
  "emoji": "un emoji",
  "rol": "Rol en UNA frase (ej: Asistente comercial de César Holguín en Aztrotech)",
  "directrices": [
    "Regla estricta 1 (ej: nunca revelar que es de Sonora Digital Corp)",
    "Regla estricta 2 (ej: nunca dar precios, capturar lead y pasar a César)",
    "Regla estricta 3"
  ],
  "skill_requerida": "skill de OpenClaw principal (wacli|playwright|telegram|fal-ai|browser-use)",
  "canal_sugerido": "telegram|whatsapp|web"
}

REGLAS:
- Cero relleno. Conciso y operativo.
- Las directrices son órdenes ejecutables para el agente, no texto bonito.
- Nunca inventar skills: usa las que existan en OpenClaw (wacli, playwright, telegram, fal-ai, github, supabase, comfyui, sherpa-onnx-tts, voice-call).

ORDEN: {orden}"""


def _call_llm(system, user):
    """LLM barato (deepseek-v4-flash) para diseñar la identidad."""
    if not OPENROUTER_KEY:
        return {"error": "OPENROUTER_API_KEY not configured"}
    import urllib.request
    body = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": 0.2,
        "max_tokens": 600,
    }
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {OPENROUTER_KEY}",
                 "HTTP-Referer": "https://sonora-digital-corp.local",
                 "X-Title": "Hermes-Factory",
                 "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
        content = data["choices"][0]["message"]["content"]
        # Extraer solo el JSON (el modelo puede envolverlo en markdown)
        start = content.find("{")
        end = content.rfind("}") + 1
        return json.loads(content[start:end])
    except Exception as e:
        return {"error": str(e)}


def _ruta_workspace(agent_id):
    """Workspace propio para el agente, bajo 02_Client_Projects/<Id>/05_Agentic_Skills"""
    proj = os.path.join(FACTORY_DIR, "..", "..", "..", "..",
                        "02_Client_Projects", agent_id.title(), "05_Agentic_Skills")
    if not os.path.isdir(proj):
        proj = os.path.join(os.path.expanduser("~"), ".openclaw", "workspace")
    return proj


def crear_agente(orden, agent_id, canal="telegram", nombre=None, emoji=None,
                 modelo=None, workspace=None, bind=True):
    """Crea (o actualiza) un agente OpenClaw a partir de una orden."""
    print(f"\n=== HERMES AGENT FACTORY ===")
    print(f"[1/4] Diseñando identidad del agente '{agent_id}' desde la orden...")
    spec = _call_llm(IDENTITY_WRITER, orden)
    if "error" in spec:
        print(f"❌ No pude diseñar identidad: {spec['error']}")
        return {"error": spec["error"]}

    nombre = nombre or spec.get("nombre", agent_id)
    emoji = emoji or spec.get("emoji", "🤖")
    rol = spec.get("rol", "Agente autónomo")
    directrices = spec.get("directrices", [])
    model = modelo or MODEL
    workspace = workspace or _ruta_workspace(agent_id)

    # 1. Escribir AGENTS.md + IDENTITY.md en el workspace del agente
    print(f"[2/4] Escribiendo identidad en workspace: {workspace}")
    os.makedirs(workspace, exist_ok=True)
    identity = f"""# {nombre} {emoji}

**Rol:** {rol}

## Directrices
"""
    for d in directrices:
        identity += f"- {d}\n"
    identity += """
## Contexto
Creado por Hermes Agent Factory (Sonora Digital Corp).
Opera de forma autónoma 24/7. Si no sabes algo, no invente — consulta o pregunta.
"""
    with open(os.path.join(workspace, "IDENTITY.md"), "w") as f:
        f.write(identity)
    with open(os.path.join(workspace, "AGENTS.md"), "w") as f:
        f.write(identity)

    # 3. Crear el agente en OpenClaw (non-interactive)
    print(f"[3/4] Registrando agente '{agent_id}' en OpenClaw...")
    cmd = [OPENCLAW, "agents", "add", agent_id,
           "--model", model,
           "--workspace", workspace,
           "--non-interactive", "--json"]
    if bind:
        cmd += ["--bind", canal]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        registro = json.loads(r.stdout) if r.stdout.strip().startswith("{") else {"raw": r.stdout}
        print(f"   OpenClaw: {r.stdout.strip()[:400]}")
        if r.returncode != 0 and r.stderr:
            print(f"   stderr: {r.stderr[:200]}")
    except Exception as e:
        registro = {"error": str(e)}

    print(f"[4/4] Agente '{agent_id}' listo. Rol: {rol}")
    print(f"   Canal: {canal} | Modelo: {model} | Emoji: {emoji}")
    print(f"   Directrices ({len(directrices)}): {directrices}")

    return {"agent_id": agent_id, "nombre": nombre, "rol": rol,
            "canal": canal, "modelo": model, "registro": registro, "spec": spec}


def listar_agentes():
    r = subprocess.run([OPENCLAW, "agents", "list"], capture_output=True, text=True, timeout=60)
    return r.stdout


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Hermes Agent Factory")
    ap.add_argument("--orden", required=True, help="Orden de negocio en lenguaje natural")
    ap.add_argument("--id", required=True, help="ID corto del agente (ej: cesar)")
    ap.add_argument("--canal", default="telegram", help="Canal a enlazar (telegram whatsapp web)")
    ap.add_argument("--nombre", default=None)
    ap.add_argument("--no-bind", action="store_true", help="No enlazar canal")
    args = ap.parse_args()

    res = crear_agente(
        orden=args.orden,
        agent_id=args.id,
        canal=args.canal,
        nombre=args.nombre,
        bind=not args.no_bind,
    )
    print("\n=== RESULTADO ===")
    print(json.dumps(res, ensure_ascii=False, indent=2))
