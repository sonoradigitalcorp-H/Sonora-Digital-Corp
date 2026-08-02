# SPEC — Mystica OS v3.0 (Autonomous Omnicall)

| Campo | Valor |
|---|---|
| **ID** | SPEC-20260730-MYSTICA-OS |
| **Fecha** | 2026-07-30 |
| **Score** | 78/100 |
| **Estado** | activo |

## 1. Objetivo
Sistema autónomo omnicanal que busca leads, los contacta, atiende por voz/texto, agenda citas y notifica al creador. Todo desde una laptop sin GPU, con página web viviente (ciudad de agentes, cartas Yu-Gi-Oh, colores dinámicos).

## 2. Stack
- **Frontend**: HTML estático + Three.js + CSS variables dinámicas
- **Backend**: Python asyncio + aiortc (WebRTC) + aiohttp
- **STT**: faster-whisper (Hugging Face, CPU)
- **TTS**: edge-tts (es-MX-DaliaNeural, CPU)
- **LLM**: OpenRouter deepseek-v4-flash
- **Memoria**: Engram (SQLite por tenant, 7 capas)
- **Scraper**: Playwright (Google Maps)
- **Colas**: Redis (futuro)
- **Workflows**: n8n (futuro)

## 3. Componentes
- `web/index.html` — Portal con ciudad de agentes, cartas interactivas, colores por hora
- `web/call.html` — Llamada WebRTC con orbe 3D
- `web/creator.html` — Panel del creador (stats, tenants, A/B, evolución)
- `campaigns/scraper.py` — Playwright busca leads en Google Maps
- `campaigns/outreach.py` — Mensajes personalizados para tenants existentes
- `daemon.py` — Loop autónomo (campañas → outreach → notificar → evolucionar)
- `pipeline/` — STT → Gates → LLM → TTS → Booking
- `tenant/service.py` — CRUD + clasificación cold/warm/hot
- `analytics/` — Scoring, A/B testing, evolution hook

## 4. Success Criteria
- [x] Búsqueda de leads autónoma con Playwright (4 nichos)
- [x] Página web con ciudad de agentes + cartas Yu-Gi-Oh
- [x] Colores dinámicos según hora del día
- [x] Llamadas WebRTC con identificación de tenant
- [x] Daemon autónomo con loop de campañas
- [x] 28 tests unitarios pasando
- [x] Panel del creador con métricas en vivo
- [ ] Outreach a tenants existentes (falta WhatsApp real)
- [ ] Booking con Google Calendar
- [ ] Notificaciones a WhatsApp + Telegram + Gmail

## 5. Eventos
| Evento | Trigger |
|---|---|
| `campaign:completed` | Campaña de scraping terminada |
| `lead:created` | Nuevo lead registrado |
| `call:completed` | Llamada finalizada |
| `evolution:applied` | Mejora automática aplicada |
