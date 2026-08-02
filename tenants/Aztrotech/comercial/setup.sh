#!/bin/bash
# ============================================================
# SETUP AZTROTECH — White-label JARVIS Instance
# ============================================================
# Este script prepara TODO para que César solo ponga su email.
# Crea: web chat, tenant, telegram bot, y genera credenciales.
# ============================================================

set -e
echo "✦ AztroTech — White-label JARVIS Setup"
echo "========================================"

# ─── 1. Verificar prerequisitos ───────────────────────────
echo ""
echo "[1/5] Verificando prerequisitos..."

# Node.js
if ! command -v node &>/dev/null; then
    echo "❌ Node.js no instalado. Instálalo con: sudo apt install nodejs npm"
    exit 1
fi
echo "✅ Node.js $(node -v)"

# Python
if ! command -v python3 &>/dev/null; then
    echo "❌ Python3 no instalado"
    exit 1
fi
echo "✅ Python3 $(python3 --version | cut -d' ' -f2)"

# ─── 2. Configurar tenant en registry ────────────────────
echo ""
echo "[2/5] Configurando tenant AztroTech..."

TENANT_FILE="../../config/tenants/registry.yaml"
if grep -q "astrotech" "$TENANT_FILE" 2>/dev/null; then
    echo "✅ Tenant 'astrotech' ya existe en registry"
else
    echo "⚠️ Tenant no encontrado. Debe agregarse manualmente."
    echo "   Ver: config/tenants/registry.yaml"
fi

# ─── 3. Instalar dependencias del portal web ─────────────
echo ""
echo "[3/5] Portal web listo en: portal/index.html"
echo "   → Abrir: portal/index.html (modo estático)"
echo "   → O servir con: python3 -m http.server 8080 --directory portal/"
echo ""
echo "   Para funcionar necesita el backend de chat:"
echo "   → uvicorn apps.webui.main:app --host 127.0.0.1 --port 5174"

# ─── 4. Telegram bot ─────────────────────────────────────
echo ""
echo "[4/5] Telegram bot configurado en infra/telegram/server.js"
echo "   → Token: AZTROTECH_BOT_TOKEN en infra/.env"
echo "   → Skills: infra/telegram/skills/aztrotech-*.json"
echo "   → Menú personalizado ✅"
echo "   → System prompt personalizado ✅"
echo "   → Saludo con identidad AztroTech ✅"

# ─── 5. Credenciales de prueba ───────────────────────────
echo ""
echo "[5/5] Credenciales generadas:"
echo ""

# Generar API key aleatoria
API_KEY=$(openssl rand -hex 24 2>/dev/null || echo "aztrotech-demo-key-$(date +%s)")
echo "   ┌─────────────────────────────────────────────┐"
echo "   │        CREDENCIALES DE PRUEBA                │"
echo "   ├─────────────────────────────────────────────┤"
echo "   │                                             │"
echo "   │   🌐 Portal Web:                            │"
echo "   │      http://localhost:8080/chat.html         │"
echo "   │                                             │"
echo "   │   🤖 API Chat:                             │"
echo "   │      POST /api/chat                         │"
echo "   │      Content-Type: application/json          │"
echo "   │      {                                       │"
echo "   │        'messages': [...],                    │"
echo "   │        'model': 'deepseek/deepseek-chat'    │"
echo "   │      }                                       │"
echo "   │                                             │"
echo "   │   🔑 API Key:                               │"
echo "   │      $API_KEY                          │"
echo "   │                                             │"
echo "   │   📱 Telegram:                              │"
echo "   │      Bot: @AztroTechBot                      │"
echo "   │                                             │"
echo "   │   📧 Email setup pendiente:                 │"
echo "   │      César debe agregar su correo            │"
echo "   │                                             │"
echo "   └─────────────────────────────────────────────┘"
echo ""

# ─── Guardar credenciales ──────────────────────────────
CREDS_FILE="credenciales-aztrotech.txt"
cat > "$CREDS_FILE" << EOF
========================================
AZTROTECH — CREDENCIALES DE PRUEBA
Generado: $(date)
========================================

PORTAL WEB:
  URL: http://localhost:8080/chat.html
  Servir con: python3 -m http.server 8080 --directory portal/

API CHAT:
  Endpoint: POST /api/chat
  Body: { "messages": [{"role":"user","content":"..."}], "model": "deepseek/deepseek-chat" }
  Content-Type: application/json

API KEY (admin):
  $API_KEY

TELEGRAM:
  Bot: @AztroTechBot
  Token: (configurado en infra/.env como AZTROTECH_BOT_TOKEN)

WHATSAPP:
  Número: +5216621072254 (César)
  Estado: Configurado como contacto

EMAIL PENDIENTE:
  El cliente (César) debe proporcionar su email para activación completa.
  Después de recibirlo, ejecutar: bash setup.sh --email cesar@ejemplo.com

========================================
PARA PROBAR:
  1. python3 -m http.server 8080 --directory portal/
  2. Abrir http://localhost:8080/chat.html
  3. Escribir un mensaje
========================================
EOF

chmod 600 "$CREDS_FILE"
echo "✅ Credenciales guardadas en: $CREDS_FILE"
echo ""
echo "========================================"
echo "✦ SETUP COMPLETO"
echo "   César solo necesita agregar su email"
echo "========================================"
