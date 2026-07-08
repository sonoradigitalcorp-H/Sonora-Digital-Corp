# YouTube Provider — SIGNAL Music Intelligence

---

## Overview

The YouTube Provider connects to the **YouTube Data API v3** to collect channel analytics and video performance data for artists. It is a read-only enrichment provider that feeds subscriber metrics, video engagement, and content frequency into the SIGNAL Intelligence Engine.

---

## Data Collected

| Field | Source | Notes |
|-------|--------|-------|
| **Subscribers** | `channels.statistics.subscriberCount` | May be hidden (private) |
| **Total views** | `channels.statistics.viewCount` | Lifetime channel views |
| **Upload count** | `channels.statistics.videoCount` | Total public videos |
| **Upload frequency** | Computed | Videos per year (videoCount / channelAge) |
| **Average views** | Computed from recent 10 videos | Views / video |
| **Channel age** | `snippet.publishedAt` | Years since channel creation |
| **Channel description** | `snippet.description` | Used as bio |
| **Country** | `snippet.country` | May be null |
| **Latest 10 videos** | `search → videos` endpoint | Title, views, likes, comments, publish date |
| **Top 10 videos** | `search?order=viewCount` | Sorted by total views |
| **Engagement estimate** | Computed | Weighted: views/subs ratio + interaction rate |
| **Thumbnails** | `snippet.thumbnails` | Small, medium, high resolution |

---

## API Setup

### 1. Enable YouTube Data API v3

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project (or select existing)
3. Navigate to **APIs & Services → Library**
4. Search for **YouTube Data API v3**
5. Click **Enable**

### 2. Create API Key

1. Go to **APIs & Services → Credentials**
2. Click **Create Credentials → API Key**
3. (Recommended) Restrict the key to YouTube Data API v3
4. Copy the key

### 3. Configure SIGNAL

```bash
# In .env.local:
YOUTUBE_PROVIDER_ENABLED=true
GOOGLE_API_KEY=your_api_key_here
# OR:
YOUTUBE_API_KEY=your_api_key_here
```

---

## Quota Limits

YouTube Data API v3 has a **daily quota** (typically 10,000 units/day for free tier).

| Operation | Cost (units) |
|-----------|-------------|
| `channels.list` | 1 |
| `search.list` | 100 |
| `videos.list` | 1 |

A full channel enrichment (search + channels + videos) costs ~202 units.
With 10,000 daily quota: ~49 full enrichments/day.

**Recommendation**: Enable cache (`YOUTUBE_CACHE_TTL_HOURS=6`) to minimize API calls.

---

## Provider Methods

### Standard DataProvider Interface

```typescript
// All standard methods implemented:
searchArtist(query)     // Search channels by name
fetchProfile(id)        // Channel description, country, name
fetchMetrics(id)        // Subscribers, engagement, (computed fields below)
fetchImages(id)         // Channel thumbnails
fetchGenres(id)         // Returns [] (no genre taxonomy)
```

### YouTube-Specific Methods

```typescript
// Extra analytics beyond standard metrics:
fetchChannelAnalytics(id)
  // → { channelAge, totalViews, totalVideos, uploadFrequency, avgViews, ... }

fetchLatestVideos(id, maxResults = 10)
  // → [{ id, title, publishedAt, views, likes, comments, thumbnailUrl }]

fetchTopVideos(id, maxResults = 10)
  // → [{ id, title, views, likes, comments, thumbnailUrl }]
```

---

## Engagement Formula

```
engagement = min(100, round(
  (avgViews / subscriberCount) * 0.7 +
  ((likes + comments) / avgViews) * 0.3
) * 50)
```

Combines:
- **View ratio**: How many views per subscriber
- **Interaction rate**: Likes + comments per view

---

## Error Handling

- **Hidden subscriber count**: `statistics.hiddenSubscriberCount` is flagged; `subscriberCount` returns 0
- **Quota exceeded**: Returns degraded health; retries with backoff
- **Invalid API key**: Returns unhealthy; logs configuration error
- **Missing env vars**: Provider initializes as disabled; all methods return empty/default
