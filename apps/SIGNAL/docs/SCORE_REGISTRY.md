# Score Registry — Managing Score Lifecycle

> **Version**: 1.0.0  
> **Status**: Production  
> **Last Updated**: July 2026

---

## Table of Contents

1. [Overview](#overview)
2. [API Reference](#api-reference)
3. [Registration Lifecycle](#registration-lifecycle)
4. [Enable / Disable](#enable--disable)
5. [Weight Configuration](#weight-configuration)
6. [Singleton Pattern](#singleton-pattern)
7. [Creating a Custom Score](#creating-a-custom-score)
8. [Factory: createDefaultScores](#factory-createdefaultscores)
9. [Testing](#testing)

---

## Overview

The Score Registry is the **central catalog** of all score modules. It manages:

- **Registration** — adding scores to the system
- **Versioning** — tracking which version of each score is registered
- **Enable/Disable** — turning scores on and off at runtime
- **Lookup** — retrieving scores by ID, category, or enabled status
- **Lifecycle** — initializing scores during registration

```
┌─────────────────────────────────────────────────────────────┐
│                     Score Registry                            │
│                                                               │
│  scores: Map<id, BaseScore>     registrations: Map<id, Reg>   │
│  ┌────────────────────────┐   ┌──────────────────────────┐   │
│  │ artist-momentum   v1.0 │   │ { enabled: true,         │   │
│  │ growth-velocity   v1.0 │   │   createdAt: ISO,        │   │
│  │ discovery-score   v1.0 │   │   updatedAt: ISO }       │   │
│  │ audience-quality  v1.0 │   └──────────────────────────┘   │
│  │ virality-index    v1.0 │                                    │
│  │ ... (10 total)         │                                    │
│  └────────────────────────┘                                    │
└─────────────────────────────────────────────────────────────┘
```

---

## API Reference

### `getRegistry()`

Returns the singleton Score Registry instance.

```typescript
import { getRegistry } from '@/scoring';

const registry = getRegistry();
```

### `register(score)`

Register a new score module. Scores are **enabled by default**.

```typescript
import { getRegistry } from '@/scoring';
import { MomentumScore } from '@/scoring/scores';

const registry = getRegistry();
await registry.register(new MomentumScore());
```

**Registration behavior:**
1. Calls `score.initialize()` (sets `initialized = true`)
2. If a score with the same ID already exists, it **replaces** the existing one silently
3. Preserves the original `createdAt` timestamp on re-registration
4. Updates `updatedAt` to the current time
5. Sets `enabled: true` by default

**Re-registration protection**: If the existing registration has a **higher or equal version**, the new one still replaces it (allows hot-reloading). If the same ID is registered again, the old score is removed before the new one is initialized.

### `unregister(scoreId)`

Remove a score from the registry entirely.

```typescript
registry.unregister('artist-momentum');
```

Removes both the score module and its registration metadata.

### `get(scoreId)`

Get a registered score by ID.

```typescript
const score = registry.get('artist-momentum');
// Returns BaseScore | undefined
```

### `getAll()`

Get all registered score instances.

```typescript
const allScores = registry.getAll();
// Returns BaseScore[]
```

### `getEnabled()`

Get only scores that are currently enabled.

```typescript
const enabledScores = registry.getEnabled();
// Returns BaseScore[] — only enabled scores
```

Used internally by the Score Engine when `evaluate()` runs.

### `enable(scoreId)`

Enable a score so it's included in evaluations.

```typescript
registry.enable('discovery-score');
```

### `disable(scoreId)`

Disable a score so it's excluded from evaluations.

```typescript
registry.disable('label-readiness');
```

### `isEnabled(scoreId)`

Check whether a score is enabled.

```typescript
if (registry.isEnabled('virality-index')) {
  // Score will run during evaluation
}
```

Returns `false` if the score is not registered.

### `getRegistration(scoreId)`

Get full registration metadata for a score.

```typescript
const reg = registry.getRegistration('artist-momentum');
// Returns ScoreRegistration | undefined
```

### `getAllRegistrations()`

Get registration metadata for all scores.

```typescript
const registrations = registry.getAllRegistrations();
// Returns ScoreRegistration[]
```

### `getState()`

Get the full registry state (for dashboard display).

```typescript
const state = registry.getState();
// Returns { scores: Map, version: string }
```

### `size`

Get the count of registered scores.

```typescript
console.log(registry.size);  // 10
```

### `reset()`

Clear all registrations from the registry (primarily for testing).

```typescript
registry.reset();
```

### `resetRegistry()`

Reset the registry singleton entirely (clears and nullifies the instance).

```typescript
import { resetRegistry } from '@/scoring';

resetRegistry();  // Next call to getRegistry() creates a fresh instance
```

---

## Registration Lifecycle

```
1. new ScoreModule()           → Instance created
2. registry.register(score)    → Calls score.initialize()
3. score.initialized = true    → Ready for use
4. registry.get(scoreId)       → Available for lookup
5. registry.getEnabled()       → Included in evaluations (if enabled)
6. registry.disable(scoreId)   → Excluded from evaluations
7. registry.enable(scoreId)    → Re-included
8. registry.unregister(scoreId)→ Removed entirely
```

### ScoreRegistration Metadata

```typescript
interface ScoreRegistration {
  identity: ScoreIdentity;  // id, version, name, description, category
  enabled: boolean;         // Whether score runs during evaluation
  createdAt: string;        // ISO timestamp of first registration
  updatedAt: string;        // ISO timestamp of last update
}
```

---

## Enable / Disable

By default, all scores are **enabled** when registered. The enable/disable mechanism allows:

- **Runtime toggling** — turn scores on/off without restarting
- **A/B testing** — run experiments with different score combinations
- **Graceful degradation** — disable complex scores when data is limited
- **Feature flags** — roll out new scores gradually

```typescript
// Disable all commercial scores
['label-readiness', 'tour-readiness', 'brand-partnership'].forEach(
  (id) => registry.disable(id)
);

// Only run growth scores
const growthScores = registry.getAll().filter(
  (s) => s.identity.category === 'growth'
);
```

---

## Weight Configuration

Weights are configured **per-score** via `ScoreInputSpec.defaultWeights`, with optional **global overrides**.

### Priority Order (lowest to highest)

```
1. Global defaults      (system-wide baseline, from weights.ts)
2. Score defaults        (score-specific, from ScoreInputSpec.defaultWeights)
                         ── Score defaults OVERRIDE global defaults ──
3. Global overrides      (user config from setGlobalWeights())
4. Provider multipliers  (adjusted per provider, e.g. Spotify ×1.0, SoundCloud ×0.5)
5. Market multipliers    (adjusted per market, e.g. US ×1.0, NG ×0.65)
6. Genre multipliers     (adjusted per genre, e.g. Pop ×1.0, Classical ×0.5)
```

### Setting Global Overrides

```typescript
import { setGlobalWeights } from '@/scoring/weights';

// Override weights globally
setGlobalWeights({
  global: {
    followerGrowth: 1.2,  // Boost follower growth importance
    engagementRate: 0.5,  // Reduce engagement importance
  },
  providers: {
    tiktok: 0.9,  // Reduce TikTok weight
  },
});
```

### Provider Default Multipliers

| Provider | Multiplier |
|----------|-----------|
| Spotify | 1.0 |
| YouTube | 0.9 |
| Instagram | 0.85 |
| TikTok | 0.8 |
| Apple Music | 0.7 |
| Deezer | 0.6 |
| SoundCloud | 0.5 |
| Bandcamp | 0.5 |

### Market Default Multipliers

| Market | Multiplier |
|--------|-----------|
| US | 1.0 |
| GB | 0.9 |
| JP | 0.85 |
| KR | 0.8 |
| DE | 0.85 |
| FR | 0.85 |
| BR | 0.8 |
| MX | 0.75 |
| IN | 0.7 |
| NG | 0.65 |

### Genre Default Multipliers

| Genre | Multiplier |
|-------|-----------|
| Pop | 1.0 |
| Hip Hop / Rap / R&B | 1.0 |
| Electronic | 0.9 |
| Rock | 0.85 |
| Indie | 0.8 |
| Latin / Reggaeton / Afrobeats / K-Pop | 0.85–0.9 |
| Country | 0.8 |
| Metal | 0.7 |
| Jazz / Classical | 0.5–0.6 |

### ML Weights (Future)

```typescript
import { enableMLWeights } from '@/scoring/weights';

// When ML model is available:
enableMLWeights('/models/weight-predictor-v1.onnx');
```

The `enableMLWeights()` function is a placeholder. When implemented, it will replace static weights with model-predicted weights per artist per score.

---

## Singleton Pattern

The Score Registry uses a **lazy singleton** pattern:

```typescript
class ScoreRegistry {
  private static instance: ScoreRegistry;

  static getInstance(): ScoreRegistry {
    if (!ScoreRegistry.instance) {
      ScoreRegistry.instance = new ScoreRegistry();
    }
    return ScoreRegistry.instance;
  }
}
```

The public API wraps this:

```typescript
export function getRegistry(): ScoreRegistry {
  return ScoreRegistry.getInstance();
}

export function resetRegistry(): void {
  const reg = ScoreRegistry.getInstance();
  reg.reset();               // Clear all scores
  ScoreRegistry.resetInstance();  // Nullify singleton
}
```

This pattern ensures:
- **One registry** throughout the application lifetime
- **Reset capability** for testing (each test gets a clean slate)
- **Direct class access** for advanced testing scenarios

**For most code**, use `getRegistry()`. **For tests**, you can also instantiate `new ScoreRegistry()` directly to get isolated instances.

---

## Creating a Custom Score

To create a new score module, extend `BaseScore` and implement three methods:

```typescript
import { BaseScore, clamp, normalizeToRange, weightedAverage } from '@/scoring/base-score';
import type { ArtistFeatures, ScoreInputSpec, ScoreIdentity, WeightConfig, ContributingFactor } from '@/scoring/types';

export class MyCustomScore extends BaseScore {
  readonly identity: ScoreIdentity = {
    id: 'my-custom-score',
    version: '1.0.0',
    name: 'My Custom Score',
    description: 'Description of what this score measures',
    category: 'growth', // One of: growth | audience | commercial | discovery | performance
  };

  readonly spec: ScoreInputSpec = {
    required: ['followers', 'followerGrowth'],
    optional: ['engagementRate', 'crossPlatformPresence'],
    minimumConfidence: 30,
    defaultWeights: {
      followerGrowth: 1.0,
      followers: 0.5,
      engagementRate: 0.7,
    },
  };

  protected computeFactors(
    features: ArtistFeatures,
    weights: WeightConfig
  ): ContributingFactor[] {
    // Compute your factors here
    return factors;
  }

  protected aggregateScore(
    factors: ContributingFactor[],
    weights: WeightConfig
  ): number {
    return clamp(weightedAverage(factors), 0, 100);
  }

  protected generateRecommendations(
    score: number,
    factors: ContributingFactor[],
    features: ArtistFeatures
  ): string[] {
    // Generate recommendations based on score and factors
    return [];
  }
}
```

### Registration

```typescript
import { getRegistry } from '@/scoring';
import { MyCustomScore } from './my-custom-score';

const registry = getRegistry();
await registry.register(new MyCustomScore());
```

### Requirements for a Valid Score

1. **Unique ID** — must not conflict with existing scores
2. **At least 3 required features** — for meaningful computation
3. **Confidence threshold >= 25** — to prevent unreliable results
4. **All three abstract methods** — `computeFactors`, `aggregateScore`, `generateRecommendations`
5. **Category** — one of the 5 defined categories
6. **Weights** — at least assign weight to each required feature

---

## Factory: createDefaultScores

SIGNAL ships with a factory that registers all 10 default scores:

```typescript
import { createDefaultScores } from '@/scoring/scores';

// Register all 10 scores in one call
const scores = await createDefaultScores();
// Returns MomentumScore[], GrowthVelocityScore[], ... (10 scores)
```

This is called during system initialization. The 10 scores are:

| # | ID | Category | Required Features |
|---|----|----------|-------------------|
| 1 | `artist-momentum` | growth | followers, followerGrowth, engagementRate, crossPlatformPresence |
| 2 | `growth-velocity` | growth | followerGrowth, followers, monthlyListeners |
| 3 | `discovery-score` | discovery | followerGrowth, crossPlatformPresence, engagementRate |
| 4 | `audience-quality` | audience | engagementRate, followers, crossPlatformPresence |
| 5 | `virality-index` | performance | followerGrowth, engagementRate, crossPlatformPresence |
| 6 | `label-readiness` | commercial | followers, followerGrowth, engagementRate, albumCount, crossPlatformPresence |
| 7 | `fan-conversion` | audience | engagementRate, followers, monthlyListeners |
| 8 | `tour-readiness` | commercial | followers, engagementRate, albumCount, monthlyListeners |
| 9 | `brand-partnership` | commercial | engagementRate, followers, crossPlatformPresence |
| 10 | `global-expansion` | growth | followerGrowth, crossPlatformPresence, followers |

---

## Testing

### Test Pattern for Score Registry Tests

Tests use **direct instances** of `ScoreRegistry` to avoid singleton state bleed:

```typescript
import { ScoreRegistry } from '@/scoring/score-registry';

describe('My Score Tests', () => {
  const createRegistry = () => new ScoreRegistry();

  it('should register my custom score', async () => {
    const registry = createRegistry();
    await registry.register(new MyCustomScore());
    expect(registry.get('my-custom-score')).toBeDefined();
    expect(registry.size).toBe(1);
  });
});
```

### Test Pattern for Score Engine Integration

Integration tests use the singleton but reset between tests:

```typescript
import { getEngine, resetEngine } from '@/scoring/score-engine';
import { getRegistry, resetRegistry } from '@/scoring/score-registry';
import { resetHistoryManager } from '@/scoring/score-history';
import { createDefaultScores } from '@/scoring/scores';

describe('Score Engine Integration', () => {
  beforeEach(async () => {
    resetEngine();
    resetRegistry();
    resetHistoryManager();
    await createDefaultScores();  // Register all scores fresh
  });

  afterEach(() => {
    resetEngine();
    resetRegistry();
    resetHistoryManager();
  });

  it('should evaluate scores', async () => {
    const engine = getEngine();
    const result = await engine.evaluate(artist);
    expect(result.scoresComputed).toBeGreaterThan(0);
  });
});
```

---

## See Also

- [Score Engine Reference](./SCORE_ENGINE.md) — How the registry is used by the engine
- [AI Scoring Philosophy](./AI_SCORING.md) — Overview of the scoring system
- [Explainability Guide](./EXPLAINABILITY.md) — How scores justify their results
