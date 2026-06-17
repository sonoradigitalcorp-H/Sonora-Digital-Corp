# SDC n8n Automations Index

## Webhooks Públicos

| Webhook | Purpose | Services |
|---------|---------|----------|
| `POST /webhook/deploy` | Deploy notification | Telegram |
| `POST /webhook/generate-image` | Generate image (Fal.ai Flux) | Fal.ai |
| `POST /webhook/alert` | Service alert | Telegram |
| `POST /webhook/new-user` | Welcome onboarding | WhatsApp, Telegram |
| `POST /webhook/social-post` | Social media auto-publish | Instagram, LinkedIn |
| `POST /webhook/nuevo-evento` | Music Hub event blast | Fal.ai, OpenRouter, Telegram |
| `POST /webhook/nuevo-fan` | Fan CRM onboarding | PostgreSQL, Telegram |

## Scheduled Workflows

| Workflow | Schedule | Purpose |
|----------|----------|---------|
| Content Factory | Every 6h | Generate + publish content |
| Content Pipeline | Mon/Wed/Fri 9am | Video + social media copy |
| Music Hub Daily | Daily 2am | Artist content generation |
| Weekly Reports | Monday 8am | Per-artist analytics |
| Health Check | Every 30min | System monitoring |
| Watchdog | Every 5min | Self-healing |
| Backups | Daily 2am | Google Drive backup |
| SAT Alerts | Day 10/14/16/17 | Fiscal deadlines |

## Payment Webhooks (Por Configurar)

| Provider | Webhook | Purpose |
|----------|---------|---------|
| Mercado Pago | `POST /webhook/mercadopago` | Payment notifications |
| Bitso | `POST /webhook/bitso` | Crypto payment confirmations |

## Environment Variables Required

```env
# Telegram
TELEGRAM_BOT_TOKEN=
TELEGRAM_CEO_CHAT_ID=
HERMES_ADMIN_CHAT_ID=

# Content & AI
ANTHROPIC_API_KEY=
OPENROUTER_API_KEY=
FAL_API_KEY=

# Payments
MERCADO_PAGO_ACCESS_TOKEN=
BITSO_API_KEY=
BITSO_API_SECRET=

# Infrastructure
DOCKER_API_URL=http://localhost:2375
N8N_BASE_URL=http://localhost:5678
N8N_API_KEY=

# Social Media
INSTAGRAM_ACCOUNT_ID=
META_ACCESS_TOKEN=
LINKEDIN_TOKEN=
LINKEDIN_PERSON_ID=
```
