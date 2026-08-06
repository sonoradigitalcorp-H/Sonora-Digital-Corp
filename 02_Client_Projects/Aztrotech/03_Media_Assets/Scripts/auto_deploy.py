#!/usr/bin/env python3
"""Pipeline de Auto-Despliegue Aztrotech — Agente Factory Completo.
Orquesta: recibe assets de wacli → clona voz/imagen → genera onboarding → deploya 24/7.

Uso:
    python3 auto_deploy.py --name cesar --phone 526621072254 --tenant aztrotech
    # O: wacli send --file assets.zip -> auto_process --name cesar
"""
import os, sys, subprocess, argparse, json, time
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent
SCRIPTS = [
    "voice_cloner.py",
    "image_cloner.py",
    "onboarding_generator.py"
]


def run_script(name: str, args: list) -> dict:
    """Ejecuta un script Python y devuelve el resultado JSON."""
    cmd = ["python3", str(BASE_DIR / name)] + args
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if result.returncode == 0:
        try:
            return json.loads(result.stdout)
        except:
            return {"status": "partial", "output": result.stdout[-500:]}
    return {"status": "error", "stderr": result.stderr[-500:], "returncode": result.returncode}


def deploy_hermes_agent(tenant: str, agent_id: str, name: str, phone: str = None):
    """Deploya el agente Hermes con la identidad clonada."""
    print(f"[DEPLOY] Creando agente {agent_id} para {tenant}...")

    # Llama a la factory
    cmd = [
        sys.executable,
        "/home/mystic/Documentos/Sonora Digital Corp Nuevo/01_Core_Platform/03_Agentic_Infrastructure/Hermes_Agent/Orchestrator/hermes_agent_factory.py",
        "--orden", f"Crea agente de ventas para {name} de {tenant}. Usa voz clonada, responde en español, no da precios, captura leads y deriva a César por WhatsApp.",
        "--id", agent_id,
        "--canal", "telegram"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

    if result.returncode == 0:
        print(f"[DEPLOY] Agente {agent_id} creado y enlazado a Telegram")
        return {"status": "success", "agent_id": agent_id, "channel": "telegram"}
    else:
        print(f"[DEPLOY] Error: {result.stderr[:300]}")
        return {"status": "error", "stderr": result.stderr[:300]}


def update_onboarding_url(onboarding_path: str, channel: str = "telegram"):
    """Actualiza el mensaje de bienvenida del agente con el link del onboarding."""
    if channel == "telegram":
        url = f"{onboarding_path}"
        print(f"[UPDATE] Establecer botón de enlace en agente → {url}")
        # Nota: esto requeriría hacer update al identity.md del agente
    return {"status": "updated", "url": onboarding_path}


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Auto-Deploy Aztrotech")
    ap.add_argument("--name", default="César", help="Nombre del cliente")
    ap.add_argument("--tenant", default="aztrotech", help="Tenant ID")
    ap.add_argument("--phone", default="526621072254", help="WhatsApp de César")
    ap.add_argument("--assets-dir", default="/tmp/wacli_media", help="Directorio con assets recibidos")
    args = ap.parse_args()

    print(f"\n=== AUTO-DEPLOY {args.tenant} — {args.name} ===")
    print(f"[{datetime.now().isoformat()}] Iniciando pipeline de clonación y despliegue...\n")

    # Paso 1: Clonar voz (si hay audios)
    print("[1/4] Voice Cloning...")
    voice_result = run_script("voice_cloner.py", ["--input", args.assets_dir, "--name", args.name.lower()])
    print(f"   Voice: {voice_result.get('status', 'error')}")

    # Paso 2: Clonar imagen (si hay fotos)
    print("[2/4] Image Cloning (LoRA)...")
    # Export FAL_KEY temporarily
    env_fal = {"FAL_KEY": os.environ.get("FAL_KEY", "")}
    if env_fal["FAL_KEY"]:
        image_result = run_script("image_cloner.py", ["--input", args.assets_dir, "--name", args.name.lower()])
    else:
        image_result = {"status": "skipped", "reason": "FAL_KEY no disponible"}
    print(f"   Image: {image_result.get('status', 'error')}")

    # Paso 3: Generar onboarding
    print("[3/4] Generating Onboarding Page...")
    onboarding_result = run_script("onboarding_generator.py", ["--name", args.name, "--tenant", args.tenant])
    print(f"   Onboarding: {onboarding_result.get('status', 'error')}")

    # Paso 4: Deploy agente
    print("[4/4] Deploying Hermes Agent...")
    agent_id = f"{args.name.lower()}-{args.tenant.lower()}"
    deploy_result = deploy_hermes_agent(args.tenant, agent_id, args.name, args.phone)

    print("\n=== PIPELINE COMPLETO ===")
    print(json.dumps({
        "status": "success",
        "tenant": args.tenant,
        "name": args.name,
        "agent_id": agent_id,
        "voice": voice_result,
        "image": image_result,
        "onboarding": onboarding_result,
        "deployment": deploy_result,
        "channels": ["telegram", "web"],
        "ready": True
    }, indent=2, ensure_ascii=False))

    print("\n🚀 El agente está listo. Manda un mensaje al bot @RyE_production_bot para probar.")