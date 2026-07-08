# SIGNAL Architecture — Provider-Based Music Intelligence Platform

> **Version**: 3.0  
> **Status**: Production  
> **Last Updated**: July 2026

---

## Architecture Overview

SIGNAL has been refactored from a monolithic data layer into an **enterprise provider-based architecture**. Every external data source is a pluggable `DataProvider` implementing a standard interface. The **Intelligence Engine** orchestrates providers, normalizes their output, and produces unified `Artist` objects.

```
┌─────────────────────────────────────────────────────────┐
│                    HTTP API Layer                         │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │ /v1/artists  │  │ /v1/refresh  │  │ future: /v1/*  │  │
│  └──────┬───────┘  └──────┬───────┘  └────────────────┘  │
└─────────┼─────────────────┼──────────────────────────────┘
          │                 │
┌─────────▼─────────────────▼──────────────────────────────┐
│              Intelligence Engine                          │
│  ┌────────────────────────────────────────────────────┐   │
│  │  - search(query) → NormalizedSearchResult[]        │   │
│  │  - buildArtist(id, name) → UnifiedArtist           │   │
│  │  - refreshArtist(id, name) → void                  │   │
│  │  - health() → system health report                 │   │
│  └──────────────┬─────────────────────────────────────┘   │
└─────────────────┼─────────────────────────────────────────┘
                  │
┌─────────────────▼─────────────────────────────────────────┐
│              Provider Registry (DI Container)              │
│  ┌─────────────┐  ┌─────────────┐  ┌───────────────────┐  │
│  │  Spotify     │  │  Deezer     │  │  Future Providers │  │
│  │  Provider    │  │  Provider   │  │  (YouTube, IG,    │  │
│  │  (enrichment)│  │  (images)   │  │   TikTok, etc.)   │  │
│  └──────┬───────┘  └──────┬──────┘  └───────────────────┘  │
└─────────┼─────────────────┼────────────────────────────────┘
          │                 │
┌─────────▼─────────────────▼────────────────────────────────┐
│                    Cache Manager                            │
│  (globalThis Map, TTL-based, per-provider stats)           │
└────────────────────────────────────────────────────────────┘
          │
┌─────────▼────────────────────────────────────────────────┐
│                    Data Sources                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐               │
│  │ Spotify  │  │ Deezer   │  │ Generated│               │
│  │ Web API  │  │ Public   │  │ Fallback │               │
│  │          │  │ API      │  │ (seed)   │               │
│  └──────────┘  └──────────┘  └──────────┘               │
└──────────────────────────────────────────────────────────┘
```

---

## Directory Structure

```
src/
├── providers/                    # Provider System (NEW)
│   ├── types.ts                  # Core interfaces & schemas
│   ├── base-provider.ts          # Abstract base with retry/rate-limit
│   ├── registry.ts               # ProviderRegistry (DI container)
│   ├── index.ts                  # Public API barrel
│   ├── spotify/
│   │   ├── spotify-auth.ts       # Auth (extracted from old spotify-service)
│   │   └── spotify-provider.ts   # Enrichment-only Spotify provider
│   ├── deezer/
│   │   └── deezer-provider.ts    # Image-focused Deezer provider
│   ├── intelligence/
│   │   ├── engine.ts             # Orchestrator: build unified Artist
│   │   └── merger.ts             # Merge partial data from providers
│   ├── cache/
│   │   └── cache-manager.ts      # Enterprise cache (replaces artist-cache)
│   └── jobs/
│       └── job-manager.ts        # Background job system
├── lib/                          # Legacy layer (backward compat shims)
│   ├── spotify-service.ts        # NOW: re-exports from providers/
│   ├── artist-cache.ts           # NOW: re-exports from providers/cache
│   ├── artist-images.ts          # NOW: re-exports from providers/deezer
│   ├── data-generator.ts         # UNCHANGED (seed data backbone)
│   ├── chat-knowledge.ts         # UNCHANGED
│   └── report-pdf.tsx            # UNCHANGED
├── app/api/v1/artists/
│   ├── route.ts                  # UPDATED: uses Intelligence Engine
│   └── refresh/
│       └── route.ts              # UPDATED: uses Job Manager
└── docs/                         # Documentation
    ├── ARCHITECTURE.md           # THIS FILE
    ├── PROVIDERS.md              # Provider development guide
    └── NORMALIZATION.md          # Data normalization schemas
```

---

## Data Flow

```
Request → GET /api/v1/artists
                │
                ▼
        1. registerDefaultProviders()  ← lazy init
                │
                ▼
        2. generateArtists()           ← seed data (metrics backbone)
                │
                ▼
        3. Intelligence.search(name)   ← searches Spotify + Deezer
                │
                ▼
        4. Intelligence.buildArtist()  ← fetchProfile + fetchImages
                │
                ▼
        5. Merge provider data         ← genres, photoUrl, external IDs
                │
                ▼
        6. Deezer image fill           ← for artists without Spotify photos
                │
                ▼
        7. Return unified Artist[]
```

---

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Provider per external source** | Easy to add/remove data sources; single responsibility |
| **Intelligence Engine orchestrates** | Centralized merge logic, confidence scoring, error handling |
| **Generated data as backbone** | Metrics are always available even when providers fail |
| **Spotify = enrichment only** | Feb 2026 API changes removed followers/popularity/top-tracks |
| **Cache Manager (globalThis)** | Survives hot reloads; per-provider stats; TTL-based |
| **Backward-compat shims in lib/** | Existing UI components import without changes |
| **DI through ProviderRegistry** | Providers are singletons; health checks run periodically |
| **Background jobs** | Refresh and invalidation without blocking API responses |
