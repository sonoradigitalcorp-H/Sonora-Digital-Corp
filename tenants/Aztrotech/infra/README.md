# Infraestructura — Sonora Digital Corp

## Cuando el VPS esté accesible

### 1. SSL Wildcard

```bash
# DNS: agregar TXT _acme-challenge en:
#   sonoradigitalcorp.com
#   *.sonoradigitalcorp.com
#   aztrotech.mx
#   *.aztrotech.mx

certbot certonly --manual --preferred-challenges dns \
  -d sonoradigitalcorp.com -d "*.sonoradigitalcorp.com" \
  -d aztrotech.mx -d "*.aztrotech.mx" \
  --email mystic@sonoradigitalcorp.com --agree-tos
```

### 2. NGINX Router

```bash
cp nginx-router.conf /etc/nginx/sites-available/sonora-router
ln -sf /etc/nginx/sites-available/sonora-router /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx
```

### 3. Servicios

```bash
docker compose up -d
```

### 4. Mysticgrimoire (chat web)

```bash
systemctl enable --now mysticgrimoire
```

## Mapa de dominios

| Dominio | Apunta a | Uso |
|---|---|---|
| sonoradigitalcorp.com | VPS directo | Landing SDC |
| *.sonoradigitalcorp.com | VPS → :8767 | Clientes Despertar/Elevar |
| aztrotech.mx | VPS → :8767 | César |
| admin.sonoradigitalcorp.com | VPS → varios | OpenClaw, Qdrant, n8n (con auth) |

## Estructura de tenants en el VPS

```
/opt/tenants/
├── astrotech/       ← César (con web/server.py + static/)
├── clinica-smile/   ← cliente 2 (cuando llegue)
├── restaurante-luna/ ← cliente 3
└── ...
```

Cada tenant tiene su propia carpeta con su server.py apuntando a su KB y voz.
