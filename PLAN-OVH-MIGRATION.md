# PLAN MAESTRO — Migración a OVH VPS
## Sonora Digital Corp · ABE Music Inc

**Arquitectura de gobierno:** VDD → EDD → PDD → ODD → SDD → BDD → TDD
**Pipeline de entrega:** Spec → Design → Tasks → Apply → Verify → Archive

---

## MILESTONE 0: FUNDACIÓN DEL VPS

### Fase 0.1: Acceso y Seguridad Inicial

#### SDD-001: Generar acceso root
- [ ] VDD: Definir política de acceso (solo key, sin password)
- [ ] EDD: Investigar mejores prácticas de hardening para Ubuntu 26.04
- [ ] PDD: Planear orden de operaciones de seguridad
- [ ] ODD: Generar password desde OVH Manager link
- [ ] SDD: Especificar configuración exacta de SSH
- [ ] BDD: "Cuando intento SSH con key, debo acceder sin prompt"
- [ ] TDD: Test: ssh -o PasswordAuthentication=no ubuntu@149.56.46.173 debe funcionar
- [ ] Apply: ssh-keygen -t ed25519 + ssh-copy-id
- [ ] Verify: Verificar que password auth está deshabilitado
- [ ] Archive: Guardar config SSH en sonora-enterprise-os/infra/

#### SDD-002: Hardening del servidor
- [ ] VDD: Servidor debe sobrevivir en internet público sin supervisión
- [ ] EDD: Investigar configs de UFW, fail2ban, automatic-updates
- [ ] PDD: Planear firewall rules
- [ ] ODD: Lista de puertos permitidos (22, 80, 443, + interno)
- [ ] SDD: Especificar reglas UFW + fail2ban jail.conf
- [ ] BDD: "Cuando alguien hace 5 SSH fallidos, debe ser baneado 10min"
- [ ] TDD: Test: ufw status verbose debe mostrar reglas exactas
- [ ] Apply: ufw default deny incoming + allow 22,80,443 + fail2ban
- [ ] Verify: Intentar SSH inválido 5 veces, verificar ban
- [ ] Archive: Documentar reglas en infra/firewall-config.md

#### SDD-003: Hostname y resolución
- [ ] VDD: Identidad clara del servidor
- [ ] EDD: Decidir naming convention para hosts SDC
- [ ] PDD: Planear asignación hostname
- [ ] ODD: hostnamectl set-hostname sdc-prod
- [ ] SDD: Especificar /etc/hosts con IPv4 + IPv6
- [ ] BDD: "hostname debe responder a sdc-prod"
- [ ] TDD: Test: hostname == sdc-prod
- [ ] Apply: hostnamectl + /etc/hosts
- [ ] Verify: ping sdc-prod debe resolver
- [ ] Archive: Documentar en infra/hosts-config.md

#### SDD-004: Usuario y sudo
- [ ] VDD: Acceso jerárquico (root solo para emergencias)
- [ ] EDD: Investigar sudoers policy
- [ ] PDD: Definir usuarios del sistema
- [ ] ODD: Crear usuario deploy, operador, admin
- [ ] SDD: Especificar grupos y permisos sudo
- [ ] BDD: "deploy debe poder ejecutar docker sin sudo"
- [ ] TDD: Test: groups deploy debe incluir docker
- [ ] Apply: useradd + usermod + sudoers.d
- [ ] Verify: Verificar cada usuario y sus permisos
- [ ] Archive: Documentar en infra/users.md

#### SDD-005: Timezone y locale
- [ ] VDD: Tiempo unificado para logs
- [ ] EDD: Decidir timezone (MST/UTC)
- [ ] PDD: --
- [ ] ODD: timedatectl set-timezone America/Hermosillo
- [ ] SDD: Especificar locale en todos los containers
- [ ] BDD: "date debe mostrar timezone correcto"
- [ ] TDD: Test: timedatectl | grep correcto
- [ ] Apply: timedatectl + locale-gen
- [ ] Verify: date y logs en timezone correcto
- [ ] Archive: --

#### SDD-006: Swap y recursos
- [ ] VDD: Sistema no debe morir por falta de RAM
- [ ] EDD: Medir RAM VPS, calcular swap
- [ ] PDD: Planear asignación de swap
- [ ] ODD: fallocate -l 2G /swapfile + chmod 600 + mkswap + swapon
- [ ] SDD: Especificar swappiness (10 para servidor)
- [ ] BDD: "swap debe estar activo con 2GB"
- [ ] TDD: Test: swapon --show
- [ ] Apply: Configurar swap + fstab
- [ ] Verify: free -m muestra swap activo
- [ ] Archive: --

---

### Fase 0.2: Docker Base

