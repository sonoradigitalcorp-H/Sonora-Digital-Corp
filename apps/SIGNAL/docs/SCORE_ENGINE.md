# Score Engine — SIGNAL Intelligence Scoring Architecture

> **Version**: 1.0.0  
> **Status**: Production  
> **Last Updated**: July 2026  
> **Test Coverage**: 66 tests, all passing

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [API Reference](#api-reference)
3. [Engine Result Types](#engine-result-types)
4. [Score Implementations](#score-implementations)
   - [Artist Momentum Score](#1-artist-momentum-score)
   - [Growth Velocity Score](#2-growth-velocity-score)
   - [Discovery Score](#3-discovery-score)
   - [Audience Quality Score](#4-audience-quality-score)
   - [Virality Index](#5-virality-index)
   - [Label Readiness Score](#6-label-readiness-score)
   - [Fan Conversion Score](#7-fan-conversion-score)
   - [Tour Readiness Score](#8-tour-readiness-score)
   - [Brand Partnership Score](#9-brand-partnership-score)
   - [Global Expansion Score](#10-global-expansion-score)
5. [Error Handling](#error-handling)
6. [Testing](#testing)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Score Engine                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  evaluate(UnifiedArtist) → EngineResult                │  │
│  │  evaluateScore(artist, scoreId) → ScoreOutput | null   │  │
│  └────────────────────┬───────────────────────────────────┘  │
│                       │                                       │
│          ┌────────────┼────────────┬──────────────┐          │
│          ▼            ▼            ▼              ▼          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │ Score #1 │  │ Score #2 │  │ Score #3 │  │  ... 10  │     │
│  │  Enabled │  │  Enabled │  │  Skipped │  │  Enabled │     │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘     │
│       │              │              │              │          │
│       ▼              ▼              ▼              ▼          │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Each score: validate → computeFactors → aggregate →   │  │
│  │  calculateConfidence → buildReasoning → recordHistory  │  │
│  └────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

The Score Engine is a **singleton orchestrator** that:

1. Reads all enabled scores from the **Score Registry**
2. Iterates through each score, calling `validate()` → `calculate()` → `reasoning()` → `history()`
3. Handles errors gracefully per score (never crashes the entire evaluation)
4. Aggregates results into a single `EngineResult` with aggregate intelligence metrics
5. Returns per-score `ScoreOutput` with full explainability data

---

## API Reference

### `getEngine()`

Returns the singleton Score Engine instance.

```typescript
import { getEngine } from '@/scoring';

const engine = getEngine();
```

### `engine.evaluate(artist, weights?)`

Run **all enabled scores** against a `UnifiedArtist`. This is the main entry point.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `artist` | `UnifiedArtist` | ✅ | Artist data from provider system |
| `weights` | `WeightOverrides` | ❌ | Optional global weight overrides |

**Returns**: `Promise<EngineResult>`

```typescript
const result = await engine.evaluate(artist);

console.log(result.aggregateScore);  // 72 (average of all computed scores)
console.log(result.scoresComputed);  // 8
console.log(result.scoresSkipped);   // 2
console.log(result.scores);          // ScoreOutput[] with details
```

### `engine.evaluateScore(artist, scoreId, weights?)`

Run a **single score** by its ID.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `artist` | `UnifiedArtist` | ✅ | Artist data from provider system |
| `scoreId` | `string` | ✅ | Score ID (e.g. `'artist-momentum'`) |
| `weights` | `WeightOverrides` | ❌ | Optional global weight overrides |

**Returns**: `Promise<ScoreOutput | null>` — `null` if score ID not found

```typescript
const momentum = await engine.evaluateScore(artist, 'artist-momentum');
if (momentum) {
  console.log(`${momentum.name}: ${momentum.score}/100`);
}
```

### `resetEngine()`

Reset the engine singleton (primarily for testing).

---

## Engine Result Types

### `EngineResult`

| Field | Type | Description |
|-------|------|-------------|
| `artist` | `string` | Artist name |
| `timestamp` | `string` | ISO timestamp |
| `scores` | `ScoreOutput[]` | Results for each score (including skipped/errored) |
| `aggregateScore` | `number` | Average of all valid scores (0–100) |
| `aggregateConfidence` | `number` | Average confidence across valid scores (0–100) |
| `scoresComputed` | `number` | Count of scores that ran successfully |
| `scoresSkipped` | `number` | Count of scores that failed validation or errored |
| `features` | `object` | Feature summary: platforms, followers, monthlyListeners, engagementRate, albumCount, crossPlatformPresence |

### `ScoreOutput`

| Field | Type | Description |
|-------|------|-------------|
| `id` | `string` | Score identity ID |
| `name` | `string` | Human-readable name |
| `version` | `string` | Score version |
| `category` | `string` | Score category |
| `score` | `number` | Score 0–100 (0 for skipped/errored) |
| `confidence` | `number` | Confidence 0–100 (0 for skipped/errored) |
| `summary` | `string` | Human-readable one-line summary |
| `factors` | `Factor[]` | Contributing factors with impacts |
| `recommendations` | `string[]` | Actionable recommendations |
| `dataQuality` | `string` | Data quality assessment |
| `trend` | `'up' \| 'down' \| 'stable'` | Historical trend |
| `volatility` | `number` | Score volatility 0–100 |
| `history` | `{ daily, weekly, monthly }` | History entry counts |
| `valid` | `boolean` | Whether score computed successfully |
| `validationMessage` | `string` | Validation or error message |

---

## Score Implementations

### 1. Artist Momentum Score

**Category**: `growth`  
**ID**: `artist-momentum`  
**Version**: `1.0.0`

Measures growth trajectory and velocity across all platforms. High = artist is gaining traction.

#### Required Inputs

| Feature | Normalization Range | Weight Default |
|---------|-------------------|----------------|
| `followers` | — (log scale in reasoning) | 0.3 |
| `followerGrowth` | -5% to 50% | **1.0** |
| `engagementRate` | 0% to 15% | 0.8 |
| `crossPlatformPresence` | 0 to 5 | 0.7 |

#### Optional Inputs

| Feature | Normalization Range | Weight Default |
|---------|-------------------|----------------|
| `monthlyListenerGrowth` | -5% to 50% | 0.9 |
| `avgViewGrowth` | -5% to 50% | 0.7 |
| `recentReleaseCount` | 0 to 10 | 0.5 |
| `genreTrendAlignment` | 0 to 100 | 0.4 |

**Minimum Confidence**: 30%

#### Factors Computed
1. **Follower Growth Rate** — weighted at 1.0 (highest). Growing > 0% = positive direction. Reasoning describes trajectory (strong vs. declining).
2. **Engagement Rate** — weighted at 0.8. Threshold at 5% for positive. Describes audience connection quality.
3. **Cross-Platform Presence** — weighted at 0.7. Threshold at 3 platforms for positive. Describes diversified reach.
4. **Monthly Listener Growth** (optional) — weighted at 0.9. Only added if `monthlyListenerGrowth !== 0`.
5. **Recent Releases** (optional) — weighted at 0.5. Threshold at 3 releases for positive.
6. **Genre Trend Alignment** (optional) — weighted at 0.4. Threshold at 60% for positive.

#### Aggregation
Weighted average of all factors, clamped 0–100.

#### Sample Recommendations
- "Reverse follower decline — run targeted engagement campaigns" (if negative growth)
- "Boost engagement rate — interactive content, polls, Q&As" (if < 3%)
- "Expand to TikTok and Instagram to capture new audiences" (if < 2 platforms)
- "Capitalize on momentum — plan a major release or tour announcement" (if >= 80/100)

---

### 2. Growth Velocity Score

**Category**: `growth`  
**ID**: `growth-velocity`  
**Version**: `1.0.0`

Measures growth speed relative to baseline and industry benchmarks. Unlike Momentum, this normalizes for artist size — a small artist growing fast scores higher than a large artist growing slowly.

#### Required Inputs

| Feature | Normalization Range | Weight Default |
|---------|-------------------|----------------|
| `followerGrowth` | -5% to 50% (via growth-to-audience ratio, 0–20) | **1.0** |
| `followers` | — (used in velocity ratio denominator) | 0.4 |
| `monthlyListeners` | — (used in listener-to-follower ratio) | 0.5 |

#### Optional Inputs

| Feature | Normalization Range | Weight Default |
|---------|-------------------|----------------|
| `engagementRate` | 0% to 15% | 0.6 |
| `crossPlatformPresence` | 0 to 5 | 0.5 |
| `channelAge` | 0 to 10 years | 0.3 |
| `avgViewGrowth` | -5% to 50% | 0.7 |
| `videoUploadFrequency` | 0 to 52/year | 0.4 |

**Minimum Confidence**: 30%

#### Factors Computed
1. **Growth-to-Audience Velocity** — `followerGrowth / log10(followers + 1)`. Normalized 0–20. Weighted at 1.0. Small artists growing fast get higher scores.
2. **Listener-to-Follower Ratio** (optional) — `monthlyListeners / followers`. Normalized 0–3. Weighted at 0.5. Only if both > 0. Ratio > 1 = strong passive reach.
3. **Platform Breadth** — crossPlatformPresence normalized 0–5. Weighted at 0.5. Threshold at 3 platforms.
4. **Channel Age** (optional) — Normalized 0–10. Weighted at 0.3. Uses age-adjusted formula: < 2 years = 0.8 (rapid early growth), > 7 years = 0.3 (sustained expected).
5. **View Growth Velocity** (optional) — avgViewGrowth normalized -5% to 50%. Weighted at 0.7.

#### Aggregation
Weighted average, clamped 0–100.

#### Sample Recommendations
- "Accelerate growth — cross-promote with similar artists" (if growth < 2%)
- "Convert listeners to followers — add follow prompts" (if ratio < 0.5)
- "Audit content strategy — identify past growth spikes" (if < 40/100)
- "Maintain velocity — consistency is #1 growth driver" (if >= 75/100)

---

### 3. Discovery Score

**Category**: `discovery`  
**ID**: `discovery-score`  
**Version**: `1.0.0`

Measures how discoverable and rapidly emerging an artist is. High = new audiences finding them rapidly.

#### Required Inputs

| Feature | Normalization Range | Weight Default |
|---------|-------------------|----------------|
| `followerGrowth` | 0% to 50% | **1.0** |
| `crossPlatformPresence` | 0 to 5 | 0.8 |
| `engagementRate` | 0% to 15% | 0.6 |

#### Optional Inputs

| Feature | Normalization Range | Weight Default |
|---------|-------------------|----------------|
| `postingFrequency` | 0 to 10/week | 0.7 |
| `albumCount` | — | 0.4 |
| `recentReleaseCount` | 0 to 10 | 0.6 |
| `videoUploadFrequency` | 0 to 52/year | 0.5 |
| `followers` | — | 0.3 |

**Minimum Confidence**: 30%

#### Factors Computed
1. **Discovery Velocity** — followerGrowth normalized 0–50%. Weighted at 1.0. > 10% = "rapid discovery phase".
2. **Discovery Surface Area** — platforms normalized 0–5. Weighted at 0.8. >= 3 = "multiple discovery entry points".
3. **New Audience Stickiness** — engagementRate normalized 0–15%. Weighted at 0.6. > 5% = "high retention".
4. **Content Cadence** (optional) — postingFrequency normalized 0–10/week. Weighted at 0.7. >= 3/week = "strong algorithmic visibility".
5. **Discovery Triggers** (optional) — recentReleaseCount normalized 0–10. Weighted at 0.6.
6. **Video Discovery Engine** (optional) — videoUploadFrequency normalized 0–52/year. Weighted at 0.5.

#### Aggregation
Weighted average, clamped 0–100.

---

### 4. Audience Quality Score

**Category**: `audience`  
**ID**: `audience-quality`  
**Version**: `1.0.0`

Measures audience depth, loyalty, and authentic engagement. High = loyal, active fanbase. Low = passive or purchased audience.

#### Required Inputs

| Feature | Normalization Range | Weight Default |
|---------|-------------------|----------------|
| `engagementRate` | 0% to 15% | **1.0** |
| `followers` | — | 0.3 |
| `crossPlatformPresence` | 0 to 5 | 0.6 |

#### Optional Inputs

| Feature | Normalization Range | Weight Default |
|---------|-------------------|----------------|
| `monthlyListeners` | — (used in listener-to-follower ratio) | 0.5 |
| `postingFrequency` | — | 0.4 |
| `subscriberCount` | — (used in subscriber-to-view ratio) | 0.5 |
| `avgViews` | — (used in ratio denominator) | 0.6 |
| `totalViews` | — | 0.3 |
| `verificationStatus` | — (boolean) | 0.2 |

**Minimum Confidence**: 30%

#### Factors Computed
1. **Audience Engagement Depth** — engagementRate normalized 0–15%. Weighted at 1.0. Thresholds: >= 8% = "elite", >= 4% = "healthy", < 4% = "passive or purchased".
2. **Audience Depth Ratio** (optional) — `monthlyListeners / followers`. Normalized 0–5. Weighted at 0.5. > 2x = "deep passive audience".
3. **Cross-Platform Consistency** — normalized 0–5. Weighted at 0.6.
4. **Subscriber-to-View Ratio** (optional) — `avgViews / subscriberCount`. Normalized 0–0.5. Weighted at 0.5. > 10% = highly engaged.
5. **Verified Authenticity** (optional) — boolean `+8` impact. Weighted at 0.2.

#### Aggregation
Weighted average, clamped 0–100.

#### Sample Recommendations
- "Improve engagement quality — reply to comments, run community polls" (if < 3%)
- "Audit audience for bots and inactive followers" (if < 40/100)
- "Leverage existing fans for word-of-mouth" (if quality high but growth low)
- "Premium audience quality — leverage for brand partnerships" (if >= 75/100)

---

### 5. Virality Index

**Category**: `performance`  
**ID**: `virality-index`  
**Version**: `1.0.0`

Measures viral potential and likelihood of content spreading rapidly. Uses **sigmoid functions** for non-linear scoring.

#### Required Inputs

| Feature | Normalization Range | Weight Default |
|---------|-------------------|----------------|
| `followerGrowth` | 0% to 100% (sigmoid, midpoint 20, steepness 0.08) | 0.9 |
| `engagementRate` | 0% to 20% (sigmoid, midpoint 8, steepness 0.4) | **1.0** |
| `crossPlatformPresence` | 0 to 5 | 0.7 |

#### Optional Inputs

| Feature | Normalization Range | Weight Default |
|---------|-------------------|----------------|
| `postingFrequency` | — | 0.6 |
| `videoUploadFrequency` | — | 0.5 |
| `avgViews` | — | 0.6 |
| `avgViewGrowth` | 0% to 100% (sigmoid, midpoint 50, steepness 0.05) | 0.8 |
| `followers` | — | 0.3 |
| `genreTrendAlignment` | 0 to 100 | 0.5 |

**Minimum Confidence**: 25%

#### Factors Computed
1. **Share Propensity** — engagementRate via sigmoid(midpoint=8, steepness=0.4). Weighted at 1.0. Non-linear: small changes near 8% have outsized impact.
2. **Growth Acceleration** — followerGrowth via sigmoid(midpoint=20, steepness=0.08). Weighted at 0.9. > 20% = "viral trajectory".
3. **Multi-Platform Amplification** — normalized 0–5. Weighted at 0.7. >= 3 = "content can cross-pollinate".
4. **View Momentum** (optional) — avgViewGrowth via sigmoid(midpoint=50, steepness=0.05). Weighted at 0.8. > 50% = "potential viral breakout".
5. **Genre Virality Potential** (optional) — genreTrendAlignment normalized 0–100. Weighted at 0.5. >= 70 = "viral tailwind".

**Key difference**: Uses `sigmoid()` instead of linear normalization for engagement and growth dimensions — viral potential is inherently non-linear.

#### Aggregation
Weighted average, clamped 0–100.

#### Sample Recommendations
- "Create short-form content for TikTok and Reels" (if < 2 platforms)
- "Test a viral challenge or trend" (if high engagement + content)
- "Prepare infrastructure — website/merch/links for viral traffic" (if >= 70/100)
- "Add social share triggers to content" (if high engagement but low sharing)

---

### 6. Label Readiness Score

**Category**: `commercial`  
**ID**: `label-readiness`  
**Version**: `1.0.0`

Evaluates how ready an artist is for major or independent label partnership.

#### Required Inputs

| Feature | Normalization Range | Weight Default |
|---------|-------------------|----------------|
| `followers` | log10 scale, 100–1M (2–6 on log) | 0.8 |
| `followerGrowth` | 0% to 30% | **0.9** |
| `engagementRate` | 0% to 10% | 0.7 |
| `albumCount` | 0 to 20 | 0.6 |
| `crossPlatformPresence` | 0 to 5 | 0.7 |

#### Optional Inputs

| Feature | Normalization Range | Weight Default |
|---------|-------------------|----------------|
| `monthlyListeners` | — | 0.7 |
| `recentReleaseCount` | — | 0.6 |
| `hasWebsite` | — (boolean, +10 impact) | 0.5 |
| `hasMerch` | — (boolean, +8 impact) | 0.4 |
| `hasTouringHistory` | — (boolean, +12 impact) | **0.6** |
| `channelAge` | — | 0.3 |
| `verificationStatus` | — (boolean) | 0.3 |

**Minimum Confidence**: 35% (highest threshold — label decisions need good data)

#### Factors Computed
1. **Audience Scale** — `log10(followers)` normalized 2–6. Weighted at 0.8. >= 100K = "strong label interest", >= 10K = "developing".
2. **Growth Trajectory** — followerGrowth normalized 0–30%. Weighted at 0.9. > 10% = "labels invest in momentum".
3. **Commercial Engagement** — engagementRate normalized 0–10%. Weighted at 0.7. >= 5% = "fans responsive to calls-to-action".
4. **Catalog Depth** — albumCount normalized 0–20. Weighted at 0.6. >= 5 = "substantial catalog for exploitation".
5. **Platform Diversification** — normalized 0–5. Weighted at 0.7. >= 3 = "labels value multi-channel".
6. **Professional Website** (optional) — boolean, +10 impact. Weighted at 0.5.
7. **Merch Operations** (optional) — boolean, +8 impact. Weighted at 0.4.
8. **Live Performance Track Record** (optional) — boolean, +12 impact. Weighted at 0.6.

#### Aggregation
Weighted average, clamped 0–100.

---

### 7. Fan Conversion Score

**Category**: `audience`  
**ID**: `fan-conversion`  
**Version**: `1.0.0`

Measures ability to convert casual listeners into dedicated fans who follow, engage, and purchase.

#### Required Inputs

| Feature | Normalization Range | Weight Default |
|---------|-------------------|----------------|
| `engagementRate` | 0% to 15% | **1.0** |
| `followers` | — | 0.5 |
| `monthlyListeners` | — (used in funnel ratio) | 0.7 |

#### Optional Inputs

| Feature | Normalization Range | Weight Default |
|---------|-------------------|----------------|
| `crossPlatformPresence` | 0 to 5 | 0.5 |
| `postingFrequency` | 0 to 7/week | 0.6 |
| `albumCount` | — | 0.4 |
| `recentReleaseCount` | 0 to 8 | 0.5 |
| `hasMerch` | — (boolean, +10 impact) | 0.5 |
| `hasWebsite` | — (boolean, +6 impact) | 0.4 |
| `verificationStatus` | — | 0.2 |

**Minimum Confidence**: 30%

#### Factors Computed
1. **Listener-to-Follower Funnel** — `followers / monthlyListeners`. Normalized 0–1. Weighted at 0.7. > 50% = "strong funnel".
2. **Fan Commitment Depth** — engagementRate normalized 0–15%. Weighted at 1.0. >= 6% = "fans highly committed".
3. **Conversion Touchpoints** (optional) — postingFrequency normalized 0–7/week. Weighted at 0.6. >= 3 = "consistent touchpoints convert".
4. **Re-Engagement Triggers** (optional) — recentReleaseCount normalized 0–8. Weighted at 0.5.
5. **Fan Monetization** (optional) — hasMerch boolean, +10 impact. Weighted at 0.5.
6. **Fan Destination** (optional) — hasWebsite boolean, +6 impact. Weighted at 0.4.
7. **Cross-Platform Re-Targeting** — normalized 0–5. Weighted at 0.5. >= 3 = "multiple re-targeting channels".

#### Aggregation
Weighted average, clamped 0–100.

---

### 8. Tour Readiness Score

**Category**: `commercial`  
**ID**: `tour-readiness`  
**Version**: `1.0.0`

Evaluates whether an artist has the audience and infrastructure to support a live tour.

#### Required Inputs

| Feature | Normalization Range | Weight Default |
|---------|-------------------|----------------|
| `followers` | log10 scale, 100–1M (2–6 on log) | **0.9** |
| `engagementRate` | 0% to 10% | 0.7 |
| `albumCount` | 0 to 15 | 0.6 |
| `monthlyListeners` | log10 scale, 100–1M (2–6 on log) | 0.8 |

#### Optional Inputs

| Feature | Normalization Range | Weight Default |
|---------|-------------------|----------------|
| `crossPlatformPresence` | 0 to 5 | 0.5 |
| `hasTouringHistory` | — (boolean, +15 impact) | **0.7** |
| `hasWebsite` | — | 0.4 |
| `hasMerch` | — | 0.3 |
| `channelAge` | — | 0.3 |
| `genreTrendAlignment` | 0 to 100 | 0.4 |
| `followerGrowth` | — | 0.5 |

**Minimum Confidence**: 30%

#### Factors Computed
1. **Ticket-Buying Audience** — `log10(followers)` normalized 2–6. Weighted at 0.9. >= 50K = "viable live event", >= 5K = "small venue".
2. **Performance Catalog** — albumCount normalized 0–15. Weighted at 0.6. >= 5 = "ample setlist material".
3. **Live Demand Signal** (optional) — `log10(monthlyListeners)` normalized 2–6. Weighted at 0.8. >= 100K = "proven demand".
4. **Ticket Conversion Potential** — engagementRate normalized 0–10%. Weighted at 0.7. >= 5% = "fans likely to buy tickets".
5. **Tour Track Record** (optional) — hasTouringHistory boolean, +15 impact. Weighted at 0.7.
6. **Market Timing** (optional) — genreTrendAlignment normalized 0–100. Weighted at 0.4.

#### Aggregation
Weighted average, clamped 0–100.

---

### 9. Brand Partnership Score

**Category**: `commercial`  
**ID**: `brand-partnership`  
**Version**: `1.0.0`

Evaluates artist suitability for brand sponsorships and commercial partnerships. **Engagement rate is the most weighted factor** — brands pay for attention, not followers.

#### Required Inputs

| Feature | Normalization Range | Weight Default |
|---------|-------------------|----------------|
| `engagementRate` | 0% to 15% (with brand premium adjustment) | **1.0** |
| `followers` | log10 scale, 100–1M (2–6 on log) | 0.7 |
| `crossPlatformPresence` | 0 to 5 | 0.8 |

#### Optional Inputs

| Feature | Normalization Range | Weight Default |
|---------|-------------------|----------------|
| `monthlyListeners` | — | 0.5 |
| `hasWebsite` | — (boolean, +10 impact) | 0.5 |
| `verificationStatus` | — (boolean, +10 impact) | 0.5 |
| `genreTrendAlignment` | 0 to 100 | 0.5 |
| `followerGrowth` | 0% to 30% | 0.6 |
| `postingFrequency` | — | 0.6 |
| `avgViews` | log10 scale, 100–1M (2–6 on log) | 0.5 |

**Minimum Confidence**: 30%

#### Factors Computed
1. **Brand Engagement Premium** — engagementRate normalized 0–15%, then **halved** if < 4%. Weighted at 1.0. >= 6% = "brands pay premium".
2. **Brand Impression Reach** — `log10(followers)` normalized 2–6. Weighted at 0.7. >= 50K = "substantial impressions", >= 10K = "micro-influencer".
3. **Brand Surface Area** — normalized 0–5. Weighted at 0.8. >= 3 = "integrated campaigns".
4. **Brand Integration Ready** (optional) — hasWebsite boolean, +10 impact. Weighted at 0.5.
5. **Authenticity Signal** (optional) — verificationStatus boolean, +10 impact. Weighted at 0.5.
6. **Brand Momentum** (optional) — followerGrowth normalized 0–30%. Weighted at 0.6. Rising artists attract brands.
7. **Content Quality Signal** (optional) — `log10(avgViews)` normalized 2–6. Weighted at 0.5.

#### Aggregation
Weighted average, clamped 0–100.

#### Sample Recommendations
- "Improve engagement rate — brands require 3-5% minimum" (if < 4%)
- "Create professional website with media kit" (if no website)
- "Brand-ready — create a media kit with audience demographics" (if >= 65/100)

---

### 10. Global Expansion Score

**Category**: `growth`  
**ID**: `global-expansion`  
**Version**: `1.0.0`

Evaluates potential for international market growth and cross-border audience development.

#### Required Inputs

| Feature | Normalization Range | Weight Default |
|---------|-------------------|----------------|
| `followerGrowth` | 0% to 30% | 0.8 |
| `crossPlatformPresence` | 0 to 5 | 0.8 |
| `followers` | log10 scale, 100–1M (2–6 on log) | 0.6 |

#### Optional Inputs

| Feature | Normalization Range | Weight Default |
|---------|-------------------|----------------|
| `monthlyListeners` | — | 0.6 |
| `genreTrendAlignment` | 0 to 100 (or genre appeal list check) | **0.7** |
| `engagementRate` | — | 0.5 |
| `channelAge` | — | 0.3 |
| `markets` | — (count normalized 1–10) | 0.4 (inline) |
| `albumCount` | 0 to 15 | 0.4 |
| `primaryLanguage` | — (en/es = +12 impact) | 0.5 |

**Minimum Confidence**: 25%

#### Factors Computed
1. **Genre Global Appeal** — checks genre against global list `[pop, electronic, latin, afrobeats, kpop, rnb, hipHop, rap, edm, reggaeton, dance]`. If match = 0.8 score. Otherwise uses genreTrendAlignment. Weighted at 0.7.
2. **Global Distribution Network** — normalized 0–5. Weighted at 0.8. >= 3 = "multiple channels for international reach".
3. **Scalable Momentum** — followerGrowth normalized 0–30%. Weighted at 0.8. > 10% = "momentum can scale internationally".
4. **International Foundation** — `log10(followers)` normalized 2–6. Weighted at 0.6. >= 100K = "strong base for international push".
5. **Language Accessibility** (optional) — `primaryLanguage === 'en' || 'es'` → +12 impact. Weighted at 0.5.
6. **Existing International Markets** (optional) — markets.length normalized 1–10. Weighted at 0.4.
7. **International Catalog** (optional) — albumCount normalized 0–15. Weighted at 0.4. >= 5 = "adequate for sustained international push".

#### Aggregation
Weighted average, clamped 0–100.

#### Sample Recommendations
- "Expand to globally-relevant platforms (YouTube, Spotify, TikTok) first"
- "Build domestic audience to 50K+ before investing internationally"
- "Identify top 3 international markets by streaming data"
- "Global-ready — plan market-specific campaigns" (if >= 70/100)

---

## Error Handling

The Score Engine handles errors **per score**, never letting one failure crash the entire evaluation:

### Validation Failure
When a score's `validate()` returns `valid: false`, the score is **skipped** with:
- `score: 0`, `confidence: 0`
- `valid: false`
- `validationMessage`: details on missing required features
- `summary`: "Cannot compute {name}: {reason}"
- `recommendations`: ["Provide data for: {missing features}"]

### Runtime Error
When `score.calculate()` throws, the score is **skipped** with:
- `score: 0`, `confidence: 0`
- `valid: false`
- `validationMessage`: "Error: {error message}"
- `summary`: "Error computing {name}: {error}"
- `recommendations`: ["Check provider data availability"]

### Aggregate Calculation
The aggregate score and confidence are computed **only from valid scores** (those where `valid: true`). Invalid/skipped scores are excluded from the average but included in the output array.

```typescript
const validScores = outputs.filter((o) => o.valid);
aggregateScore = average(validScores.map(s => s.score));
aggregateConfidence = average(validScores.map(s => s.confidence));
```

---

## Testing

66 tests cover the full Score Engine:

| Suite | Tests | What's Tested |
|-------|-------|---------------|
| Feature Extractor | 3 | Full extraction, minimal data, normalization |
| Weights Engine | 8 | Defaults, overrides, multipliers (provider/market/genre), reset, effective weight |
| Confidence Engine | 7 | Zero features, high/low confidence, factor agreement, freshness, build input |
| Reasoning Engine | 7 | Summary, data quality, format factors, trend, volatility, display format |
| Score History | 5 | Record/retrieve, trend tracking, empty history, stats |
| Score Registry | 5 | Register, enable/disable, unregister, list registrations, details |
| BaseScore | 9 | Init, calculate, not-initialized error, missing features, validate, warnings, history, weights, reasoning |
| Score Utilities | 6 | Clamp, normalize, weighted impact (+/-), weighted average, sigmoid |
| Score Engine Integration | 5 | All scores, single score, unknown score, minimal data, explainability |
| All Score Modules | 11 | Each of 10 scores individually + all produce different values |

Run with:
```bash
npx vitest run src/__tests__/scoring/score-engine.test.ts
```

## See Also

- [AI Scoring Philosophy](./AI_SCORING.md) — How and why AI scoring works
- [Explainability Guide](./EXPLAINABILITY.md) — How every score justifies itself
- [Score Registry Guide](./SCORE_REGISTRY.md) — Managing score lifecycle
- [Provider Architecture](./PROVIDERS.md) — How provider data feeds into scoring
