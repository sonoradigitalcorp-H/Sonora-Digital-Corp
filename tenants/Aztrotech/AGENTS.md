# Proyecto AstroTech — Sonora Digital Corp

**Owner**: Luis Daniel Guerrero Enciso — dueño de Sonora Digital Corp
**Cliente**: César Holguín — CEO de Aztrotech (AstroTech)
**Otro cliente**: Abraham Ortega — CEO de ABE Music Group
**Tenant**: `Aztrotech` en `~/Documentos/Sonora Digital Corp/sonora-digital-corp/tenants/Aztrotech/`
**Workspace**: `/home/mystic/Documentos/Sonora Digital Corp`

## Relación comercial
- Luis Daniel Guerrero Enciso es el propietario de Sonora Digital Corp
- César Holguín es CEO de Aztrotech y **cliente** de Luis Daniel
- Abraham Ortega es CEO de ABE Music Group y **cliente** de Luis Daniel
- El bot AstroTech atiende a los clientes de Luis Daniel

## Stack

- **Bot Telegram**: @AztroTechBot (token: 8825008004:AAFHdxypgGK8LZD0yEH9g0hsCdl2pJmDd8g)
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
│   ├── tenants/Aztrotech/   → Tenant AstroTech (bot, config, skills)
│   ├── tenants/abe-music/   → Tenant ABE Music Group
│   ├── scripts/             → Scripts compartidos (evals, sync, etc.)
│   ├── docs/adrs/           → Architecture Decision Records
│   ├── ops/state/           → State (engram, snapshots, media)
│   └── .github/workflows/   → CI/CD
├── Clientes/                → Carpetas de clientes
│   ├── Aztrotech/           → Archivos del proyecto AstroTech
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

## Servicios que ofrece AstroTech (para el bot)

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

- El bot NUNCA revela SDC. Habla como "AstroTech AI"
- Todo cambio al tenant se sincroniza al VPS con `deploy`
- Las ADRs del cliente van en `docs/adrs/`
- **Modo operativo**: build (no plan). Se permiten cambios de archivos, ejecución de comandos y uso de herramientas.
- **Owner del sistema**: Luis Daniel Guerrero Enciso. César Holguín es cliente (CEO de Aztrotech). Abraham Ortega es cliente (CEO de ABE Music Group).

## Canal de Telegram (AstroTech)

- **Canal**: por crear (script: `scripts/create_channel.py`)
- **Bot admin**: @AztroTechBot
- **Estrategia**: contenido rotativo no-robótico (educativo, casos de éxito, encuestas, reflexiones, venta suave)
- **Automatización**: `scripts/channel_automation.py` — posts programados en horarios humanos (9am, 1pm, 4pm, 7pm)
- **Estrategia completa**: `scripts/channel_strategy.md`
- **Regla clave**: nunca revelar precios, nunca sonar a robot, educar antes de vender
