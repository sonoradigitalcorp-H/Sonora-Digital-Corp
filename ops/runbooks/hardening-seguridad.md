# Hardening de Seguridad — Cerrar todo, abrir solo lo necesario

## Estado actual (desde fuera)

```
Puertos abiertos: 80, 443
Dominios públicos:
  ✅ sonoradigitalcorp.com     → producción (landing)
  ✅ git.sonoradigitalcorp.com → 🔴 GITEA DEBE IRSE A PRIVADO
  ✅ api.sonoradigitalcorp.com → producción (API partners)
  ❌ voice.sonoradigitalcorp.com → no resuelve (hay que crearlo)
  ❌ grimorio.sonoradigitalcorp.com → no resuelve (hay que crearlo)
```

## Objetivo

```
PÚBLICO (solo producción):
  voice.sonoradigitalcorp.com   → Mystic Voice + Kokoro
  grimorio.sonoradigitalcorp.com → Grimoire 3D (Agentic OS)
  api.sonoradigitalcorp.com     → Galaxy Backend (partners)
  sonoradigitalcorp.com         → Landing page

PRIVADO (solo vía túnel):
  git.sonoradigitalcorp.com     → Gitea (fuera de DNS público)
  postgres, neo4j, qdrant, redis → localhost:puerto
  n8n                             → localhost:5678
  ollama                          → localhost:11434
  hermes                          → localhost:18789
```

## Plan de acción (cuando SSH reconecte)

### PASO 1: Quitar Gitea de la cara pública

```bash
# 1. Deshabilitar el sitio nginx de Gitea
sudo rm /etc/nginx/sites-enabled/gitea.conf

# 2. Eliminar el registro DNS git.sonoradigitalcorp.com (desde Hostinger)

# 3. Gitea sigue corriendo en localhost:3080
#    Accesible solo vía SSH tunnel o Tailscale
```

### PASO 2: Instalar Tailscale (red privada mesh)

```bash
# En el VPS:
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up --auth-key=tskey-auth-xxxxx

# En tu laptop:
#    1. Instalar Tailscale desde https://tailscale.com/download
#    2. Iniciar sesión con la misma cuenta
#    3. Ambas máquinas se ven en la red 100.x.x.x

# Verificar:
tailscale status
# sdc-prod  100.64.0.1  ubuntu
# laptop    100.64.0.2  luis-daniel
```

### PASO 3: Acceder a Gitea desde la laptop vía Tailscale

```bash
# La laptop ahora puede acceder a Gitea directamente:
git remote set-url origin http://100.64.0.1:3080/mystic/Sonora-Digital-Corp.git
# O por SSH tunnel si prefieres:
ssh -L 3080:localhost:3080 ovh
# Y luego:
git remote set-url origin http://localhost:3080/mystic/Sonora-Digital-Corp.git
```

### PASO 4: Configurar nginx solo para producción

```bash
# Crear sitio para voice
sudo tee /etc/nginx/sites-enabled/voice.conf << 'EOF'
server {
    listen 443 ssl;
    server_name voice.sonoradigitalcorp.com;
    ssl_certificate /etc/letsencrypt/live/sonoradigitalcorp.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/sonoradigitalcorp.com/privkey.pem;
    location / {
        proxy_pass http://127.0.0.1:8900;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
EOF

# Crear sitio para grimoire
sudo tee /etc/nginx/sites-enabled/grimoire.conf << 'EOF'
server {
    listen 443 ssl;
    server_name grimorio.sonoradigitalcorp.com;
    ssl_certificate /etc/letsencrypt/live/sonoradigitalcorp.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/sonoradigitalcorp.com/privkey.pem;
    root /var/www/grimoire;
    index index.html;
    location / {
        try_files $uri $uri/ /index.html;
    }
}
EOF

# Crear sitio para API de partners
sudo tee /etc/nginx/sites-enabled/api.conf << 'EOF'
server {
    listen 443 ssl;
    server_name api.sonoradigitalcorp.com;
    ssl_certificate /etc/letsencrypt/live/sonoradigitalcorp.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/sonoradigitalcorp.com/privkey.pem;
    location / {
        proxy_pass http://127.0.0.1:8100;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
EOF

# Quitar sitios que no deben estar públicos
sudo rm -f /etc/nginx/sites-enabled/gitea.conf
sudo rm -f /etc/nginx/sites-enabled/abe
sudo rm -f /etc/nginx/sites-enabled/lovable
# ... quitar cualquier otro que no sea producción

# Recargar nginx
sudo nginx -t && sudo nginx -s reload
```

### PASO 5: UFW - Firewall de mínimos

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 2222/tcp    # SSH desde tu IP fija
sudo ufw --force enable
sudo ufw status verbose
```

### Acceso del desarrollador (tú)

Después de esto, tu flujo de trabajo será:

```
# Opción A: Tailscale (recomendado)
git remote set-url origin http://100.64.0.1:3080/mystic/Sonora-Digital-Corp.git
git push origin main  # funciona directo, sin tunnel

# Opción B: SSH Tunnel (alternativa)
ssh -L 3080:localhost:3080 ovh -f -N
git remote set-url origin http://localhost:3080/mystic/Sonora-Digital-Corp.git
git push origin main

# Opción C: Deploy con Coolify (cuando esté instalado)
# Interfaz web para deploy con 1 click, todo en red privada
```
