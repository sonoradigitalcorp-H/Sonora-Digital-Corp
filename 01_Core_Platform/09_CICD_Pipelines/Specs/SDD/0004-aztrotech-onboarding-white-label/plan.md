# Plan 0004: Aztrotech Onboarding Inteligente + White-Label

## Fases

### Fase 1: Core Onboarding Aztrotech (P0) — 1-2 días
**Objetivo**: Lead entra por Telegram → capturado + cita agendada + César notificado < 30s

| Task | Archivo | Descripción | Dependencia |
|------|---------|-------------|-------------|
| T1.1 | `tests/integration/test_aztrotech_onboard.py` | Tests TDD: routing, lead capture, scheduling, notification | — |
| T1.2 | `01_Core_Platform/03_Agentic_Infrastructure/onboarding_engine.py` | Motor determinista: captura lead, valida cita, persiste SQLite, notifica César | T1.1 |
| T1.3 | `01_Core_Platform/03_Agentic_Infrastructure/lead_classifier.py` | LLM + schema JSON: intención → campos obligatorios (nombre, empresa, servicio, fecha, hora) | T1.1 |
| T1.4 | `01_Core_Platform/03_Agentic_Infrastructure/voice_pipeline.py` | Wrapper unificado: STT (faster-whisper) + TTS (edge-tts) + envío Telegram/WhatsApp | T1.1 |
| T1.5 | `02_Client_Projects/Aztrotech/03_Media_Assets/webhooks/multi_tenant_webhook.py` | Extender: soporte voz (media_path), routing completo a onboarding_engine | T1.2, T1.3, T1.4 |
| T1.6 | `02_Client_Projects/Aztrotech/03_Media_Assets/tenant_router.py` | Añadir `route_message(bot, user, msg, media_path)` que devuelve acción ejecutada | T1.5 |
| T1.7 | `01_Core_Platform/03_Agentic_Infrastructure/Databases/Aztrotech_Citas/leads.db` | SQLite schema leads + migración | T1.2 |
| T1.8 | `run_onboarding.py` | Entry point único: webhook server + scheduler recordatorios | T1.5 |

### Fase 2: White-Label Provisioning (P1) — 1 día
**Objetivo**: 1 comando crea tenant operable (bot + landing + webhook)

| Task | Archivo | Descripción | Dependencia |
|------|---------|-------------|-------------|
| T2.1 | `01_Core_Platform/Infrastructure/sonora-digital-corp/scripts/provision_tenant.py` | CLI: crea registry, directorio tenant, config, policies, server.py, index.html | Fase 1 |
| T2.2 | `01_Core_Platform/Infrastructure/sonora-digital-corp/tenants/{tenant}/web/index.html` | Plantilla landing Three.js + branding + botón WhatsApp + widget voz | T2.1 |
| T2.3 | `01_Core_Platform/Infrastructure/sonora-digital-corp/tenants/{tenant}/config.yaml` | Plantilla config por tenant (modelo, voz, canales, rate limits) | T2.1 |
| T2.4 | `01_Core_Platform/Infrastructure/sonora-digital-corp/tenants/{tenant}/policies.yaml` | Plantilla policies (injection, rate limits, masking, sandbox) | T2.1 |
| T2.5 | `tests/integration/test_provision_tenant.py` | Test: provision → bot responde + landing sirve + webhook rutea | T2.1 |

### Fase 3: Multi-Canal + Voz Completa (P1) — 1-2 días
| Task | Archivo | Descripción |
|------|---------|-------------|
| T3.1 | `01_Core_Platform/04_Automations_and_Workflows/02_Voice_Agents/whisper_stt.py` | STT local faster-whisper small int8 (ya existe, validar) |
| T3.2 | `01_Core_Platform/04_Automations_and_Workflows/01_Telegram_Bots/webhook_voice.py` | Handler voice update → STT → onboarding_engine |
| T3.3 | `01_Core_Platform/Infrastructure/sonora-digital-corp/tenants/{tenant}/web/voice_widget.js` | MediaRecorder widget en landing → POST /webhook con audio |
| T3.4 | WhatsApp Business API webhook (wacli bridge) | Cuando tengas Business API aprobado |

### Fase 4: Dashboard César (P2) — 1 día
| Task | Archivo | Descripción |
|------|---------|-------------|
| T4.1 | `01_Core_Platform/10_Client_Interfaces/Telegram_Handlers/cesar_dashboard.py` | Panel: leads día, estado, audios, botones "Llamar", "Reagendar" |

## Orden de Ejecución Inmediato
1. **T1.1** - Tests primero (TDD)
2. **T1.2** - onboarding_engine (corazón determinista)
3. **T1.3** - lead_classifier (LLM con schema)
4. **T1.4** - voice_pipeline (unifica lo que ya existe)
5. **T1.5/T1.6** - Webhook + Router integrados
6. **T1.7** - SQLite leads
7. **T1.8** - Entry point

## Validación de Constitución (cada task)
Antes de cada implementación: Constitution Check (5 principios) → tests → código → validar.

## Métricas Target
- Lead capture → response < 3s (texto), < 10s (voz)
- Cita agendada → César notificado < 5s
- Provision tenant → operable < 30s
- Tests coverage > 80% lógica crítica