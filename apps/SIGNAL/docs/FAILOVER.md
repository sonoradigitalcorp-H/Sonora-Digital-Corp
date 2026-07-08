# SIGNAL Failover Architecture

> **Design Principle:** No single provider failure should crash the application or produce an invalid artist object.

---

## Architecture

```
                    ┌─────────────────────┐
                    │   Intelligence      │
                    │     Engine          │
                    │  (orchestrates)     │
                    └─────────┬───────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
        ┌─────▼────┐   ┌─────▼────┐   ┌─────▼────┐
        │ Spotify  │   │ YouTube  │   │ TikTok   │
        │ Provider │   │ Provider │   │ Provider │
        └──────────┘   └──────────┘   └──────────┘
              │               │               │
        ┌─────▼────┐   ┌─────▼────┐   ┌─────▼────┐
        │  Cache   │   │  Cache   │   │  Cache   │
        └──────────┘   └──────────┘   └──────────┘
```

## Failover Layers

### Layer 1: Provider Isolation

Each provider is an independent `DataProvider` implementation. Failures are contained:

- **Initialization failure**: One provider failing `initialize()` does not prevent others from initializing
- **Runtime failure**: One provider throwing in `searchArtist()`, `fetchProfile()`, etc. does not affect other providers
- **Provider unregistration**: Removing a provider mid-operation doesn't crash remaining operations

### Layer 2: Error Absorption

The Intelligence Engine wraps every provider call in try-catch:

```typescript
try {
  const results = await provider.searchArtist(query);
  return results;
} catch (error) {
  // Log but don't crash
  this.log('warn', `Provider search failed: ${provider.name}`, { error });
  return [];
}
```

Errors are collected into the `IntelligenceResult.errors` array with `recoverable: true`.

### Layer 3: Graceful Degradation

| Scenario | Behavior | User Impact |
|----------|----------|-------------|
| All providers fail | Returns low confidence, empty/null data | Artist shows with no enrichment |
| Some providers fail | Returns data from working providers | Partial enrichment |
| Spotify disabled | YouTube/Instagram/TikTok still provide data | Less genres and albums |
| YouTube disabled | Other providers fill metrics | No video data |
| Instagram disabled | Other providers fill profile | No Instagram metrics |
| TikTok disabled | Other providers fill profile | No TikTok data |
| All disabled | Falls back to generated data | Base artist only |

### Layer 4: Cache Persistence

The in-memory cache persists across provider failures:

- Cached data remains retrievable even when the provider is down
- `shouldRefresh()` detects stale entries (past 25% of TTL) and triggers refresh
- `isFresh()` correctly identifies expired entries

### Layer 5: Registry Robustness

```typescript
// Mutex pattern prevents race conditions
async initializeAll(): Promise<{ success: string[]; failed: string[] }> {
  if (this.initPromise) return this.initPromise; // Dedup concurrent calls
  this.initPromise = this._initializeAll();
  return this.initPromise;
}
```

## Failover Test Scenarios (53 tests)

| Category | Test | Validation |
|----------|------|------------|
| **All disabled** | search returns empty | ✅ |
| **All disabled** | buildArtist returns low confidence, empty sources | ✅ |
| **Partial disable** | Only YouTube enabled builds valid artist | ✅ |
| **All fail search** | search returns empty array, no crash | ✅ |
| **All fail build** | buildArtist returns low confidence, errors collected | ✅ |
| **Mixed failures** | search returns partial results | ✅ |
| **Mixed failures** | merged result valid with data from working providers | ✅ |
| **Unregister** | search works after removing a provider | ✅ |
| **Unregister** | healthAll works after removing all | ✅ |
| **Unregister** | buildArtist works after removing a provider | ✅ |
| **No providers** | search returns empty array | ✅ |
| **No providers** | health returns unhealthy | ✅ |
| **Health degraded** | mixed healthy/degraded/unhealthy reported correctly | ✅ |
| **Error isolation** | one provider throwing doesn't prevent others | ✅ |
| **Partial init** | failed init providers don't block successful ones | ✅ |
| **Cache survival** | cached data retrievable when provider is down | ✅ |
| **Double registration** | replacing provider doesn't increase registry size | ✅ |

## Implementation Details

### BaseProvider Error Handling

```typescript
// Retries with exponential backoff + jitter
const delay = Math.min(30000,
  options.baseDelayMs * Math.pow(2, attempt) + Math.random() * 1000
);
```

### Intelligence Engine Error Absorption

```typescript
// Every provider call is independently caught
const errors: IntelligenceError[] = [];
// ... for each provider operation:
try { /* provider call */ }
catch (error) {
  errors.push({ provider, error, recoverable: true });
}
// Result always returned, even with errors
```

### Cache Layer Resilience

```typescript
// Cached data is always returned regardless of provider status
const cached = cache.get(provider, type, key);
if (cached && cache.isFresh(cached)) return cached.data;
// Only if no cached data, fall through to provider call
```

## Metrics

- **Recovery time**: Sub-second (immediate fallback to next provider)
- **Degradation granularity**: Per-provider, per-field
- **Failure detection**: Health checks every 5 minutes (configurable)
- **Cache TTL**: 24h default (configurable per provider)
