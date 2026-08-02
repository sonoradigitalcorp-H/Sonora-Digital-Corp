# Abe Music Hub

Hub físico y digital para músicos en Hermosillo, Sonora.
Token musical `$RESO` · CRM de fans · Bot Telegram · Reels IA · VR Cabinas.

**Backend**: [HERMES OS](https://github.com/perrykingla69-cyber/sonora-digital-corp) — nunca conectar a BD directamente desde aquí.

---

## Setup rápido (5 pasos)

### 1. Clonar y configurar env
```bash
git clone git@github.com:perrykingla69-cyber/ABE-MUSIC-HUB.git
cd ABE-MUSIC-HUB
cp .env.example .env
# Editar .env con los tokens reales
```

### 2. Variables de entorno requeridas
| Variable | Descripción |
|---|---|
| `ABE_MUSIC_BOT_TOKEN` | Token del bot Telegram (BotFather) |
| `HERMES_API_URL` | URL de HERMES OS API (default: http://localhost:8000) |
| `ABRAHAM_CHAT_ID` | Chat ID de Abraham para notificaciones |
| `STRIPE_SECRET_KEY` | Key de Stripe para suscripciones |

### 3. Levantar con Docker Compose
```bash
docker compose up -d
```

### 4. Aplicar migración en HERMES OS
```bash
# En el repo hermes-os:
docker exec -i hermes-postgres psql -U hermes_user -d hermes_db \
  < infra/migrations/008_abe_music_hub.sql
```

### 5. Verificar
```bash
docker compose ps
# Bot: logs en abe-music-bot
# Frontend: http://localhost:3010
```

---

## Estructura
```
ABE-MUSIC-HUB/
├── CLAUDE.md                  ← Instrucciones para Claude Code
├── .env.example               ← Variables de entorno requeridas
├── docker-compose.yml         ← Bot + frontend (sin duplicar infra HERMES)
├── frontend/
│   ├── index.html             ← Landing pública (demo vanilla)
│   ├── dashboard.html         ← Dashboard Abraham (demo vanilla)
│   └── app/                  ← Next.js 15 (producción — pendiente)
├── bots/
│   └── abe-music-bot.ts       ← Bot Telegram principal (Telegraf)
└── infra/
    └── migrations/
        └── 008_abe_music_hub.sql  ← Tablas hub (hub_services, hub_bookings, token_ledger, etc.)
```

---

## Servicios del hub

**Físicos**: Sala ensayo · Estudio grabación · Clases · Podcast studio · Zona gym · Retiros creativos · VR cabinas · Mini shows · Eventos privados · Creación contenido

**Digitales**: Clon IA artista · Cursos online · Pipeline reels 3AM · Marketing digital · Dashboard CRM · Token $RESO · Suscripciones · Merch · Baquetas artesanales · Renta equipo

---

## Token $RESO

| Acción | Ganancia |
|---|---|
| Crear meme validado | +25 $RESO |
| Dueto/stitch reel | +15 $RESO |
| Referido suscrito | +200 $RESO |
| Live virtual | +50 $RESO |
| Completar curso | +150 $RESO |

**Niveles**: EMERGENTE (0) → LOCAL (500) → REGIONAL (2,000) → NACIONAL (5,000)

---

## Stack

| Área | Tecnología |
|---|---|
| Frontend (prod) | Next.js 15, TypeScript, Tailwind, shadcn/ui |
| Bot Telegram | Telegraf (Node.js), TypeScript |
| API calls | axios → HERMES_API_URL |
| Pagos | Stripe via HERMES API |
| Deploy frontend | Vercel |
| Deploy bot | VPS Hostinger (Docker Compose) |

---

**Filosofía**: Coraje · Luz · Brillo · Unidad · Refugio · Aprendizaje · Constancia · Valentía
