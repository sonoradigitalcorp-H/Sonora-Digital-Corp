// ───────────────────────────────────────────────
// Deezer Image Provider
// Public API — no API key needed
// Provides: artist images at multiple sizes
// ───────────────────────────────────────────────

import { BaseProvider } from '../base-provider';
import { getCacheManager } from '../cache/cache-manager';
import type {
  ProviderHealth,
  NormalizedSearchResult,
  NormalizedProfile,
  NormalizedMetrics,
  NormalizedImages,
} from '../types';

const DEEZER_API_BASE = 'https://api.deezer.com';

// ── Internal Types ──

interface DeezerArtistResult {
  id: number;
  name: string;
  picture_small?: string;
  picture_medium?: string;
  picture_big?: string;
  picture_xl?: string;
  tracklist?: string;
  type?: string;
}

interface DeezerSearchResponse {
  data?: DeezerArtistResult[];
}

// ── Provider ──

export class DeezerProvider extends BaseProvider {
  readonly name = 'deezer';

  constructor() {
    super({
      name: 'deezer',
      rateLimitIntervalMs: 300, // Deezer is more restrictive
      maxRetries: 2,
      timeoutMs: 5000,
      cacheTTLMs: 7 * 24 * 60 * 60 * 1000, // 7 days (images rarely change)
    });
  }

  async initialize(): Promise<void> {
    // Deezer is a public API — no auth needed
    this.initialized = true;
    this.log('info', 'Deezer provider initialized');
  }

  async health(): Promise<ProviderHealth> {
    const start = Date.now();

    try {
      const result = await this.request<{ data?: unknown[] }>(
        `${DEEZER_API_BASE}/search/artist?q=test&limit=1`,
        { headers: { Accept: 'application/json' } }
      );

      if (!result.ok) {
        return this.buildHealthResult(
          'degraded',
          `Deezer API error: ${result.error}`,
          Date.now() - start,
          true,
          null
        );
      }

      return this.buildHealthResult('healthy', 'Deezer API operational', Date.now() - start, true, null);
    } catch (error) {
      return this.buildHealthResult(
        'unhealthy',
        error instanceof Error ? error.message : String(error),
        Date.now() - start,
        true,
        null
      );
    }
  }

  async searchArtist(query: string): Promise<NormalizedSearchResult[]> {
    const cache = getCacheManager();
    const cacheKey = `search:${query.toLowerCase().trim()}`;
    const cached = cache.get<NormalizedSearchResult[]>('deezer', 'search', cacheKey);
    if (cached && cache.isFresh(cached)) {
      return cached.data;
    }

    const result = await this.request<DeezerSearchResponse>(
      `${DEEZER_API_BASE}/search/artist?q=${encodeURIComponent(query)}&limit=5&order=RATING_DESC`,
      { headers: { Accept: 'application/json' } }
    );

    if (!result.ok || !result.data?.data) {
      return [];
    }

    const searchResults: NormalizedSearchResult[] = result.data.data.map((item, index) => ({
      externalId: String(item.id),
      name: item.name,
      genres: [],
      imageUrl: item.picture_medium ?? null,
      matchScore: Math.max(0, 100 - index * 20),
      provider: 'deezer',
    }));

    cache.set('deezer', 'search', cacheKey, searchResults, 60 * 60 * 1000);
    return searchResults;
  }

  async fetchProfile(externalId: string): Promise<Partial<NormalizedProfile> | null> {
    const cache = getCacheManager();
    const cached = cache.get<Partial<NormalizedProfile>>('deezer', 'profile', externalId);
    if (cached && cache.isFresh(cached)) {
      return cached.data;
    }

    const result = await this.request<DeezerArtistResult>(
      `${DEEZER_API_BASE}/artist/${externalId}`,
      { headers: { Accept: 'application/json' } }
    );

    if (!result.ok || !result.data) return null;

    const profile: Partial<NormalizedProfile> = {
      externalId: String(result.data.id),
      name: result.data.name,
      bio: null,
      genres: [],
      country: null,
      city: null,
      profileUrl: `https://www.deezer.com/artist/${result.data.id}`,
      provider: 'deezer',
    };

    cache.set('deezer', 'profile', externalId, profile, this.config.cacheTTLMs);
    return profile;
  }

  async fetchMetrics(_externalId: string): Promise<Partial<NormalizedMetrics> | null> {
    // Deezer API doesn't expose metrics easily via public API
    return null;
  }

  async fetchImages(externalId: string): Promise<Partial<NormalizedImages>> {
    const cache = getCacheManager();
    const cacheKey = `images:${externalId}`;
    const cached = cache.get<Partial<NormalizedImages>>('deezer', 'images', cacheKey);
    if (cached && cache.isFresh(cached)) {
      return cached.data;
    }

    const result = await this.request<DeezerArtistResult>(
      `${DEEZER_API_BASE}/artist/${externalId}`,
      { headers: { Accept: 'application/json' } }
    );

    if (!result.ok || !result.data) {
      return { externalId, small: null, medium: null, large: null, provider: 'deezer' };
    }

    const normalized: Partial<NormalizedImages> = {
      externalId,
      small: result.data.picture_small ?? null,
      medium: result.data.picture_medium ?? null,
      large: result.data.picture_big ?? result.data.picture_xl ?? null,
      provider: 'deezer',
    };

    cache.set('deezer', 'images', cacheKey, normalized, this.config.cacheTTLMs);
    return normalized;
  }

  async fetchGenres(_externalId: string): Promise<string[]> {
    // Deezer doesn't expose genres via artist endpoint
    return [];
  }

  async refresh(): Promise<void> {
    this.log('info', 'Refreshing Deezer provider');
    getCacheManager().removeByProvider('deezer');
  }

  async cache(): Promise<{ hits: number; misses: number; size: number }> {
    const stats = getCacheManager().getStats();
    const deezerStats = stats.byProvider['deezer'];
    return {
      hits: deezerStats?.hits ?? 0,
      misses: deezerStats?.misses ?? 0,
      size: deezerStats?.entries ?? 0,
    };
  }
}

// ── Image Search Convenience ──
// Allows searching for images by artist name (not just by Deezer ID)

export async function fetchArtistImageByName(artistName: string): Promise<Partial<NormalizedImages>> {
  const provider = getDeezerProvider();
  const results = await provider.searchArtist(artistName);

  if (results.length === 0) {
    return { externalId: '', small: null, medium: null, large: null, provider: 'deezer' };
  }

  return provider.fetchImages(results[0].externalId);
}

export async function fetchAllArtistImagesByName(
  names: string[]
): Promise<Map<string, Partial<NormalizedImages>>> {
  const results = new Map<string, Partial<NormalizedImages>>();

  // Process in batches of 5
  const batchSize = 5;
  for (let i = 0; i < names.length; i += batchSize) {
    const batch = names.slice(i, i + batchSize);
    const batchResults = await Promise.allSettled(
      batch.map(async (name) => {
        const images = await fetchArtistImageByName(name);
        return { name, images };
      })
    );

    for (const result of batchResults) {
      if (result.status === 'fulfilled') {
        results.set(result.value.name, result.value.images);
      }
    }

    // Rate limiting delay
    if (i + batchSize < names.length) {
      await new Promise(resolve => setTimeout(resolve, 300));
    }
  }

  return results;
}

// ── Singleton ──

let instance: DeezerProvider | null = null;

export function getDeezerProvider(): DeezerProvider {
  if (!instance) {
    instance = new DeezerProvider();
  }
  return instance;
}