#### SDD-007: Instalar Docker Engine
- [ ] VDD: Todo corre en containers, portátil y reproducible
- [ ] EDD: Investigar compatibilidad Ubuntu 26.04 + Docker
- [ ] PDD: Planear versión exacta de Docker
- [ ] ODD: Instalar docker.io + docker-compose-plugin
- [ ] SDD: Especificar docker daemon.json (logs, storage, network)
- [ ] BDD: "docker ps debe funcionar sin sudo"
- [ ] TDD: Test: docker run hello-world
- [ ] Apply: apt install + usermod + daemon.json
- [ ] Verify: docker info + docker ps
- [ ] Archive: Guardar daemon.json en infra/

#### SDD-008: Docker network
- [ ] VDD: Red aislada para servicios internos
- [ ] EDD: Investigar network driver overlay/bridge
- [ ] PDD: --
- [ ] ODD: docker network create sdc-network --driver bridge
- [ ] SDD: Especificar subred 10.10.0.0/16
- [ ] BDD: "containers deben comunicarse por nombre"
- [ ] TDD: Test: ping neo4j desde otro container
- [ ] Apply: docker network create
- [ ] Verify: docker network inspect sdc-network
- [ ] Archive: --

#### SDD-009: Docker Compose base
- [ ] VDD: Infraestructura como código
- [ ] EDD: Investigar docker-compose.yml estructura
- [ ] PDD: Planear orden de servicios
- [ ] ODD: Crear docker-compose.yml con volumes, networks, envs
- [ ] SDD: Especificar healthchecks de cada servicio
- [ ] BDD: "docker compose up -d debe levantar todos los servicios"
- [ ] TDD: Test: docker compose ps debe mostrar healthy
- [ ] Apply: docker compose up -d
- [ ] Verify: curl healthcheck endpoints
- [ ] Archive: Guardar compose en infra/docker-compose.yml

#### SDD-010: Volúmenes persistentes
- [ ] VDD: Datos sobreviven a containers muertos
- [ ] EDD: Investigar Docker volumes vs bind mounts
- [ ] PDD: Mapear qué datos son persistentes
- [ ] ODD: docker volume create neo4j_data, qdrant_data, pg_data, redis_data
- [ ] SDD: Especificar backup strategy para cada volume
- [ ] BDD: "docker rm + docker compose up debe preservar datos"
- [ ] TDD: Test: docker volume ls
- [ ] Apply: docker volume create
- [ ] Verify: Verificar monturas en /var/lib/docker/volumes/
- [ ] Archive: Documentar volumes en infra/

---

### Fase 0.3: nginx + SSL

#### SDD-011: Instalar nginx
- [ ] VDD: Punto único de entrada para todos los servicios
- [ ] EDD: Investigar nginx config para reverse proxy
- [ ] PDD: Planear estructura de server blocks
- [ ] ODD: apt install nginx + crear /etc/nginx/sites-available/
- [ ] SDD: Especificar nginx.conf global (limites, gzip, timeout)
- [ ] BDD: "curl localhost:80 debe responder 200"
- [ ] TDD: Test: nginx -t
- [ ] Apply: Instalar + configurar
- [ ] Verify: systemctl status nginx
- [ ] Archive: Guardar nginx.conf en infra/

#### SDD-012: SSL con Let's Encrypt
- [ ] VDD: Sin HTTPS no hay negocio real
- [ ] EDD: Investigar certbot + nginx plugin
- [ ] PDD: --
- [ ] ODD: certbot --nginx -d sonoradigitalcorp.com -d www.sonoradigitalcorp.com
- [ ] SDD: Especificar auto-renovación (certbot renew --dry-run)
- [ ] BDD: "https://sonoradigitalcorp.com debe responder 200 sin warnings"
- [ ] TDD: Test: curl -I https://sonoradigitalcorp.com
- [ ] Apply: certbot + cron para renovación
- [ ] Verify: SSL Labs test (o ssllabs.com)
- [ ] Archive: Guardar certbot config en infra/

#### SDD-013: Proxy services
- [ ] VDD: Cada servicio en su subdominio
- [ ] EDD: --
- [ ] PDD: --
- [ ] ODD: Configurar nginx server blocks para cada subdominio
- [ ] SDD: Especificar location blocks con proxy_pass
- [ ] BDD: "abe.sonoradigitalcorp.com debe redirigir al dashboard"
- [ ] TDD: Test: curl a cada subdominio
- [ ] Apply: Crear server blocks + habilitar
- [ ] Verify: Verificar cada ruta
- [ ] Archive: Guardar server blocks en infra/

---

### Fase 0.4: Monitoreo Base

