# SIGNAL Provider Configuration Guide

---

## Master Switches

Each provider can be individually enabled or disabled via environment variables:

```bash
SPOTIFY_PROVIDER_ENABLED=true     # Default: true
DEEZER_PROVIDER_ENABLED=true      # Default: true
YOUTUBE_PROVIDER_ENABLED=true     # Default: true
INSTAGRAM_PROVIDER_ENABLED=true   # Default: true
TIKTOK_PROVIDER_ENABLED=true      # Default: true
```

Set any to `false` to disable without removing code.

---

## Environment Variables Reference

### Spotify

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SPOTIFY_CLIENT_ID` | ❓ | — | 32-char hex Client ID |
| `SPOTIFY_CLIENT_SECRET` | ❓ | — | 32-char hex Client Secret |
| `SPOTIFY_CACHE_TTL_HOURS` | No | 24 | Cache TTL in hours |
| `SPOTIFY_REQUEST_TIMEOUT` | No | 10000 | Request timeout in ms |
| `SPOTIFY_RATE_LIMIT_INTERVAL` | No | 200 | Min ms between requests |
| `SPOTIFY_MAX_RETRIES` | No | 3 | Max retries on 429 |
| `SPOTIFY_TOKEN_BUFFER` | No | 300000 | Token renewal buffer (ms) |

### YouTube

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GOOGLE_API_KEY` | ❓ | — | Google Cloud API key |
| `YOUTUBE_API_KEY` | ❓ | — | Alternative env var name |
| `YOUTUBE_CACHE_TTL_HOURS` | No | 6 | Cache TTL in hours |
| `YOUTUBE_REQUEST_TIMEOUT` | No | 10000 | Request timeout in ms |
| `YOUTUBE_RATE_LIMIT_INTERVAL` | No | 300 | Min ms between requests |
| `YOUTUBE_MAX_RETRIES` | No | 3 | Max retries |

### Instagram

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `META_ACCESS_TOKEN` | ❓ | — | Meta Graph API token |
| `INSTAGRAM_ACCESS_TOKEN` | ❓ | — | Alternative token env var |
| `INSTAGRAM_BUSINESS_ID` | ❓ | — | Business Account ID (full access) |
| `IG_BUSINESS_ID` | ❓ | — | Alternative env var name |
| `INSTAGRAM_CACHE_TTL_HOURS` | No | 6 | Cache TTL in hours |
| `INSTAGRAM_REQUEST_TIMEOUT` | No | 10000 | Request timeout in ms |
| `INSTAGRAM_RATE_LIMIT_INTERVAL` | No | 500 | Min ms between requests |
| `INSTAGRAM_MAX_RETRIES` | No | 2 | Max retries |

### TikTok

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `TIKTOK_ACCESS_TOKEN` | ❓ | — | Research API token |
| `TIKTOK_BUSINESS_TOKEN` | ❓ | — | Business API token |
| `TIKTOK_CACHE_TTL_HOURS` | No | 6 | Cache TTL in hours |
| `TIKTOK_REQUEST_TIMEOUT` | No | 10000 | Request timeout in ms |
| `TIKTOK_RATE_LIMIT_INTERVAL` | No | 500 | Min ms between requests |
| `TIKTOK_MAX_RETRIES` | No | 2 | Max retries |

### Deezer

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| (None) | — | — | Public API — no configuration needed |

---

## Provider Capabilities Summary

| Provider | Search | Profile | Metrics | Images | Genres | Albums | Videos | Engagement |
|----------|:------:|:-------:|:-------:|:------:|:------:|:------:|:------:|:----------:|
| Spotify | ✅ | ✅ | ❌ⁱ | ✅ | ✅ | ✅ | ❌ | ❌ |
| Deezer | ✅ | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ |
| YouTube | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ | ✅ |
| Instagram | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ |
| TikTok | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ | ✅ |

ⁱ Spotify removed `followers`, `popularity`, and `top-tracks` in Feb 2026.

---

## Provider Initialization Order

When SIGNAL starts, providers are initialized in this order:

1. **Spotify** — Client Credentials flow
2. **Deezer** — No auth needed
3. **YouTube** — API key validation
4. **Instagram** — Token validation (Business → Basic → placeholder)
5. **TikTok** — Token validation (Research → Business → placeholder)

Each provider initializes independently. A failure in one does not affect others.

---

## Monitoring

The Provider Dashboard is available at:

```
GET /api/v1/providers
```

Or visit the UI at `/providers` in the SIGNAL web app.

The dashboard shows for each provider:
- Health status (healthy / degraded / unhealthy)
- Latency (ms)
- Configuration status
- Cache statistics
- Capabilities list
- Last checked timestamp
