'use client';

import useSWR from 'swr';

const fetcher = (url: string) => fetch(url).then(r => r.json());

export function MarketOverview() {
  const { data, error, isLoading } = useSWR('/api/v1/market', fetcher);

  if (error) {
    return (
      <div className="rounded-xl border bg-card p-5">
        <p className="text-destructive text-sm">Failed to load market data</p>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="rounded-xl border bg-card animate-pulse">
        <div className="p-5 border-b">
          <div className="h-5 w-28 bg-muted rounded" />
          <div className="h-3 w-32 bg-muted rounded mt-2" />
        </div>
        <div className="divide-y">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="p-4 space-y-1">
              <div className="flex items-center justify-between">
                <div className="h-3 w-24 bg-muted rounded" />
                <div className="h-3 w-10 bg-muted rounded" />
              </div>
              <div className="h-4 w-32 bg-muted rounded" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  const items: { label: string; value: string; growth?: string }[] = [];

  if (data?.metrics) {
    data.metrics.forEach((m: { label: string; value: string; growth?: string }) => items.push(m));
  }

  if (data?.genreMetrics) {
    Object.entries(data.genreMetrics).forEach(([genre, val]) => {
      items.push({ label: `Genre: ${genre}`, value: String(val) });
    });
  }

  if (data?.topGenres) {
    data.topGenres.forEach((g: { name: string; share?: number; percentage?: number; growth?: string }) => {
      items.push({
        label: g.name,
        value: `${g.share ?? g.percentage ?? 0}%`,
        growth: g.growth,
      });
    });
  }

  if (!items.length) {
    return (
      <div className="rounded-xl border bg-card p-5">
        <p className="text-muted-foreground text-sm">No market data available</p>
      </div>
    );
  }

  return (
    <div className="rounded-xl border bg-card">
      <div className="p-5 border-b">
        <h2 className="font-semibold">Market Pulse</h2>
        <p className="text-xs text-muted-foreground mt-0.5">Key market indicators</p>
      </div>

      <div className="divide-y">
        {items.map((item) => (
          <div key={item.label} className="p-4">
            <div className="flex items-center justify-between mb-1">
              <p className="text-xs text-muted-foreground">{item.label}</p>
              {item.growth && (
                <span className={`text-xs font-medium ${String(item.growth).startsWith('+') ? 'text-green-500' : 'text-orange-500'}`}>
                  {item.growth}
                </span>
              )}
            </div>
            <p className="text-sm font-medium">{item.value}</p>
          </div>
        ))}
      </div>

      <div className="p-3 border-t">
        <button className="w-full text-center text-sm text-muted-foreground hover:text-foreground transition-colors">
          Full Market Report →
        </button>
      </div>
    </div>
  );
}