#### SDD-014: Healthchecks
- [ ] VDD: Saber si el sistema está vivo antes que el cliente
- [ ] EDD: Investigar healthcheck solutions (simple bash)
- [ ] PDD: --
- [ ] ODD: Script que checkea cada servicio cada 5min
- [ ] SDD: Especificar endpoints y thresholds
- [ ] BDD: "Si Neo4j se cae, debe llegar alerta a Telegram en <1min"
- [ ] TDD: Test: matar container y verificar alerta
- [ ] Apply: Crear /usr/local/bin/sdc-healthcheck.sh
- [ ] Verify: Probar con container detenido
- [ ] Archive: Guardar script en infra/monitoring/

#### SDD-015: Log rotation
- [ ] VDD: Logs no deben llenar disco
- [ ] EDD: Investigar logrotate defaults
- [ ] PDD: --
- [ ] ODD: Configurar logrotate para docker, nginx, servicios
- [ ] SDD: Especificar retention (30 días)
- [ ] BDD: "Logs de más de 30 días deben comprimirse"
- [ ] TDD: Test: logrotate --dry-run /etc/logrotate.conf
- [ ] Apply: Configurar logrotate
- [ ] Verify: Verificar rotación
- [ ] Archive: --

#### SDD-016: Backup script
- [ ] VDD: Una sola rm -rf y perdemos todo
- [ ] EDD: Investigar opciones de backup
- [ ] PDD: Planear backup semanal + diario
- [ ] ODD: Script que exporta Neo4j, Qdrant, PostgreSQL + guarda en /backups/
- [ ] SDD: Especificar formato y retención
- [ ] BDD: "Los backups deben poder restaurarse en un VPS nuevo"
- [ ] TDD: Test: restaurar backup en container fresco
- [ ] Apply: Crear script + cron
- [ ] Verify: Verificar integridad del backup
- [ ] Archive: Guardar en infra/backup/

---

## MILESTONE 1: INFRAESTRUCTURA CORE

### Fase 1.1: Neo4j

#### SDD-101: Neo4j container
- [ ] VDD: Corazón del CRM, artistas, relaciones
- [ ] EDD: Investigar imagen oficial + config para 1GB RAM
- [ ] PDD: --
- [ ] ODD: Docker compose con Neo4j 5.x + volume + envs
- [ ] SDD: Especificar NEO4J_AUTH, heap, pagecache
- [ ] BDD: "Neo4j debe responder en bolt://localhost:7687"
- [ ] TDD: Test: Cypher query CREATE + MATCH
- [ ] Apply: docker compose up -d neo4j
- [ ] Verify: curl http://localhost:7474
- [ ] Archive: Guardar config en infra/neo4j/

#### SDD-102: Migrar datos Neo4j
- [ ] VDD: Los artistas de ABE no pueden perderse
- [ ] EDD: Investigar dump/load de Neo4j
- [ ] PDD: Planear ventana de migración
- [ ] ODD: neo4j-admin dump --database=neo4j + scp a OVH + load
- [ ] SDD: Especificar procedimiento exacto import/export
- [ ] BDD: "Los 3 artistas de ABE deben existir después de migrar"
- [ ] TDD: Test: MATCH (a:Artist) RETURN count(a) == 3
- [ ] Apply: Exportar en local, importar en OVH
- [ ] Verify: Consultar datos migrados
- [ ] Archive: Documentar procedimiento en infra/neo4j/migration.md

#### SDD-103: Neo4j backup automático
- [ ] VDD: No repetir migración manual
- [ ] EDD: --
- [ ] PDD: --
- [ ] ODD: Cron job semanal con neo4j-admin dump
- [ ] SDD: Especificar retention
- [ ] BDD: "Debe existir backup de Neo4j con menos de 7 días"
- [ ] TDD: Test: ls -la /backups/neo4j/
- [ ] Apply: Configurar cron
- [ ] Verify: Inspeccionar backup
- [ ] Archive: Guardar script en infra/neo4j/backup.sh

---

### Fase 1.2: Qdrant

#### SDD-104: Qdrant container
- [ ] VDD: Memoria vectorial del ecosistema
- [ ] EDD: Investigar config Qdrant
- [ ] PDD: --
- [ ] ODD: Docker compose con Qdrant + volume
- [ ] SDD: Especificar API key, limites, performance
- [ ] BDD: "Qdrant debe responder en :6333"
- [ ] TDD: Test: curl http://localhost:6333/collections
- [ ] Apply: docker compose up -d qdrant
- [ ] Verify: Verificar health
- [ ] Archive: Guardar en infra/qdrant/

#### SDD-105: Migrar vectores
- [ ] VDD: Memoria de sesiones y conocimiento
- [ ] EDD: Investigar Qdrant snapshot/restore
- [ ] PDD: --
- [ ] ODD: Qdrant snapshot en local → scp → restore en OVH
- [ ] SDD: Especificar procedimiento
- [ ] BDD: "Puntos vectoriales deben migrarse completos"
- [ ] TDD: Test: collections count post-migración
- [ ] Apply: Snapshot + transfer + restore
- [ ] Verify: Verificar colecciones migradas
- [ ] Archive: Documentar en infra/qdrant/migration.md

