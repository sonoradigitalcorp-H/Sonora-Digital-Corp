// ───────────────────────────────────────────────
// Spotify Web API Service
// Client Credentials flow — no user login required
// Conforms to Spotify Developer Platform Jul-2026
// ───────────────────────────────────────────────

const SPOTIFY_AUTH_URL = 'https://accounts.spotify.com/api/token';
const SPOTIFY_API_BASE = 'https://api.spotify.com/v1';

// ── Configuration ──
// All configurable via environment variables with sensible defaults

interface SpotifyConfig {
  clientId: string;
  clientSecret: string;
  /** Market for top-tracks endpoint (default: 'US') */
  market: string;
  /** Request timeout in ms (default: 10000) */
  requestTimeoutMs: number;
  /** Min ms between requests for rate limiting (default: 200) */
  rateLimitIntervalMs: number;
  /** Max retries for 429 rate limits (default: 3) */
  maxRetries: number;
  /** Cache TTL for access token buffer in ms (default: 300000 = 5min) */
  tokenExpiryBufferMs: number;
}

function loadConfig(): SpotifyConfig {
  return {
    clientId: process.env.SPOTIFY_CLIENT_ID || '',
    clientSecret: process.env.SPOTIFY_CLIENT_SECRET || '',
    market: process.env.SPOTIFY_MARKET || 'US',
    requestTimeoutMs: parseInt(process.env.SPOTIFY_REQUEST_TIMEOUT || '10000', 10),
    rateLimitIntervalMs: parseInt(process.env.SPOTIFY_RATE_LIMIT_INTERVAL || '200', 10),
    maxRetries: parseInt(process.env.SPOTIFY_MAX_RETRIES || '3', 10),
    tokenExpiryBufferMs: parseInt(process.env.SPOTIFY_TOKEN_BUFFER || '300000', 10),
  };
}

// ── Validation ──

/**
 * Validates Spotify credentials format (basic sanity check).
 * Returns null if valid, or an error message string.
 */
export function validateSpotifyCredentials(): string | null {
  const { clientId, clientSecret } = loadConfig();

  if (!clientId || !clientSecret) {
    return 'SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET must be set';
  }

  // Spotify IDs are 32-character hex strings
  if (clientId.length < 10 || clientSecret.length < 10) {
    return 'SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET look invalid (too short)';
  }

  return null;
}

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

export interface SpotifyError {
  status: number;
  message: string;
  context: string;
}

export interface BatchResult {
  found: number;
  notFound: number;
  errors: SpotifyError[];
  total: number;
}

// ── Logger ──

const LOG_PREFIX = '[Spotify API]';

function log(level: 'info' | 'warn' | 'error', message: string, context?: Record<string, unknown>): void {
  const timestamp = new Date().toISOString();
  const prefix = `${LOG_PREFIX} ${timestamp}`;
  const ctx = context ? ` ${JSON.stringify(context)}` : '';

  switch (level) {
    case 'info':
      console.log(`${prefix} ${message}${ctx}`);
      break;
    case 'warn':
      console.warn(`${prefix} ⚠️ ${message}${ctx}`);
      break;
    case 'error':
      console.error(`${prefix} ❌ ${message}${ctx}`);
      break;
  }
}

// ── AbortController Helper ──
// Use AbortController instead of AbortSignal.timeout() for broader
// compatibility with older Node.js versions in serverless environments.

function createTimeoutSignal(ms: number): { signal: AbortSignal; clear: () => void } {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(new DOMException('Request timed out', 'TimeoutError')), ms);
  return {
    signal: controller.signal,
    clear: () => clearTimeout(timeoutId),
  };
}

// ── Token Management ──

let cachedToken: { token: string; expiresAt: number } | null = null;
let tokenFetchInProgress: Promise<string> | null = null;

