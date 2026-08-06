#!/usr/bin/env python3
"""Tenant Router — Sonora Digital Corp Multi-Bot Routing.

Mantén un registry de bots → tenant_mapping.
Cuando llega mensaje a cualquier bot:
  1. Identifica el bot desde el token
  2. Busca el tenant mapping
  3. Enruta al agente correspondiente

Uso:
    python3 tenant_router.py --bot aztro_tech_bot --user +52... --message "hola"
    python3 tenant_router.py --list  # muestra mappings
"""
import os, json, sys, argparse
from pathlib import Path
from datetime import datetime

# Registry: bot_name/token_hash → tenant_id
REGISTRY_PATH = Path.home() / ".openclaw" / "workspace" / "tenant_registry.json"

DEFAULT_REGISTRY = {
    "rye": {
        "bot_name": "RyE_production_bot",
        "tenant_id": "rye",
        "agent": "rye",
        "owner": "Iván Guerrero",
        "client": "Cheesee Assistant",
        "channels": ["telegram", "whatsapp"],
        "description": "Ecosistema tecnológico de Iván Guerrero"
    },
    "cesar": {
        "bot_name": "Aztro_tech_bot",
        "tenant_id": "aztrotech",
        "agent": "cesar",
        "owner": "César Holguín",
        "client": "Aztrotech Hermosillo",
        "channels": ["telegram", "web", "whatsapp"],
        "description": "Asistente de ventas de César Holguín"
    },
    "main": {
        "bot_name": "sonora_main_bot",
        "tenant_id": "sonora-digital-corp",
        "agent": "main",
        "owner": "Luis Daniel Guerrero",
        "client": "Sonora Digital Corp",
        "channels": ["telegram", "whatsapp", "web"],
        "description": "Plantilla universal"
    }
}


def init_registry():
    """Crea el archivo de registry si no existe."""
    if not REGISTRY_PATH.exists():
        REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(REGISTRY_PATH, "w") as f:
            json.dump(DEFAULT_REGISTRY, f, indent=2)
    return load_registry()


def load_registry() -> dict:
    """Carga el registry de tenants."""
    if REGISTRY_PATH.exists():
        with open(REGISTRY_PATH) as f:
            return json.load(f)
    return {}


def get_tenant_for_bot(bot_name: str) -> dict:
    """Devuelve el tenant config para un bot específico."""
    registry = load_registry()
    for tenant_id, config in registry.items():
        if config.get("bot_name") == bot_name:
            return {"tenant_id": tenant_id, **config}
    return None


def get_tenant_for_token(token_prefix: str) -> dict:
    """Identifica tenant desde el token (hash o nombre)."""
    registry = load_registry()
    for tenant_id, config in registry.items():
        if token_prefix in tenant_id:
            return {"tenant_id": tenant_id, **config}
    return None


def register_new_tenant(bot_token: str, tenant_id: str, bot_name: str, owner: str, client: str, agent: str = None):
    """Registra un nuevo bot/tenant mapping."""
    registry = load_registry()
    if tenant_id in registry:
        print(f"[WARN] Tenant '{tenant_id}' ya existe. Actualizando...")
    else:
        print(f"[REGISTER] Creando nuevo tenant: {tenant_id}")

    registry[tenant_id] = {
        "bot_name": bot_name,
        "tenant_id": tenant_id,
        "agent": agent or tenant_id,
        "owner": owner,
        "client": client,
        "channels": ["telegram"],
        "registered_at": datetime.utcnow().isoformat(),
        "token_hash": hash(bot_token) % (10**9)  # store hash only
    }

    with open(REGISTRY_PATH, "w") as f:
        json.dump(registry, f, indent=2)
    print(f"[OK] Tenant '{tenant_id}' registrado para bot @{bot_name}")
    return registry[tenant_id]


def list_tenants():
    """Muestra todos los tenants registrados."""
    registry = load_registry()
    if not registry:
        print("No hay tenants registrados")
        return
    print("\n📋 TENANTS REGISTRADOS")
    print("=" * 60)
    for tid, cfg in registry.items():
        print(f"\n🆔 {tid}")
        print(f"   Bot: @{cfg['bot_name']}")
        print(f"   Agente: {cfg['agent']}")
        print(f"   Dueño: {cfg['owner']}")
        print(f"   Cliente: {cfg['client']}")
        print(f"   Canales: {', '.join(cfg['channels'])}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Tenant Router for Multi-Bot")
    ap.add_argument("--list", action="store_true", help="List tenants")
    ap.add_argument("--bot", help="Bot name to route")
    ap.add_argument("--tenant", help="Tenant ID to register")
    ap.add_argument("--owner", help="Owner name")
    ap.add_argument("--client", help="Client name")
    ap.add_argument("--agent", help="Agent ID (optional)")
    ap.add_argument("--token", help="Bot token (for auto-register)")
    args = ap.parse_args()

    init_registry()

    if args.list:
        list_tenants()
    elif args.bot:
        result = get_tenant_for_bot(args.bot)
        if result:
            print(json.dumps(result, indent=2))
        else:
            print(f"No tenant found for bot @{args.bot}")
    elif args.tenant:
        register_new_tenant(args.token or "", args.tenant, args.bot, args.owner, args.client, args.agent)
    else:
        ap.print_help()