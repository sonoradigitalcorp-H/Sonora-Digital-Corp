#!/usr/bin/env python3
"""White-Label Tenant Provisioner — Crea nuevos tenants para clientes.

Modo PLATAFORMA (usando infra de SDC):
  - Bot en Telegram/WhatsApp con dominio SDC
  - RAG en Qdrant compartido
  - Postgres compartido (schema separado)
  - TTS/STT compartido
  - Costo: $25,000-35,000 MXN/mes

Modo DOMINIO PROPIO (cliente tiene su infra):
  - Bot en dominio del cliente
  - RAG self-hosted
  - Postgres dedicado
  - TTS/STT dedicado
  - Costo: $75,000-150,000 MXN/mes (implementación) + renta

Uso:
  python3 provision_tenant.py --name "MiEmpresa" --mode platform
  python3 provision_tenant.py --name "MiEmpresa" --mode dedicated --domain emp.mx
"""

import argparse
import json
import os
import sys
import uuid
import yaml
import asyncpg
import subprocess
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent.parent.parent
TENANTS_DIR = BASE_DIR / "tenants"
TEMPLATE_DIR = TENANTS_DIR / "Aztrotech"  # template
QDRANT_URL = "http://localhost:6333"
DB_URL = os.getenv("DATABASE_URL", "postgresql://sdc:${POSTGRES_PASSWORD:-}@localhost:5432/sdc")

# ── Pricing Model ─────────────────────────────────────────────

PRICING = {
    "platform": {
        "name": "Plataforma SDC",
        "description": "Bot en infra compartida de SDC (Telegram/WhatsApp/Web)",
        "implementation": 75000,  # MXN one-time
        "monthly": 25000,  # MXN/mes
        "includes": [
            "Bot Telegram/WhatsApp en dominio SDC",
            "RAG compartido (Qdrant)",
            "Postgres compartido (schema separado)",
            "TTS/STT compartido (edge-tts + whisper)",
            "Soporte estándar",
            "Actualizaciones incluidas",
        ],
        "limits": {
            "conversations_month": 5000,
            "agents": 2,
            "channels": ["telegram", "whatsapp"],
            "voice": True,
            "rag_docs": 50,
        },
    },
    "dedicated": {
        "name": "Dominio Propio",
        "description": "Infra dedicada en dominio del cliente",
        "implementation": 150000,  # MXN one-time
        "monthly": 35000,  # MXN/mes
        "includes": [
            "Bot en dominio del cliente (bot.emp.mx)",
            "RAG self-hosted (Qdrant dedicado)",
            "Postgres dedicado",
            "TTS/STT dedicado (edge-tts + whisper)",
            "Dominio + SSL incluido",
            "Soporte prioritario 24/7",
            "Actualizaciones + customización",
        ],
        "limits": {
            "conversations_month": -1,  # unlimited
            "agents": 5,
            "channels": ["telegram", "whatsapp", "web", "instagram"],
            "voice": True,
            "rag_docs": -1,  # unlimited
        },
    },
    "enterprise": {
        "name": "Enterprise",
        "description": "Solución completa white-label para empresas grandes",
        "implementation": 300000,
        "monthly": 100000,
        "includes": [
            "Todo lo de Dominio Propio",
            "Clon de voz personalizado",
            "CRM integrado",
            "Multi-idioma completo",
            "API personalizada",
            "Equipo dedicado",
            "SLA 99.9%",
        ],
        "limits": {
            "conversations_month": -1,
            "agents": -1,
            "channels": ["telegram", "whatsapp", "web", "instagram", "facebook", "voice"],
            "voice": True,
            "rag_docs": -1,
        },
    },
}

# ── Tenant Template ───────────────────────────────────────────

