// ───────────────────────────────────────────────
// Artist Image Fetching Utility
// Uses Deezer's public API (no API key needed)
// ───────────────────────────────────────────────

const ARTIST_IMAGE_CACHE = new Map<string, string | null>();

export async function fetchArtistImage(artistName: string): Promise<string | null> {
  // Check cache first
  if (ARTIST_IMAGE_CACHE.has(artistName)) {
    return ARTIST_IMAGE_CACHE.get(artistName) ?? null;
  }

  try {
    const response = await fetch(
      `https://api.deezer.com/search/artist?q=${encodeURIComponent(artistName)}&limit=1&order=RATING_DESC`,
      {
        headers: { Accept: 'application/json' },
        signal: AbortSignal.timeout(5000),
      }
    );

    if (!response.ok) {
      ARTIST_IMAGE_CACHE.set(artistName, null);
      return null;
    }

    const data = await response.json() as { data?: Array<{ picture_medium?: string }> };
    const imageUrl = data?.data?.[0]?.picture_medium ?? null;

    ARTIST_IMAGE_CACHE.set(artistName, imageUrl);
    return imageUrl;
  } catch {
    ARTIST_IMAGE_CACHE.set(artistName, null);
    return null;
  }
}

export async function fetchAllArtistImages(
  names: string[]
): Promise<Record<string, string | null>> {
  const uncached = names.filter(n => !ARTIST_IMAGE_CACHE.has(n));

  // Process uncached names in batches
  if (uncached.length > 0) {
    const batchSize = 5;
    for (let i = 0; i < uncached.length; i += batchSize) {
      const batch = uncached.slice(i, i + batchSize);
      await Promise.all(batch.map(name => fetchArtistImage(name)));

      // Rate limiting delay between batches
      if (i + batchSize < uncached.length) {
        await new Promise(resolve => setTimeout(resolve, 300));
      }
    }
  }

  // Build result from cache
  const result: Record<string, string | null> = {};
  for (const name of names) {
    result[name] = ARTIST_IMAGE_CACHE.get(name) ?? null;
  }
  return result;
}
