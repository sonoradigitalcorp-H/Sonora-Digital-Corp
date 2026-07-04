// ───────────────────────────────────────────────
// Spotify Enrichment Provider
// ⚠️ Feb 2026: enrichment-only — no followers/popularity/top-tracks
// Provides: genres, image, spotify URL, spotify ID, albums
// ───────────────────────────────────────────────

import { BaseProvider } from '../base-provider';
import { getAccessToken, validateCredentials, isConfigured, getTokenStatus, clearTokenCache as clearAuthTokenCache } from './spotify-auth';
import { getCacheManager } from '../cache/cache-manager';
import type {
  ProviderHealth,
  NormalizedSearchResult,
  NormalizedProfile,
  NormalizedMetrics,
  NormalizedImages,
  NormalizedAlbum,
} from '../types';

const SPOTIFY_API_BASE = 'https://api.spotify.com/v1';

// ── Internal Types ──

interface SpotifyArtistRaw {
  id: string;
  name: string;
  genres: string[];
  images?: Array<{ url: string; width?: number; height?: number }>;
  external_urls?: { spotify?: string };
  followers?: { total: number };
  popularity?: number;
}

interface SpotifyAlbumRaw {
  id: string;
  name: string;
  release_date?: string;
  images?: Array<{ url: string }>;
  total_tracks?: number;
  album_type?: 'album' | 'single' | 'compilation';
  external_urls?: { spotify?: string };
}

interface SpotifySearchResponse {
  artists?: {
    items?: SpotifyArtistRaw[];
  };
}

interface SpotifyAlbumsResponse {
  items?: SpotifyAlbumRaw[];
}

// ── Provider ──

export class SpotifyProvider extends BaseProvider {
  readonly name = 'spotify';

  constructor() {
    super({
      name: 'spotify',
      rateLimitIntervalMs: parseInt(process.env.SPOTIFY_RATE_LIMIT_INTERVAL || '200', 10),
      maxRetries: parseInt(process.env.SPOTIFY_MAX_RETRIES || '3', 10),
      timeoutMs: parseInt(process.env.SPOTIFY_REQUEST_TIMEOUT || '10000', 10),
      cacheTTLMs: parseInt(process.env.SPOTIFY_CACHE_TTL_HOURS || '24', 10) * 60 * 60 * 1000,
    });
  }

  async initialize(): Promise<void> {
    const validationError = validateCredentials();
    if (validationError) {
      this.log('warn', 'Spotify provider not configured', { error: validationError });
      this.initialized = false;
      return;
    }

    // Try to get a token to verify connectivity
    try {
      const token = await getAccessToken();
      if (token) {
        this.initialized = true;
        this.log('info', 'Spotify provider initialized successfully');
      }
    } catch (error) {
      this.log('error', 'Spotify provider initialization failed', {
        error: error instanceof Error ? error.message : String(error),
      });
      this.initialized = false;
    }
  }

