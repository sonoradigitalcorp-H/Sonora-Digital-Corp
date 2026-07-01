# CLAUDE.md — ABE MUSIC HUB
> Instrucciones para Claude Code. Idioma: **español siempre**.

---

## CONTEXTO DEL PROYECTO

**Abe Music Inc.** — Hub físico y digital para músicos en Hermosillo, Sonora.
**Dueño**: Abraham (WhatsApp: +13238192000, California)
**Repo**: `github.com/perrykingla69-cyber/ABE-MUSIC-HUB`
**Backend**: HERMES OS API en `http://localhost:8000` (o `HERMES_API_URL` en .env)

Este repo contiene **solo el frontend y los bots de Abe Music Hub**.
La infraestructura (PostgreSQL, Redis, Qdrant, FastAPI) vive en HERMES OS.
Todo acceso a datos pasa por `HERMES_API_URL` — **nunca conectar a DB directamente desde aquí**.

---

## ARQUITECTURA

```
Abraham (WhatsApp / Telegram / Web)
    ↓
ABE-MUSIC-HUB (este repo)
  ├── frontend/           Next.js 15 — landing + dashboard CRM
  ├── bots/               Bot Telegram Abe Music Hub (Telegraf)
  └── infra/migrations/   008_abe_music_hub.sql (tablas hub)
    ↓ HTTP (HERMES_API_URL)
HERMES OS (hermes-os repo)
  ├── FastAPI :8000        Endpoints: /hub/* /tokens/* /reels/*
  ├── PostgreSQL          RLS multi-tenant, tablas de 006 + 008
  ├── Redis               Cache + JWT JTI
  └── Qdrant              RAG vectorial
```

---

## STACK

| Área | Tecnología |
|------|-----------|
| Frontend | Next.js 15 (App Router), TypeScript, Tailwind CSS, shadcn/ui |
| Bot Telegram | Telegraf (Node.js), TypeScript |
| API calls | axios hacia `HERMES_API_URL` |
| Pagos | Stripe (via HERMES API) |
| Deploy frontend | Vercel |
| Deploy bot | VPS Hostinger (Docker Compose) |

---

## REGLAS CRÍTICAS (nunca olvidar)

1. **No conectar a DB directamente** — siempre via HERMES_API_URL
2. **JWT field**: `usuario` (no `user`) en tokens de HERMES OS
3. **docker compose** v2 — nunca `docker-compose`
4. **Variables de entorno**: nunca hardcodear tokens — leer de `process.env`
5. **Logging**: `console.log` solo en dev — en producción usar `logger`
6. **Mensajes al usuario**: siempre en español
7. **Nombres de variables/funciones**: inglés (camelCase)
8. **Token del proyecto**: `$RESO` — moneda musical del hub

---

## SERVICIOS DEL HUB (20+ fuentes de ingreso)

```
Físicas:                          Digitales:
- Renta cuartos de ensayo         - Clon digital IA del artista
- Estudio de grabación            - Cursos online (plataforma)
- Clases de música                - Pipeline reels 3 AM (IA)
- Podcast studio                  - Marketing digital para artistas
- Zona gym                        - Dashboard CRM para creadores
- Retiros creativos               - Token $RESO gamificación
- VR cabinas inmersivas           - Suscripciones mensuales
- Mini shows en hub               - Merch con firma artista
- Eventos privados                - Baquetas artesanales (torno)
- Espacio creación contenido      - Renta equipo sonido
```

---

## GAMIFICACIÓN ($RESO TOKEN)

**Niveles**: EMERGENTE → LOCAL → REGIONAL → NACIONAL
**Ganar $RESO**:
- Crear meme del artista validado: 25 $RESO
- Dueto/stitch de reel: 15 $RESO
- Referido que se suscribe: 200 $RESO
- Asistir a live virtual: 50 $RESO
- Completar curso: 150 $RESO

