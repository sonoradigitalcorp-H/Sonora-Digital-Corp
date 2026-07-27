# Data Policy — Paths, Locations & Pipelines

**Source**: TRUTH.md (migrated)
**Audit ID**: DAT-001

---

## Unified Root Path {#unified-path}

The monorepo root is `/home/mystic/sonora-digital-corp/`.
All agents MUST use this path. No exceptions.

## Key Locations {#key-locations}

| What | Where |
|------|-------|
| Constitution | `constitution/` |
| JARVIS core | `apps/jarvis/src/core/` |
| Web UI | `apps/webui/` (FastAPI, port 5174) |
| MCP Gateway | `mcp/gateway/` |
| MCP Tools | `mcp/tools/` (31 modules) |
| Agents | `agents/` (18 JARVIS + 24 ADK) |
| Docker compose | `infra/docker-compose.yml` |
| Tests | `tests/` |
| State & logs | `state/` |
| ABE Music data | `data/abe-music.json` |
| Scrapers | `scrapers/` (crw :3000, Playwright :8931) |

## Collectors Data Schema {#collectors-schema}

Every collector (Deezer, YouTube, TikTok, Wikipedia, etc.) MUST emit this schema:

```json
{
  "source": "deezer",
  "artist_name": "Hector Rubio",
  "followers": 45000,
  "monthly_listeners": 1100000,
  "top_tracks": [{"name": "Se Volvieron Locos", "plays": 16000000}],
  "popularity": 78,
  "genres": ["Regional Mexicano"],
  "url": "https://www.deezer.com/artist/...",
  "fetched_at": "2026-07-01T..."
}
```

## Pipeline System {#pipeline-system}

Lifecycle: `Tier 1: Execute → Lección | Tier 2: Spec → Score → Gherkin → Tests → Code → Events → ADR → Lección | Tier 3: VDD → EDD → PDD → ODD → SDD → BDD → TDD → ADR → Events → Lección`

CLI: `bash scripts/process-pipeline.sh <command>`

## Engram Memory System {#engram}

SQLite + FTS5 at `state/engram.db`.
Importance levels: critical(3), high(2), medium(1), low(0).
Decay: 30 days.
