'use client';

import { Sparkles, Music2, TrendingUp, Globe, UserPlus } from 'lucide-react';
import useSWR from 'swr';

const fetcher = (url: string) => fetch(url).then(r => r.json());

const typeIcons: Record<string, typeof Sparkles> = {
  breakout: TrendingUp,
  discovery: Sparkles,
  milestone: Music2,
  market: Globe,
  signing: UserPlus,
};

const typeColors: Record<string, string> = {
  breakout: 'text-green-500 bg-green-500/10',
  discovery: 'text-purple-400 bg-purple-400/10',
  milestone: 'text-primary bg-primary/10',
  market: 'text-cyan-400 bg-cyan-400/10',
  signing: 'text-amber-400 bg-amber-400/10',
};

export function DiscoveryFeed() {
  const { data, error, isLoading } = useSWR('/api/v1/discovery?count=5', fetcher);

  if (error) {
    return (
      <div className="kpi-card p-4">
        <p className="text-destructive text-xs">Failed to load discovery feed</p>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="kpi-card animate-pulse">
        <div className="px-4 pt-4 pb-3 border-b border-border flex items-center justify-between">
          <div className="space-y-1.5">
            <div className="h-4 w-32 bg-muted rounded" />
            <div className="h-2.5 w-28 bg-muted rounded" />
          </div>
          <div className="h-3 w-6 bg-muted rounded" />
        </div>
        <div>
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="flex items-start gap-4 px-4 py-3">
              <div className="w-7 h-7 rounded-md bg-muted" />
              <div className="flex-1 space-y-1">
                <div className="h-3.5 w-24 bg-muted rounded" />
                <div className="h-2.5 w-40 bg-muted rounded" />
              </div>
              <div className="h-2.5 w-8 bg-muted rounded" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  const items = Array.isArray(data) ? data : data?.items ?? data?.discoveries ?? [];

  if (!items.length) {
    return (
      <div className="kpi-card p-6 text-center">
        <Sparkles className="h-6 w-6 text-muted-foreground mx-auto mb-2" />
        <p className="text-xs text-muted-foreground">No recent discoveries</p>
      </div>
    );
  }

  return (
    <div className="kpi-card">
      <div className="px-4 pt-4 pb-3 border-b border-border flex items-center justify-between">
        <div>
          <h2 className="text-sm font-semibold tracking-tight">Live Discovery Feed</h2>
          <p className="text-[11px] text-muted-foreground mt-0.5">Real-time intelligence stream</p>
        </div>
        <span className="badge badge-live">
          <span className="w-1.5 h-1.5 rounded-full bg-green-500" />
          Live
        </span>
      </div>

      <div>
        {items.map((item: {
          id?: string;
          type: string;
          artist?: string;
          description: string;
          time: string;
        }, i: number) => {
          const Icon = typeIcons[item.type] ?? Sparkles;
          const colorClass = typeColors[item.type] ?? 'bg-muted text-muted-foreground';
          return (
            <div key={item.id ?? i} className="flex items-start gap-4 px-4 py-3 hover:bg-surface-hover transition-colors">
              <div className={`p-1.5 rounded-md ${colorClass} shrink-0`}>
                <Icon className="h-3.5 w-3.5" />
              </div>
              <div className="flex-1 min-w-0">
                {item.artist && (
                  <p className="text-xs font-medium">{item.artist}</p>
                )}
                <p className="text-[11px] text-muted-foreground">{item.description}</p>
              </div>
              <span className="text-[10px] text-muted-foreground whitespace-nowrap">{item.time}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
