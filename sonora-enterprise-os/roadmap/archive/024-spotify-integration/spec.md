# Spec: ABE Music — Spotify API Integration

- **Status**: Approved
- **Author**: @sdd
- **Revenue Gate**: ✅ — streams reales → revenue tracking → splits automáticos
- **Priority**: P1
- **Estimated Effort**: 5 story points

## 1. Problem

ABE Music tiene 3 artistas con datos importantes (Héctor Rubio: 115M streams, $460K revenue) pero toda la data es manual/estimada. No hay conexión con Spotify API para:

- Traer streams reales, monthly listeners, popularidad
- Sincronizar automáticamente cada 6h
- Mostrar datos vivos en dashboards y reports
- Detectar tendencias y oportunidades de marketing

Sin esto, los KPIs del CEO dashboard son stale, los reports semanales no reflejan la realidad, y ABE Music no puede tomar decisiones data-driven.

## 2. Goal

Conectar Spotify API para ABE Music y sincronizar datos reales de los 3 artistas activos.

**Métrica de éxito**: Dashboard CEO refleja streams reales de Spotify con < 6h de latencia. Pipeline corre automáticamente cada 6h sin intervención.

## 3. Scope

### In scope

- Configurar Spotify Developer App credentials en `.env`
- Configurar `spotify_artist_id` para Héctor Rubio, Jesus Urquijo, Javier Arvayo en `config/artists.json`
- Activar integración en `config/abe-system.json` (`enabled: true`)
- Mejorar pipeline Python (`clients/abe-music/pipeline.py`) para traer: monthly listeners, popularity, genres, top tracks
- Mejorar dashboard CEO para mostrar datos de Spotify (popularity badge, last sync timestamp)
- Sincronización automática cada 6h vía cron/scheduler
- Logging de sync events para observabilidad

### Out of scope

- Refresh Token flow (solo Client Credentials por ahora — datos públicos)
- Apple Music API
- Distribución/push de música a Spotify
- Payouts automáticos basados en streams

## 4. User Stories

```gherkin
Feature: Spotify Data Sync
  As the ABE Music CEO
  I want real streaming data from Spotify
  So that I can make informed decisions about marketing and A&R

  Scenario: Sync all artists successfully
    Given Spotify API credentials are configured in .env
    And 3 artists have valid spotify_artist_ids
    When the pipeline runs
    Then each artist's monthly_listeners is updated
    And each artist's popularity score is recorded
    And each artist's genres are recorded
    And the sync timestamp is saved
    And the total streams and revenue in the CEO dashboard match Spotify data

  Scenario: Missing credentials
    Given no SPOTIFY_CLIENT_ID in .env
    When the pipeline runs
    Then it logs a warning
    And existing data is preserved unchanged

  Scenario: Invalid artist ID
    Given an artist has a wrong spotify_artist_id
    When the pipeline runs
    Then that artist is skipped with a warning
    And other artists still sync successfully

  Scenario: Spotify API is down
    Given the Spotify API returns 5xx errors
    When the pipeline runs
    Then it retries up to 3 times
    And if still failing, logs the error
    And existing data is preserved

  Scenario: View sync status in MCP
  As the system operator
  I want to check the sync status of each artist
  So that I know the freshness of the data

    Given an artist has been synced
    When I call the artist_status tool
    Then I see last_sync timestamp and spotify:ok status
```

## 5. Technical Approach

### Architecture

```
Spotify API (accounts.spotify.com/api/token + /v1/artists/{id})
    ↑ Client Credentials (Client ID + Client Secret)
    ↓
pipeline.py (Python) — scheduled every 6h via cron/abe-daemon
    ↓
data/abe-music.json — updated with live data
    ↓
abe_music.py / KPIDashboard — reads data
    ↓
abe_router.py (FastAPI) — serves via REST API
abe-portal.html, abe-saas.html — show in dashboards
```

### Data flow

1. Pipeline reads SPOTIFY_CLIENT_ID + SPOTIFY_CLIENT_SECRET from .env
2. Gets OAuth token via Client Credentials grant
3. For each artist with a spotify_url, extracts the Spotify Artist ID
4. Calls GET /v1/artists/{id} for monthly listeners, popularity, genres
5. Calls GET /v1/artists/{id}/top-tracks?market=US for top tracks
6. Updates data/abe-music.json with fresh data
7. Logs results

### Components to modify

| File | Change |
|------|--------|
| `config/abe-system.json` | Set `spotify.enabled: true`, add `spotify.client_id` placeholder |
| `config/artists.json` | Fill `spotify_artist_id` for all 3 artists |
| `clients/abe-music/pipeline.py` | Add top-tracks fetch, better error handling, retry logic |
| `apps/jarvis/src/core/abe_music.py` | Add `last_spotify_sync`, `popularity`, `genres` fields to artist model |
| `apps/webui/routes/abe_router.py` | Add GET /api/abe/sync/status endpoint |
| `.env` | Add SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET (placeholder) |
| `state/logs/` | Sync events logged to events.jsonl |

## 6. Dependencies

| Dependency | Status |
|-----------|--------|
| Spotify Developer App (Abraham) | **PENDING** — needs to create at developer.spotify.com |
| `SPOTIFY_CLIENT_ID` | **PENDING** — from Spotify Dashboard |
| `SPOTIFY_CLIENT_SECRET` | **PENDING** — from Spotify Dashboard |
| `requests` library | ✅ already in requirements.txt |
| Python 3.10+ | ✅ already in use |

## 7. Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Abraham doesn't create Spotify app | H | M | Spec is ready; only missing credentials |
| Spotify API rate limits | M | L | 0.5s delay between requests, max 3 artists |
| Artist ID changes | M | L | Use Spotify URL as canonical, log warnings |
| API format changes | M | L | Add JSON schema validation on response |
| Credentials leak | H | L | Store in .env (gitignored), never hardcoded |

## 8. Acceptance Criteria

- [ ] All Gherkin scenarios pass
- [ ] Pipeline fetches real data for all 3 artists when credentials present
- [ ] Pipeline gracefully handles missing/invalid credentials
- [ ] `data/abe-music.json` updated with `monthly_listeners`, `popularity`, `genres`, `top_tracks`, `last_spotify_sync`
- [ ] CEO dashboard reflects Spotify freshness (last sync timestamp)
- [ ] Sync status available via MCP tool `artist_status`
- [ ] Pipeline runs on schedule (every 6h)
- [ ] Tests pass: `pytest tests/unit/test_abe_music.py`
- [ ] Spec approved by human before implementation
