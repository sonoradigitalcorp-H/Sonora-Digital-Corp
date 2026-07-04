# Frontend Consumption Guide — SIGNAL Intelligence

> **Rule:** The frontend **never** accesses providers, raw features, or internal scoring logic.  
> **All data comes from** `GET /api/v1/intelligence/[id]`.

## SWR Pattern

```tsx
import useSWR from 'swr';

const fetcher = (url: string) => fetch(url).then(r => r.json());

function ArtistIntelligence({ artistId }: { artistId: string }) {
  const { data, error, isLoading } = useSWR(
    `/api/v1/intelligence/${artistId}`,
    fetcher,
    { revalidateOnFocus: false }
  );

  if (isLoading) return <Loader />;
  if (error) return <ErrorState />;
  if (!data) return <EmptyState />;

  return (
    <div>
      <AggregateScore value={data.aggregate.score} />
      <ScoreGrid scores={data.scores} />
      <InsightPanel insights={data.insights} />
    </div>
  );
}
```

## Available Data

### Artist Profile

```ts
data.artist: {
  id: string;
  name: string;
  genres: string[];
  country: string | null;
  image: string | null;
}
```

### Aggregate Intelligence

```ts
data.aggregate: {
  score: number;        // 0-100
  confidence: number;   // 0-100
  scoresComputed: number;
  scoresSkipped: number;
}
```

### Individual Scores

Each score has full explainability built-in:

```ts
data.scores: [{
  id: string;           // e.g., "artist-momentum"
  name: string;         // e.g., "Artist Momentum"
  category: string;     // growth | audience | commercial | discovery | performance
  score: number;        // 0-100
  confidence: number;   // 0-100
  summary: string;      // one-line human readable
  factors: [{           // what influenced the score
    name: string;
    impact: number;
    direction: 'positive' | 'negative';
    reasoning: string;
  }];
  recommendations: string[];  // actionable steps
  dataQuality: string;        // human-readable quality assessment
  trend: 'up' | 'down' | 'stable';
  volatility: number;         // 0-100
  valid: boolean;
}]
```

### Insights

```ts
data.insights: {
  items: [{
    type: 'growth' | 'risk' | 'opportunity' | 'achievement' | 'warning';
    message: string;
    severity: 'high' | 'medium' | 'low';
    category: string;
    source: string;
  }];
  summary: string[];  // top 2-3 most important insights
}
```

### Feature Metadata

```ts
data.features.platforms: [{
  name: string;       // e.g., "followers", "engagementRate"
  value: number;      // actual value
  quality: number;    // 0-1
  provider: string;   // e.g., "spotify", "instagram"
  source: 'provider' | 'extracted' | 'default';
}]
```

## Score Display Guidelines

### Score Colors

| Range | Color | Meaning |
|-------|-------|---------|
| 80-100 | Green (`text-green-400`) | Exceptional |
| 60-79 | Blue (`text-primary`) | Strong |
| 40-59 | Amber (`text-amber-400`) | Moderate |
| 0-39 | Red (`text-rose-400`) | Needs attention |

### Insight Severity

| Severity | Style |
|----------|-------|
| `high` | Rose/red background border |
| `medium` | Amber background border |
| `low` | Muted background border |

### Insight Types

| Type | Icon | Meaning |
|------|------|---------|
| `growth` | TrendingUp | Positive momentum |
| `risk` | AlertTriangle | Metrics declining |
| `opportunity` | Lightbulb | Untapped potential |
| `achievement` | Award | Exceptional scores |
| `warning` | AlertTriangle | Below average |

## No Direct Provider Access

```tsx
// ❌ WRONG — Frontend accesses providers directly
const spotifyData = await fetch('/api/v1/providers/spotify/artist/123');

// ✅ CORRECT — Frontend uses Intelligence API
const intelligence = await fetch('/api/v1/intelligence/art-amg-01');
```

## Example: Complete Dashboard Component

```tsx
'use client';
import useSWR from 'swr';
import { BrainCircuit, Loader2 } from 'lucide-react';

export function IntelligenceView({ artistId }: { artistId: string }) {
  const { data, error, isLoading } = useSWR(
    `/api/v1/intelligence/${artistId}`,
    (url: string) => fetch(url).then(r => r.json())
  );

  if (isLoading) return <Loader2 className="animate-spin" />;
  if (error) return <div className="text-rose-400">Failed to load</div>;
  if (!data) return null;

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold">{data.artist.name}</h2>
      <div className="text-2xl font-black">{data.aggregate.score}/100</div>
    </div>
  );
}
```
