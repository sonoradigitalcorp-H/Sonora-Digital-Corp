# Nathy Conta — Arquitectura

**Cliente**: Nathy (Contadora)
**Stack**: CFDI 4.0, SAT, RESICO, CONTPAQi, nóminas, conciliación
**Teléfono**: +5216622681111 (WhatsApp)
**Laptop**: Windows (Edge Client)

## Estructura SDC

```
packs/nathy-conta/
├── pack.yaml                     — definición del pack
├── agents/                       — 4 agentes contables
├── skills/                       — 7 skills contables
├── use-cases/                    — 6 features Gherkin
└── tests/                        — 10 tests

clients/nathy-conta/
├── opencode.json                 — config opencode del proyecto
├── bot/                          — Telegram bot (existente)
├── web/                          — Landing page (existente)
├── branding/                     — Logo y assets
├── deploy.sh                     — Script de deploy
└── requirements.txt              — Dependencias

config/
├── tenants.json                  — tenant nathy-conta registrado
├── tenants.yaml                  — partner nathy_conta
├── tenant-routing.yaml           — +5216622681111 → nathy_conta
└── registry.json                 — 7 capabilities + 4 agentes + 6 skills

apps/openclaw_edge/
├── nathy_edge_client.py          — Cliente Windows (watchdog + organizador)
├── nathy_config.yaml             — Config de ejemplo
├── nathy_setup.bat               — Instalador Windows
└── nathy_requirements.txt        — Dependencias
```

## Flujo

```
Nathy recibe XMLs por correo
    → descarga a C:\NathyConta\Inbox\
    → Edge Client organiza: Clientes/{RFC}/{Año}/{Mes}/{tipo}/
    → renombra y clasifica automáticamente
    → notifica resultados por WhatsApp o notificación Windows
    → si hay VPS configurado, envía copia para respaldo/procesamiento

Nathy escribe al bot de WhatsApp
    → webhook detecta número +5216622681111
    → routing: nathy_conta (client)
    → responde con agente contable
    → skills activos: CFDI, SAT, RESICO, nóminas, CONTPAQi, conciliación
```

## Acceso

1. Provisionar: `bash scripts/provision-tenant.sh nathy-conta "Nathy Conta"`
2. Usar: `opencode --config clients/nathy-conta/opencode.json`
3. WhatsApp: escribir al bot de SDC desde el 6622681111
4. Windows: ejecutar `nathy_setup.bat` en su laptop
