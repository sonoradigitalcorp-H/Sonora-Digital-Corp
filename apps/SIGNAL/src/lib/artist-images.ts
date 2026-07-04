// ───────────────────────────────────────────────
// ⚠️ DEPRECATED — Backward Compatibility Shim
// Please use getDeezerProvider() or fetchArtistImageByName()
// from '@/providers/deezer/deezer-provider'
// ───────────────────────────────────────────────

import { fetchArtistImageByName, fetchAllArtistImagesByName } from '@/providers/deezer/deezer-provider';

// ── Simple in-memory cache (backward compat) ──
const legacyCache = new Map<string, string | null>();

/**
 * Fetch a single artist image from Deezer.
 */
export async function fetchArtistImage(artistName: string): Promise<string | null> {
  if (legacyCache.has(artistName)) {
    return legacyCache.get(artistName) ?? null;
  }

  try {
    const images = await fetchArtistImageByName(artistName);
    const url = images.large ?? images.medium ?? images.small;
    legacyCache.set(artistName, url);
    return url;
  } catch {
    legacyCache.set(artistName, null);
    return null;
  }
}

/**
 * Fetch images for multiple artists from Deezer.
 */
export async function fetchAllArtistImages(
  names: string[]
): Promise<Record<string, string | null>> {
  const result: Record<string, string | null> = {};

  // Check legacy cache first
  const uncached = names.filter(n => {
    if (legacyCache.has(n)) {
      result[n] = legacyCache.get(n) ?? null;
      return false;
    }
    return true;
  });

  if (uncached.length > 0) {
    try {
      const imageMap = await fetchAllArtistImagesByName(uncached);
      for (const [name, images] of imageMap) {
        const url = images.large ?? images.medium ?? images.small;
        legacyCache.set(name, url);
        result[name] = url;
      }
    } catch {
      for (const name of uncached) {
        legacyCache.set(name, null);
        result[name] = null;
      }
    }
  }

  return result;
}
