# AI Scoring — SIGNAL Intelligence Scoring System

> **Version**: 1.0.0  
> **Status**: Production  
> **Last Updated**: July 2026

---

## Table of Contents

1. [What Is AI Scoring?](#what-is-ai-scoring)
2. [Philosophy](#philosophy)
3. [The Data Pipeline](#the-data-pipeline)
4. [Scores vs. Metrics](#scores-vs-metrics)
5. [The 10 Intelligence Dimensions](#the-10-intelligence-dimensions)
6. [Why This Is "AI"](#why-this-is-ai)
7. [Future: ML Weight Prediction](#future-ml-weight-prediction)

---

## What Is AI Scoring?

AI Scoring is the system that transforms raw artist data from multiple providers (Spotify, YouTube, Instagram, TikTok, etc.) into **explainable, actionable intelligence scores** — each from 0–100 — that measure specific dimensions of an artist's career: momentum, growth velocity, audience quality, commercial readiness, and more.

This is not a black-box model. Every score must:

- **Justify** its output with human-readable reasoning
- **Show** the factors that drove the result
- **Recommend** concrete actions based on the score
- **Quantify** its own confidence in the result

---

## Philosophy

### 1. Scores Never Read Providers Directly

```
Provider Data → Feature Extractor → Normalized Features → Score Modules → Results
```

There is a strict **firewall** between provider data and scores. The `Feature Extractor` is the **only bridge**. This means:

- Scores are **provider-agnostic** — they work regardless of which data sources are available
- Adding a new provider never requires changing a score
- Scores can be tested with synthetic data in complete isolation

### 2. Every Score Is Independent

Each score is a standalone module implementing the `BaseScore` abstract class (Strategy Pattern + Template Method). They:

- Declare their own required/optional features
- Define their own weights and weight defaults
- Compute their own factors independently
- Have zero knowledge of other scores

This means scores can be **added, removed, enabled, disabled, or updated** without affecting any other score.

### 3. Explainability Is Mandatory

> "Never show only numbers."

Every score produces:
- A **human-readable summary** (e.g., "Artist Momentum: 72/100 — Strong (moderate confidence). Driven by +30 Follower Growth Rate, +18 Cross-Platform Presence. Offset by -8 Engagement Rate.")
- A **breakdown of contributing factors** — each with name, value, impact, weight, direction, and natural-language reasoning
- **Actionable recommendations** — specific things the artist can do to improve
- A **data quality assessment** — so the user knows how much to trust the score

### 4. Confidence Is Data-Driven

Confidence is not a guess. It comes from four weighted dimensions:

| Dimension | Weight | Description |
|-----------|--------|-------------|
| Feature Coverage | 40% | How many required/optional features are present |
| Data Freshness | 25% | How recent the source data is |
| Platform Diversity | 20% | How many platforms contribute data |
| Factor Agreement | 15% | Whether multiple signals point in the same direction |

---

## The Data Pipeline

```
┌──────────────┐    ┌────────────────────┐    ┌──────────────────┐    ┌──────────────┐
│   Providers   │    │  Feature Extractor  │    │  Score Engine    │    │   Output     │
│  (Spotify,    │───→│  extractFeatures()  │───→│  evaluate()      │───→│  Scores +    │
│   YouTube,    │    │  normalizeFeatures()│    │  evaluateScore() │    │  Reasoning   │
│   Instagram,  │    └────────────────────┘    └──────────────────┘    └──────────────┘
│   ...)        │              │                         │
└──────────────┘              │                         │
                              ▼                         ▼
                     UnifiedArtist              Score Registry
                     (Provider-agnostic)        (Which scores run?)
```

### Step-by-Step

1. **Provider Fetching**: The Intelligence Engine calls all enabled providers to gather data about an artist
2. **UnifiedArtist Assembly**: Data is merged into a single `UnifiedArtist` object with profile, metrics, socials, links, albums
3. **Feature Extraction**: `extractFeatures()` converts `UnifiedArtist` → `ArtistFeatures` — the normalized input that scores consume
4. **Feature Normalization**: `normalizeFeatures()` clamps all values to safe ranges (no NaN, no Infinity, no negative zeros)
5. **Score Evaluation**: The Score Engine iterates through all enabled scores in the Registry
6. **Validation**: Each score validates whether sufficient features are present
7. **Calculation**: Scores compute their factors, aggregate into 0–100, generate reasoning and recommendations
8. **History Recording**: Every result is recorded in the history manager for trend analysis
9. **Aggregation**: The engine computes aggregate intelligence metrics across all scores

---

## Scores vs. Metrics

| Metric | Score |
|--------|-------|
| Raw number (42,000 followers) | Normalized 0–100 (Audience Quality: 68/100) |
| No context | Always with reasoning ("Strong engagement at 6.5%") |
| Standalone | Compared against benchmarks |
| No recommendation | Always has actionable next steps |
| Varies by platform | Platform-agnostic |
| No confidence | Always reports confidence 0–100 |

A **metric** tells you *what*. A **score** tells you *what it means*, *how much to trust it*, and *what to do about it*.

---

## The 10 Intelligence Dimensions

SIGNAL ships with 10 default scores covering the full spectrum of artist intelligence:

| Score | Category | What It Measures |
|-------|----------|-----------------|
| [Artist Momentum](./SCORE_ENGINE.md#artist-momentum-score) | growth | Growth trajectory and velocity across platforms |
| [Growth Velocity](./SCORE_ENGINE.md#growth-velocity-score) | growth | Growth speed relative to baseline and benchmarks |
| [Discovery](./SCORE_ENGINE.md#discovery-score) | discovery | Discoverability and emergence rate |
| [Audience Quality](./SCORE_ENGINE.md#audience-quality-score) | audience | Audience depth, authenticity, and engagement quality |
| [Virality Index](./SCORE_ENGINE.md#virality-index) | performance | Viral potential and content amplification |
| [Label Readiness](./SCORE_ENGINE.md#label-readiness-score) | commercial | Readiness for label partnership |
| [Fan Conversion](./SCORE_ENGINE.md#fan-conversion-score) | audience | Listener-to-fan conversion efficiency |
| [Tour Readiness](./SCORE_ENGINE.md#tour-readiness-score) | commercial | Audience and infrastructure for live touring |
| [Brand Partnership](./SCORE_ENGINE.md#brand-partnership-score) | commercial | Suitability for brand sponsorships |
| [Global Expansion](./SCORE_ENGINE.md#global-expansion-score) | growth | International market potential |

---

## Why This Is "AI"

SIGNAL's scoring system is considered "AI" — Artificial Intelligence — for several reasons:

### 1. Multi-Signal Synthesis
Like a human analyst, each score looks at multiple signals simultaneously (growth rate + engagement + platform diversity + release cadence + genre trends) and synthesizes them into a single judgment. No single metric tells the whole story.

### 2. Context-Aware Normalization
Raw numbers are meaningless without context. SIGNAL normalizes against:
- **Domain-specific ranges** (engagement rate 0–15%, not 0–100%)
- **Non-linear transformations** using sigmoid functions (viral potential is not linear)
- **Size-adjusted ratios** (growth velocity accounts for artist size — a small artist growing fast is different from a large artist growing slowly)

### 3. Explainable Reasoning
Unlike black-box ML models, every score output includes:
- **Natural-language summary** of what was computed
- **Factor-by-factor breakdown** with human-readable explanations
- **Actionable recommendations** derived from the specific score factors
- **Data quality assessment** so users can calibrate trust

### 4. Configurable Intelligence
Weights are not hardcoded. They can be:
- Set per-score with intelligent defaults
- Overridden globally via configuration
- Adjusted per-provider, per-market, or per-genre
- **Future**: Replaced entirely by ML-predicted weights

### 5. Self-Aware Confidence
The system knows what it doesn't know. Confidence scoring means:
- Low-confidence results are clearly flagged
- Users see *why* confidence is low (missing features, stale data, etc.)
- Decisions can account for data quality, not just the number

### 6. Pattern Recognition Across Dimensions
The aggregate intelligence score across all 10 dimensions provides a **multi-dimensional profile** that no single metric could capture — the difference between "an artist with numbers" and "an artist with potential."

---

## Future: ML Weight Prediction

The architecture includes a placeholder for ML-predicted weights:

```typescript
import { enableMLWeights } from '@/scoring/weights';

// When ML model is available:
enableMLWeights('/models/weight-predictor-v1.onnx');
```

When enabled, the weights engine will:
1. Accept feature vectors as input to a trained model
2. Output dynamic weights per score per artist
3. Fall back to configured defaults when ML is unavailable

This allows the system to **learn from outcomes** — which weight configurations best predicted actual label signings, viral breaks, or tour sell-outs — and continuously improve its scoring accuracy over time.

---

## See Also

- [Score Engine Reference](./SCORE_ENGINE.md) — Full API and architecture
- [Explainability Guide](./EXPLAINABILITY.md) — How every score justifies itself
- [Score Registry Guide](./SCORE_REGISTRY.md) — Managing score lifecycle
- [Provider Architecture](./PROVIDERS.md) — How provider data feeds into scoring
- [Normalization](./NORMALIZATION.md) — How data is normalized before scoring
