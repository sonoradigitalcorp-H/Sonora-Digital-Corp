# Proyecto Aztrotech — Sonora Digital Corp

**Owner**: Luis Daniel Guerrero Enciso — dueño de Sonora Digital Corp
**Cliente**: César Holguín — CEO de Aztrotech
**Otro cliente**: Abraham Ortega — CEO de ABE Music Group
**Tenant**: `Aztrotech` en `~/Documentos/Sonora Digital Corp/sonora-digital-corp/tenants/Aztrotech/`
**Workspace**: `/home/mystic/Documentos/Sonora Digital Corp`

## Relación comercial
- Luis Daniel Guerrero Enciso es el propietario de Sonora Digital Corp
- César Holguín es CEO de Aztrotech y **cliente** de Luis Daniel
- Abraham Ortega es CEO de ABE Music Group y **cliente** de Luis Daniel
- El bot Aztrotech atiende a los clientes de César

## Stack

- **Bot Telegram (conversación)**: @AztrotechBot (token: ${AZTROTECH_BOT_TOKEN})
- **Bot Telegram (notificaciones)**: @MysticUnity_bot (token: ${NOTIF_BOT_TOKEN})
- **Chat ID César**: 5738935134
- **WhatsApp owner (Luis Daniel)**: 6623538272 (E.164: 5216623538272)
- **WhatsApp César (cliente)**: 5216621072254
- **Gateway**: OpenClaw (:18789) vía MCP
- **VPS**: sdc-prod (149.56.46.173) — SSH alias `ovh` (actualmente caído)
- **Gitea**: http://149.56.46.173:3080 (VPS muerto, repo en GitHub: sonoradigitalcorp-H/Sonora-Digital-Corp)

## Estructura del workspace

```
/home/mystic/Documentos/Sonora Digital Corp/
├── sonora-digital-corp/     → Repo principal (git)
│   ├── tenants/Aztrotech/   → Tenant Aztrotech (bot, config, skills)
│   ├── tenants/abe-music/   → Tenant ABE Music Group
│   ├── scripts/             → Scripts compartidos (evals, sync, etc.)
│   ├── docs/adrs/           → Architecture Decision Records
│   ├── ops/state/           → State (engram, snapshots, media)
│   └── .github/workflows/   → CI/CD
├── Clientes/                → Carpetas de clientes
│   ├── Aztrotech/           → Archivos del proyecto Aztrotech
│   ├── ABE Music Group/     → Archivos del proyecto ABE Music
│   ├── Sonora Digital Corp/ → Docs comerciales de SDC
│   ├── Conrado/
│   ├── Fourgea México/
│   ├── Milenius Construcasa/
│   └── Solutech Intercomm/
├── Audiovisuales/           → Assets audiovisuales por cliente
├── Prototipos/              → Prototipos (vacíos actualmente)
├── Finanzas/                → Facturas, nóminas, SAT
└── Referencia/              → Documentación de referencia
```

## Servicios que ofrece Aztrotech (para el bot)

1. **Empleado Digital** — Agente IA 24/7 en WhatsApp/Instagram/Facebook
2. **Sistema de Ventas Autónomo** — CRM + agentes + scoring
3. **Desarrollo de Software a la Medida** — ERPs, apps, APIs
4. **Empresa 90 Días** — Mentoría intensiva con César
5. **Socio Estratégico** — Relación de largo plazo

## Comandos rápidos

```bash
make deploy    → rsync tenant al VPS
make bot-logs  → journalctl -u sdc-aztrotech-telegram
make vps-health → docker ps + systemd + disk
```

## Reglas

- El bot NUNCA revela SDC. Habla como "Aztrotech AI"
- Todo cambio al tenant se sincroniza al VPS con `deploy`
- Las ADRs del cliente van en `docs/adrs/`
- **Modo operativo**: build (no plan). Se permiten cambios de archivos, ejecución de comandos y uso de herramientas.
- **Owner del sistema**: Luis Daniel Guerrero Enciso. César Holguín es cliente (CEO de Aztrotech). Abraham Ortega es cliente (CEO de ABE Music Group).

## Canal de Telegram (Aztrotech)

- **Canal**: por crear (script: `scripts/create_channel.py` — requiere api_id/api_hash de César en my.telegram.org)
- **Bot admin**: @AztrotechBot
- **Estrategia**: contenido rotativo no-robótico (educativo, casos de éxito, encuestas, reflexiones, venta suave)
- **Automatización**: `scripts/channel_automation.py` — posts programados en horarios humanos (9am, 1pm, 4pm, 7pm)
- **Estrategia completa**: `scripts/channel_strategy.md`
- **Regla clave**: nunca revelar precios, nunca sonar a robot, educar antes de vender

## Estado del sistema (2026-08-02)

### Servicios 24/7 activos (systemd)
```
sdc-aztrotech-bot.service      → Bot conversación César (RAG-first) :telegram
sdc-aztrotech-notif.service    → Bot notificaciones (@MysticUnity_bot) :telegram
sdc-aztrotech-tts.service      → TTS DaliaNeural (:8765)
sdc-aztrotech-voice.service    → Asistente de voz (:8770) + Calendar + Email
sdc-aztrotech-dashboard.service → Dashboard monitoreo (:9090)
sdc-n8n-bridge.service         → Webhook bridge bot ↔ n8n (:8767)
```

### Infraestructura local
- **Postgres**: 7 tablas (conversations, messages, leads, daily_metrics, emerge_promotions, user_identities, session_cache)
- **Qdrant**: 16 puntos RAG (384-dim Cosine, collection sdc_knowledge)
- **Redis**: cache de sesiones (TTL 24h, key `bot:ctx:<user_id>`)
- **n8n**: UP (:5678), bridge integrado (:8767)
- **Hermes**: UP (:8643, 19 skills)
- **Engram**: 39 memorias unificadas

### MCPs conectados
- **Engram memory**: 39 memorias (SQLite)
- **User identities**: 3 usuarios reconocidos (Postgres)
- **Hermes**: :8643 (skills)
- **OpenClaw**: OFFLINE (pendiente)

### Métricas
- Lead accuracy: **100%** (24 casos eval)
- Safety issues: 0
- LLM response: ~2.5s (deepseek-chat)
- Costo ~$0.0001/mensaje

### Pendiente (credenciales)
- Google Calendar: Service Account para booking automático
- SMTP: App Password para emails de confirmación
- Telegram canal: api_id/api_hash de César
- WhatsApp: re-auth con QR
- OpenClaw: verificar por qué está offline
