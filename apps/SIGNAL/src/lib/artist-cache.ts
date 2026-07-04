// ───────────────────────────────────────────────
// ⚠️ DEPRECATED — Backward Compatibility Shim
// Please use getCacheManager() from '@/providers/cache/cache-manager'
// ───────────────────────────────────────────────

import type { SpotifyArtistData } from './spotify-service';
import { getCacheManager } from '@/providers/cache/cache-manager';

// ── Types (kept for backward compatibility) ──

export interface CachedArtist {
  key: string;
  name: string;
  spotify: SpotifyArtistData | null;
  cachedAt: number;
  expiresAt: number;
  hits: number;
}

export interface CacheStats {
  total: number;
  fresh: number;
  expired: number;
  pending: number;
  totalHits: number;
  lastClearedAt: number | null;
}

// ── Re-exports using new cache system ──

function getCache() {
  return getCacheManager();
}

export function getCachedArtist(name: string): CachedArtist | undefined {
  const cache = getCache();
  const entry = cache.get<SpotifyArtistData | null>('spotify', 'profile', name);

  if (!entry) return undefined;

  return {
    key: name.toLowerCase().trim(),
    name: entry.provider,
    spotify: entry.data
      ? {
          id: (entry.data as any).externalId ?? '',
          name: name,
          followers: 0,
          popularity: 0,
          genres: [],
          imageUrl: null,
          spotifyUrl: '',
        }
      : null,
    cachedAt: entry.cachedAt,
    expiresAt: entry.expiresAt,
    hits: entry.hits,
  };
}

export function getCachedArtists(names: string[]): Map<string, CachedArtist> {
  const results = new Map<string, CachedArtist>();
  for (const name of names) {
    const cached = getCachedArtist(name);
    if (cached) results.set(name, cached);
  }
  return results;
}

export function setCachedArtist(
  name: string,
  spotifyData: SpotifyArtistData | null
): CachedArtist {
  const cache = getCache();
  const ttl = parseInt(process.env.SPOTIFY_CACHE_TTL_HOURS || '24', 10) * 60 * 60 * 1000;

  cache.set('spotify', 'profile', name, spotifyData, ttl);

  const now = Date.now();
  return {
    key: name.toLowerCase().trim(),
    name,
    spotify: spotifyData,
    cachedAt: now,
    expiresAt: now + ttl,
    hits: 1,
  };
}

export function setCachedArtists(
  entries: Array<{ name: string; data: SpotifyArtistData | null }>
): number {
  let count = 0;
  for (const { name, data } of entries) {
    setCachedArtist(name, data);
    count++;
  }
  return count;
}

export function isFresh(entry: CachedArtist): boolean {
  return Date.now() < entry.expiresAt;
}

export function shouldRefresh(entry: CachedArtist): boolean {
  if (!isFresh(entry)) return true;
  const ttl = entry.expiresAt - entry.cachedAt;
  return (Date.now() - entry.cachedAt) > ttl / 4;
}

export function getCacheStats(): CacheStats {
  const stats = getCache().getStats();
  return {
    total: stats.total,
    fresh: stats.fresh,
    expired: stats.expired,
    pending: 0,
    totalHits: stats.totalHits,
    lastClearedAt: stats.lastClearedAt,
  };
}

export function hasFreshData(name: string): boolean {
  return getCache().has('spotify', 'profile', name);
}

export function getStaleArtistNames(names?: string[]): string[] {
  if (!names) return [];
  return getCache().getStaleIds('spotify', 'profile', names);
}

export function getAllCachedData(): Record<string, CachedArtist> {
  return {};
}

export function removeCachedArtist(name: string): boolean {
  return getCache().remove('spotify', 'profile', name);
}

export function clearCache(): void {
  getCache().clear();
}
