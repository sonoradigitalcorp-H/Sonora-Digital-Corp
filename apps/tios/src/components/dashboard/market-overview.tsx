'use client';

import useSWR from 'swr';

const fetcher = (url: string) => fetch(url).then(r => r.json());

export function MarketOverview() {
  const { data, error, isLoading } = useSWR('/api/v1/market', fetcher);

  if (error) {
    return (
      <div className="kpi-card p-4">
        <p className="text-destructive text-xs">Failed to load market data</p>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="kpi-card animate-pulse">
        <div className="px-4 pt-4 pb-3 border-b border-border">
          <div className="h-4 w-24 bg-muted rounded" />
          <div className="h-2.5 w-28 bg-muted rounded mt-1.5" />
        </div>
        <div>
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="px-4 py-3 space-y-1">
              <div className="flex items-center justify-between">
                <div className="h-2.5 w-20 bg-muted rounded" />
                <div className="h-2.5 w-8 bg-muted rounded" />
              </div>
              <div className="h-3.5 w-28 bg-muted rounded" />
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
      <div className="kpi-card p-4">
        <p className="text-muted-foreground text-xs">No market data available</p>
      </div>
    );
  }

  return (
    <div className="kpi-card">
      <div className="px-4 pt-4 pb-3 border-b border-border">
        <h2 className="text-sm font-semibold tracking-tight">Market Pulse</h2>
        <p className="text-[11px] text-muted-foreground mt-0.5">Key market indicators</p>
      </div>

      <div>
        {items.map((item) => (
          <div key={item.label} className="px-4 py-3">
            <div className="flex items-center justify-between mb-0.5">
              <p className="text-[11px] text-muted-foreground">{item.label}</p>
              {item.growth && (
                <span className={`text-[10px] font-medium ${String(item.growth).startsWith('+') ? 'text-green-500' : 'text-rose-500'}`}>
                  {item.growth}
                </span>
              )}
            </div>
            <p className="text-sm font-medium">{item.value}</p>
          </div>
        ))}
      </div>

      <div className="p-3 border-t border-border">
        <button className="w-full text-center text-xs text-muted-foreground hover:text-foreground transition-colors">
          Full Market Report →
        </button>
      </div>
    </div>
  );
}