def create_tenant_config(name: str, mode: str, **kwargs) -> dict:
    """Create tenant config from template."""
    slug = name.lower().replace(" ", "_").replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
    
    pricing = PRICING.get(mode, PRICING["platform"])
    
    config = {
        "tenant_id": slug,
        "display_name": name,
        "company": name,
        "owner": kwargs.get("owner", ""),
        "language": kwargs.get("language", "es"),
        "timezone": kwargs.get("timezone", "America/Mexico_City"),
        "default_model": "deepseek/deepseek-v4-flash",
        "max_tokens": 4096,
        
        "models": {
            "default": "deepseek/deepseek-v4-flash",
            "reasoning": "z-ai/glm-5.2",
            "premium": "moonshotai/kimi-k2.7-code",
            "embeddings": {
                "provider": "fastembed",
                "model": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
            },
        },
        
        "openrouter": {
            "base_url": "https://openrouter.ai/api/v1",
            "max_retries": 3,
            "timeout": 30,
        },
        
        "channels": {
            "telegram": {
                "enabled": True,
                "bot_token": kwargs.get("telegram_token", ""),
                "owner_chat_id": kwargs.get("owner_chat_id", ""),
            },
            "whatsapp": {
                "enabled": False,
                "provider": "wacli",
            },
        },
        
        "voice": {
            "stt": {
                "provider": "faster-whisper",
                "model": "small",
                "language": "es",
            },
            "tts": {
                "provider": "edge-tts",
                "voice": "es-MX-DaliaNeural",
            },
        },
        
        "rag": {
            "chunk_size": 512,
            "chunk_overlap": 64,
            "top_k": 5,
            "min_score": 0.65,
        },
        
        "white_label": {
            "mode": mode,
            "pricing": pricing,
            "domain": kwargs.get("domain", ""),
            "provisioned_at": datetime.now().isoformat(),
        },
    }
    
    return config


def create_tenant_dir(name: str, config: dict):
    """Create tenant directory structure."""
    slug = config["tenant_id"]
    tenant_dir = TENANTS_DIR / slug
    tenant_dir.mkdir(parents=True, exist_ok=True)
    
    # Config
    (tenant_dir / "config.yaml").write_text(yaml.dump(config, default_flow_style=False, allow_unicode=True))
    
    # Bot directory
    bot_dir = tenant_dir / "bot"
    bot_dir.mkdir(exist_ok=True)
    
    # Copy template files from Aztrotech
    template_bot = TENANTS_DIR / "Aztrotech" / "bot"
    if template_bot.exists():
        for f in ["conversation_engine.py", "lead_classifier.py", "emotion_analyzer.py", 
                   "prompt_builder.py", "rag_retriever.py", "persistence.py", "token_tracker.py",
                   "identity_resolver.py", "emerge_memory.py"]:
            src = template_bot / f
            if src.exists():
                (bot_dir / f).write_text(src.read_text())
    
    # Skills directory
    (tenant_dir / "skills").mkdir(exist_ok=True)
    
    # Knowledge directory
    (tenant_dir / "knowledge").mkdir(exist_ok=True)
    
    return tenant_dir


