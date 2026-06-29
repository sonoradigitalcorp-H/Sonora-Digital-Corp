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

const typeTextColors: Record<string, string> = {
  breakout: 'text-green-500',
  discovery: 'text-purple-500',
  milestone: 'text-blue-500',
  market: 'text-cyan-500',
  signing: 'text-amber-500',
};

const typeBgColors: Record<string, string> = {
  breakout: 'bg-green-500/10',
  discovery: 'bg-purple-500/10',
  milestone: 'bg-blue-500/10',
  market: 'bg-cyan-500/10',
  signing: 'bg-amber-500/10',
};

export function DiscoveryFeed() {
  const { data, error, isLoading } = useSWR('/api/v1/discovery?count=5', fetcher);

  if (error) {
    return (
      <div className="rounded-xl border bg-card p-5">
        <p className="text-destructive text-sm">Failed to load discovery feed</p>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="rounded-xl border bg-card animate-pulse">
        <div className="p-5 border-b flex items-center justify-between">
          <div className="space-y-2">
            <div className="h-5 w-36 bg-muted rounded" />
            <div className="h-3 w-32 bg-muted rounded" />
          </div>
          <div className="h-4 w-10 bg-muted rounded" />
        </div>
        <div className="divide-y">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="flex items-start gap-4 p-4">
              <div className="w-8 h-8 rounded-lg bg-muted" />
              <div className="flex-1 space-y-1">
                <div className="h-4 w-28 bg-muted rounded" />
                <div className="h-3 w-48 bg-muted rounded" />
              </div>
              <div className="h-3 w-10 bg-muted rounded" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  const items = Array.isArray(data) ? data : data?.items ?? data?.discoveries ?? [];

  if (!items.length) {
    return (
      <div className="rounded-xl border bg-card p-5 text-center">
        <Sparkles className="h-8 w-8 text-muted-foreground mx-auto mb-2" />
        <p className="text-sm text-muted-foreground">No recent discoveries</p>
      </div>
    );
  }

  return (
    <div className="rounded-xl border bg-card">
      <div className="p-5 border-b flex items-center justify-between">
        <div>
          <h2 className="font-semibold">Live Discovery Feed</h2>
          <p className="text-xs text-muted-foreground mt-0.5">Real-time intelligence stream</p>
        </div>
        <span className="flex items-center gap-1 text-xs text-muted-foreground">
          <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
          Live
        </span>
      </div>

      <div className="divide-y">
        {items.map((item: {
          id?: string;
          type: string;
          artist?: string;
          description: string;
          time: string;
        }, i: number) => {
          const Icon = typeIcons[item.type] ?? Sparkles;
          const textColor = typeTextColors[item.type] ?? 'text-muted-foreground';
          const bgColor = typeBgColors[item.type] ?? 'bg-muted';
          return (
            <div key={item.id ?? i} className="flex items-start gap-4 p-4 hover:bg-accent/50 transition-colors">
              <div className={`p-2 rounded-lg ${bgColor}`}>
                <Icon className={`h-4 w-4 ${textColor}`} />
              </div>
              <div className="flex-1 min-w-0">
                {item.artist && (
                  <p className="text-sm font-medium">{item.artist}</p>
                )}
                <p className="text-sm text-muted-foreground">{item.description}</p>
              </div>
              <span className="text-xs text-muted-foreground whitespace-nowrap">{item.time}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
