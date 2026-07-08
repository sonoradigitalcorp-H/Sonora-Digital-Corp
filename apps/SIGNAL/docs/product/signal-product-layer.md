# SIGNAL Product Layer — Intelligence Product

> **Version:** 3.5.0  
> **Goal:** Expose intelligence scoring as a consumable product — not just a backend capability.

## What Changed

Phase 3.5 built the product layer on top of Phase 3's Score Engine:

| Before (Phase 3) | After (Phase 3.5) |
|------------------|-------------------|
| Score Engine exists internally | ✅ Intelligence API exposes it |
| No feature tracking | ✅ Feature Store tracks provenance |
| No insight generation | ✅ Deterministic insight engine |
| No frontend consumption | ✅ Intelligence Dashboard |
| No public interface | ✅ `GET /api/v1/intelligence/[id]` |

## Architecture Decision: Single Interface

> **The Intelligence API is the ONLY public interface.**

This decision enforces:
- **Security:** Providers, features, and internal logic are never exposed
- **Consistency:** All consumers get the same data shape
- **Evolvability:** Internal changes don't break frontend
- **Observability:** Single point to monitor, log, and cache

New consumers (mobile app, third-party API, etc.) **must** go through the Intelligence API, never through providers or scoring directly.

## What's Included

### 1. Feature Store (`src/scoring/feature-store.ts`)

Internal service that:
- Ingests `UnifiedArtist` → featured data with metadata
- Tracks feature provenance (which provider contributed what)
- Computes quality scores per feature (0-1)
- Maintains freshness timestamps
- **Never exposed to frontend**

### 2. Insight Generation (`src/scoring/insights.ts`)

Deterministic engine that produces:
- **Growth signals** — positive momentum indicators
- **Risk signals** — declining or concerning metrics
- **Opportunity signals** — untapped potential
- **Achievement signals** — exceptional score performance
- **Warning signals** — below-average metrics

All insights are **rule-based** — no ML or LLM involved.

### 3. Intelligence API (`src/app/api/v1/intelligence/[id]/route.ts`)

The only public gateway:
- Accepts artist ID
- Builds `UnifiedArtist` from generated data
- Runs through Feature Store → Score Engine → Insights
- Returns combined JSON response
- Cached at CDN level

### 4. Intelligence Dashboard (`src/app/dashboard/intelligence/page.tsx`)

Frontend consumer with:
- Left panel: searchable artist list with scores
- Right panel: full intelligence profile
- Score cards with expand/collapse for detail
- Insight panel with severity coloring
- Feature source quality visualization

## Rule: Frontend Never Accesses Internals

```
✅ Dashboard → Intelligence API → JSON response
❌ Dashboard → Provider API directly
❌ Dashboard → Score Engine directly
❌ Dashboard → Feature Store directly
```

## Data Flow

```
User selects artist
       │
       ▼
SWR fetches GET /api/v1/intelligence/[id]
       │
       ▼
API route builds UnifiedArtist from generated data
       │
       ▼
Feature Store ingests → quality metadata
       │
       ▼
Score Engine evaluates → 10 scores with explainability
       │
       ▼
Insight Generator → growth, risk, opportunity, achievement
       │
       ▼
Combined JSON response → Dashboard renders
```

## Validation

The product layer is verified by:

1. **Integration tests** — `test_integration.py` covering Intelligence API endpoint
2. **Score Engine tests** — 66 tests in `score-engine.test.ts`
3. **TypeScript compilation** — `tsc --noEmit` for type safety
4. **Dashboard rendering** — manual verification of all states (loading, error, empty, data)

## Future

- Add `/api/v1/intelligence/search?q=...` for search-driven intelligence
- Add historical score tracking (trending over time)
- Add comparison endpoint for benchmarking vs peers
- Add export/sharing capabilities
