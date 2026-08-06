#!/usr/bin/env python3
"""Hermes Supervisor (Orquestador) - Sonora Digital Corp.
Receptor UNIVERSAL: recibe una orden desde CUALQUIER canal (CLI, Telegram, WhatsApp, web, voz)
y decide qué hacer:
  1. ¿Pregunta de conocimiento? -> OKF/Engram -> respuesta natural
  2. ¿Requiere ejecutar una tarea manual? -> delega a OpenCode (este agente) para editar/deployar
  3. ¿Requiere un agente autónomo nuevo? -> Hermes Agent Factory crea uno en OpenClaw
  4. ¿Requiere enviar msj/ejecutar skill? -> OpenClaw agent/skill

Es el cerebro. No crea bots manuales: produce agentes y orquesta capacidades.
"""
import os, sys, json, argparse

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..")
sys.path.insert(0, os.path.join(BASE, "03_Agentic_Infrastructure", "Hermes_Agent", "Tools"))
sys.path.insert(0, os.path.join(BASE, "05_Shared_Libraries", "SDK_Python"))

from sdc_sdk import SDC_Client
from okf_navigator import retrieve_context

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
AGENT_FACTORY = os.path.join(BASE, "03_Agentic_Infrastructure", "Hermes_Agent", "Orchestrator", "hermes_agent_factory.py")

ROUTER_SYSTEM = """Eres HERMES, el orquestador de Sonora Digital Corp. Recibes la ORDEN del dueño (MYSTIC)
y decides el MINIMO accionable. NO ejecutes tú las tareas manuales: delegas.

Clasifica la orden y responde SOLO JSON:
{
  "tipo": "pregunta" | "agente" | "ejecutar" | "enviar" | "crear_asset",
  "tenant": "cliente implicado o null",
  "razon": "una línea: por qué es este tipo",
  "accion_propuesta": "un verbo claro de lo que se hará"
}

Reglas de clasificacion:
- "pregunta": es un dato/conocimiento/reserva que se responde con texto (no toca archivos).
- "agente": el dueño pide captar/atender/vender/responder a clientes de forma autónoma y continua -> crear agente OpenClaw.
- "ejecutar": hay que tocar código/archivos/deployar/automatizar una tarea especifica que hace OpenCode (este agente).
- "enviar": mandar un mensaje/audio/archivo YA a alguien (WhatsApp/Telegram) -> OpenClaw skill.
- "crear_asset": generar imagen/voz/video/documento -> skill de generacion (fal-ai, comfyui, tts).

ORDEN: {orden}"""


def clasificar(orden, tenant="aztrotech"):
    client = SDC_Client(tenant or "General")
    res = client.call_llm([
        {"role": "system", "content": ROUTER_SYSTEM},
        {"role": "user", "content": f"ORDEN: {orden}\n\nTENANT actual: {tenant}"},
    ], max_tokens=300)
    if res.get("status") != "success":
        return {"tipo": "ejecutar", "tenant": tenant, "razon": "router fallo, default a ejecutar",
                "accion_propuesta": res.get("error", "error")}
    content = res["content"]
    try:
        start, end = content.find("{"), content.rfind("}") + 1
        return json.loads(content[start:end])
    except Exception:
        return {"tipo": "ejecutar", "tenant": tenant, "razon": "router no devolvio JSON",
                "accion_propuesta": content[:200]}


def responder_pregunta(orden, tenant):
    """Capa conocimiento: OKF exacto -> Engram -> respuesta natural."""
    okf = retrieve_context(orden, tenant)
    ctx = ""
    if okf["corpus"] == "okf":
        ctx = f"[OKF-{okf['concept_id']}]\n{okf['context'][:600]}"
    elif okf["corpus"] == "rag":
        ctx = f"[Engram-experiencial]\n{okf['context'][:600]}"
    else:
        ctx = "No tengo datos verificados."
    client = SDC_Client(tenant or "General")
    res = client.call_llm([
        {"role": "system", "content": "Eres Hermes. Responde en español, conciso, cita la fuente. Nunca inventes."},
        {"role": "user", "content": f"Pregunta: {orden}\n\nContexto:\n{ctx}"},
    ])
    return res.get("content", "No tengo respuesta verificada.") if res.get("status") == "success" else res.get("error")


def crear_agente(orden, agent_id, canal="telegram"):
    """Delega a la Agent Factory."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("hermes_agent_factory", AGENT_FACTORY)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.crear_agente(orden=orden, agent_id=agent_id, canal=canal)


def parse_orchestrate(args):
    if args.auto and not args.orden:
        print("❌ --orden requerido con --auto")
        return
    if not args.auto:
        # Modo directo: el dueño especifica tipo
        if args.tipo == "pregunta":
            print(responder_pregunta(args.orden, args.tenant))
        elif args.tipo == "agente":
            r = crear_agente(args.orden, args.id, args.canal)
            print(json.dumps(r, ensure_ascii=False, indent=2))
        else:
            # ejecutar / enviar / asset: esto lo hace OpenCode -> instruccion para el agente
            print(json.dumps({
                "mensaje": "Tarea delegada a OpenCode (agente de ejecución)",
                "orden": args.orden,
                "tipo": args.tipo,
                "tenant": args.tenant,
            }, ensure_ascii=False, indent=2))
        return

    # Modo AUTO: Hermes clasifica y actua
    print(f"🤖 Hermes: recibiendo orden... '{args.orden}'")
    decision = clasificar(args.orden, args.tenant)
    print(f"🧠 Hermes decidió: {json.dumps(decision, ensure_ascii=False)}")
    t = decision.get("tipo", "ejecutar")
    tenant = decision.get("tenant") or args.tenant
    if t == "pregunta":
        print(f"\n📖 [Hermes] Respuesta:\n{responder_pregunta(args.orden, tenant)}")
    elif t == "agente":
        print(f"\n🛠️ [Hermes] Creando agente autónomo...")
        r = crear_agente(args.orden, args.id or "auto", args.canal)
        print(json.dumps(r, ensure_ascii=False, indent=2))
    elif t == "enviar":
        print(f"\n📤 [Hermes] Delegado a OpenClaw skill para enviar: '{args.orden}'")
        print("   (Este agente ejecuta: openclaw agent / wacli)")
    else:
        print(f"\n⚙️ [Hermes] Tarea de ejecución delegada a OpenCode:")
        print(json.dumps({"orden": args.orden, "tipo": t, "tenant": tenant}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Hermes Supervisor - orquestador universal")
    ap.add_argument("--orden", help="Orden en lenguaje natural")
    ap.add_argument("--tipo", choices=["pregunta", "agente", "ejecutar", "enviar", "crear_asset"],
                    default=None)
    ap.add_argument("--tenant", default="Aztrotech")
    ap.add_argument("--id", default="auto", help="ID del agente si tipo=agente")
    ap.add_argument("--canal", default="telegram")
    ap.add_argument("--auto", action="store_true", help="Hermes clasifica la orden solo")
    args = ap.parse_args()
    parse_orchestrate(args)