async function getAccessToken(): Promise<string> {
  const config = loadConfig();

  // Return cached token if still valid (with configurable buffer)
  if (cachedToken && Date.now() < cachedToken.expiresAt - config.tokenExpiryBufferMs) {
    return cachedToken.token;
  }

  // Deduplicate concurrent token requests
  if (tokenFetchInProgress) {
    return tokenFetchInProgress;
  }

  tokenFetchInProgress = (async () => {
    const { clientId, clientSecret } = config;

    if (!clientId || !clientSecret) {
      throw new Error(
        'Spotify API credentials not configured. ' +
        'Set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET in .env'
      );
    }

    const basic = Buffer.from(`${clientId}:${clientSecret}`).toString('base64');
    const { signal, clear } = createTimeoutSignal(config.requestTimeoutMs);

    try {
      const response = await fetch(SPOTIFY_AUTH_URL, {
        method: 'POST',
        headers: {
          Authorization: `Basic ${basic}`,
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({ grant_type: 'client_credentials' }),
        signal,
      });

      if (!response.ok) {
        const errorBody = await response.text().catch(() => '(empty)');
        throw new Error(
          `Spotify auth failed: ${response.status} ${response.statusText} — ${errorBody}`
        );
      }

      const data = await response.json() as { access_token: string; expires_in: number };

      cachedToken = {
        token: data.access_token,
        expiresAt: Date.now() + data.expires_in * 1000,
      };

      log('info', 'Access token obtained', { expiresIn: data.expires_in });
      return data.access_token;
    } finally {
      clear();
    }
  })();

  try {
    return await tokenFetchInProgress;
  } finally {
    tokenFetchInProgress = null;
  }
}

// ── Rate Limiting & Retry ──

let lastRequestTime = 0;

async function rateLimitedFetch(
  url: string,
  token: string,
  retryCount = 0
): Promise<Response> {
  const config = loadConfig();

  // Ensure minimum time between requests
  const now = Date.now();
  const elapsed = now - lastRequestTime;
  const waitTime = Math.max(0, config.rateLimitIntervalMs - elapsed);

  if (waitTime > 0) {
    await new Promise(resolve => setTimeout(resolve, waitTime));
  }

  lastRequestTime = Date.now();

  const { signal, clear } = createTimeoutSignal(config.requestTimeoutMs);

  try {
    const response = await fetch(url, {
      headers: { Authorization: `Bearer ${token}` },
      signal,
    });

    // Handle rate limiting (429 Too Many Requests)
    if (response.status === 429) {
      const retryAfter = parseInt(response.headers.get('Retry-After') || '1', 10);
      const retryWithBackoff = retryCount + 1;

      if (retryWithBackoff >= config.maxRetries) {
        log('error', 'Max retries exceeded for rate limit', {
          url: url.substring(0, 80),
          retries: retryCount,
          retryAfter,
        });
        return response; // Return the 429 response
      }

      // Exponential backoff: base delay × 2^retryCount + retry-after header
      const backoffDelay = Math.min(
        30000, // Cap at 30s
        (retryAfter * 1000) + (1000 * Math.pow(2, retryCount))
      );

      log('warn', 'Rate limited — backing off', {
        retryAfter,
        attempt: retryWithBackoff,
        maxRetries: config.maxRetries,
        backoffMs: backoffDelay,
      });

      await new Promise(resolve => setTimeout(resolve, backoffDelay));
      return rateLimitedFetch(url, token, retryWithBackoff);
    }

    return response;
  } finally {
    clear();
  }
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
      log('warn', 'Search failed', { name, status: response.status });
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
    if (!artist) {
      log('info', 'Artist not found on Spotify', { name });
      return null;
    }

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
    log('error', 'Search error', {
      name,
      error: error instanceof Error ? error.message : String(error),
    });
    return null;
  }
}

/**
 * Search multiple artists in batch with concurrency control and retry.
 * Returns a map of name → data for found artists, plus error stats.
 */
export async function searchArtistsBatch(
  names: string[]
): Promise<Map<string, SpotifyArtistData>> {
  const results = new Map<string, SpotifyArtistData>();

  // Process in batches of 3 to stay within rate limits
  const batchSize = 3;
  let totalErrors = 0;

  for (let i = 0; i < names.length; i += batchSize) {
    const batch = names.slice(i, i + batchSize);
    const batchResults = await Promise.allSettled(
      batch.map(async (name) => {
        try {
          const data = await searchArtist(name);
          return { name, data, error: null };
        } catch (err) {
          return {
            name,
            data: null,
            error: err instanceof Error ? err.message : String(err),
          };
        }
      })
    );

    for (const result of batchResults) {
      if (result.status === 'fulfilled') {
        if (result.value.data) {
          results.set(result.value.name, result.value.data);
        }
        if (result.value.error) {
          totalErrors++;
          log('warn', 'Batch search item failed', {
            name: result.value.name,
            error: result.value.error,
          });
        }
      } else {
        totalErrors++;
        log('error', 'Batch search promise rejected', {
          reason: result.reason,
        });
      }
    }

    // Delay between batches to respect rate limits
    if (i + batchSize < names.length) {
      await new Promise(resolve => setTimeout(resolve, 300));
    }
  }

  if (totalErrors > 0) {
    log('warn', 'Batch search completed with errors', {
      total: names.length,
      found: results.size,
      errors: totalErrors,
    });
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

    if (!response.ok) {
      log('warn', 'getArtist failed', { spotifyId, status: response.status });
      return null;
    }

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
    log('error', 'getArtist error', {
      spotifyId,
      error: error instanceof Error ? error.message : String(error),
    });
    return null;
  }
}

/**
 * Get top tracks for an artist.
 * Market is configurable via SPOTIFY_MARKET env var (default: 'US').
 */
export async function getArtistTopTracks(
  spotifyId: string,
  market?: string
): Promise<SpotifyTrack[]> {
  const config = loadConfig();
  const resolvedMarket = market || config.market;

  try {
    const token = await getAccessToken();
    const url = `${SPOTIFY_API_BASE}/artists/${spotifyId}/top-tracks?market=${resolvedMarket}`;
    const response = await rateLimitedFetch(url, token);

    if (!response.ok) {
      log('warn', 'Top tracks failed', {
        spotifyId,
        market: resolvedMarket,
        status: response.status,
      });
      return [];
    }

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
    log('error', 'Top tracks error', {
      spotifyId,
      market: resolvedMarket,
      error: error instanceof Error ? error.message : String(error),
    });
    return [];
  }
}

/**
 * Check if Spotify API is configured (credentials exist and look valid).
 */
export function isSpotifyConfigured(): boolean {
  return validateSpotifyCredentials() === null;
}

/**
 * Get access token TTL status for diagnostics.
 */
export function getTokenStatus(): { configured: boolean; cached: boolean; expiresAt: number | null } {
  return {
    configured: isSpotifyConfigured(),
    cached: cachedToken !== null,
    expiresAt: cachedToken?.expiresAt ?? null,
  };
}
