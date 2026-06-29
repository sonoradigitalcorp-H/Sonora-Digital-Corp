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
      <div className="rounded-xl border bg-card p-5">
        <p className="text-destructive text-sm">Failed to load top artists</p>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="rounded-xl border bg-card animate-pulse">
        <div className="p-5 border-b">
          <div className="h-5 w-48 bg-muted rounded" />
          <div className="h-3 w-36 bg-muted rounded mt-2" />
        </div>
        <div className="divide-y">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="flex items-center gap-4 p-4">
              <div className="w-6 h-4 bg-muted rounded" />
              <div className="w-10 h-10 rounded-full bg-muted" />
              <div className="flex-1 space-y-1">
                <div className="h-4 w-24 bg-muted rounded" />
                <div className="h-3 w-16 bg-muted rounded" />
              </div>
              <div className="flex items-center gap-2">
                <div className="h-4 w-12 bg-muted rounded" />
                <div className="w-12 h-8 rounded-md bg-muted" />
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
      <div className="rounded-xl border bg-card p-5">
        <p className="text-muted-foreground text-sm">No artist data available</p>
      </div>
    );
  }

  return (
    <div className="rounded-xl border bg-card">
      <div className="p-5 border-b">
        <h2 className="font-semibold">Top Artists by Discovery Score</h2>
        <p className="text-xs text-muted-foreground mt-0.5">Real-time intelligence ranking</p>
      </div>

      <div className="divide-y">
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
          <div key={artist.rank} className="flex items-center gap-4 p-4 hover:bg-accent/50 transition-colors cursor-pointer">
            <span className="text-sm font-bold text-muted-foreground w-6">{artist.rank}</span>
            <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-xs font-bold overflow-hidden">
              {(artist.photoUrl || artist.image) ? (
                <img src={artist.photoUrl || artist.image} alt={artist.name} className="w-full h-full object-cover" />
              ) : (
                artist.name.charAt(0)
              )}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">{artist.name}</p>
              <p className="text-xs text-muted-foreground">{artist.contact ?? `${artist.listeners?.toLocaleString() ?? '—'} listeners`}</p>
            </div>
            <div className="flex items-center gap-2">
              <div className="flex items-center gap-1">
                <TrendIcon growth={artist.growth} />
                <span className={`text-xs ${artist.growth > 0 ? 'text-green-500' : artist.growth < 0 ? 'text-red-500' : ''}`}>
                  {artist.growth > 0 ? '+' : ''}{artist.growth}%
                </span>
              </div>
              <div className="w-12 h-8 rounded-md bg-primary/10 flex items-center justify-center" title={artist.reason ?? ''}>
                <span className="text-sm font-bold text-primary">{artist.score}</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="p-3 border-t">
        <button className="w-full text-center text-sm text-muted-foreground hover:text-foreground transition-colors">
          View All Artists →
        </button>
      </div>
    </div>
  );
}