---

### Fase 1.3: PostgreSQL

#### SDD-106: PostgreSQL container
- [ ] VDD: Datos relacionales (eventos, métricas, usuarios)
- [ ] EDD: Investigar imagen + tuning
- [ ] PDD: --
- [ ] ODD: Docker compose con PostgreSQL 15 + volume
- [ ] SDD: Especificar max_connections, shared_buffers
- [ ] BDD: "PostgreSQL debe responder en :5432"
- [ ] TDD: Test: psql -c 'SELECT 1'
- [ ] Apply: docker compose up -d postgres
- [ ] Verify: Verificar conexión
- [ ] Archive: Guardar en infra/postgres/

#### SDD-107: Migrar datos PostgreSQL
- [ ] VDD: Eventos, sesiones, configuraciones
- [ ] EDD: Investigar pg_dump/pg_restore
- [ ] PDD: --
- [ ] ODD: pg_dump + scp + pg_restore
- [ ] SDD: Especificar procedimiento exacto
- [ ] BDD: "Tablas y datos deben coincidir post-migración"
- [ ] TDD: Test: row counts pre y post migración
- [ ] Apply: Exportar/importar
- [ ] Verify: Verificar integridad
- [ ] Archive: Documentar en infra/postgres/migration.md

---

### Fase 1.4: Redis

#### SDD-108: Redis container
- [ ] VDD: Cache rápido, sesiones, rate limiting
- [ ] EDD: Investigar config Redis
- [ ] PDD: --
- [ ] ODD: Docker compose con Redis 7 + volume + password
- [ ] SDD: Especificar maxmemory, eviction policy
- [ ] BDD: "Redis debe responder en :6379"
- [ ] TDD: Test: redis-cli PING
- [ ] Apply: docker compose up -d redis
- [ ] Verify: Verificar conexión
- [ ] Archive: Guardar en infra/redis/

---

## MILESTONE 2: SERVIDORES DE APLICACIÓN

### Fase 2.1: Hermes API

#### SDD-201: Hermes container
- [ ] VDD: Gateway multi-canal (Telegram, WhatsApp, etc.)
- [ ] EDD: Revisar Dockerfile existente de Hermes
- [ ] PDD: --
- [ ] ODD: Construir imagen + docker-compose
- [ ] SDD: Especificar envs, ports, depends_on
- [ ] BDD: "Hermes debe responder GET /health con 200"
- [ ] TDD: Test: curl http://hermes:8000/health
- [ ] Apply: docker compose up -d hermes
- [ ] Verify: Verificar health + logs
- [ ] Archive: Guardar en apps/hermes/

#### SDD-202: Hermes systemd service
- [ ] VDD: Hermes no debe morir si Docker reinicia
- [ ] EDD: --
- [ ] PDD: --
- [ ] ODD: Crear /etc/systemd/system/hermes-gateway.service
- [ ] SDD: Especificar Restart=always, After=docker
- [ ] BDD: "Si Hermes muere, debe reiniciar automáticamente"
- [ ] TDD: Test: kill proceso + systemctl status
- [ ] Apply: Crear service + enable
- [ ] Verify: Verificar restart automático
- [ ] Archive: Guardar service file

---

### Fase 2.2: JARVIS Web UI

#### SDD-203: JARVIS Web UI container
- [ ] VDD: Interfaz del ecosistema
- [ ] EDD: Revisar Dockerfile de apps/webui/
- [ ] PDD: --
- [ ] ODD: Construir imagen + docker-compose
- [ ] SDD: Especificar envs + healthcheck
- [ ] BDD: "JARVIS Web UI debe servir HTML en /"
- [ ] TDD: Test: curl http://webui:5174/ | grep html
- [ ] Apply: docker compose up -d webui
- [ ] Verify: Verificar que sirve páginas
- [ ] Archive: Guardar en apps/webui/

#### SDD-204: Migrar ABE router
- [ ] VDD: ABE dashboard debe funcionar en el nuevo servidor
- [ ] EDD: Verificar que los imports funcionan
- [ ] PDD: --
- [ ] ODD: Copiar apps/webui/ con abe_router.py
- [ ] SDD: Especificar dependencias
- [ ] BDD: "/api/abe/dashboard/ceo debe devolver JSON con datos"
- [ ] TDD: Test: curl /api/abe/dashboard/ceo
- [ ] Apply: Migrar código
- [ ] Verify: Verificar endpoints
- [ ] Archive: --

