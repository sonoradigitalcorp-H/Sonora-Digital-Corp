# SONORA DIGITAL CORP — ESTADO DEL SISTEMA
# Ultima actualizacion: 2026-06-12 16:20 MST
# Este archivo se carga al inicio de cada sesion via brain-feed.sh

## VERDADES ABSOLUTAS
- **Public IP**: 201.175.210.106 (Hostinger VPS)
- **Domain**: sonoradigitalcorp.com → apunta a 187.124.85.191 (WRONG! Cambiar a 201.175.210.106)
- **RAM**: 3.2GB total, 1.0GB disponible, 2.0GB swap usado de 4.4GB
- **Modelo**: DeepSeek V4 Flash

## SERVICIOS ACTIVOS
- nginx: 80 (HTTP), 443 (SSL pending)
- Docker: 10 contenedores (hermes_api, frontend, n8n, neo4j, qdrant, postgres, redis, telegram_bot, whatsapp_bridge, wa)
- Ollama: nomic-embed-text
- SSH: puerto 22, solo key, rate limited
- UFW: 22/80/443 only, deny all else

## AUTOMATIZACIONES CONFIRMADAS (11/14)
✅ Healthcheck (cada 15min) - OK
✅ Backup script - syntax OK
✅ Self-improve (cada 6h) - syntax OK
✅ Secure backup - syntax OK
✅ Social automation - syntax OK
✅ Memory save (cada hora) - syntax OK
✅ Docker: 10 containers running
✅ nginx config - OK
✅ Ollama - OK
✅ Neo4j - OK
✅ Frontend (3000) - OK (200)
✅ API Backend (8000) - OK (sirve /status)
❌ sync_vps.sh - FIXED (VPS anterior muerto)
✅ n8n (5678) - OK (200, necesita auth)
✅ Qdrant (6333) - OK

## FIREWALL + SEGURIDAD
- RDP (3389): CERRADO y masked
- SSH: solo key, MaxAuthTries 3, MaxSessions 5
- UFW: default deny incoming, allow 22/80/443
- RAM monitor: mata proceso mas pesado si >90%

## LLECCIONES APRENDIDAS (ERRORES QUE NO REPETIR)
1. No inventar comandos sin verificar primero
2. No saltarse el paso de deploy
3. Verificar con grep antes de afirmar
4. No cambiar de direccion cada sesion
5. Documentar errores inmediatamente
6. Preguntar antes de asumir preferencias
7. Guardar estado antes de compactar sesion
8. Verificar automaciones periodicamente

## SITIOS DEPLOYADOS
- https://sonoradigitalcorp-h.github.io/productos-hector-rubio/ (GitHub Pages)
- https://sonoradigitalcorp-h.github.io/productos-jesus-urquijo/ (GitHub Pages)
- https://sonoradigitalcorp-h.github.io/productos-javier-arvayo/ (GitHub Pages)
- http://201.175.210.106/ (Frontend Next.js)
- http://201.175.210.106:5678/ (n8n)
- http://201.175.210.106:8000/status (API)

## PROXIMOS PASOS (en orden)
1. [CEO] Ir a Hostinger → DNS → cambiar A record → 201.175.210.106
2. [AUTOMATICO] sudo certbot --nginx -d sonoradigitalcorp.com -d www.sonoradigitalcorp.com
3. [DEV] Ensamblar voice loop (wake → STT → LLM → TTS)
4. [DEV] Unificar repos en monorepo
5. [SEC] Rotar 29 API keys expuestas
