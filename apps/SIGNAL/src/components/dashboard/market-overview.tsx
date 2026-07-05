'use client';

import useSWR from 'swr';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

const fetcher = (url: string) => fetch(url).then(r => r.json());

function Sparkline({ data, color = '#3B82F6', height = 24 }: { data?: number[]; color?: string; height?: number }) {
  const points = data && data.length > 0 ? data : [30, 45, 38, 52, 48, 60, 55, 62];
  const max = Math.max(...points) || 1;
  const min = Math.min(...points) || 0;
  const range = max - min || 1;
  const width = points.length * 6;

  const pathD = points.map((p, i) => {
    const x = (i / (points.length - 1)) * width;
    const y = height - ((p - min) / range) * (height - 4) - 2;
    return `${i === 0 ? 'M' : 'L'} ${x} ${y}`;
  }).join(' ');

  return (
    <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`} className="w-full h-full" preserveAspectRatio="none">
      <path d={pathD} fill="none" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

export function MarketOverview() {
  const { data, error, isLoading } = useSWR('/api/v1/market', fetcher);

  if (error) {
    return <div className="kpi-card p-4"><p className="text-destructive text-xs">Failed to load market data</p></div>;
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

  const items: { label: string; value: string; growth?: string; history?: number[] }[] = [];

  if (data?.metrics) {
    data.metrics.forEach((m: { label: string; value: string; growth?: string; history?: number[] }) => items.push(m));
  }
  if (data?.genreMetrics) {
    Object.entries(data.genreMetrics).forEach(([genre, val]) => {
      items.push({ label: `Genre: ${genre}`, value: String(val) });
    });
  }
  if (data?.topGenres) {
    data.topGenres.forEach((g: { name: string; share?: number; percentage?: number; growth?: string }) => {
      items.push({ label: g.name, value: `${g.share ?? g.percentage ?? 0}%`, growth: g.growth });
    });
  }

  if (!items.length) {
    return <div className="kpi-card p-4"><p className="text-muted-foreground text-xs">No market data available</p></div>;
  }

  return (
    <div className="kpi-card">
      <div className="px-4 pt-4 pb-3 border-b border-border">
        <h2 className="text-sm font-semibold tracking-tight">Market Pulse</h2>
        <p className="text-[11px] text-muted-foreground mt-0.5">Key market indicators</p>
      </div>

      <div>
        {items.slice(0, 5).map((item) => {
          const growthNum = item.growth ? parseFloat(String(item.growth).replace(/[+%]/g, '')) : 0;
          const isPositive = growthNum >= 0;
          return (
            <div key={item.label} className="flex items-center justify-between px-4 py-3 data-row">
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between">
                  <p className="text-xs text-muted-foreground truncate">{item.label}</p>
                  {item.growth && (
                    <span className={`flex items-center gap-0.5 text-[10px] font-medium tabular-nums ${isPositive ? 'text-green-500' : 'text-rose-500'}`}>
                      {isPositive ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
                      {item.growth}
                    </span>
                  )}
                </div>
                <p className="text-sm font-semibold tabular-nums mt-0.5">{item.value}</p>
              </div>
              <div className="w-20 h-6 ml-3 opacity-40">
                <Sparkline data={item.history} />
              </div>
            </div>
          );
        })}
      </div>

      <div className="p-3 border-t border-border">
        <button className="w-full text-center text-xs text-muted-foreground hover:text-foreground transition-colors group">
          Full Market Report <span className="inline-block transition-transform group-hover:translate-x-0.5">→</span>
        </button>
      </div>
    </div>
  );
}
