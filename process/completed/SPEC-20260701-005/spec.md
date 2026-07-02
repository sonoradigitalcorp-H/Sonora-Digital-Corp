# SPEC — Production Hardening + Infrastructure Automation

| Campo | Valor |
|-------|-------|
| **ID** | `SPEC-20260701-005` |
| **Fecha** | 2026-07-01 |
| **Autor** | OpenClaw |
| **Tier** | 2 |
| **Estado** | activo |
| **Score requerido** | ≥60 |

---

## 1. Objetivo

Cerrar los 6 broken items y 5 missing features del sistema — sync automático, lead bridge funcional, Qdrant seedeado, dashboard de salud, y commits sin fricción. El sistema debe operar sin intervención humana por 7 días consecutivos.

---

## 2. Value Driver

founder-independence, automation, reliability

---

## 3. Functional Requirements

| FR# | Descripción |
|-----|-------------|
| FR1 | Sync automático cada 6h via cron — datos siempre frescos |
| FR2 | Lead bridge funcional — leads llegan a Neo4j sin error de import |
| FR3 | Commits sin bloqueo — spec de mantenimiento permanente o hook condicional |
| FR4 | Qdrant seedeado con artistas — búsqueda vectorial funcional |
| FR5 | Dashboard de salud de providers — verde/rojo por provider |
| FR6 | Wikipedia 403 resuelto o reemplazado por fuente alternativa |
| FR7 | TikTok handles corregidos en CEO data o scraping con fallback |

---

## 4. Success Criteria

- [ ] Sync corre automático cada 6h sin intervención
- [ ] `data/abe-music.json` se actualiza solo — comprobable via `last_sync`
- [ ] Lead bridge no tira error de import — leads en Neo4j
- [ ] `git commit` funciona sin `--no-verify` en ausencia de spec activa
- [ ] Qdrant responde queries de artistas
- [ ] Dashboard salud muestra estado de ≥8 providers
- [ ] Score ≥60

---

## 5. Gherkin Scenarios

Ver `gherkin/SPEC-20260701-005.feature`

---

## 6. Edge Cases

- [EC1] Cron corre pero VPS reinicia → systemd timer en vez de crontab
- [EC2] Neo4j offline → lead bridge debe fallar graceful, no crashear sync
- [EC3] Qdrant offline → seed debe reintentar, no fallar silenciosamente
- [EC4] Provider dashboard sin datos históricos → mostrar solo estado actual
- [EC5] Wikipedia sigue 403 → marcar como degraded, no como critical

---

## 7. Technical Approach

```
Fase 1 — Produccion: sync cron + lead bridge + commit hook
  scripts/install-sync-cron.sh → validar + ejecutar
  scrapers/sync.py → fix import path en bridge_lead_to_pipeline()
  process/active/ → crear MANTENIMIENTO spec permanente

Fase 2 — Datos: Qdrant seed
  scripts/seed-qdrant.py → leer data/abe-music.json → upsert a Qdrant
  coleccion: "abe-artists"

Fase 3 — Monitoreo: dashboard salud
  planner/health.py → endpoint simple HTTP en ABE Service :5180/health
  HTML visual con status de cada provider
```

Archivos afectados:
- `scripts/install-sync-cron.sh` — validar que funcione
- `scrapers/sync.py` — fix import path
- `process/hooks/pre-commit` — permitir commits sin spec
- `scripts/seed-qdrant.py` — nuevo
- `apps/abe-service/api/rest.py` — endpoint /health/providers

---

## 8. Dependencies

- Neo4j corriendo en :7687 (Docker)
- Qdrant corriendo en :6333 (Docker)
- `planner/` package funcional con health checks
- `data/abe-music.json` con datos actualizados

---

## 9. Events to Emit

| Evento | Cuándo |
|--------|--------|
| `cron_installed` | Cron configurado exitosamente |
| `lead_bridged` | Lead enviado a Neo4j sin error |
| `qdrant_seeded` | Colección abe-artists poblada |
| `provider_health_changed` | Estado de un provider cambia |

---

## 10. Kill Criteria

Si después de 2 días:
1. Sync cron no está corriendo, o
2. Lead bridge sigue roto, o
3. Qdrant no tiene datos
→ Pausar, priorizar lo que sí funciona.

---

## 11. Scale Criteria

- Monitoreo de latencia de sync cycle (alertar si > 5min)
- Provider dashboard con histórico 7 días
- Qdrant con embeddings de artistas para RAG
- Auto-repair: si cron falla 3 veces seguidas, notificar a Telegram
