# Research: Automation Tools & Stack

**Context**: Leveraging existing infra — n8n (7 workflows), 15 agents, Hermes, OpenClaw, Neo4j, Qdrant, Engram.

---

## Existing Automation Assets (ya funcionan)

| Asset | Ubicación | Propósito |
|-------|-----------|-----------|
| n8n workflow `content_factory.json` | `config/n8n/` | Factory de contenido (múltiples copias en backups) |
| n8n `healthcheck-workflow.json` | `config/n8n/` | Healthcheck automático |
| n8n `backup-workflow.json` | `config/n8n/` | Backup diario |
| n8n `webhook-bridge.json` | `config/n8n/` | Bridge Hermes ↔ n8n |
| n8n `workflow-daily-content.json` | `config/n8n/` | Contenido diario |
| n8n `workflow-content-payment.json` | `config/n8n/` | Pago por contenido |
| n8n `workflow-social-automation.json` | `config/n8n/` | Redes sociales automáticas |
| n8n `workflow-video-publish.json` | `config/n8n/` | Publicación video |
| 15 agents en `src/core/agents/` | orchestrator.py | Research, Code, Explore, Memory, Skill, Voice, Review, Hermes, OpenClaw, Gbrain |
| Hermes Agent | Hermes bridge | Telegram, Slack, notificaciones |
| OpenClaw | Gateway | Skills + agentes especializados |
| Neo4j + Qdrant | Docker | Memoria grafos + búsqueda vectorial |
| Engram (SQLite+FTS5) | `src/core/engram.py` | Contexto de sesión, caché de respuestas |
| `src/core/payments.py` | Core | Integración pagos existente |
| `src/core/harness.py` | Core | SDD Agent Harness pipeline |

## Tools to Integrate

| Tool | Propósito | Fase | Integración |
|------|-----------|------|-------------|
| Mercado Pago API | Cobros LATAM | 3 | REST API + webhooks |
| Stripe API | Cobros globales | 3 | REST API + webhooks |
| ElevenLabs / sag TTS | Voz para videos | 2 | CLI `sag` |
| fal.ai | Generación imágenes | 2-3 | REST API (FLUX, SDXL) |
| Canva Connect API | Assets visuales | 3 | REST API (solo export/upload) |
| Google Trends API | Investigación temas | 2 | `pytrends` o REST |
| OpenRouter | LLM para agentes | 1-5 | API compatible OpenAI |
| Systemd | Gestión servicios | 1 | `systemctl` + timer |
| Cron | Scheduling | 1 | `crontab` |
| Telegram Bot API | Notificaciones | 1-5 | vía Hermes |

## Architecture Decisions

1. **n8n como orquestador visual** — los workflows existentes se extienden, no se reemplazan
2. **Agentes Python para lógica** — cada agente CFO/Estratega/Creador es un skill de OpenClaw que llama a Python
3. **Hermes como message bus** — todas las notificaciones pasan por Hermes → multi-canal
4. **Neo4j como memoria financiera** — transacciones, productos, costos como grafos
5. **Cron + systemd timer** — scheduling sin dependencias externas
6. **Engram para contexto** — reportes anteriores, tendencias, caché de LLM

## Riesgos Técnicos

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|-------------|---------|------------|
| OpenRouter sin fondos | Media | Alto | Alerta <$20 + recarga automática |
| n8n se cuelga | Baja | Medio | Healthcheck + restart automático |
| API MP/Stripe cambia | Baja | Alto | Versión fija en integración |
| Neo4j corrupción | Baja | Alto | Backup diario + verificado |
| Rate limiting APIs | Media | Medio | Retry con backoff + cola |

## Referencias

- n8n docs: https://docs.n8n.io
- Mercado Pago API: https://www.mercadopago.com.ar/developers
- Stripe API: https://stripe.com/docs/api
- OpenRouter: https://openrouter.ai/docs
- ElevenLabs: https://elevenlabs.io/docs
