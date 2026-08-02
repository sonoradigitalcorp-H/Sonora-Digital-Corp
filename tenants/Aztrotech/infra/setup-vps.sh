#!/bin/bash
# Setup VPS — Wildcard SSL + Router NGINX + Servicios
# Ejecutar en VPS como root o con sudo

set -e

DOMAIN_SDC="sonoradigitalcorp.com"
DOMAIN_AT="aztrotech.mx"
EMAIL="mystic@sonoradigitalcorp.com"

echo "=== 1. Actualizar sistema ==="
apt update && apt upgrade -y

echo "=== 2. Instalar NGINX + Certbot ==="
apt install -y nginx certbot python3-certbot-nginx

echo "=== 3. Wildcard SSL (manual - requiere DNS TXT) ==="
echo ""
echo "Ejecuta ESTO y agrega los registros TXT en tu DNS:"
echo ""
echo "  certbot certonly --manual --preferred-challenges dns \\"
echo "    -d $DOMAIN_SDC -d '*.$DOMAIN_SDC' \\"
echo "    -d $DOMAIN_AT -d '*.$DOMAIN_AT' \\"
echo "    --email $EMAIL --agree-tos"
echo ""
echo "Luego de obtener los certificados, copia nginx-router.conf:"
echo ""
echo "  cp nginx-router.conf /etc/nginx/sites-available/sonora-router"
echo "  ln -sf /etc/nginx/sites-available/sonora-router /etc/nginx/sites-enabled/"
echo "  nginx -t && systemctl reload nginx"
echo ""

echo "=== 4. Directorios web ==="
mkdir -p /var/www/sonoradigitalcorp
echo "<h1>Sonora Digital Corp</h1>" > /var/www/sonoradigitalcorp/index.html

echo "=== 5. Servicios (Docker) ==="
cd /opt/sonora
docker compose up -d 2>/dev/null || echo "Docker compose no encontrado, instalar manual"

echo "=== 6. Mysticgrimoire (chat web) ==="
cat > /etc/systemd/system/mysticgrimoire.service << 'SERV'
[Unit]
Description=Mysticgrimoire - AstroTech AI Chat
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/tenants/astrotech/web
Environment=OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
ExecStart=/usr/bin/python3 -m uvicorn server:app --host 0.0.0.0 --port 8767
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
SERV

echo ""
echo "=== 7. Firewall ==="
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 22/tcp
ufw --force enable

echo ""
echo "=== LISTO ==="
echo "Cuando tengas los certificados, corre:"
echo "  systemctl enable --now mysticgrimoire"
echo "  systemctl reload nginx"