#### SDD-205: ABE Command Center
- [ ] VDD: Abraham debe ver su dashboard en dominio real
- [ ] EDD: --
- [ ] PDD: --
- [ ] ODD: Copiar static/abe-command-center.html
- [ ] SDD: Especificar URL base
- [ ] BDD: "/static/abe-command-center.html debe cargar completo"
- [ ] TDD: Test: verificar que fetch al API funciona
- [ ] Apply: Migrar HTML
- [ ] Verify: Abrir en browser
- [ ] Archive: --

---

### Fase 2.3: OpenClaw Gateway

#### SDD-206: OpenClaw gateway
- [ ] VDD: Skills engine, 42+ skills habilitadas
- [ ] EDD: Investigar cómo corre OpenClaw en modo server
- [ ] PDD: --
- [ ] ODD: openclaw gateway start + systemd service
- [ ] SDD: Especificar port, token, skills permitidas
- [ ] BDD: "OpenClaw debe responder en :18789"
- [ ] TDD: Test: curl http://localhost:18789/health
- [ ] Apply: Configurar gateway en OVH
- [ ] Verify: Verificar skills disponibles
- [ ] Archive: Guardar config en .openclaw/openclaw.json

#### SDD-207: Skills migration
- [ ] VDD: Las skills que funcionan local deben funcionar en cloud
- [ ] EDD: Identificar skills que dependen de hardware local
- [ ] PDD: --
- [ ] ODD: Copiar .openclaw/workspace/skills/ a OVH
- [ ] SDD: Especificar qué skills migrar y cuáles no
- [ ] BDD: "Skills sin dependencia local deben responder"
- [ ] TDD: Test: Llamar skill via MCP
- [ ] Apply: Migrar skills
- [ ] Verify: Verificar skills críticas
- [ ] Archive: Documentar skills compatibles

---

## MILESTONE 3: ABE MUSIC — PRODUCTO

### Fase 3.1: Telegram Bot Producción

#### SDD-301: Systemd service para Telegram bot
- [ ] VDD: Bot 24/7 que Abraham pueda usar cuando quiera
- [ ] EDD: --
- [ ] PDD: --
- [ ] ODD: Crear /etc/systemd/system/abe-telegram-bot.service
- [ ] SDD: Especificar WorkingDirectory, Environment, Restart
- [ ] BDD: "abe-telegram-bot debe responder /kpi a cualquier hora"
- [ ] TDD: Test: curl API de Telegram con comando
- [ ] Apply: Crear service + habilitar
- [ ] Verify: Enviar /start al bot, verificar respuesta
- [ ] Archive: Guardar service file en infra/

#### SDD-302: Bot commands expansion
- [ ] VDD: Abraham necesita más que solo KPIs
- [ ] EDD: Encuestar qué necesita Abraham
- [ ] PDD: --
- [ ] ODD: Agregar comandos al bot:
  - /add-artist [nombre] [genero] [pais]
  - /add-release [artista] [titulo] [tipo]
  - /report [diario|semanal|mensual]
  - /artist [nombre] — detalle del artista
  - /revenue — breakdown de revenue
- [ ] SDD: Especificar estructura de cada comando
- [ ] BDD: "Cuando envío /add-artist, debe crear artista en CRM"
- [ ] TDD: Test: /add-artist → GET /api/abe/artists → verificar
- [ ] Apply: Modificar abe-telegram-bot.py
- [ ] Verify: Probar cada comando
- [ ] Archive: Documentar comandos en products/abe-music/bot-commands.md

#### SDD-303: Reportes automáticos
- [ ] VDD: Abraham recibe KPIs sin pedirlos
- [ ] EDD: --
- [ ] PDD: --
- [ ] ODD: Cron job que envía reporte cada 6h al chat
- [ ] SDD: Especificar formato del reporte
- [ ] BDD: "Cada 6h debe llegar mensaje con KPIs actualizados"
- [ ] TDD: Test: ejecutar script manualmente, verificar mensaje
- [ ] Apply: Configurar cron/systemd timer
- [ ] Verify: Esperar primer reporte
- [ ] Archive: --

#### SDD-304: ABE Daemon ligero
- [ ] VDD: Daemon original falla por RAM, hay que optimizarlo
- [ ] EDD: Analizar qué funciones del daemon son críticas
- [ ] PDD: --
- [ ] ODD: Reescribir abe-daemon.py como script bash minimalista
  - Solo healthchecks + alerts
  - Sin git commit automático
  - Sin tests automáticos
  - Sin push_report (el bot ya hace eso)
- [ ] SDD: Especificar cada función mínima
- [ ] BDD: "Daemon debe consumir <20MB RAM"
- [ ] TDD: Test: ps -o rss -p $(pidof daemon)
- [ ] Apply: Reemplazar script + systemd
- [ ] Verify: Verificar consumo de RAM
- [ ] Archive: Guardar en scripts/abe-daemon-lite.sh

---

### Fase 3.2: ABE Experience OS

