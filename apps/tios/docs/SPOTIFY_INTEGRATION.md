# 🔷 Spotify Integration — Architecture & Reference

> **Platform**: SIGNAL Music Intelligence
> **Last audit**: 04-Jul-2026
> **Spotify Developer Platform**: Client Credentials Flow (server-to-server)

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Authentication Flow](#2-authentication-flow)
3. [API Endpoints Used](#3-api-endpoints-used)
4. [Required Credentials](#4-required-credentials)
5. [Environment Variables](#5-environment-variables)
6. [Integration Architecture](#6-integration-architecture)
7. [Setup Instructions](#7-setup-instructions)
8. [Fallback Behavior](#8-fallback-behavior)
9. [Rate Limiting Strategy](#9-rate-limiting-strategy)
10. [Caching Strategy](#10-caching-strategy)
11. [Security Recommendations](#11-security-recommendations)
12. [Troubleshooting](#12-troubleshooting)
13. [Migration Notes](#13-migration-notes)
14. [Remaining Issues](#14-remaining-issues)

---

## 1. Architecture Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                       SIGNAL Next.js App                         │
│                                                                  │
│  ┌──────────────┐   ┌─────────────────┐   ┌──────────────────┐  │
│  │  artists/route│──▶│  spotify-       │──▶│  artist-cache.ts │  │
│  │  (API)        │   │  service.ts     │   │  (globalThis)   │  │
│  └──────────────┘   └────────┬────────┘   └────────┬─────────┘  │
│                              │                      │            │
│  ┌──────────────┐            │                      │            │
│  │  refresh/    │────────────┘                      │            │
│  │  route (API) │                                   │            │
│  └──────────────┘                         ┌─────────┴─────────┐  │
│                                           │  Cache: Map() in  │  │
│                                           │  globalThis       │  │
│                                           │  TTL: 24h config  │  │
│                                           └───────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
                      │
                      ▼
          ┌───────────────────────┐
          │  Spotify Web API      │
          │  api.spotify.com/v1   │
          └───────────────────────┘
```

### Files involved (core SIGNAL app only)

| File | Role |
|------|------|
| `src/lib/spotify-service.ts` | Spotify API client (auth, requests, rate limiting) |
| `src/lib/artist-cache.ts` | In-memory cache layer for Spotify results |
| `src/app/api/v1/artists/route.ts` | Artists endpoint with Spotify enrichment |
| `src/app/api/v1/artists/refresh/route.ts` | Cache refresh endpoint |
| `.env.local.example` | Environment variable template |

---

## 2. Authentication Flow

### Flow: Client Credentials (OAuth 2.0)

```
                                    ┌─────────────────┐
                                    │  Spotify Auth    │
                                    │  Server          │
                                    └────────┬────────┘
         ┌────────────────────┐              │
         │  SIGNAL Backend    │              │
         │                    │              │
         │  1. POST           │─────────────▶│  Basic Auth (Base64)
         │     /api/token     │              │  grant_type=client_credentials
         │                    │◀─────────────│
         │  2. Receive        │              │  { access_token, expires_in }
         │     access_token   │              │
         │                    │              │
         │  3. GET /v1/...    │─────────────▶│  Authorization: Bearer <token>
         │                    │              │
         │  4. Receive        │◀─────────────│  { artist data }
         │     response       │              │
         └────────────────────┘              └─────────────────┘
```

### Why not Authorization Code or PKCE?

- **Client Credentials** is correct because SIGNAL only accesses **public artist data**
- No user login required (no user playlists, no user-specific endpoints)
- Authorization Code flow would require a redirect URI and user login — unnecessary overhead
- The app **cannot and should not** access user-private data (playlists, saved tracks, etc.)

### Token lifecycle

| Step | Detail |
|------|--------|
| Token request | `POST https://accounts.spotify.com/api/token` |
| Grant type | `client_credentials` |
| Auth header | `Basic {base64(client_id:client_secret)}` |
| Response | `{ access_token, token_type, expires_in }` |
| Token expiry | `expires_in` seconds (typically 3600 = 1 hour) |
| Caching | Token cached in-memory, refreshed 5 min before expiry |
| Deduplication | Concurrent requests share the same token fetch promise |

---

## 3. API Endpoints Used

| Endpoint | Method | Used In | Status |
|----------|--------|---------|--------|
| `/api/token` | POST | Auth | ✅ Active |
| `/v1/search?q={name}&type=artist&limit=1` | GET | `searchArtist()` | ✅ Active |
| `/v1/artists/{id}` | GET | `getArtist()` | ✅ Active |
| `/v1/artists/{id}/top-tracks?market={market}` | GET | `getArtistTopTracks()` | ✅ Active |

All endpoints are **stable** and supported as of July 2026.

### Deprecated endpoints — NOT used
- `v1/tracks/{id}` (not needed)
- `v1/audio-features` (not needed)
- `v1/audio-analysis` (not needed)
- `v1/recommendations` (not needed)
- `v1/me/*` (requires user auth)

### Deprecated scopes — NOT used
We use Client Credentials which doesn't require any OAuth scopes.

---

## 4. Required Credentials

### Mandatory

| Credential | Source | Format |
|------------|--------|--------|
| `SPOTIFY_CLIENT_ID` | Spotify Dashboard | 32-character hex string |
| `SPOTIFY_CLIENT_SECRET` | Spotify Dashboard | 32-character hex string |

### How to obtain

1. Go to [https://developer.spotify.com/dashboard/](https://developer.spotify.com/dashboard/)
2. Log in with any Spotify account (free tier works)
3. Click **"Create app"**
4. App name: `SIGNAL Music Intelligence` (or any name)
5. App description: `Artist data enrichment for SIGNAL platform`
6. Redirect URI: `http://localhost:3000/api/v1/artists/callback` (required but unused for Client Credentials)
7. Check "**Web API**" as the API to use
8. Accept terms → **Create**
9. Copy **Client ID** and **Client Secret** from the app dashboard

> ⚠️ **Do NOT commit Client Secret to git.** It's already in `.gitignore`.

---

## 5. Environment Variables

### Full reference

```env
# ═══════════════════════════════════════════
# SPOTIFY WEB API — OBLIGATORIOS
# ═══════════════════════════════════════════
SPOTIFY_CLIENT_ID=                                     # 32-char hex
SPOTIFY_CLIENT_SECRET=                                 # 32-char hex

# ═══════════════════════════════════════════
# SPOTIFY WEB API — OPCIONALES
# ═══════════════════════════════════════════
SPOTIFY_MARKET=US                                       # ISO 3166-1 alpha-2 (default: US)
SPOTIFY_CACHE_TTL_HOURS=24                              # Cache TTL in hours (default: 24)
SPOTIFY_REQUEST_TIMEOUT=10000                           # ms (default: 10000)
SPOTIFY_RATE_LIMIT_INTERVAL=200                         # ms between requests (default: 200)
SPOTIFY_MAX_RETRIES=3                                   # 429 retry count (default: 3)
SPOTIFY_TOKEN_BUFFER=300000                             # ms before expiry to refresh (default: 300000)
```

### Vercel configuration

Set these in your Vercel project dashboard:

```
Settings → Environment Variables → Add New
SPOTIFY_CLIENT_ID        → <your-client-id>
SPOTIFY_CLIENT_SECRET    → <your-client-secret>
SPOTIFY_MARKET           → US (or MX for Latin focus)
SPOTIFY_CACHE_TTL_HOURS  → 24
```

---

## 6. Integration Architecture

### Data flow for artist requests

```
GET /api/v1/artists?genre=Latin&count=20
  │
  ├── 1. Generate fallback data via generateArtists()
  │
  ├── 2. Check SPOTIFY_CLIENT_ID / SECRET
  │     └── Not configured → skip to step 5
  │
  ├── 3. For each artist:
  │     ├── Check in-memory cache (globalThis.__artistCache)
  │     │   ├── Hit + fresh → use cached Spotify data
  │     │   └── Miss / stale → fetch from Spotify API
  │     │
  │     └── Store result in cache (including "not found" = null)
  │
  ├── 4. Override generated data with Spotify real data:
  │     ├── followers (real)
  │     ├── popularity → score (mapped 0-100 → 65-98)
  │     ├── genres (real, up to 3)
  │     └── photoUrl (real, fallback to Spotify CDN)
  │
  ├── 5. Prepend AMG signed artists (frozen, never Spotify-enriched)
  │
  ├── 6. Deezer photo enrichment (for artists without Spotify)
  │
  └── 7. Return { artists, total, signedCount, spotifyConnected }
```

### Auto-refresh flow

```
POST /api/v1/artists/refresh
  │
  ├── 1. Validate credentials
  ├── 2. List all ARTIST_POOL (non-AMG)
  ├── 3. Check which are stale/missing from cache
  ├── 4. Batch search Spotify (batchSize=3, 300ms delay)
  ├── 5. Update cache
  └── 6. Return { found, notFound, refreshed, stats }
```

---

## 7. Setup Instructions

### Local development

```bash
# 1. Copy env template
cp .env.local.example .env.local

# 2. Edit .env.local with your Spotify credentials
#    SPOTIFY_CLIENT_ID=xxx
#    SPOTIFY_CLIENT_SECRET=xxx

# 3. Start dev server
pnpm dev

# 4. Verify integration
curl http://localhost:3000/api/v1/artists?count=1
# Response includes: spotifyConnected: true
```

### Production (Vercel)

```bash
# Install Vercel CLI
pnpm add -g vercel

# Pull environment variables
vercel env pull

# Or set manually:
vercel env add SPOTIFY_CLIENT_ID
vercel env add SPOTIFY_CLIENT_SECRET

# Deploy
vercel --prod
```

Or via Vercel Dashboard:
1. Go to project → Settings → Environment Variables
2. Add `SPOTIFY_CLIENT_ID` and `SPOTIFY_CLIENT_SECRET`
3. Redeploy

---

## 8. Fallback Behavior

### When credentials are missing

```
┌─────────────────────────────────────────────┐
│          isSpotifyConfigured()               │
│                                              │
│  validateSpotifyCredentials() → null?        │
│                                              │
│  YES ───▶ Spotify data is attached to        │
│            API responses                     │
│                                              │
│  NO ────▶ Application continues normally     │
│            with generated data                │
│            Response includes:                │
│              spotifyConnected: false          │
│            Console warning logged             │
│                                              │
│  ERROR ──▶ Validation error message           │
│            returned in refresh endpoint       │
└─────────────────────────────────────────────┘
```

**Guarantees:**
- ✅ Application never crashes
- ✅ All API routes work without credentials
- ✅ Generated data is realistic, varied, and seeded
- ✅ AMG artists always use their verified real data
- ✅ Clear `spotifyConnected: false` flag in response
- ✅ Warnings in logs explaining fallback activation
- ✅ Validation endpoint to check credential health

### When Spotify API is unreachable

- Individual search failures return `null` (graceful degradation)
- Batch searches complete with partial results
- Logs record the failure with context
- Cache retains last known good data (stale reads permitted)

---

## 9. Rate Limiting Strategy

Spotify's rate limit for standard apps: **~300 requests per minute** (~1 req/200ms).

### Implementation

```typescript
// Layer 1: Request spacing
const MIN_INTERVAL = 200; // ms between requests (from SPOTIFY_RATE_LIMIT_INTERVAL)

// Layer 2: Batch concurrency control
const BATCH_SIZE = 3; // concurrent search queries

// Layer 3: 429 retry with exponential backoff
// - Retry-After header respected
// - Exponential backoff: 1s → 2s → 4s (capped at 30s)
// - Max retries: 3 (from SPOTIFY_MAX_RETRIES)
```

### Token refresh optimization
- Tokens cached in memory
- Refreshed 5 minutes before expiry (configurable via `SPOTIFY_TOKEN_BUFFER`)
- Concurrent auth requests deduplicated via shared promise

---

## 10. Caching Strategy

### Cache structure

```typescript
// In-memory Map<string, CachedArtist> via globalThis
interface CachedArtist {
  key: string;                     // normalized name (lowercase, trimmed)
  name: string;                    // display name
  spotify: SpotifyArtistData | null; // null = not found (avoids re-lookup)
  cachedAt: number;                // timestamp
  expiresAt: number;               // cachedAt + TTL
  hits: number;                    // access counter
}
```

### TTL configuration

| Scenario | TTL | Config |
|----------|-----|--------|
| Normal artist data | 24 hours | `SPOTIFY_CACHE_TTL_HOURS` |
| "Not found" entries | Same as normal | Rechecked on next TTL cycle |
| Access token | 1 hour (Spotify default) | Auto-managed |

### Cache stats

Available via `GET /api/v1/artists/refresh`:
```json
{
  "cacheStats": {
    "total": 150,
    "fresh": 120,
    "expired": 30,
    "totalHits": 450,
    "lastClearedAt": 1720000000000
  }
}
```

---

## 11. Security Recommendations

### Current security measures

| Measure | Status |
|---------|--------|
| `.env.local` in `.gitignore` | ✅ Enforced |
| Secrets never logged | ✅ Implemented |
| No OAuth scopes exposed | ✅ N/A (Client Credentials) |
| Rate limiting | ✅ Implemented |
| Request timeout protection | ✅ Implemented |
| Input sanitization (URL encoding) | ✅ Implemented |
| Token expiry management | ✅ Implemented |

### Recommendations

1. **Never expose credentials in client-side code**
   - ✅ Already done — `spotify-service.ts` is server-side only (in `lib/`)
   
2. **Use Vercel environment variables for production**
   - ✅ Documented in setup guide
   - Never commit `.env.local` to git

3. **Monitor rate limit violations**
   - 429 responses are logged with `[Spotify API]` prefix
   - Monitor logs for rate limit warnings

4. **Regular credential rotation**
   - Spotify Client Secrets can be regenerated from the dashboard
   - Recommended: rotate every 6 months

5. **Do not add user-facing Spotify login**
   - Client Credentials is the correct choice for server-to-server
   - Adding Authorization Code flow would introduce redirect URI handling, PKCE complexity, and user token storage

---

## 12. Troubleshooting

### "Spotify credentials not configured"

```
Error: Spotify API credentials not configured.
Set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET in .env
```

**Check:**
```bash
# Verify env vars are set
echo $env:SPOTIFY_CLIENT_ID         # PowerShell
echo $SPOTIFY_CLIENT_ID              # Bash

# Check .env.local exists
Test-Path .env.local

# Verify the validation endpoint
curl http://localhost:3000/api/v1/artists/refresh
# → { configured: false, validationError: "..." }
```

### "Spotify auth failed: 400"

Usually means invalid credentials.

**Fix:**
1. Go to [Spotify Dashboard](https://developer.spotify.com/dashboard/)
2. Click your app
3. Copy Client ID and Secret again
4. Ensure no extra whitespace in .env values

### "Spotify rate limited"

```
[Spotify API] ⚠️ Rate limited — backing off
```

The system handles this automatically with exponential backoff. If persistent:
- Reduce `SPOTIFY_RATE_LIMIT_INTERVAL` (increase delay between requests)
- Increase `SPOTIFY_CACHE_TTL_HOURS` to reduce API calls
- Check [Spotify API status](https://status.spotify.com/)

### "Artist not found on Spotify"

Some unsigned/independent artists may not be on Spotify.

**Behavior:**
- Artist is cached as `null` (not found)
- No repeated lookup attempts
- Generated data is used as fallback
- Deezer photos still enrich the artist card

---

## 13. Migration Notes

### From v2 data generator (before Fase 2A)

**Before:**
- All artist data was generated with `ARTIST_POOL` + seeded random
- No real Spotify data
- `spotifyConnected: false` always

**After:**
- Spotify data enriches generated data when credentials are available
- Cache layer prevents redundant API calls
- `spotifyConnected: true` when credentials are configured
- `validateSpotifyCredentials()` returns descriptive error messages

### Breaking changes

None. Architecture is fully backward-compatible:
- Existing exports unchanged (`searchArtist`, `getArtist`, etc.)
- Fallback behavior preserves all existing functionality
- Cache structures backward-compatible

---

## 14. Remaining Issues

| Issue | Impact | Status |
|-------|--------|--------|
| ❓ No user auth | Cannot access user-specific data (playlists, saved tracks) | Wontfix — not needed |
| ❓ Serverless cache | Cache lives in `globalThis` — reset per serverless instance | Accepted — 24h TTL mitigates |
| ❓ No persistent cache | Cache lost on server restart | Accepted — suitable for current scale |
| ❓ 1 moderate vulnerability | postcss@8.4.31 bundled in Next.js 15.5.19 | Waiting for Next.js release |
| ❓ No CI test with real creds | Tests use generated data only | Future improvement |
| ❓ No monitoring dashboard | Rate limit warnings only in logs | Future improvement |

---

## Appendix: Complete File Inventory

```
apps/tios/
├── src/
│   ├── lib/
│   │   ├── spotify-service.ts      # ★ Core: Spotify API client
│   │   ├── artist-cache.ts          # ★ Core: Artist data cache
│   │   ├── data-generator.ts        # References Spotify IDs + platforms
│   │   └── chat-knowledge.ts        # Chatbot FAQ references
│   └── app/api/v1/artists/
│       ├── route.ts                 # GET /api/v1/artists (Spotify enrichment)
│       └── refresh/
│           └── route.ts             # GET+POST /api/v1/artists/refresh
├── docs/
│   └── SPOTIFY_INTEGRATION.md       # THIS FILE
├── .env.local.example               # Env var template
└── package.json                     # Dependencies
```
