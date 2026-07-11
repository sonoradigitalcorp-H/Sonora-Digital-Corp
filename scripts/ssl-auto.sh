#!/bin/bash
# ssl-auto.sh — Automatiza SSL para nuevos dominios
# Uso: ./scripts/ssl-auto.sh <dominio> [puerto] [email]
# Ejemplo: ./scripts/ssl-auto.sh client.sonoradigitalcorp.com 3001 luis@sonora.com

set -euo pipefail

DOMAIN="${1:?Uso: ssl-auto.sh <dominio> [puerto] [email]}"
PORT="${2:-3001}"
EMAIL="${3:-sonoradigitalcorp@gmail.com}"
NGINX_CONF="/etc/nginx/sites-enabled/ssl-auto-${DOMAIN}.conf"

echo "=== SSL Auto: $DOMAIN → :$PORT ==="

# 1. Obtener certificado
sudo certbot certonly --nginx -d "$DOMAIN" --non-interactive --agree-tos --email "$EMAIL" || {
    echo "⚠️  Certbot falló. Asegúrate que el DNS apunte a este servidor."
    exit 1
}

# 2. Generar config nginx
sudo tee "$NGINX_CONF" > /dev/null <<NGINX
server {
    listen 80;
    server_name $DOMAIN;
    return 301 https://\$host\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name $DOMAIN;

    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    location / {
        proxy_pass http://127.0.0.1:$PORT;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
NGINX

# 3. Validar y recargar
sudo nginx -t && sudo systemctl reload nginx
echo "✅ SSL activo: https://$DOMAIN → :$PORT"
