# TikTok Provider — SIGNAL Music Intelligence

---

## Overview

The TikTok Provider connects to **TikTok's official APIs only**. It does NOT scrape or use unofficial methods. The provider uses the **TikTok Research API** as the primary data source, with graceful fallback to placeholder mode when API access is unavailable.

---

## API Options

### Option 1: Research API (Recommended)

The [TikTok Research API](https://developers.tiktok.com/products/research-api/) provides read-only access to public TikTok data.

**Eligibility**: Available to approved academic institutions, researchers, and business partners.

**Data available**:
- User profile (display name, username, bio, avatar)
- Follower count
- Following count
- Like count
- Video count
- Verified status
- Video metadata (title, description, create time, view/like/comment/share counts)

### Option 2: Business API

The TikTok Business API is for official business partners and advertising clients.

**Eligibility**: Requires TikTok for Business account.

**Data**: Similar to Research API but focused on advertising analytics.

### Option 3: Placeholder Mode

When neither API is configured, the provider operates in **placeholder mode**:

- Returns empty arrays for `searchArtist()`, `fetchRecentVideos()`
- Returns null for `fetchProfile()`, `fetchMetrics()`
- Returns default empty images for `fetchImages()`
- Health check reports "degraded" with setup instructions

**No scraping. Ever.**

---

## Data Collected

| Field | Source | Requires |
|-------|--------|----------|
| Display name | `user.info.display_name` | Research API |
| Username | `user.info.username` | Research API |
| Bio | `user.info.bio_description` | Research API |
| Avatar | `user.info.avatar_url` | Research API |
| Followers | `user.info.follower_count` | Research API |
| Following | `user.info.following_count` | Research API |
| Total likes | `user.info.likes_count` | Research API |
| Video count | `user.info.video_count` | Research API |
| Verified | `user.info.is_verified` | Research API |
| Video views | `video.view_count` | Research API |
| Video likes | `video.like_count` | Research API |
| Video comments | `video.comment_count` | Research API |
| Video shares | `video.share_count` | Research API |
| Engagement estimate | Computed | Research API |

---

## Engagement Formula

```
engagement = min(100, round(
  (avgLikes + avgComments + avgShares) / avgViews * 150
))
```

TikTok engagement weights likes, comments, and shares against view count.

---

## Architecture

```
TikTokProvider
  ├── TikTokAPIClient (interface)
  │     ├── ResearchClient (primary)
  │     ├── BusinessClient (future)
  │     └── PlaceholderClient (fallback)
  └── Standard DataProvider methods
```

The abstraction layer (`tiktok-types.ts`) defines the `TikTokAPIClient` interface.
The factory function `createTikTokClient()` picks the best available client based on environment variables.

---

## Setup

### Research API

1. Apply for access at [TikTok for Developers](https://developers.tiktok.com/)
2. Request Research API access (approval may take weeks)
3. Generate access token
4. Configure in `.env.local`:

```bash
TIKTOK_PROVIDER_ENABLED=true
TIKTOK_ACCESS_TOKEN=your_research_api_token
```

### Without API Access

When no API credentials are available:

```bash
TIKTOK_PROVIDER_ENABLED=true
# No TIKTOK_ACCESS_TOKEN — provider works in placeholder mode
```

The provider will initialize successfully but return empty data gracefully. This allows the rest of the SIGNAL platform to function without TikTok integration.

---

## Ethical Note

SIGNAL uses official TikTok APIs exclusively. We do not scrape, reverse-engineer, or otherwise circumvent TikTok's terms of service. The placeholder mode ensures the platform works without TikTok data rather than compromising on data collection methods.
