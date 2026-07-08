// ───────────────────────────────────────────────
// Spotify Authentication Module
// Client Credentials flow — no user login required
// Token caching + deduplication
// ───────────────────────────────────────────────

const SPOTIFY_AUTH_URL = 'https://accounts.spotify.com/api/token';

// ── Token Cache ──

let cachedToken: { token: string; expiresAt: number } | null = null;
let tokenFetchInProgress: Promise<string> | null = null;

export interface SpotifyAuthConfig {
  clientId: string;
  clientSecret: string;
  /** Buffer before expiry to refresh token (ms) */
  expiryBufferMs: number;
  /** Request timeout for auth (ms) */
  timeoutMs: number;
}

function loadAuthConfig(): SpotifyAuthConfig {
  return {
    clientId: process.env.SPOTIFY_CLIENT_ID || '',
    clientSecret: process.env.SPOTIFY_CLIENT_SECRET || '',
    expiryBufferMs: parseInt(process.env.SPOTIFY_TOKEN_BUFFER || '300000', 10),
    timeoutMs: parseInt(process.env.SPOTIFY_REQUEST_TIMEOUT || '10000', 10),
  };
}

// ── Credential Validation ──

export function validateCredentials(): string | null {
  const { clientId, clientSecret } = loadAuthConfig();

  if (!clientId || !clientSecret) {
    return 'SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET must be set';
  }

  if (clientId.length < 10 || clientSecret.length < 10) {
    return 'SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET look invalid (too short)';
  }

  return null;
}

export function isConfigured(): boolean {
  return validateCredentials() === null;
}

// ── Access Token ──

export async function getAccessToken(): Promise<string> {
  const config = loadAuthConfig();

  // Return cached if still valid
  if (cachedToken && Date.now() < cachedToken.expiresAt - config.expiryBufferMs) {
    return cachedToken.token;
  }

  // Deduplicate concurrent requests
  if (tokenFetchInProgress) {
    return tokenFetchInProgress;
  }

  tokenFetchInProgress = (async () => {
    const { clientId, clientSecret } = config;

    if (!clientId || !clientSecret) {
      throw new Error('Spotify credentials not configured');
    }

    const basic = Buffer.from(`${clientId}:${clientSecret}`).toString('base64');
    const controller = new AbortController();
    const timeoutId = setTimeout(
      () => controller.abort(new DOMException('Auth request timed out', 'TimeoutError')),
      config.timeoutMs
    );

    try {
      const response = await fetch(SPOTIFY_AUTH_URL, {
        method: 'POST',
        headers: {
          Authorization: `Basic ${basic}`,
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({ grant_type: 'client_credentials' }),
        signal: controller.signal,
      });

      if (!response.ok) {
        const errorBody = await response.text().catch(() => '(empty)');
        throw new Error(`Auth failed: ${response.status} — ${errorBody.slice(0, 200)}`);
      }

      const data = await response.json() as { access_token: string; expires_in: number };

      cachedToken = {
        token: data.access_token,
        expiresAt: Date.now() + data.expires_in * 1000,
      };

      return data.access_token;
    } finally {
      clearTimeout(timeoutId);
    }
  })();

  try {
    return await tokenFetchInProgress;
  } finally {
    tokenFetchInProgress = null;
  }
}

// ── Diagnostics ──

export function getTokenStatus(): { configured: boolean; cached: boolean; expiresAt: number | null } {
  return {
    configured: isConfigured(),
    cached: cachedToken !== null,
    expiresAt: cachedToken?.expiresAt ?? null,
  };
}

export function clearTokenCache(): void {
  cachedToken = null;
  tokenFetchInProgress = null;
}
