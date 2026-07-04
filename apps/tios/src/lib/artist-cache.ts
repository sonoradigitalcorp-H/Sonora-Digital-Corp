// ───────────────────────────────────────────────
// Artist Data Cache
// Persists Spotify API results to avoid rate limits
// Uses globalThis for per-instance caching
// ───────────────────────────────────────────────

import type { SpotifyArtistData } from './spotify-service';

// ── Types ──

export interface CachedArtist {
  /** Normalized artist name (lowercase) */
  key: string;
  /** Display name */
  name: string;
  /** Spotify data (null = not found on Spotify) */
  spotify: SpotifyArtistData | null;
  /** When this was cached */
  cachedAt: number;
  /** When this expires */
  expiresAt: number;
}

export interface CacheStats {
  total: number;
  fresh: number;
  expired: number;
  pending: number;
}

// ── Cache Configuration ──

const CACHE_TTL_MS = 24 * 60 * 60 * 1000; // 24 hours
const REFRESH_THRESHOLD_MS = 6 * 60 * 60 * 1000; // Refresh after 6 hours

// ── Global Cache Singleton ──

declare global {
  var __artistCache: Map<string, CachedArtist> | undefined;
}

function getCache(): Map<string, CachedArtist> {
  if (!global.__artistCache) {
    global.__artistCache = new Map();
  }
  return global.__artistCache;
}

// ── Cache Operations ──

/**
 * Get an artist from cache by normalized name.
 */
export function getCachedArtist(name: string): CachedArtist | undefined {
  const cache = getCache();
  return cache.get(normalizeKey(name));
}

/**
 * Get multiple cached artists.
 */
export function getCachedArtists(names: string[]): Map<string, CachedArtist> {
  const cache = getCache();
  const results = new Map<string, CachedArtist>();
  for (const name of names) {
    const cached = cache.get(normalizeKey(name));
    if (cached) results.set(name, cached);
  }
  return results;
}

/**
 * Set an artist in cache.
 */
export function setCachedArtist(
  name: string,
  spotifyData: SpotifyArtistData | null
): CachedArtist {
  const cache = getCache();
  const now = Date.now();
  const entry: CachedArtist = {
    key: normalizeKey(name),
    name,
    spotify: spotifyData,
    cachedAt: now,
    expiresAt: now + CACHE_TTL_MS,
  };
  cache.set(entry.key, entry);
  return entry;
}

/**
 * Set multiple artists in cache.
 */
export function setCachedArtists(
  entries: Array<{ name: string; data: SpotifyArtistData | null }>
): void {
  for (const { name, data } of entries) {
    setCachedArtist(name, data);
  }
}

/**
 * Check if a cached entry is still fresh.
 */
export function isFresh(entry: CachedArtist): boolean {
  return Date.now() < entry.expiresAt;
}

/**
 * Check if a cached entry should be refreshed (expired or old).
 */
export function shouldRefresh(entry: CachedArtist): boolean {
  return Date.now() > entry.expiresAt || // Expired
    (Date.now() - entry.cachedAt) > REFRESH_THRESHOLD_MS; // Stale
}

/**
 * Get cache statistics.
 */
export function getCacheStats(): CacheStats {
  const cache = getCache();
  const now = Date.now();
  let fresh = 0;
  let expired = 0;

  for (const entry of cache.values()) {
    if (now < entry.expiresAt) fresh++;
    else expired++;
  }

  return {
    total: cache.size,
    fresh,
    expired,
    pending: 0,
  };
}

/**
 * Get all artist names that need refresh.
 */
export function getStaleArtistNames(): string[] {
  const cache = getCache();
  const stale: string[] = [];
  for (const entry of cache.values()) {
    if (shouldRefresh(entry)) {
      stale.push(entry.name);
    }
  }
  return stale;
}

/**
 * Get all cached artist data as a plain object (for serialization).
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
 * Clear the cache.
 */
export function clearCache(): void {
  global.__artistCache = new Map();
}

// ── Helpers ──

function normalizeKey(name: string): string {
  return name.toLowerCase().trim().replace(/\s+/g, ' ');
}