async def create_postgres_schema(slug: str):
    """Create Postgres schema for tenant."""
    try:
        pool = await asyncpg.create_pool(DB_URL, min_size=1, max_size=2)
        
        # Create schema
        await pool.execute(f"CREATE SCHEMA IF NOT EXISTS {slug}")
        
        # Create tables in schema
        await pool.execute(f"""
            CREATE TABLE IF NOT EXISTS {slug}.conversations (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                platform VARCHAR(20) NOT NULL,
                platform_conversation_id VARCHAR(100),
                lead_type VARCHAR(10),
                lead_confidence DOUBLE PRECISION,
                emotion_snapshot JSONB DEFAULT '{{}}',
                language VARCHAR(10) DEFAULT 'es',
                started_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW(),
                closed_at TIMESTAMPTZ,
                metadata JSONB DEFAULT '{{}}'
            );
            
            CREATE TABLE IF NOT EXISTS {slug}.messages (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                conversation_id UUID REFERENCES {slug}.conversations(id),
                turn_number INTEGER NOT NULL,
                role VARCHAR(10) NOT NULL,
                content TEXT NOT NULL,
                tokens_in INTEGER,
                tokens_out INTEGER,
                model VARCHAR(80),
                cost_usd NUMERIC(12,6),
                emotion_scores JSONB DEFAULT '{{}}',
                rag_chunks_used JSONB DEFAULT '[]',
                language VARCHAR(10),
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
            
            CREATE TABLE IF NOT EXISTS {slug}.leads (
                id SERIAL PRIMARY KEY,
                phone TEXT,
                name TEXT,
                source TEXT DEFAULT 'telegram',
                lead_score INTEGER DEFAULT 0,
                lead_type TEXT DEFAULT 'cold',
                notes TEXT,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            );
            
            CREATE TABLE IF NOT EXISTS {slug}.daily_metrics (
                id SERIAL PRIMARY KEY,
                day DATE NOT NULL,
                conversations INTEGER DEFAULT 0,
                messages INTEGER DEFAULT 0,
                tokens_in INTEGER DEFAULT 0,
                tokens_out INTEGER DEFAULT 0,
                cost_usd NUMERIC(12,6) DEFAULT 0,
                leads INTEGER DEFAULT 0,
                hot_leads INTEGER DEFAULT 0
            );
        """)
        
        await pool.close()
        print(f"  ✅ Postgres schema '{slug}' created")
    except Exception as e:
        print(f"  ❌ Postgres error: {e}")


async def create_qdrant_collection(slug: str):
    """Create Qdrant collection for tenant."""
    try:
        import httpx
        collection_name = f"{slug}_knowledge"
        
        async with httpx.AsyncClient(timeout=10) as client:
            # Check if exists
            r = await client.get(f"{QDRANT_URL}/collections/{collection_name}")
            if r.status_code == 200:
                print(f"  ⚠️  Collection '{collection_name}' already exists")
                return
            
            # Create collection
            r = await client.put(f"{QDRANT_URL}/collections/{collection_name}", json={
                "vectors": {
                    "size": 384,
                    "distance": "Cosine",
                }
            })
            
            if r.status_code == 200:
                print(f"  ✅ Qdrant collection '{collection_name}' created")
            else:
                print(f"  ❌ Qdrant error: {r.text}")
    except Exception as e:
        print(f"  ❌ Qdrant error: {e}")


def create_systemd_services(slug: str, config: dict):
    """Create systemd services for tenant."""
    pricing = config["white_label"]["pricing"]
    
    # Bot service
    bot_service = f"""[Unit]
Description={config['display_name']} Bot - White Label
After=network.target

[Service]
Type=simple
User=mystic
WorkingDirectory=/home/mystic/Documentos/Sonora Digital Corp/sonora-digital-corp/tenants/{slug}/bot
Environment="OPENROUTER_API_KEY={os.getenv('OPENROUTER_API_KEY', '')}"
Environment="TENANT_ID={slug}"
ExecStart=/usr/bin/python3 main.py
Restart=always
RestartSec=5
StandardOutput=append:/var/log/sdc/{slug}-bot.log
StandardError=append:/var/log/sdc/{slug}-bot-error.log

[Install]
WantedBy=multi-user.target
"""
    
    service_path = f"/etc/systemd/system/sdc-{slug}-bot.service"
    try:
        with open(service_path, "w") as f:
            f.write(bot_service)
        print(f"  ✅ Systemd service 'sdc-{slug}-bot.service' created")
    except PermissionError:
        # Write to temp and suggest sudo
        tmp_path = TENANTS_DIR / slug / "sdc-bot.service"
        tmp_path.write_text(bot_service)
        print(f"  ⚠️  Systemd service saved to {tmp_path} (run: sudo cp {tmp_path} {service_path})")


