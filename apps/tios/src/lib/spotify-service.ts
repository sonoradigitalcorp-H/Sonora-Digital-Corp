// ───────────────────────────────────────────────
// Spotify Web API Service
// Client Credentials flow — no user login required
// ───────────────────────────────────────────────

const SPOTIFY_AUTH_URL = 'https://accounts.spotify.com/api/token';
const SPOTIFY_API_BASE = 'https://api.spotify.com/v1';

// ── Types ──

export interface SpotifyArtistData {
  id: string;
  name: string;
  followers: number;
  popularity: number;         // 0-100
  genres: string[];
  imageUrl: string | null;
  spotifyUrl: string;
}

export interface SpotifyTrack {
  id: string;
  name: string;
  popularity: number;
  durationMs: number;
  album: string;
  albumImage: string | null;
  spotifyUrl: string;
}

// ── Token Management ──

let cachedToken: { token: string; expiresAt: number } | null = null;

async function getAccessToken(): Promise<string> {
  // Return cached token if still valid (with 5 min buffer)
  if (cachedToken && Date.now() < cachedToken.expiresAt - 300000) {
    return cachedToken.token;
  }

  const clientId = process.env.SPOTIFY_CLIENT_ID;
  const clientSecret = process.env.SPOTIFY_CLIENT_SECRET;

  if (!clientId || !clientSecret) {
    throw new Error(
      'Spotify API credentials not configured. ' +
      'Set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET in .env'
    );
  }

  const basic = Buffer.from(`${clientId}:${clientSecret}`).toString('base64');

  const response = await fetch(SPOTIFY_AUTH_URL, {
    method: 'POST',
    headers: {
      Authorization: `Basic ${basic}`,
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: new URLSearchParams({ grant_type: 'client_credentials' }),
    signal: AbortSignal.timeout(10000),
  });

  if (!response.ok) {
    throw new Error(`Spotify auth failed: ${response.status} ${response.statusText}`);
  }

  const data = await response.json() as { access_token: string; expires_in: number };

  cachedToken = {
    token: data.access_token,
    expiresAt: Date.now() + data.expires_in * 1000,
  };

  return data.access_token;
}

// ── Rate Limiting ──

const requestQueue: Array<() => Promise<void>> = [];
let processingQueue = false;
let lastRequestTime = 0;
const MIN_REQUEST_INTERVAL = 50; // ms between requests (conservative)

async function rateLimitedFetch(url: string, token: string): Promise<Response> {
  // Ensure minimum time between requests
  const now = Date.now();
  const waitTime = Math.max(0, MIN_REQUEST_INTERVAL - (now - lastRequestTime));

  if (waitTime > 0) {
    await new Promise(resolve => setTimeout(resolve, waitTime));
  }

  lastRequestTime = Date.now();

  const response = await fetch(url, {
    headers: { Authorization: `Bearer ${token}` },
    signal: AbortSignal.timeout(8000),
  });

  // Handle rate limiting (429 Too Many Requests)
  if (response.status === 429) {
    const retryAfter = parseInt(response.headers.get('Retry-After') || '1', 10);
    console.warn(`Spotify rate limited. Waiting ${retryAfter}s...`);
    await new Promise(resolve => setTimeout(resolve, retryAfter * 1000 + 100));
    return rateLimitedFetch(url, token); // Retry
  }

  return response;
}

// ── API Methods ──

/**
 * Search for an artist on Spotify by name.
 * Returns the best match or null if not found.
 */
export async function searchArtist(name: string): Promise<SpotifyArtistData | null> {
  try {
    const token = await getAccessToken();
    const url = `${SPOTIFY_API_BASE}/search?q=${encodeURIComponent(name)}&type=artist&limit=1`;
    const response = await rateLimitedFetch(url, token);

    if (!response.ok) {
      console.warn(`Spotify search failed for "${name}": ${response.status}`);
      return null;
    }

    const data = await response.json() as {
      artists?: { items?: Array<{
        id: string; name: string; followers?: { total: number };
        popularity: number; genres: string[];
        images?: Array<{ url: string }>;
        external_urls?: { spotify?: string };
      }> };
    };

    const artist = data?.artists?.items?.[0];
    if (!artist) return null;

    return {
      id: artist.id,
      name: artist.name,
      followers: artist.followers?.total ?? 0,
      popularity: artist.popularity,
      genres: artist.genres ?? [],
      imageUrl: artist.images?.[0]?.url ?? null,
      spotifyUrl: artist.external_urls?.spotify ?? `https://open.spotify.com/artist/${artist.id}`,
    };
  } catch (error) {
    console.warn(`Spotify search error for "${name}":`, error);
    return null;
  }
}

/**
 * Search multiple artists in batch (with rate limiting).
 * Returns a map of name → data for found artists.
 */
export async function searchArtistsBatch(
  names: string[]
): Promise<Map<string, SpotifyArtistData>> {
  const results = new Map<string, SpotifyArtistData>();

  // Process in batches of 3 to be kind to rate limits
  const batchSize = 3;
  for (let i = 0; i < names.length; i += batchSize) {
    const batch = names.slice(i, i + batchSize);
    const batchResults = await Promise.all(
      batch.map(async (name) => {
        const data = await searchArtist(name);
        return { name, data };
      })
    );

    for (const { name, data } of batchResults) {
      if (data) results.set(name, data);
    }

    // Delay between batches
    if (i + batchSize < names.length) {
      await new Promise(resolve => setTimeout(resolve, 200));
    }
  }

  return results;
}

/**
 * Get full artist details by Spotify ID.
 */
export async function getArtist(spotifyId: string): Promise<SpotifyArtistData | null> {
  try {
    const token = await getAccessToken();
    const url = `${SPOTIFY_API_BASE}/artists/${spotifyId}`;
    const response = await rateLimitedFetch(url, token);

    if (!response.ok) return null;

    const data = await response.json() as {
      id: string; name: string; followers?: { total: number };
      popularity: number; genres: string[];
      images?: Array<{ url: string }>;
      external_urls?: { spotify?: string };
    };

    return {
      id: data.id,
      name: data.name,
      followers: data.followers?.total ?? 0,
      popularity: data.popularity,
      genres: data.genres ?? [],
      imageUrl: data.images?.[0]?.url ?? null,
      spotifyUrl: data.external_urls?.spotify ?? `https://open.spotify.com/artist/${data.id}`,
    };
  } catch (error) {
    console.warn(`Spotify getArtist error for "${spotifyId}":`, error);
    return null;
  }
}

/**
 * Get top tracks for an artist.
 */
export async function getArtistTopTracks(
  spotifyId: string,
  market = 'US'
): Promise<SpotifyTrack[]> {
  try {
    const token = await getAccessToken();
    const url = `${SPOTIFY_API_BASE}/artists/${spotifyId}/top-tracks?market=${market}`;
    const response = await rateLimitedFetch(url, token);

    if (!response.ok) return [];

    const data = await response.json() as {
      tracks?: Array<{
        id: string; name: string; popularity: number;
        duration_ms: number;
        album: { name: string; images?: Array<{ url: string }> };
        external_urls?: { spotify?: string };
      }>;
    };

    return (data.tracks ?? []).map(t => ({
      id: t.id,
      name: t.name,
      popularity: t.popularity,
      durationMs: t.duration_ms,
      album: t.album.name,
      albumImage: t.album.images?.[0]?.url ?? null,
      spotifyUrl: t.external_urls?.spotify ?? `https://open.spotify.com/track/${t.id}`,
    }));
  } catch (error) {
    console.warn(`Spotify top tracks error for "${spotifyId}":`, error);
    return [];
  }
}

/**
 * Check if Spotify API is configured (credentials exist).
 */
export function isSpotifyConfigured(): boolean {
  return !!(process.env.SPOTIFY_CLIENT_ID && process.env.SPOTIFY_CLIENT_SECRET);
}
