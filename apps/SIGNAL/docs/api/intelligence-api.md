# Intelligence API — SIGNAL Product Layer

> **Endpoint:** `GET /api/v1/intelligence/[id]`
> **Version:** 3.5.0
> **Only public interface for intelligence data.**

## Purpose

The Intelligence API is the **single public gateway** for all artist intelligence data. It orchestrates:

1. **Feature Extraction** — converts raw artist data into normalized features
2. **Feature Store** — tracks feature provenance, quality, and freshness
3. **Score Engine** — evaluates 10 AI scores against the artist
4. **Insight Generation** — produces deterministic insights from scores + features

The frontend **never** accesses providers, raw features, or internal scoring logic.

## Response Format

```json
{
  "artist": {
    "id": "art-amg-01",
    "name": "Héctor Rubio",
    "genres": ["Regional Mexicano", "Corridos", "Corridos Bélicos"],
    "country": "México",
    "image": "https://..."
  },
  "scores": [
    {
      "id": "artist-momentum",
      "name": "Artist Momentum",
      "category": "growth",
      "version": "1.0.0",
      "score": 87,
      "confidence": 72,
      "summary": "Strong upward trajectory...",
      "factors": [ /* impacting factors */ ],
      "recommendations": [ /* actionable steps */ ],
      "dataQuality": "Real-time provider data with strong signal confidence",
      "trend": "up",
      "volatility": 12,
      "valid": true,
      "validationMessage": ""
    }
  ],
  "aggregate": {
    "score": 74.2,
    "confidence": 68,
    "scoresComputed": 10,
    "scoresSkipped": 0
  },
  "features": {
    "platforms": [
      { "name": "followers", "value": 45862, "quality": 0.85, "provider": "spotify", "source": "provider" }
    ],
    "summary": { "platforms": [...], "followers": 45862, "monthlyListeners": 1105586 }
  },
  "insights": {
    "items": [
      {
        "type": "growth",
        "message": "Strong follower growth at 32.5%...",
        "severity": "high",
        "category": "audience growth",
        "source": "followerGrowth"
      }
    ],
    "summary": ["Strong follower growth...", "Elite engagement rate..."]
  },
  "metadata": {
    "computedAt": "2026-07-04T14:30:00.000Z",
    "version": "3.5.0"
  }
}
```

## Score Categories

| Category | Scores |
|----------|--------|
| `growth` | Artist Momentum, Growth Velocity |
| `audience` | Discovery, Audience Quality |
| `commercial` | Label Readiness, Brand Partnership, Tour Readiness |
| `discovery` | Virality Index, Fan Conversion |
| `performance` | Global Expansion |

## Insights Types

| Type | Color | Description |
|------|-------|-------------|
| `growth` | Green | Positive growth signals |
| `risk` | Red | Declining or dangerous metrics |
| `opportunity` | Amber | Untapped potential |
| `achievement` | Blue | Exceptional performance |
| `warning` | Yellow | Below-average metrics |

## Caching

- Response cached: `s-maxage=60, stale-while-revalidate=300`
- Feature Store: in-memory per serverless instance
- Scores: recomputed on every request (deterministic from features)

## Error Responses

```json
{ "error": "Artist not found", "id": "art-unknown" }
```

Status: `404` when artist ID not found in the artist pool.