def create_env_file(slug: str, config: dict):
    """Create .env file for tenant."""
    env_content = f"""# {config['display_name']} - White Label Environment
TENANT_ID={slug}
OPENROUTER_API_KEY={os.getenv('OPENROUTER_API_KEY', '')}
TELEGRAM_BOT_TOKEN={config['channels']['telegram'].get('bot_token', '')}
OWNER_CHAT_ID={config['channels']['telegram'].get('owner_chat_id', '')}
"""
    
    env_path = TENANTS_DIR / slug / ".env"
    env_path.write_text(env_content)
    print(f"  ✅ .env file created")


async def provision_tenant(name: str, mode: str, **kwargs):
    """Provision a new white-label tenant."""
    print(f"\n{'='*60}")
    print(f"🏢 PROVISIONING WHITE-LABEL TENANT")
    print(f"{'='*60}")
    print(f"  Nombre: {name}")
    print(f"  Modo: {mode}")
    print(f"  Precio: ${PRICING[mode]['monthly']:,}/mes + ${PRICING[mode]['implementation']:,} implementación")
    print()
    
    # 1. Create config
    config = create_tenant_config(name, mode, **kwargs)
    print(f"  ✅ Config created")
    
    # 2. Create directory structure
    tenant_dir = create_tenant_dir(name, config)
    print(f"  ✅ Directory structure: {tenant_dir}")
    
    # 3. Create Postgres schema
    await create_postgres_schema(config["tenant_id"])
    
    # 4. Create Qdrant collection
    await create_qdrant_collection(config["tenant_id"])
    
    # 5. Create systemd services
    create_systemd_services(config["tenant_id"], config)
    
    # 6. Create .env
    create_env_file(config["tenant_id"], config)
    
    # 7. Print summary
    pricing = PRICING[mode]
    print(f"\n{'='*60}")
    print(f"✅ TENANT '{name}' PROVISIONED SUCCESSFULLY")
    print(f"{'='*60}")
    print(f"  Tenant ID: {config['tenant_id']}")
    print(f"  Directorio: {tenant_dir}")
    print(f"  Schema Postgres: {config['tenant_id']}")
    print(f"  Collection Qdrant: {config['tenant_id']}_knowledge")
    print(f"  Systemd: sdc-{config['tenant_id']}-bot.service")
    print()
    print(f"  💰 PRICING:")
    print(f"     Implementación: ${pricing['implementation']:,} MXN (una vez)")
    print(f"     Renta mensual: ${pricing['monthly']:,} MXN/mes")
    print(f"     Incluye: {', '.join(pricing['includes'][:3])}...")
    print()
    print(f"  📋 PRÓXIMOS PASOS:")
    print(f"     1. Configurar bot_token en {tenant_dir}/config.yaml")
    print(f"     2. Añadir knowledge docs en {tenant_dir}/knowledge/")
    print(f"     3. Crear systemd service: sudo systemctl enable sdc-{config['tenant_id']}-bot")
    print(f"     4. Iniciar: sudo systemctl start sdc-{config['tenant_id']}-bot")
    
    return config


def main():
    parser = argparse.ArgumentParser(description="Provision white-label tenant")
    parser.add_argument("--name", required=True, help="Company name")
    parser.add_argument("--mode", choices=["platform", "dedicated", "enterprise"], default="platform")
    parser.add_argument("--owner", default="", help="Owner name")
    parser.add_argument("--domain", default="", help="Custom domain (dedicated mode)")
    parser.add_argument("--telegram-token", default="", help="Telegram bot token")
    parser.add_argument("--owner-chat-id", default="", help="Owner Telegram chat ID")
    args = parser.parse_args()
    
    asyncio.run(provision_tenant(
        name=args.name,
        mode=args.mode,
        owner=args.owner,
        domain=args.domain,
        telegram_token=args.telegram_token,
        owner_chat_id=args.owner_chat_id,
    ))


if __name__ == "__main__":
    import asyncio
    main()