  async health(): Promise<ProviderHealth> {
    const start = Date.now();
    const configured = isConfigured();
    const validationError = validateCredentials();

    if (!configured) {
      return this.buildHealthResult('unhealthy', 'Spotify not configured', Date.now() - start, false, validationError);
    }

    try {
      const token = await getAccessToken();
      if (!token) {
        return this.buildHealthResult('degraded', 'Failed to obtain token', Date.now() - start, true, null);
      }

      // Quick API test
      const result = await this.request<{ limit: number }>(`${SPOTIFY_API_BASE}/search?q=test&type=artist&limit=1`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (!result.ok) {
        return this.buildHealthResult(
          'degraded',
          `API error: ${result.error}`,
          Date.now() - start,
          true,
          null
        );
      }

      return this.buildHealthResult('healthy', 'Spotify API operational', Date.now() - start, true, null);
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
    const cached = cache.get<NormalizedSearchResult[]>('spotify', 'search', cacheKey);
    if (cached && cache.isFresh(cached)) {
      return cached.data;
    }

    const token = await getAccessToken();
    if (!token) return [];

    const result = await this.request<SpotifySearchResponse>(
      `${SPOTIFY_API_BASE}/search?q=${encodeURIComponent(query)}&type=artist&limit=5`,
      { headers: { Authorization: `Bearer ${token}` } }
    );

    if (!result.ok || !result.data?.artists?.items) {
      cache.set('spotify', 'search', cacheKey, [], 5 * 60 * 1000); // Cache empty for 5 min
      return [];
    }

    const items = result.data.artists.items;
    const searchResults: NormalizedSearchResult[] = items.map((item, index) => ({
      externalId: item.id,
      name: item.name,
      genres: item.genres ?? [],
      imageUrl: item.images?.[0]?.url ?? null,
      matchScore: Math.max(0, 100 - index * 20),
      provider: 'spotify',
    }));

    // Cache for 1 hour (search results change slowly)
    cache.set('spotify', 'search', cacheKey, searchResults, 60 * 60 * 1000);
    return searchResults;
  }

  async fetchProfile(externalId: string): Promise<Partial<NormalizedProfile> | null> {
    const cache = getCacheManager();
    const cached = cache.get<Partial<NormalizedProfile>>('spotify', 'profile', externalId);
    if (cached && cache.isFresh(cached)) {
      return cached.data;
    }

    const token = await getAccessToken();
    if (!token) return null;

    const result = await this.request<SpotifyArtistRaw>(
      `${SPOTIFY_API_BASE}/artists/${externalId}`,
      { headers: { Authorization: `Bearer ${token}` } }
    );

    if (!result.ok || !result.data) return null;

    const raw = result.data;
    const profile: Partial<NormalizedProfile> = {
      externalId: raw.id,
      name: raw.name,
      bio: null, // Spotify API doesn't provide bios via Web API
      genres: raw.genres ?? [],
      country: null,
      city: null,
      profileUrl: raw.external_urls?.spotify ?? `https://open.spotify.com/artist/${raw.id}`,
      provider: 'spotify',
    };

    cache.set('spotify', 'profile', externalId, profile, this.config.cacheTTLMs);
    return profile;
  }

  async fetchMetrics(_externalId: string): Promise<Partial<NormalizedMetrics> | null> {
    // ⚠️ Feb 2026: followers and popularity REMOVED from Spotify API.
    // This provider intentionally returns null for metrics.
    // SIGNAL uses generated metrics based on actual tier estimates.
    return null;
  }

  async fetchImages(externalId: string): Promise<Partial<NormalizedImages>> {
    const cache = getCacheManager();
    const cacheKey = `images:${externalId}`;
    const cached = cache.get<Partial<NormalizedImages>>('spotify', 'images', cacheKey);
    if (cached && cache.isFresh(cached)) {
      return cached.data;
    }

    const token = await getAccessToken();
    if (!token) return { externalId, small: null, medium: null, large: null, provider: 'spotify' };

    const result = await this.request<SpotifyArtistRaw>(
      `${SPOTIFY_API_BASE}/artists/${externalId}`,
      { headers: { Authorization: `Bearer ${token}` } }
    );

    if (!result.ok || !result.data?.images) {
      return { externalId, small: null, medium: null, large: null, provider: 'spotify' };
    }

    const images = result.data.images;
    // Spotify returns images in order: largest first
    const large = images[0]?.url ?? null;
    const medium = images[Math.min(1, images.length - 1)]?.url ?? large;
    const small = images[images.length - 1]?.url ?? medium;

    const normalized: Partial<NormalizedImages> = {
      externalId,
      small,
      medium,
      large,
      provider: 'spotify',
    };

    cache.set('spotify', 'images', cacheKey, normalized, this.config.cacheTTLMs);
    return normalized;
  }

  async fetchGenres(externalId: string): Promise<string[]> {
    const cache = getCacheManager();
    const cacheKey = `genres:${externalId}`;
    const cached = cache.get<string[]>('spotify', 'genres', cacheKey);
    if (cached && cache.isFresh(cached)) {
      return cached.data;
    }

    const token = await getAccessToken();
    if (!token) return [];

    const result = await this.request<SpotifyArtistRaw>(
      `${SPOTIFY_API_BASE}/artists/${externalId}`,
      { headers: { Authorization: `Bearer ${token}` } }
    );

    if (!result.ok || !result.data) return [];

    const genres = result.data.genres ?? [];
    cache.set('spotify', 'genres', cacheKey, genres, this.config.cacheTTLMs);
    return genres;
  }

  async fetchAlbums(externalId: string): Promise<NormalizedAlbum[]> {
    const cache = getCacheManager();
    const cacheKey = `albums:${externalId}`;
    const cached = cache.get<NormalizedAlbum[]>('spotify', 'albums', cacheKey);
    if (cached && cache.isFresh(cached)) {
      return cached.data;
    }

    const token = await getAccessToken();
    if (!token) return [];

    const result = await this.request<SpotifyAlbumsResponse>(
      `${SPOTIFY_API_BASE}/artists/${externalId}/albums?include_groups=album,single&limit=10`,
      { headers: { Authorization: `Bearer ${token}` } }
    );

    if (!result.ok || !result.data?.items) return [];

    const albums: NormalizedAlbum[] = result.data.items.map((item) => ({
      externalId: item.id,
      title: item.name,
      releaseDate: item.release_date ?? null,
      imageUrl: item.images?.[0]?.url ?? null,
      trackCount: item.total_tracks ?? null,
      albumType: (item.album_type as NormalizedAlbum['albumType']) ?? 'unknown',
      provider: 'spotify',
    }));

    cache.set('spotify', 'albums', cacheKey, albums, this.config.cacheTTLMs);
    return albums;
  }

  async refresh(): Promise<void> {
    this.log('info', 'Refreshing Spotify provider');
    clearTokenCache();
    await this.initialize();
  }

  async cache(): Promise<{ hits: number; misses: number; size: number }> {
    const stats = getCacheManager().getStats();
    const spotifyStats = stats.byProvider['spotify'];
    return {
      hits: spotifyStats?.hits ?? 0,
      misses: 0,
      size: spotifyStats?.entries ?? 0,
    };
  }
}

// ── Token Cache Control ──

function clearTokenCache(): void {
  clearAuthTokenCache();
}

// ── Singleton ──

let instance: SpotifyProvider | null = null;

export function getSpotifyProvider(): SpotifyProvider {
  if (!instance) {
    instance = new SpotifyProvider();
  }
  return instance;
}