#### SDD-305: Dashboard dominio real
- [ ] VDD: abe.sonoradigitalcorp.com debe funcionar
- [ ] EDD: --
- [ ] PDD: --
- [ ] ODD: Configurar subdominio en nginx
- [ ] SDD: Especificar proxy_pass a webui + SSL
- [ ] BDD: "https://abe.sonoradigitalcorp.com debe cargar dashboard"
- [ ] TDD: Test: curl https://abe.sonoradigitalcorp.com
- [ ] Apply: nginx config + certbot
- [ ] Verify: Abrir en navegador
- [ ] Archive: Guardar config en infra/nginx/abe.conf

#### SDD-306: Branded landing Abraham
- [ ] VDD: Abraham necesita una página que pueda compartir
- [ ] EDD: Revisar products/abe-music/index.html
- [ ] PDD: --
- [ ] ODD: Personalizar con logo ABE, colores, copy
- [ ] SDD: Especificar secciones (hero, artistas, servicios, contacto)
- [ ] BDD: "La landing debe cargar en <3s"
- [ ] TDD: Test: lighthouse report
- [ ] Apply: Modificar HTML/CSS
- [ ] Verify: Verificar en mobile + desktop
- [ ] Archive: Guardar en products/abe-music/landing/

#### SDD-307: Artist detail pages
- [ ] VDD: Cada artista necesita su página individual
- [ ] EDD: --
- [ ] PDD: --
- [ ] ODD: Generar páginas dinámicas desde API
- [ ] SDD: Especificar template
- [ ] BDD: "/artist/hector-rubio debe mostrar stats en vivo"
- [ ] TDD: Test: verificar HTML generado
- [ ] Apply: Crear template + endpoint
- [ ] Verify: Verificar render
- [ ] Archive: --

#### SDD-308: Sistema de contratación
- [ ] VDD: Abraham debe poder firmar artistas digitalmente
- [ ] EDD: Investigar opciones (DocuSign API, PDF)
- [ ] PDD: --
- [ ] ODD: Template de contrato + generación PDF
- [ ] SDD: Especificar cláusulas mínimas
- [ ] BDD: "Generar contrato debe producir PDF descargable"
- [ ] TDD: Test: endpoint genera PDF
- [ ] Apply: Crear generador de contratos
- [ ] Verify: Descargar y verificar PDF
- [ ] Archive: Guardar templates en products/abe-music/contracts/

#### SDD-309: Distribución digital
- [ ] VDD: ABE necesita distribuir música a plataformas
- [ ] EDD: Investigar distribuidoras (Tunecore, DistroKid, etc.)
- [ ] PDD: Planear integración
- [ ] ODD: Módulo de distribución con tracking de entregas
- [ ] SDD: Especificar pipeline de distribución
- [ ] BDD: "Crear release → debe generar assets para distribución"
- [ ] TDD: Test: release pipeline
- [ ] Apply: Implementar
- [ ] Verify: Probar release flow
- [ ] Archive: --

#### SDD-310: Royalty tracking UI
- [ ] VDD: Abraham debe ver cuánto debe pagar a cada artista
- [ ] EDD: --
- [ ] PDD: --
- [ ] ODD: UI de royalties con split: 70/20/10
- [ ] SDD: Especificar breakdown
- [ ] BDD: "/abe/royalties debe mostrar cálculo exacto"
- [ ] TDD: Test: montos cuadran
- [ ] Apply: Implementar vista
- [ ] Verify: Verificar cálculos
- [ ] Archive: --

---

## MILESTONE 4: DOMINIO Y DNS

### Fase 4.1: sonoradigitalcorp.com

#### SDD-401: DNS A record
- [ ] VDD: El dominio debe apuntar al servidor correcto
- [ ] EDD: Verificar panel de Hostinger DNS
- [ ] PDD: --
- [ ] ODD: Cambiar A record → 149.56.46.173
- [ ] SDD: Especificar TTL (300s para migración)
- [ ] BDD: "sonoradigitalcorp.com debe resolver a 149.56.46.173"
- [ ] TDD: Test: dig sonoradigitalcorp.com
- [ ] Apply: Cambiar en Hostinger DNS panel
- [ ] Verify: dig + curl hasta propagar
- [ ] Archive: Documentar DNS config

#### SDD-402: Subdominios
- [ ] VDD: Cada producto su propio subdominio
- [ ] EDD: --
- [ ] PDD: --
- [ ] ODD: Crear CNAME records:
  - abe.sonoradigitalcorp.com
  - azrec.sonoradigitalcorp.com
  - masterclass.sonoradigitalcorp.com
  - api.sonoradigitalcorp.com
  - bot.sonoradigitalcorp.com
- [ ] SDD: Especificar cada subdominio + servicio
- [ ] BDD: "Cada subdominio debe resolver y servir HTTPS"
- [ ] TDD: Test: dig + curl cada subdominio
- [ ] Apply: DNS + nginx + certbot
- [ ] Verify: Verificar cada uno
- [ ] Archive: Documentar en infra/dns-records.md

