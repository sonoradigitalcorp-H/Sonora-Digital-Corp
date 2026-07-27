#!/bin/bash
# Aplicar config de WebSocket Bridge a nginx
# EJECUTAR EN EL VPS COMO ROOT

set -euo pipefail

NGINX_SITE="/etc/nginx/sites-available/sonoradigitalcorp"
WS_CONF="/home/ubuntu/sonora-digital-corp/infra/nginx/ws-bridge.conf"

echo "╔═══════════════════════════════════════════════╗"
echo "║   Aplicar WebSocket Bridge a nginx            ║"
echo "╚═══════════════════════════════════════════════╝"

# 1. Verificar que el archivo de config existe
if [ ! -f "$WS_CONF" ]; then
    echo "❌ No se encuentra $WS_CONF"
    exit 1
fi

# 2. Hacer backup del site actual
cp "$NGINX_SITE" "${NGINX_SITE}.bak.$(date +%Y%m%d%H%M%S)"
echo "✅ Backup creado"

# 3. Insertar la config WS antes del cierre del server block
if grep -q "location /ws" "$NGINX_SITE"; then
    echo "⚠️  Ya existe config /ws, saltando"
else
    # Buscar el cierre del server block y agregar antes
    cp "$NGINX_SITE" /tmp/nginx-tmp
    # Remover el último '}' del archivo temporal
    head -n -1 /tmp/nginx-tmp > /tmp/nginx-tmp2
    # Agregar la config WS
    cat "$WS_CONF" >> /tmp/nginx-tmp2
    # Agregar el cierre del server
    echo "}" >> /tmp/nginx-tmp2
    # Reemplazar
    mv /tmp/nginx-tmp2 "$NGINX_SITE"
    echo "✅ Config /ws insertada"
fi

# 4. Verificar sintaxis
nginx -t && echo "✅ Sintaxis nginx OK" || { echo "❌ Error de sintaxis"; exit 1; }

# 5. Recargar nginx
systemctl reload nginx && echo "✅ nginx recargado" || { echo "❌ Error al recargar"; exit 1; }

echo ""
echo "╔═══════════════════════════════════════════════╗"
echo "║   ✅ WebSocket Bridge activado                ║"
echo "║   wss://sonoradigitalcorp.com/ws → :8181      ║"
echo "╚═══════════════════════════════════════════════╝"
