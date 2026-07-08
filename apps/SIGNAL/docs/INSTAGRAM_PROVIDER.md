# Instagram Provider — SIGNAL Music Intelligence

---

## Overview

The Instagram Provider connects to **Meta's Graph API** to collect public profile data and metrics for artists. It supports two authentication modes with graceful degradation.

---

## Authentication Modes

### Mode 1: Business API (Full Data)

Requires:
- Facebook App (Meta for Developers)
- Instagram Business Account connected to Facebook Page
- Long-lived Page Access Token

**Provides**: Profile, bio, image, verified status, followers, follows, media count, recent media, posting frequency, engagement estimates

### Mode 2: Basic API (Limited Data)

Requires:
- Facebook App
- Instagram Basic Display API access
- User Token

**Provides**: Profile, username, name

**Does NOT provide**: Metrics, media, posting frequency

### Mode 3: Unconfigured

If no API credentials are set, the provider returns empty data for all methods. The health check reports "not configured".

---

## Data Collected

| Field | Business API | Basic API |
|-------|:---:|:---:|
| Name | ✅ | ✅ |
| Username | ✅ | ✅ |
| Biography | ✅ | ❌ |
| Profile picture | ✅ | ❌ |
| Verified status | ✅ | ❌ |
| Follower count | ✅ | ❌ |
| Following count | ✅ | ❌ |
| Media count | ✅ | ❌ |
| Recent media (last 10) | ✅ | ❌ |
| Like count (per post) | ✅ | ❌ |
| Comment count (per post) | ✅ | ❌ |
| Posting frequency | ✅ (computed) | ❌ |
| Engagement estimate | ✅ (computed) | ❌ |

---

## API Setup

### 1. Create Facebook App

1. Go to [Meta for Developers](https://developers.facebook.com/)
2. Create a new app (Business type)
3. Add **Instagram Graph API** product

### 2. Get Instagram Business Account ID

1. Go to **Graph API Explorer**
2. Select your app and token
3. `GET /me/accounts` → get Page ID
4. `GET /{page-id}?fields=instagram_business_account` → get IG Business ID

### 3. Generate Long-Lived Token

Use the **Facebook Login** flow with `pages_read_engagement` and `instagram_basic` permissions.

### 4. Configure SIGNAL

```bash
INSTAGRAM_PROVIDER_ENABLED=true
META_ACCESS_TOKEN=your_long_lived_token
INSTAGRAM_BUSINESS_ID=your_ig_business_id
```

---

## Graceful Degradation

The provider implements three tiers of functionality:

```
Business API available
  → Full data: profile, metrics, images, media
  ↓ (Business ID not configured)
Basic API available
  → Partial data: profile only
  ↓ (No token at all)
Placeholder mode
  → Empty results for all methods
```

The health endpoint reports the current mode:
- `healthy` — Business API operational
- `degraded` — Basic API (limited data)
- `unhealthy` — Not configured

---

## Engagement Formula

```
engagement = min(100, round(
  (likes + comments) / postCount / followerCount * 1000
))
```

Measured per-post interaction relative to audience size.

---

## Rate Limits

Meta Graph API has a per-app rate limit (typically 200 calls/hour per user).
The provider enforces a 500ms minimum interval between requests.
