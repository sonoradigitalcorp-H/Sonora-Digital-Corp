# SIGNAL Provider System — Development Guide

---

## DataProvider Interface

Every data source must implement this contract:

```typescript
interface DataProvider {
  readonly name: string;

  initialize(): Promise<void>;
  health(): Promise<ProviderHealth>;

  searchArtist(query: string): Promise<NormalizedSearchResult[]>;
  fetchProfile(externalId: string): Promise<Partial<NormalizedProfile> | null>;
  fetchMetrics(externalId: string): Promise<Partial<NormalizedMetrics> | null>;
  fetchImages(externalId: string): Promise<Partial<NormalizedImages>>;
  fetchGenres(externalId: string): Promise<string[]>;
  fetchAlbums?(externalId: string): Promise<NormalizedAlbum[]>;

  refresh?(): Promise<void>;
  cache?(): Promise<{ hits: number; misses: number; size: number }>;
}
```

---

## Built-in Providers

### Spotify (`providers/spotify/`)

| Aspect | Detail |
|--------|--------|
| **Role** | Enrichment only |
| **Provides** | Genres, images, Spotify URL, albums |
| **Never provides** | Followers, popularity, top-tracks (removed Feb 2026) |
| **Auth** | Client Credentials (no user login) |
| **Config** | `SPOTIFY_CLIENT_ID`, `SPOTIFY_CLIENT_SECRET` |
| **Rate limit** | 200ms between requests (configurable) |
| **Requires** | Spotify Premium (Feb 2026 requirement) |

### Deezer (`providers/deezer/`)

| Aspect | Detail |
|--------|--------|
| **Role** | Image provider |
| **Provides** | Artist images (small, medium, large) |
| **Auth** | None (public API) |
| **Rate limit** | 300ms between requests |
| **Cache TTL** | 7 days (images rarely change) |

---

## Adding a New Provider

### Step 1: Create the provider file

```typescript
// src/providers/youtube/youtube-provider.ts
import { BaseProvider } from '../base-provider';
import { getCacheManager } from '../cache/cache-manager';
import type { ProviderHealth, NormalizedSearchResult, /* ... */ } from '../types';

export class YouTubeProvider extends BaseProvider {
  readonly name = 'youtube';

  constructor() {
    super({
      name: 'youtube',
      rateLimitIntervalMs: 500,
      maxRetries: 3,
      timeoutMs: 10000,
      cacheTTLMs: 6 * 60 * 60 * 1000, // 6 hours
    });
  }

  async initialize(): Promise<void> {
    // Validate API key, test connection
    this.initialized = true;
  }

  async health(): Promise<ProviderHealth> {
    // Return health check result
  }

  async searchArtist(query: string): Promise<NormalizedSearchResult[]> {
    // Search YouTube API, return normalized results
  }

  async fetchProfile(externalId: string): Promise<Partial<NormalizedProfile> | null> {
    // Fetch channel/artist profile
  }

  async fetchMetrics(externalId: string): Promise<Partial<NormalizedMetrics> | null> {
    // Fetch subscriber count, video views, etc.
  }

  async fetchImages(externalId: string): Promise<Partial<NormalizedImages>> {
    // Fetch channel thumbnail
  }

  async fetchGenres(externalId: string): Promise<string[]> {
    // Return empty array if not supported
    return [];
  }
}
```

### Step 2: Register the provider

```typescript
// In providers/registry.ts or during app initialization
import { YouTubeProvider } from './youtube/youtube-provider';

const registry = getProviderRegistry();
registry.register(new YouTubeProvider());
await registry.initializeAll();
```

### Step 3: Export from barrel

```typescript
// In providers/index.ts
export { YouTubeProvider, getYouTubeProvider } from './youtube/youtube-provider';
```

---

## Provider Best Practices

1. **Use `BaseProvider`** — it provides retry logic, rate limiting, timeout handling, and logging for free.

2. **Cache aggressively** — Use `getCacheManager()` for all external API results. Set appropriate TTLs based on data volatility.

3. **Never block on provider failure** — The Intelligence Engine handles partial failures gracefully.

4. **Return normalized types** — Every provider must return `NormalizedProfile`, `NormalizedMetrics`, etc. Never return raw API types.

5. **Handle rate limits** — 429 responses are automatically retried with exponential backoff via `BaseProvider.request()`.

6. **Log providerately** — Use `this.log()` for all logging. It includes provider name and timestamp.

7. **Keep singleton pattern** — Use the `getXProvider()` pattern for singleton access.

---

## Configuration

Providers read configuration from environment variables:

```bash
# Spotify
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
SPOTIFY_REQUEST_TIMEOUT=10000
SPOTIFY_RATE_LIMIT_INTERVAL=200
SPOTIFY_MAX_RETRIES=3
SPOTIFY_TOKEN_BUFFER=300000
SPOTIFY_CACHE_TTL_HOURS=24
```

---

## Health Checks

Each provider exposes a `health()` method. The registry runs periodic health checks every 5 minutes.

```typescript
const registry = getProviderRegistry();
const health = await registry.healthAll();
// Returns: [{ name: 'spotify', status: 'healthy', ... }, ...]
```

Unhealthy providers are automatically flagged. The `GET /api/v1/artists/refresh` endpoint exposes provider health status.
