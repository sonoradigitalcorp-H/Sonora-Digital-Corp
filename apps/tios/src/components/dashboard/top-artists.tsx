'use client';

import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import useSWR from 'swr';

const fetcher = (url: string) => fetch(url).then(r => r.json());

const TrendIcon = ({ growth }: { growth: number }) => {
  if (growth > 0) return <TrendingUp className="h-3 w-3 text-green-500" />;
  if (growth < 0) return <TrendingDown className="h-3 w-3 text-red-500" />;
  return <Minus className="h-3 w-3 text-muted-foreground" />;
};

export function TopArtists() {
  const { data, error, isLoading } = useSWR('/api/v1/analytics', fetcher);

  if (error) {
    return (
      <div className="kpi-card p-4">
        <p className="text-destructive text-xs">Failed to load top artists</p>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="kpi-card animate-pulse">
        <div className="px-4 pt-4 pb-3 border-b border-border">
          <div className="h-4 w-36 bg-muted rounded" />
          <div className="h-2.5 w-28 bg-muted rounded mt-1.5" />
        </div>
        <div>
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="flex items-center gap-4 px-4 py-3">
              <div className="w-5 h-3 bg-muted rounded" />
              <div className="w-9 h-9 rounded-full bg-muted" />
              <div className="flex-1 space-y-1">
                <div className="h-3.5 w-24 bg-muted rounded" />
                <div className="h-2.5 w-16 bg-muted rounded" />
              </div>
              <div className="flex items-center gap-2">
                <div className="h-3 w-10 bg-muted rounded" />
                <div className="w-10 h-7 rounded-md bg-muted" />
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  const artists = data?.topForSigning ?? [];

  if (!artists.length) {
    return (
      <div className="kpi-card p-4">
        <p className="text-muted-foreground text-xs">No artist data available</p>
      </div>
    );
  }

  return (
    <div className="kpi-card">
      <div className="px-4 pt-4 pb-3 border-b border-border">
        <h2 className="text-sm font-semibold tracking-tight">Top Artists by Discovery Score</h2>
        <p className="text-[11px] text-muted-foreground mt-0.5">Real-time intelligence ranking</p>
      </div>

      <div>
        {artists.map((artist: {
          rank: number;
          name: string;
          score: number;
          growth: number;
          listeners?: number;
          dealEstimate?: number;
          momentum?: number;
          reason?: string;
          image?: string;
          photoUrl?: string;
          contact?: string;
        }) => (
          <div key={artist.rank} className="flex items-center gap-4 px-4 py-3 hover:bg-surface-hover transition-colors cursor-pointer">
            <span className="text-xs font-bold text-muted-foreground w-5">{artist.rank}</span>
            <div className="w-9 h-9 rounded-full bg-primary/10 flex items-center justify-center text-xs font-bold overflow-hidden shrink-0 ring-1 ring-border">
              {(artist.photoUrl || artist.image) ? (
                <img src={artist.photoUrl || artist.image} alt={artist.name} className="w-full h-full object-cover" />
              ) : (
                artist.name.charAt(0)
              )}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">{artist.name}</p>
              <p className="text-[11px] text-muted-foreground">{artist.contact ?? `${artist.listeners?.toLocaleString() ?? '—'} listeners`}</p>
            </div>
            <div className="flex items-center gap-2">
              <div className="flex items-center gap-1">
                <TrendIcon growth={artist.growth} />
                <span className={`text-xs ${artist.growth > 0 ? 'text-green-500' : artist.growth < 0 ? 'text-red-500' : ''}`}>
                  {artist.growth > 0 ? '+' : ''}{artist.growth}%
                </span>
              </div>
              <div className="w-10 h-7 rounded-md bg-primary/10 flex items-center justify-center" title={artist.reason ?? ''}>
                <span className="text-xs font-bold text-primary">{artist.score}</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="p-3 border-t border-border">
        <button className="w-full text-center text-xs text-muted-foreground hover:text-foreground transition-colors">
          View All Artists →
        </button>
      </div>
    </div>
  );
}
