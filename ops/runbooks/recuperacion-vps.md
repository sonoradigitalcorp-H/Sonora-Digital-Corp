# Runbook: Recuperación VPS sdc-prod

## Goal
Recuperar el VPS de producción tras caída, OOM, o degradación severa.

## Síntomas comunes
- SSH no responde
- `docker ps` muestra contenedores muertos
- `free -h` muestra swap al 100%
- Servicios devuelven 502

## Recovery steps

### 1. Conectar
```bash
ssh sdc-prod@149.56.46.173
```

### 2. Diagnóstico rápido
```bash
free -h                    # RAM y swap
df -h                      # disco
docker ps -a               # estado de contenedores
systemctl --failed         # servicios caídos
journalctl -xe -n 50       # errores recientes
```

### 3. Liberar memoria
```bash
# Matar contenedores no esenciales
docker stop sdc-langfuse sdc-langfuse-db sdc-telegram-bot

# Limpiar caché
sync && echo 3 > /proc/sys/vm/drop_caches

# Verificar swap
swapoff -a && swapon -a
```

### 4. Orden de arranque
```bash
# 1. Base de datos primero
docker start sdc-postgres
sleep 5

# 2. Redis (no tiene dependencias)
docker start sdc-redis

# 3. Qdrant + Neo4j
docker start sdc-qdrant sdc-neo4j
sleep 3

# 4. n8n (necesita postgres)
docker start sdc-n8n
sleep 3

# 5. Servicios de aplicación
docker start sdc-mcp-server sdc-hermes-gateway
systemctl start openclaw-gateway.service --user
```

### 5. Verificar todo
```bash
docker ps --format 'table {{.Names}}\t{{.Status}}'
curl -sf http://localhost:8000/health && echo "MCP OK"
curl -sf http://localhost:5678/healthz && echo "n8n OK"
curl -sf http://localhost:6333/health && echo "Qdrant OK"
```

### 6. Si el VPS no responde SSH
- Reboot desde panel de OVH
- Esperar 2-3 minutos
- Intentar SSH
- Si no responde → abrir ticket en OVH

## Datos críticos
- Los datos persistentes están en volúmenes Docker
- `.env.age` cifrado con age key local
- Las bases de datos tienen backup diario vía `sdc ops backup`
- Git remote: `http://149.56.46.173:3080/mystic/Sonora-Digital-Corp.git`