#### SDD-403: Email
- [ ] VDD: info@sonoradigitalcorp.com para contacto
- [ ] EDD: Investigar opciones (Google Workspace, Zoho, etc.)
- [ ] PDD: --
- [ ] ODD: Configurar MX records + SPF + DKIM
- [ ] SDD: Especificar DNS records de email
- [ ] BDD: "Enviar correo a info@sonoradigitalcorp.com debe llegar"
- [ ] TDD: Test: MX record lookup
- [ ] Apply: Configurar email
- [ ] Verify: Enviar correo de prueba
- [ ] Archive: --

#### SDD-404: GitHub Pages redirect
- [ ] VDD: Las páginas en GitHub Pages deben migrarse al dominio principal
- [ ] EDD: --
- [ ] PDD: --
- [ ] ODD: Redireccionar gh-pages a subdominios SDC
- [ ] SDD: Especificar nginx redirects
- [ ] BDD: "gh-pages debe redirigir 301 a dominio SDC"
- [ ] TDD: Test: curl -I gh-pages URL
- [ ] Apply: Configurar redirects
- [ ] Verify: Verificar redirección
- [ ] Archive: --

---

## MILESTONE 5: MONITOREO Y AUTOMATIZACIÓN

### Fase 5.1: Sistema de Alertas

#### SDD-501: Telegram alert channel
- [ ] VDD: Saber antes que el cliente que algo falló
- [ ] EDD: --
- [ ] PDD: --
- [ ] ODD: Bot envía alerta cuando servicio se cae
- [ ] SDD: Especificar niveles (critical, warning, info)
- [ ] BDD: "Alerta crítica debe llegar en <1 minuto"
- [ ] TDD: Test: matar container, medir tiempo de alerta
- [ ] Apply: Script + systemd timer
- [ ] Verify: Probar cada nivel
- [ ] Archive: --

#### SDD-502: Uptime monitoring externo
- [ ] VDD: Monitoreo desde fuera del VPS
- [ ] EDD: Investigar opciones (uptimerobot, betteruptime, etc.)
- [ ] PDD: --
- [ ] ODD: Configurar monitor externo
- [ ] SDD: Especificar endpoints monitoreados
- [ ] BDD: "Si el VPS se cae, debe llegar alerta externa"
- [ ] TDD: Test: simular caída
- [ ] Apply: Configurar
- [ ] Verify: Verificar alerta
- [ ] Archive: --

---

### Fase 5.2: n8n Workflows

#### SDD-503: n8n deployment
- [ ] VDD: Automatización de procesos de negocio
- [ ] EDD: Revisar infra/ existente
- [ ] PDD: --
- [ ] ODD: Docker compose + n8n container
- [ ] SDD: Especificar credenciales, workflows seed
- [ ] BDD: "n8n debe responder en :5678"
- [ ] TDD: Test: curl n8n health
- [ ] Apply: docker compose up
- [ ] Verify: Acceder a UI
- [ ] Archive: --

#### SDD-504: Workflows ABE
- [ ] VDD: ABE debe automatizarse (facturación, reportes)
- [ ] EDD: --
- [ ] PDD: --
- [ ] ODD: Crear workflows:
  - Nuevo artista → crear en CRM + enviar bienvenida
  - Nueva release → generar assets + notificar
  - Royalty mensual → calcular + reportar
  - Healthcheck → verificar + alertar
- [ ] SDD: Especificar trigger + acciones
- [ ] BDD: "Nuevo artista en API → debe crear nodo en Neo4j"
- [ ] TDD: Test: POST artista → verificar Neo4j
- [ ] Apply: Configurar workflows
- [ ] Verify: Probar cada workflow
- [ ] Archive: Exportar workflows a infra/n8n/

---

## MILESTONE 6: SEGURIDAD Y CUMPLIMIENTO

### Fase 6.1: Hardening

#### SDD-601: Rotar API keys
- [ ] VDD: 29 keys expuestas en el repo
- [ ] EDD: Identificar todas las keys
- [ ] PDD: Planear rotación
- [ ] ODD: Regenerar cada key, actualizar .env
- [ ] SDD: Especificar .env template + vault
- [ ] BDD: "Ninguna key debe estar hardcodeada en código"
- [ ] TDD: Test: grep -r "sk-" o "api_key" en código
- [ ] Apply: Rotar + mover a .env
- [ ] Verify: Verificar que servicios funcionan con nuevas keys
- [ ] Archive: Documentar en SECURITY.md

