# ADR-20260802-SDC-SYSTEM-SESSION

| Campo | Valor |
|-------|-------|
| **ID** | `ADR-20260802-SDC-SYSTEM-SESSION` |
| **Fecha** | 2026-08-02 |
| **Spec** | Sesión completa de auditoría, fixes, automatización y protección |
| **Estado** | aceptado |

---

## Context

Sesión larga (00:00 - 04:30) donde se hizo una auditoría completa del sistema SDC, se arreglaron errores críticos, se implementaron protecciones, se conectó automatización de redes sociales, y se creó un dashboard 3D. Todo comenzó con un check del estado del sistema y terminó con un JARVIS 3D funcional.

## Decision — Lo que se hizo

### 1. Auditoría del Sistema (00:00-00:30)
- Git remote fix: `origin` ahora apunta a GitHub (Gitea muerto removido)
- Postgres: creada tabla `leads` + `session_cache` (7 tablas total)
- Qdrant: poblados 16 puntos RAG (catálogo, ventas, objeciones, tech)
- Redis: integrado como cache de sesiones del bot (TTL 24h)
- MCP: verificados 6 servers (sdc-mcp, filesystem, playwright, obsidian, wacli, playwright-social)
- Engram: 18 memorias unificadas
- Servicios: 4 systemd services 24/7 (bot, notif, tts, n8n-bridge)
- Cron: auto-heal (5min), shield audit (1h), auto-improve (3am)

### 2. Lead Classifier Fixes (00:30-01:00)
- Fix regex `necesito\s+\w*\s+ya` → `necesito\s+\S+\s+ya` (hot messages)
- Add `duda` group a warm ("no estoy seguro", "conviene cambiar")
- Add `rechazo` group a cold ("caro", "olvídalo", "no me convence")
- Result: 83.3% → 94.4% lead accuracy (solo reglas, 18 casos)
- Fix prompt_builder: opciones específicas en botones (no genéricas)

### 3. Voice Pipeline (01:00-01:30)
- TTS server fix: full path para edge-tts (systemd no tiene ~/.local/bin)
- Generados 6 audios de prueba (saludo, servicios, objeciones, hot/warm/cold)
- Enviados a César via Telegram
- Pipeline completo verificado: TTS → WAV → OGG opus → Telegram

### 4. Bot Dual (01:30-02:00)
- Bot notificaciones: @MysticUnity_bot (token nuevo de BotFather)
- Bot conversación: @Aztro_tech_bot (token original)
- Ambos corriendo como systemd services 24/7

### 5. Mystic Shield — Seguridad (02:00-02:30)
- Rate limiting: 10 msg/min, 50/hora, 200/día
- Anti-spam: flood detection, repeated chars, multiple URLs
- Anti-prompt-injection: override, jailbreak, DAN detection
- Anti-SQL/XSS/command injection: pattern matching
- Ban system: 3 warnings = 24h ban
- Audit logger: hourly cron scans bot logs
- Shield state persisted in `ops/state/shield.json`

### 6. Secrets Cleanup (02:30-03:00)
- Todos los bot tokens reemplazados con env vars
- DB URLs usan `${POSTGRES_PASSWORD}` fallback
- `.gitignore` actualizado para secretos
- `.env.example` creado como template
- `openclaw.json` token reemplazado
- ADRs limpiados de passwords

### 7. White-Label Multi-Tenant (03:00-03:30)
- `provision_white_label.py`: 3 tiers (platform $25K, dedicated $35K, enterprise $100K)
- Auto-crea: Postgres schema, Qdrant collection, systemd, .env
- Demo client provisioned como example

### 8. Gherkin Tests (03:30-04:00)
- 92 escenarios en 4 features (lead, voice, conversation, notifications)
- Runner completo con pipeline testing
- Result: 84/92 passing (91.3%), 445/453 steps (98.2%)

### 9. Social Media Automation (04:00-04:15)
- `social_automation.py`: Twitter, Instagram, Facebook
- Anti-loop: 512MB RAM, 10 actions/hour, 2min cooldown
- Session persistence: SQLite cookies
- Content scheduler: 5 posts programados para hoy
- Cookie import from Chrome (Twitter, Instagram, Facebook, TikTok, LinkedIn)

### 10. Playwright Audit — 8 Critical Fixes (04:15-04:30)
1. MemoryGuard: process RAM (not system RAM)
2. Chromium auto-detect (no hardcoded version)
3. Playwright MCP: reuses browser instance (30min session)
4. engine.py consolidated with social_automation.py
5. playwright.config.ts: headless via CI env
6. Docker: proper healthcheck, shm 256mb
7. Anti-detection delays: 10-30s (was 2-5s)
8. MCP gateway: async, no execSync

### 11. JARVIS 3D Dashboard (04:30)
- Three.js 3D scene with orbiting client nodes
- Central wireframe sphere, orbital rings, particle field
- Interactive: click nodes → popup with metrics
- HUD: infrastructure, bots, activity feed
- Real-time data from n8n bridge

## Options Considered

| Opción | Pros | Contras |
|--------|------|---------|
| **Todo en una sesión** | Coordinación completa, contexto fresco | Sesión larga, muchos cambios |
| Sesiones separadas por feature | Menos riesgo | Fragmentación, pérdida de contexto |

## Consequences

- **Positivas**: sistema completo funcional, 4 clientes soportados, 12 servicios 24/7, seguridad activa, dashboard 3D
- **Positivas**: 0 secrets expuestos en código, auto-healing automático, tests 91.3%
- **Deuda**: login interactivo de redes sociales pendiente (una vez)
- **Deuda**: canal Telegram requiere api_id de César
- **Deuda**: WhatsApp re-auth requiere QR interactivo
- **Deuda**: 235 archivos untracked necesitan commit

## Related

- Commits: `35d8925` → `b0eaabe` → `5314aed` → `13e5903` → `6efad0a` → `4ec4354` → `89b9b08` → `1a32ed5` → `3ab137f` → `2e8505f`
- ADRs previos: `ADR-20260802-AZROTECH-MVP-RAG-MEMORIA`, `VOZ-LOCAL`, `WHATSAPP-SANDBOX`, `GITHUB-CI`
