// ───────────────────────────────────────────────
// Artist Data Cache
// Persists Spotify API results to avoid rate limits
// Uses globalThis for per-instance caching
// TTL configurable via SPOTIFY_CACHE_TTL_HOURS env var
// ───────────────────────────────────────────────

import type { SpotifyArtistData } from './spotify-service';

// ── Types ──

export interface CachedArtist {
  /** Normalized artist name (lowercase) */
  key: string;
  /** Display name */
  name: string;
  /** Spotify data (null = not found on Spotify — cached to avoid re-lookup) */
  spotify: SpotifyArtistData | null;
  /** When this was cached */
  cachedAt: number;
  /** When this expires */
  expiresAt: number;
  /** Counter: how many times this entry was accessed from cache */
  hits: number;
}

export interface CacheStats {
  total: number;
  fresh: number;
  expired: number;
  pending: number;
  /** Total cache hits across all entries */
  totalHits: number;
  /** Timestamp of last cache clear */
  lastClearedAt: number | null;
}

// ── Cache Configuration ──

function getCacheTTL(): { ttl: number; refreshThreshold: number } {
  const ttlHours = parseInt(process.env.SPOTIFY_CACHE_TTL_HOURS || '24', 10);
  const ttl = ttlHours * 60 * 60 * 1000;
  const refreshThreshold = ttl / 4; // Refresh after 25% of TTL has elapsed
  return { ttl, refreshThreshold };
}

// ── Global Cache Singleton ──

declare global {
  var __artistCache: Map<string, CachedArtist> | undefined;
  var __artistCacheLastCleared: number | undefined;
}

function getCache(): Map<string, CachedArtist> {
  if (!global.__artistCache) {
    global.__artistCache = new Map();
    global.__artistCacheLastCleared = Date.now();
  }
  return global.__artistCache;
}

function getLastCleared(): number | null {
  return global.__artistCacheLastCleared ?? null;
}

// ── Cache Operations ──

/**
 * Get an artist from cache by normalized name.
 * Tracks hit count for statistics.
 */
export function getCachedArtist(name: string): CachedArtist | undefined {
  const cache = getCache();
  const entry = cache.get(normalizeKey(name));
  if (entry) {
    entry.hits = (entry.hits || 0) + 1;
  }
  return entry;
}

/**
 * Get multiple cached artists.
 */
export function getCachedArtists(names: string[]): Map<string, CachedArtist> {
  const results = new Map<string, CachedArtist>();
  for (const name of names) {
    const cached = getCachedArtist(name);
    if (cached) results.set(name, cached);
  }
  return results;
}

/**
 * Set an artist in cache.
 * Marks as not-found on Spotify when spotifyData is null (avoids re-lookup).
 */
export function setCachedArtist(
  name: string,
  spotifyData: SpotifyArtistData | null
): CachedArtist {
  const cache = getCache();
  const { ttl } = getCacheTTL();
  const now = Date.now();
  const key = normalizeKey(name);

  const existing = cache.get(key);
  const entry: CachedArtist = {
    key,
    name,
    spotify: spotifyData,
    cachedAt: now,
    expiresAt: now + ttl,
    hits: (existing?.hits || 0) + 1,
  };
  cache.set(key, entry);
  return entry;
}

/**
 * Set multiple artists in cache.
 */
export function setCachedArtists(
  entries: Array<{ name: string; data: SpotifyArtistData | null }>
): number {
  let updated = 0;
  for (const { name, data } of entries) {
    setCachedArtist(name, data);
    updated++;
  }
  return updated;
}

/**
 * Check if a cached entry is still fresh.
 */
export function isFresh(entry: CachedArtist): boolean {
  // null entries (not found on Spotify) have shorter TTL — recheck weekly
  if (entry.spotify === null) {
    const { ttl } = getCacheTTL();
    return Date.now() < entry.cachedAt + ttl;
  }
  return Date.now() < entry.expiresAt;
}

/**
 * Check if a cached entry should be refreshed (expired or old).
 */
export function shouldRefresh(entry: CachedArtist): boolean {
  if (!isFresh(entry)) return true;
  const { refreshThreshold } = getCacheTTL();
  return (Date.now() - entry.cachedAt) > refreshThreshold;
}

/**
 * Get cache statistics.
 */
export function getCacheStats(): CacheStats {
  const cache = getCache();
  const now = Date.now();
  let fresh = 0;
  let expired = 0;
  let totalHits = 0;

  for (const entry of cache.values()) {
    totalHits += entry.hits || 0;
    if (now < entry.expiresAt) fresh++;
    else expired++;
  }

  return {
    total: cache.size,
    fresh,
    expired,
    pending: 0,
    totalHits,
    lastClearedAt: getLastCleared(),
  };
}

/**
 * Check if the cache has any fresh data for a given name.
 */
export function hasFreshData(name: string): boolean {
  const entry = getCachedArtist(name);
  return entry !== undefined && isFresh(entry) && entry.spotify !== null;
}

/**
 * Get all artist names that need refresh.
 * Optionally pass a whitelist of names to check.
 */
export function getStaleArtistNames(names?: string[]): string[] {
  const cache = getCache();
  const stale: string[] = [];

  const entries = names
    ? names.map(n => ({ name: n, entry: cache.get(normalizeKey(n)) }))
    : Array.from(cache.entries()).map(([key, entry]) => ({ name: entry.name, entry }));

  for (const { name, entry } of entries) {
    if (!entry || shouldRefresh(entry)) {
      stale.push(name);
    }
  }
  return stale;
}

/**
 * Get all cached artist data as a plain object (for serialization/debugging).
 */
export function getAllCachedData(): Record<string, CachedArtist> {
  const cache = getCache();
  const obj: Record<string, CachedArtist> = {};
  for (const [key, value] of cache.entries()) {
    obj[key] = value;
  }
  return obj;
}

/**
 * Remove a specific artist from cache.
 */
export function removeCachedArtist(name: string): boolean {
  const cache = getCache();
  return cache.delete(normalizeKey(name));
}

/**
 * Clear the entire cache.
 */
export function clearCache(): void {
  global.__artistCache = new Map();
  global.__artistCacheLastCleared = Date.now();
}

// ── Helpers ──

function normalizeKey(name: string): string {
  return name.toLowerCase().trim().replace(/\s+/g, ' ');
}