#### SDD-602: Secrets management
- [ ] VDD: No más keys en git
- [ ] EDD: Investigar solutions (sops, vault, pass)
- [ ] PDD: --
- [ ] ODD: Configurar encrypted .env con sops
- [ ] SDD: Especificar workflow de secrets
- [ ] BDD: "Los secrets deben estar cifrados en repo"
- [ ] TDD: Test: git grep key → vacío
- [ ] Apply: sops encrypt .env
- [ ] Verify: Desencriptar y verificar
- [ ] Archive: Documentar en SECURITY.md

#### SDD-603: Audit logging
- [ ] VDD: Saber quién hizo qué y cuándo
- [ ] EDD: --
- [ ] PDD: --
- [ ] ODD: Audit trail en Neo4j o PostgreSQL
- [ ] SDD: Especificar eventos auditables
- [ ] BDD: "Cada acción crítica debe tener log de auditoría"
- [ ] TDD: Test: realizar acción, verificar audit log
- [ ] Apply: Implementar middleware de auditoría
- [ ] Verify: --
- [ ] Archive: --

---

## MILESTONE 7: EXPANSIÓN

### Fase 7.1: AZREC

#### SDD-701: Alejandro Zamora onboarding
- [ ] VDD: Nuevo cliente, mismo stack
- [ ] EDD: Entender necesidades de AZREC
- [ ] PDD: --
- [ ] ODD: Crear subdominio + CRM + bot
- [ ] SDD: Especificar productos AZREC
- [ ] BDD: "AZREC debe tener su propio dashboard"
- [ ] TDD: Test: GET /azrec/dashboard
- [ ] Apply: Configurar
- [ ] Verify: --
- [ ] Archive: Documentar en products/azrec/

---

### Fase 7.2: Masterclass

#### SDD-702: Plataforma de cursos
- [ ] VDD: Cursos online para artistas
- [ ] EDD: Investigar plataformas o construir propia
- [ ] PDD: --
- [ ] ODD: MVP con landing + contenido + payments
- [ ] SDD: Especificar features v1
- [ ] BDD: "Usuario debe poder registrarse a un curso"
- [ ] TDD: Test: registro flow
- [ ] Apply: Implementar
- [ ] Verify: --
- [ ] Archive: --

---

### Fase 7.3: Stripe Payments

#### SDD-703: Stripe integration
- [ ] VDD: Cobrar a clientes
- [ ] EDD: Investigar Stripe API + webhooks
- [ ] PDD: --
- [ ] ODD: Configurar Stripe en JARVIS
- [ ] SDD: Especificar productos, planes, webhooks
- [ ] BDD: "Cliente debe poder pagar y recibir acceso"
- [ ] TDD: Test: Stripe checkout flow
- [ ] Apply: Integrar
- [ ] Verify: Probar pago real ($1)
- [ ] Archive: --

---

## RESUMEN DE FASES Y PRIORIDAD

| Prioridad | Fase | Tiempo estimado | Depende de |
|-----------|------|----------------|------------|
| 🔴 Crítica | F0.1: Acceso y seguridad | 30min | N/A |
| 🔴 Crítica | F0.2: Docker base | 30min | F0.1 |
| 🔴 Crítica | F0.3: nginx + SSL | 1h | F0.2 |
| 🔴 Crítica | F4.1: DNS | 30min | F0.3 |
| 🟡 Alta | F1.1: Neo4j | 1h | F0.2 |
| 🟡 Alta | F1.2: Qdrant | 30min | F0.2 |
| 🟡 Alta | F1.3: PostgreSQL | 30min | F0.2 |
| 🟡 Alta | F1.4: Redis | 15min | F0.2 |
| 🟡 Alta | F2.1: Hermes | 1h | F1.x |
| 🟡 Alta | F2.2: JARVIS Web UI | 1h | F2.1 |
| 🟡 Alta | F3.1: Telegram Bot | 1h | F2.2 |
| 🟡 Alta | F0.4: Monitoreo | 30min | F1.x |
| 🟢 Media | F3.2: ABE Experience OS | 2h | F3.1 |
| 🟢 Media | F5.1: Alertas | 1h | F3.1 |
| 🟢 Media | F5.2: n8n | 1h | F1.x |
| 🔵 Baja | F6.x: Seguridad avanzada | 2h | Todo |
| 🔵 Baja | F7.x: Expansión | 4h | Todo |

---

## MÉTRICAS DE ÉXITO

- **Disponibilidad:** 99.9% uptime (máximo 45min downtime/mes)
- **Latencia API:** <200ms p95
- **Telegram bot:** Responde en <5s
- **Dashboard:** Carga en <3s
- **Backups:** Automáticos diarios, probados semanalmente
- **Seguridad:** 0 keys en código, 0 puertos extra abiertos
- **ABE Music:** Abraham puede abrir el dashboard desde su celular

---

*Este plan se actualiza a medida que se completan fases.*
*Próxima revisión: Al completar Fase 0 completa.*
