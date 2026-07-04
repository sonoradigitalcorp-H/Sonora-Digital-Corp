# Data Flow Architecture — SIGNAL Product Layer

```
                          ┌─────────────────────────────────────┐
                          │         Intelligence API            │
                          │   GET /api/v1/intelligence/[id]     │
                          │   THE ONLY public interface         │
                          └───────────┬─────────────────────────┘
                                      │
              ┌───────────────────────┼───────────────────────┐
              │                       │                       │
              ▼                       ▼                       ▼
     ┌────────────────┐     ┌────────────────┐      ┌──────────────────┐
     │  Feature Store  │     │  Score Engine   │      │  Insight Gen.    │
     │  (internal)     │     │  (internal)     │      │  (internal)      │
     │                 │     │                 │      │                  │
     │ • Provenance    │     │ • Momentum     │      │ • Growth signals │
     │ • Quality       │     │ • Velocity     │      │ • Risk signals   │
     │ • Freshness     │     │ • Discovery    │      │ • Opportunities  │
     │ • Metadata      │     │ • Virality     │      │ • Achievements   │
     └────────┬────────┘     │ • ...10 scores │      └──────────────────┘
              │              └────────┬───────┘
              │                       │
              └───────┬───────────────┘
                      │
                      ▼
            ┌─────────────────────┐
            │  Feature Extractor   │
            │  (only bridge)       │
            │  UnifiedArtist →     │
            │  ArtistFeatures      │
            └─────────┬───────────┘
                      │
                      ▼
            ┌─────────────────────┐
            │  Intelligence Engine│
            │  (provider merge)   │
            └─────────┬───────────┘
                      │
                      ▼
            ┌─────────────────────┐
            │  Provider Registry   │
            │  (Spotify, YouTube,  │
            │   Instagram, TikTok) │
            └─────────────────────┘
```

## Strict Layering

```
┌─────────────────────────────────────────────┐
│  🖥️  FRONTEND (Dashboard)                    │
│  • SWR → Intelligence API only               │
│  • NEVER touches providers, features, scores │
├─────────────────────────────────────────────┤
│  🌐  INTELLIGENCE API (public gateway)        │
│  • Orchestrates: FeatureStore + ScoreEngine  │
│  • + Insight Generation                      │
│  • Returns combined response                 │
├─────────────────────────────────────────────┤
│  ⚙️  FEATURE STORE (internal)                 │
│  • Ingests UnifiedArtist → FeatureMetadata[] │
│  • Tracks quality, provider, freshness       │
│  • Feeds Score Engine with ArtistFeatures    │
├─────────────────────────────────────────────┤
│  📊  SCORE ENGINE (internal)                  │
│  • 10 scores (Strategy Pattern + Template)   │
│  • Weight Config → Confidence → Reasoning    │
│  • Registry, History, Validation             │
├─────────────────────────────────────────────┤
│  🔌  PROVIDER LAYER (internal)                │
│  • IntelligenceEngine.buildArtist()          │
│  • ProviderRegistry, Cache, Failover         │
│  • DataProvider interface                    │
└─────────────────────────────────────────────┘
```

## What Goes Where

| Component | Accesses Providers? | Consumes Features? | Exposed to Frontend? |
|-----------|-------------------|-------------------|---------------------|
| Intelligence API | ❌ | ✅ (via FeatureStore) | ✅ (only interface) |
| Feature Store | ❌ | ✅ (extracts from UnifiedArtist) | ❌ |
| Score Engine | ❌ | ✅ (ArtistFeatures only) | ❌ |
| Feature Extractor | ❌ | ✅ (reads UnifiedArtist only) | ❌ |
| Insight Generator | ❌ | ✅ (features + scores) | ❌ |
| Intelligence Engine | ✅ (via providers) | ❌ | ❌ |
| Provider Registry | ✅ (manages providers) | ❌ | ❌ |
| Dashboard | ❌ | ❌ | ✅ (reads API only) |

## Data Flow Per Request

1. **Frontend** calls `GET /api/v1/intelligence/[id]` via SWR
2. **API route** resolves artist from generated data pool
3. **Converter** transforms `Artist` → `UnifiedArtist`
4. **Feature Store** ingests `UnifiedArtist` → `FeaturedArtist` with metadata
5. **Score Engine** evaluates `FeaturedArtist.raw` (ArtistFeatures) → `EngineResult`
6. **Insight Generator** produces insights from features + scores
7. **API** assembles and returns combined JSON response
