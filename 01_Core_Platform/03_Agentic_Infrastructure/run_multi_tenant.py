#!/usr/bin/env python3
"""run_multi_tenant.py — Entrypoint para servicio systemd multi-tenant bot webhook."""
import sys
import os
from pathlib import Path

# Agregar ruta de webhooks al sys.path
PROJECT_ROOT = Path("/home/mystic/Documentos/Sonora Digital Corp Nuevo")
WEBHOOKS_DIR = PROJECT_ROOT / "02_Client_Projects" / "Aztrotech" / "03_Media_Assets" / "webhooks"

sys.path.insert(0, str(WEBHOOKS_DIR))
os.chdir(str(WEBHOOKS_DIR))

try:
    from multi_tenant_webhook import run_server
    print("🚀 Iniciando Multi-Tenant Webhook server en puerto 5289...")
    run_server(5289)
except Exception as e:
    print(f"❌ Error al iniciar Multi-Tenant Webhook: {e}")
    sys.exit(1)
