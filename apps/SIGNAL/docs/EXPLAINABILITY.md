# Explainability — How Every Score Justifies Itself

> **Version**: 1.0.0  
> **Status**: Production  
> **Last Updated**: July 2026

> _Never show only numbers._ Every score in SIGNAL must explain itself in human terms — what it measured, why the number is what it is, how much to trust it, and what to do about it.

---

## Table of Contents

1. [The Explainability Contract](#the-explainability-contract)
2. [ScoreResult — The Core Output](#scoreresult--the-core-output)
3. [ScoreReasoning — The Human Story](#scorereasoning--the-human-story)
4. [ScoreOutput — The API Response](#scoreoutput--the-api-response)
5. [Confidence Model](#confidence-model)
6. [Contributing Factors](#contributing-factors)
7. [Data Quality Assessment](#data-quality-assessment)
8. [Trend and Volatility](#trend-and-volatility)
9. [History: Daily, Weekly, Monthly](#history-daily-weekly-monthly)
10. [Complete Example](#complete-example)
11. [Implementation Reference](#implementation-reference)

---

## The Explainability Contract

Every score module must produce:

| Output | Description | Always Present? |
|--------|-------------|-----------------|
| **Score 0–100** | Normalized intelligence score | ✅ Yes |
| **Confidence 0–100** | How much to trust the score | ✅ Yes |
| **Summary** | One-line human-readable explanation | ✅ Yes |
| **Contributing Factors** | What drove the score, with impact breakdown | ✅ Yes |
| **Recommendations** | Actionable next steps | ✅ Yes |
| **Data Quality** | Assessment of input data completeness | ✅ Yes |
| **Trend** | Direction vs. previous scores | ✅ Yes (history required) |
| **Volatility** | Score fluctuation measure | ✅ Yes (history required) |
| **Factor Reasoning** | Natural-language explanation per factor | ✅ Yes |

This contract is enforced by the `BaseScore` abstract class — every score that extends it automatically gains the explainability pipeline.

---

## ScoreResult — The Core Output

`ScoreResult` is what every score's `calculate()` method returns:

```typescript
interface ScoreResult {
  score: number;           // 0–100
  confidence: number;      // 0–100
  timestamp: string;       // ISO 8601
  factors: ContributingFactor[];
  recommendations: string[];
  metadata: Record<string, unknown>;
}
```

### Metadata Includes
```typescript
metadata: {
  scoreId: 'artist-momentum',           // Which score
  version: '1.0.0',                     // Score version
  featuresUsed: 4,                      // How many required features had data
  featuresTotal: 4,                     // Total required features
}
```

This allows any consumer to know **exactly how many data points contributed** to the result.

---

## ScoreReasoning — The Human Story

`ScoreReasoning` is what `score.reasoning(result, features)` returns. It transforms raw numbers into human understanding:

```typescript
interface ScoreReasoning {
  summary: string;              // "Artist Momentum: 72/100 — Strong (moderate confidence)..."
  factors: ContributingFactor[];// Full factor breakdown
  recommendations: string[];    // Actionable next steps
  dataQuality: string;          // "Good — most data dimensions available"
}
```

### Summary Format

```
{Score Name}: {score}/100 — {Level} ({confidence note}).
Driven by +{impact} {factor}, +{impact} {factor}.
Offset by -{impact} {factor}.
```

**Level thresholds**:
| Score Range | Label |
|-------------|-------|
| >= 80 | Exceptional |
| >= 65 | Strong |
| >= 50 | Moderate |
| >= 35 | Developing |
| < 35 | Emerging |

**Confidence notes**:
| Confidence Range | Note |
|-----------------|------|
| >= 80 | "high confidence" |
| >= 50 | "moderate confidence" |
| < 50 | "low confidence — more data needed" |

---

## ScoreOutput — The API Response

When the Score Engine runs, it produces `ScoreOutput` — the structure returned via API:

```typescript
interface ScoreOutput {
  id: string;                    // 'artist-momentum'
  name: string;                  // 'Artist Momentum'
  version: string;               // '1.0.0'
  category: string;              // 'growth'

  // Core
  score: number;                 // 72
  confidence: number;            // 68

  // Human explanation
  summary: string;               // One-line summary
  factors: Array<{               // Top factors
    name: string;
    impact: number;              // -100 to +100
    direction: string;           // 'positive' | 'negative'
    reasoning: string;           // "Growing at 15% — strong upward trajectory"
  }>;
  recommendations: string[];

  // Data quality
  dataQuality: string;           // "Good — most data dimensions available"

  // Trend analysis
  trend: string;                 // 'up' | 'down' | 'stable'
  volatility: number;            // 0–100

  // History summary
  history: {
    daily: number;               // entries in last 30 days
    weekly: number;              // entries in last 12 weeks
    monthly: number;             // entries in last 12 months
  };

  // Validation
  valid: boolean;                // true = computed successfully
  validationMessage: string;     // "All required features present"
}
```

---

## Confidence Model

Confidence is **data-driven**, not arbitrary. It uses four weighted dimensions:

```typescript
function calculateConfidence(input: ConfidenceInput): number {
  const featureScore =    requiredRatio * 0.7 + optionalRatio * 0.3;
  const freshnessScore =  dataFreshness;
  const platformScore =   min(1, platformCount / 3);
  const agreementScore =  factorAgreement;

  return featureScore * 0.40 +     // 40% — feature coverage
         freshnessScore * 0.25 +   // 25% — data freshness
         platformScore * 0.20 +    // 20% — platform diversity
         agreementScore * 0.15;    // 15% — factor agreement
}
```

| Dimension | Weight | How It's Measured |
|-----------|--------|-------------------|
| **Feature Coverage** | 40% | Required features present (70%) + Optional features present (30%) |
| **Data Freshness** | 25% | Currently returns 0.9 if any data exists. Future: cache staleness timestamps |
| **Platform Diversity** | 20% | `min(1, platformCount / 3)` — 3+ platforms = full score |
| **Factor Agreement** | 15% | How one-sided the factors are (all positive or all negative = high agreement) |

### When Confidence Is Zero
If `featuresRequired === 0` (no required features defined), confidence returns 0 immediately.

### Factor Agreement Calculation
```typescript
function computeFactorAgreement(factors: ContributingFactor[]): number {
  const ratio = Math.max(positiveCount, negativeCount) / total;
  const sizeBonus = Math.min(1, total / 5);  // 5+ factors = full bonus
  return ratio * 0.7 + sizeBonus * 0.3;
}
```

Agreement is higher when most factors point in the **same direction**. Volatility in signals reduces confidence.

---

## Contributing Factors

Each factor is a complete explainability unit:

```typescript
interface ContributingFactor {
  name: string;        // "Follower Growth Rate"
  value: number;       // Raw value that was measured
  impact: number;      // Net impact on final score (-100 to +100)
  weight: number;      // Weight applied to this factor (0-1)
  direction: string;   // 'positive' | 'negative'
  reasoning: string;   // Natural-language explanation
}
```

### How Factors Drive the Score

The score is computed as a **weighted average of factor impacts**:

```typescript
function weightedAverage(factors: ContributingFactor[]): number {
  const totalWeight = factors.reduce((a, f) => a + f.weight, 0);
  const weightedSum = factors.reduce((a, f) => a + f.impact * f.weight, 0);
  return 50 + weightedSum / totalWeight;  // 50 is neutral baseline
}
```

Each factor's `impact` is:
- A **normalized value** (0–100) × the factor's weight
- Multiplied by provider/market/genre adjustments
- Signed positive or negative based on whether the factor helps or hurts

The final score is the **cumulative effect of all factors** against a neutral baseline of 50.

---

## Data Quality Assessment

The `assessDataQuality()` function evaluates input completeness:

```typescript
function assessDataQuality(features: ArtistFeatures): string {
  // Checks 5 data health signals:
  const dataPoints = [
    features.platforms.length >= 1,
    features.followers > 0,
    features.engagementRate > 0,
    features.followerGrowth !== 0,
    features.albumCount > 0,
    features.platforms.length >= 2,
  ];
  // ...
}
```

| Data Points Present | Assessment |
|---------------------|------------|
| 6/6 | "Excellent — full data across multiple platforms" |
| 5/6 | "Good — most data dimensions available" |
| 3–4/6 | "Adequate — core metrics present, some gaps" |
| 0–2/6 | "Limited — few data points available, score may be unreliable" |

---

## Trend and Volatility

### Trend Direction
Determined by analyzing the change across the last 5 history entries:

```typescript
function determineTrend(history: ScoreHistoryEntry[]): TrendDirection {
  const avgChange = average of last 5 changes;
  if (avgChange > 3) return 'up';
  if (avgChange < -3) return 'down';
  return 'stable';
}
```

### Score Volatility
Measured as normalized standard deviation:

```typescript
function calculateVolatility(history: ScoreHistoryEntry[]): number {
  const stdDev = standardDeviation of scores;
  return min(100, (stdDev / 30) * 100);  // Max reasonable stdDev = 30 on 0–100 scale
}
```

| Volatility | Meaning |
|------------|---------|
| 0–15 | Stable — consistent score |
| 15–40 | Moderate fluctuation |
| 40–70 | Variable — significant changes |
| 70–100 | Highly volatile — rapidly changing |

---

## History: Daily, Weekly, Monthly

Every score evaluation is recorded in the `ScoreHistoryManager`:

```
Key: "{scoreId}:{artistName}"
```

### Retention
| Granularity | Retention | Max Entries |
|-------------|-----------|-------------|
| Daily | Last 30 days | 90 total |
| Weekly | Last 12 weeks | Aggregated from daily |
| Monthly | Last 12 months | Aggregated from daily |

### Aggregation
- **Daily**: Raw entries from last 30 days
- **Weekly**: Latest entry per 7-day window, last 12 weeks
- **Monthly**: Latest entry per 30-day window, last 12 months

### History Entry
```typescript
interface ScoreHistoryEntry {
  score: number;          // 0–100
  confidence: number;     // 0–100
  timestamp: string;      // ISO 8601
  trend: TrendDirection;  // 'up' | 'down' | 'stable'
  change: number;         // Absolute change from previous
  reason: string;         // "Increased by 5.2 — driven by Follower Growth Rate"
  factors: ContributingFactor[];
}
```

### Reason Inference
The history manager generates human-readable reasons for each change:

```typescript
if (Math.abs(change) < 1) return 'Stable — no significant change';
return `{Increased/Decreased} by {X} — driven by {top factor name}`;
```

---

## Complete Example

Here's what a complete score output looks like for **Artist Momentum** on an artist with strong growth:

```json
{
  "id": "artist-momentum",
  "name": "Artist Momentum",
  "version": "1.0.0",
  "category": "growth",
  "score": 72,
  "confidence": 68,
  "summary": "Artist Momentum: 72/100 — Strong (moderate confidence). Driven by +30 Follower Growth Rate, +18 Cross-Platform Presence. Offset by -8 Engagement Rate.",
  "factors": [
    {
      "name": "Follower Growth Rate",
      "impact": 30,
      "direction": "positive",
      "reasoning": "Growing at 15.0% — strong upward trajectory"
    },
    {
      "name": "Engagement Rate",
      "impact": -8,
      "direction": "negative",
      "reasoning": "Engagement at 2.1% — room for improvement"
    },
    {
      "name": "Cross-Platform Presence",
      "impact": 18,
      "direction": "positive",
      "reasoning": "Active on 4 platforms — diversified reach"
    },
    {
      "name": "Monthly Listener Growth",
      "impact": 22,
      "direction": "positive",
      "reasoning": "Monthly listeners growing at 12.0%"
    }
  ],
  "recommendations": [
    "Boost engagement rate — interactive content, polls, Q&As",
    "Capitalize on momentum — plan a major release or tour announcement"
  ],
  "dataQuality": "Good — most data dimensions available",
  "trend": "up",
  "volatility": 12,
  "history": { "daily": 8, "weekly": 4, "monthly": 2 },
  "valid": true,
  "validationMessage": "All required features present for Artist Momentum"
}
```

---

## Implementation Reference

The explainability pipeline lives in `src/scoring/reasoning.ts`:

| Function | Purpose |
|----------|---------|
| `buildReasoning(scoreName, result, features)` | Creates full ScoreReasoning with summary, factors, data quality |
| `buildSummary(scoreName, result, topPositive, topNegative)` | Generates one-line natural language summary |
| `assessDataQuality(features)` | Evaluates input completeness across 6 signals |
| `formatFactors(factors)` | Formats factor list for display with sorting |
| `determineTrend(history)` | Calculates trend direction from last 5 entries |
| `calculateVolatility(history)` | Computes normalized standard deviation |
| `formatScoreForDisplay(scoreName, result, features, history?)` | Full display-ready output object |

Related files:
- `src/scoring/confidence.ts` — Confidence calculation and factor agreement
- `src/scoring/base-score.ts` — Template method that orchestrates the explainability pipeline
- `src/scoring/score-history.ts` — History recording and aggregation
- `src/scoring/score-engine.ts` — Builds ScoreOutput from ScoreResult + ScoreReasoning + History

## See Also

- [AI Scoring Philosophy](./AI_SCORING.md) — Why explainability matters
- [Score Engine Reference](./SCORE_ENGINE.md) — Full score architecture and API
- [Score Registry Guide](./SCORE_REGISTRY.md) — Managing score lifecycle
