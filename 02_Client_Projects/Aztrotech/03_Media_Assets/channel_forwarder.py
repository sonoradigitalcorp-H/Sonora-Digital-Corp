#!/usr/bin/env python3
"""Channel Forwarder — Multi-Bot Routing para OpenClaw.

Este script actúa como middleware entre múltiples bots Telegram y los agentes OpenClaw.
Cuando un mensaje llega a CUALQUIER bot:
  1. El gateway lo recibe en modo polling global
  2. Este script determina a qué tenant/agente debe ir
  3. Hace forward del mensaje al agente correcto

Para usar:
  - Setea MULTI_TENANT_ROUTER=1 en el entorno del gateway
  - El gateway llama a este script para cada mensaje
"""
import os, sys, json
from pathlib import Path

# Import bridge functions
try:
    from channel_bridge import route_message, channel_registry
except ImportError:
    channel_bridge = None

TENANT_REGISTRY = Path.home() / ".openclaw" / "workspace" / "tenant_registry.json"


def load_registry():
    if TENANT_REGISTRY.exists():
        with open(TENANT_REGISTRY) as f:
            return json.load(f)
    return {}


def route_by_bot_name(bot_name: str, user_id: int, message: str, media_path: str = None):
    """
    Determina el tenant correcto y despacha el mensaje.

    Args:
        bot_name: Nombre del bot (@RyE_production_bot, @Aztro_tech_bot, etc.)
        user_id: ID del usuario en Telegram
        message: Texto del mensaje
        media_path: Ruta a archivo multimedia si aplica

    Returns:
        Path to result JSON that agent can process
    """
    registry = load_registry()

    # Buscar tenant por bot_name
    tenant_id = None
    tenant_config = None

    for tid, cfg in registry.items():
        if cfg.get("bot_name") == bot_name:
            tenant_id = tid
            tenant_config = cfg
            break

    if not tenant_id:
        # Fallback: usar el agente default si el bot no está registrado
        print(f"[WARN] Bot @{bot_name} no registrado, usando agente default")
        tenant_id = "main"
        tenant_config = {"agent": "main", "tenant_id": "main"}

    agent_id = tenant_config.get("agent", tenant_id)

    # Construir payload para agente OpenClaw
    payload = {
        "tenant_id": tenant_id,
        "agent_id": agent_id,
        "source": "telegram",
        "user_id": user_id,
        "channel": "telegram",
        "message": message,
        "media_path": media_path,
        "bot_name": bot_name,
        "routed_at": __import__('datetime').datetime.utcnow().isoformat()
    }

    # Serializar para el agente
    tenant_dir = Path.home() / ".openclaw" / "agents" / agent_id
    tenant_dir.mkdir(parents=True, exist_ok=True)

    payload_file = tenant_dir / "incoming_message.json"
    with open(payload_file, "w") as f:
        json.dump(payload, f, indent=2)

    print(f"[FORWARD] Mensaje a tenant={tenant_id}, agent={agent_id}, user={user_id}")
    return str(payload_file)


def register_tenant_from_wacli():
    """
    Cuando wacli recibe archivos de un bot, registra automáticamente el tenant.
    Útil para: WhatsApp → wacli → auto-detect tenant
    """
    env = {
        "TELEGRAM_BOT_NAME": os.environ.get("TELEGRAM_BOT_NAME", ""),
        "TENANT_ID": os.environ.get("TENANT_ID", ""),
        "CLIENT_NAME": os.environ.get("CLIENT_NAME", "")
    }
    return env


if __name__ == "__main__":
    # Modo CLI para testing
    import argparse
    ap = argparse.ArgumentParser(description="Channel Forwarder")
    ap.add_argument("--bot", required=True, help="Bot name")
    ap.add_argument("--user", type=int, required=True, help="User Telegram ID")
    ap.add_argument("--message", required=True, help="Message text")
    ap.add_argument("--media", default=None, help="Media file path")
    args = ap.parse_args()

    result = route_by_bot_name(args.bot, args.user, args.message, args.media)
    print(f"Payload escrito en: {result}")