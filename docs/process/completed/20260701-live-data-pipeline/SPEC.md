# SPEC — Live Data Pipeline: Collectors → Revenue Events

| Campo | Valor |
|-------|-------|
| **ID** | `SPEC-20260701-003` |
| **Fecha** | 2026-07-01 |
| **Autor** | Mystic (Strategy OS) |
| **Tier** | 2 |
| **Estado** | activo |
| **Score requerido** | ≥60 |

---

## 1. Objetivo

Conectar datos públicos de artistas ABE Music (vía Deezer, YouTube, Wikipedia) a un pipeline de revenue events que alimente lead generation, enterprise score y content engine, sin usar ninguna API key.

---

## 2. Value Driver

revenue, automation, founder-independence, knowledge

---

## 3. Functional Requirements

| FR# | Descripción |
|-----|-------------|
| FR1 | Desplegar crw (Rust scraper, MCP nativo) en VPS como contenedor Docker con healthcheck |
| FR2 | Crear collector Deezer que obtenga: followers, monthly_listeners, top_tracks, popularity, genres para cada artista ABE |
| FR3 | Auto-sync cada 6h: collector → validación schema → actualizar `data/abe-music.json` con backup del anterior |
| FR4 | Emitir evento `data_sync_completed` con diff de métricas por artista |
| FR5 | Pipeline de revenue: datos vivos → lead scoring (artistas con >1M streams = qualified lead) → proposal auto-generada |
| FR6 | Dashboard live: mostrar métricas actualizadas de cada artista con delta vs sync anterior |
| FR7 | Fallback chain: crw → Python httpx/bs4 → Wikipedia API si Deezer falla |
| FR8 | Playwright MCP como alternativa para fuentes JS-heavy (TikTok, YouTube) |

---

## 4. Success Criteria

- [ ] crw corre en VPS, healthcheck pasa, consume <100MB RAM
- [ ] Collector Deezer obtiene datos de los 3 artistas ABE sin API key
- [ ] `data/abe-music.json` se actualiza automáticamente cada 6h con backup
- [ ] Evento `data_sync_completed` emitido con diff de métricas
- [ ] Lead generado automáticamente para Héctor Rubio (115M streams) en pipeline de ventas
- [ ] Enterprise Score sube de 23 → ≥60
- [ ] Zero nuevas API keys en todo el sistema

---

## 5. Gherkin Scenarios

Ver `process/active/gherkin/SPEC-20260701-003.feature`

---

## 6. Edge Cases

- [EC1] Artista existe en ABE pero no en Deezer → log warning, mantener datos static
- [EC2] Deezer devuelve datos parciales (ej. sin top_tracks) → merge parcial, no overwrite total
- [EC3] Sync falla 3 veces seguidas → alerta + mantener último backup exitoso
- [EC4] Nuevo artista agregado a ABE → auto-detectado y sync comienza automático
- [EC5] crw container se cae → restart policy + healthcheck notification

---

## 7. Technical Approach

```
scrapers/
├── docker-compose.scrapers.yml     # crw + playwright containers
├── crw/
│   └── Dockerfile                  # Rust binary, ~50MB
├── collectors/
│   ├── deezer.py                   # Python collector (fallback)
│   ├── youtube.py                  # Playwright-based
│   └── wikipedia.py                # API pública
└── sync.py                         # Orchestrator: collect → validate → merge → emit
```

Pipeline:
```
crw/collector → validate schema → backup data/abe-music.json → merge → write → emit event
                                                                       ↓
                                                            pipeline_bridge.py → Engram
                                                                       ↓
                                                            sales_pipeline → lead qualified
```

Archivos a crear/modificar:
- `scrapers/docker-compose.scrapers.yml` — nuevo
- `scrapers/Dockerfile` — nuevo (crw)
- `scrapers/collectors/deezer.py` — nuevo
- `scrapers/collectors/youtube.py` — nuevo
- `scrapers/sync.py` — nuevo
- `data/abe-music.json` — modificar (auto-sync)
- `state/backups/abe-music/` — backups automáticos
- `scripts/deploy-scrapers.sh` — script de deploy

---

## 8. Dependencies

- Docker en VPS (ya instalado)
- crw Rust binary compatible con linux/amd64
- Python 3.10+ con httpx, beautifulsoup4 (como fallback)
- `data/abe-music.json` existente con artistas
- Playwright MCP wrapper (`scripts/playwright-mcp-wrapper.sh`) — para YouTube

---

## 9. Events to Emit

| Evento | Cuándo |
|--------|--------|
| `data_sync_started` | Inicio de ciclo de sync |
| `data_sync_completed` | Sync exitoso con diff de métricas |
| `data_sync_failed` | Sync falló después de 3 intentos |
| `artist_metrics_changed` | Δ significativo en métricas de artista |
| `lead_generated_from_data` | Artista califica como lead calificado |

---

## 10. Kill Criteria

Si después de 1 semana complete de implementación:
1. crw no corre estable en VPS, o
2. Deezer bloquea scraping, o
3. No se genera ningún revenue event real
→ Abortar, migrar a Python-only collectors con datos manuales.

---

## 11. Scale Criteria

Cuando el pipeline maneje >10 artistas o >100 syncs/día:
- Agregar cola de mensajes (Redis Streams) para syncs
- Rate limiting por fuente
- Caché de respuestas para reducir llamadas
- Dashboard de salud de collectors