**Quemar $RESO**:
- Entradas a eventos flash (precio dinámico según demanda)
- Horas extra de ensayo: 100 $RESO = 1 hora
- Merch exclusivo
- Acceso VR cabinas

**API endpoints a consumir** (en HERMES OS):
- `POST /hub/tokens/earn` — ganar $RESO
- `POST /hub/tokens/burn` — quemar $RESO
- `GET /hub/tokens/balance/:userId` — saldo
- `GET /hub/leaderboard/:period` — ranking weekly/monthly

---

## PLANES DE SUSCRIPCIÓN

| Plan | Precio MXN/mes | $RESO mensual | Beneficios clave |
|------|---------------|--------------|-----------------|
| Básico | $99 | 100 | Acceso dashboard, 5 reels IA/mes |
| Pro | $299 | 400 | Clon IA básico, 20 reels, merch 10% dto |
| Élite | $999 | 1200 | Clon IA avanzado, VIP eventos, merch 20% dto |

---

## ESTRUCTURA DE CARPETAS

```
ABE-MUSIC-HUB/
├── CLAUDE.md                    ← Este archivo
├── README.md
├── .env.example
├── docker-compose.yml           ← Solo servicios nuevos (bot, frontend)
├── frontend/
│   ├── index.html               ← Landing pública (Vanilla HTML - demo)
│   ├── dashboard.html           ← Dashboard Abraham (Vanilla HTML - demo)
│   └── app/                    ← Next.js 15 (producción)
│       ├── layout.tsx
│       ├── page.tsx             ← Landing
│       ├── dashboard/
│       │   └── page.tsx         ← CRM dashboard Abraham
│       └── hub/
│           └── page.tsx         ← Servicios del hub
├── bots/
│   └── abe-music-bot.ts         ← Bot Telegram principal
├── infra/
│   └── migrations/
│       └── 008_abe_music_hub.sql ← Tablas hub-específicas
└── docs/
    ├── servicios-hub.md
    └── gamificacion.md
```

---

## ENDPOINTS HERMES OS (a consumir desde este repo)

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/hub/services` | GET | Lista servicios disponibles |
| `/hub/bookings` | POST | Crear reserva (sala, estudio, etc.) |
| `/hub/bookings/:id` | GET | Estado de reserva |
| `/hub/tokens/earn` | POST | Ganar $RESO |
| `/hub/tokens/burn` | POST | Quemar $RESO por beneficio |
| `/hub/tokens/balance/:userId` | GET | Saldo $RESO |
| `/hub/leaderboard/:period` | GET | Ranking weekly/monthly |
| `/hub/events/flash` | POST | Crear evento flash |
| `/hub/events/join` | POST | Unirse a evento |
| `/hub/reels/generate` | POST | Trigger pipeline reels 3 AM |
| `/artists/:tenantId` | GET | Perfil artista |
| `/artist-fans` | GET/POST | CRM fans del artista |

---

## CUANDO TE PIDA CÓDIGO, RESPONDE SIEMPRE CON:

1. **Objetivo** (1 frase)
2. **Archivos afectados**
3. **Código completo** (listo para copiar)
4. **Llamadas a HERMES OS** que necesita
5. **Variables de entorno** nuevas que requiere

---

## CÓMO TRABAJAR CON CLAUDE CODE

```bash
# El usuario siempre empezará con:
# "Siguiendo CLAUDE.md, genera [componente]..."

# Ejemplo de sesión típica:
# "Siguiendo CLAUDE.md, genera el endpoint POST /hub/bookings
#  en HERMES OS (FastAPI) y el componente BookingForm.tsx en el dashboard"
```

---

**Filosofía Abe Music**: Coraje · Luz · Brillo · Unidad · Refugio · Aprendizaje · Constancia · Valentía.
El hub es más que un estudio — es el hogar del músico sonorense.

**Última actualización**: 2026-05-08 | **Versión**: 1.0
