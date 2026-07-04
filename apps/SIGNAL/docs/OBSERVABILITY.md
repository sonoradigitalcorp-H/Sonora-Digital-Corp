# SIGNAL Observability Architecture

> **Design Principle:** Every provider operation must be measurable, and every failure must be observable.

---

## 1. Structured Logging

### Format

All logs are JSON-structured for ingestion by log aggregators (CloudWatch, DataDog, Loki, etc.):

```json
{
  "timestamp": "2026-07-04T22:20:35.055Z",
  "level": "info",
  "service": "provider",
  "provider": "spotify",
  "message": "Spotify provider initialized successfully"
}
```

### Log Levels

| Level | Usage | Output |
|-------|-------|--------|
| `debug` | Development details only | Console.debug (dev only) |
| `info` | Normal operations | Console.log |
| `warn` | Degraded behavior | Console.warn |
| `error` | Failures requiring attention | Console.error |

### Log Sources

| Logger | Service Tag | Location |
|--------|-------------|----------|
| `logProvider()` | `provider` | `base-provider.ts` |
| `StructuredLogger` | Configurable | `lib/observability.ts` |
| Intelligence Engine | `Intelligence` | `intelligence/engine.ts` |
| Registry | `registry` | `registry.ts` |

---

## 2. Provider Latency Tracking

### Data Collection

Every provider HTTP request through `BaseProvider.request()` is automatically tracked:

```typescript
recordProviderLatency(this.name, operation, durationMs, success);
```

### Storage

Up to 1000 latency entries are kept in memory (ring buffer pattern).

### Statistics

The `getProviderLatencyStats()` function computes:

| Metric | Description |
|--------|-------------|
| `totalCalls` | Total operations for this provider |
| `successCalls` | Successful operations count |
| `failedCalls` | Failed operations count |
| `avgLatencyMs` | Average response time |
| `p50Ms` | Median response time |
| `p95Ms` | 95th percentile response time |
| `p99Ms` | 99th percentile response time |

---

## 3. Correlation IDs

### Generation

```typescript
generateCorrelationId() // → "sig-lxj3m-a1b2c3-1"
```

Format: `sig-{timestamp_base36}-{random}-{counter}`

### Usage

Correlation IDs can be passed through multi-step operations to trace requests across providers. The ID format is URL-safe and sortable.

---

## 4. Health Endpoint

### `GET /api/v1/health`

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2026-07-04T22:20:35.055Z",
  "uptime": 3600,
  "checks": {
    "providers": {
      "status": "healthy",
      "message": "5/5 providers healthy"
    },
    "cache": {
      "status": "healthy",
      "message": "42 entries, 156 hits, 12 misses"
    }
  },
  "cache": {
    "entries": 42,
    "hits": 156,
    "misses": 12
  },
  "registry": {
    "size": 5,
    "initialized": true,
    "providerNames": ["spotify", "deezer", "youtube", "instagram", "tiktok"]
  },
  "latency": {
    "spotify": {
      "totalCalls": 10,
      "successCalls": 8,
      "failedCalls": 2,
      "avgLatencyMs": 245,
      "p50Ms": 200,
      "p95Ms": 500,
      "p99Ms": 800
    }
  }
}
```

### Status Codes

| Status | HTTP Code | Meaning |
|--------|-----------|---------|
| `healthy` | 200 | All subsystems operational |
| `degraded` | 200 | Some subsystems degraded |
| `unhealthy` | 503 | Critical subsystems unavailable |

---

## 5. Provider Dashboard

### `GET /api/v1/providers`

Returns per-provider:

| Field | Description |
|-------|-------------|
| `name` | Provider identifier |
| `status` | healthy / degraded / unhealthy |
| `message` | Human-readable status |
| `configured` | Whether credentials are set |
| `configurationError` | Specific config error |
| `latencyMs` | Last health check latency |
| `lastChecked` | ISO timestamp |
| `cache` | Entries, hits, misses per provider |
| `capabilities` | Feature list (genres, images, etc.) |

### Provider Dashboard UI

Located at `/providers` in the SIGNAL web app:

- Color-coded status cards per provider
- Expandable detail panel
- Auto-refresh every 30 seconds
- Summary badges (total healthy / degraded / unhealthy)
- Cache statistics

---

## 6. Key Metrics to Monitor

| Metric | Where | Alert Threshold |
|--------|-------|-----------------|
| Provider health status | `/api/v1/health` → checks.providers | Any unhealthy >5min |
| Cache hit rate | CacheStats → totalHits / (totalHits + totalMisses) | < 60% |
| Provider latency p95 | `getProviderLatencyStats()` | > 5s |
| Failed provider calls | Latency stats → failedCalls | > 10% of total |
| Registry initialization | registry.initialized | false after 30s startup |
| Cache size | cache.entries | > 10000 (memory warning) |

---

## 7. StructuredLogger Usage

```typescript
import { StructuredLogger } from '@/lib/observability';

const logger = new StructuredLogger('my-service');

logger.info('Operation completed', { operation: 'sync', durationMs: 150 });
logger.warn('Degraded performance', { provider: 'spotify', latencyMs: 5000 });
logger.error('Failed to connect', {
  provider: 'youtube',
  error: 'API key not configured',
  correlationId: 'sig-abc-123'
});

// Timed operations
const result = await logger.timed('data-fetch', async () => {
  return await fetchData();
}, { source: 'api' });
```
