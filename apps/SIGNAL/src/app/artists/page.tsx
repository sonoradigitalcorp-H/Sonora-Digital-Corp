'use client';

import { useState, useMemo, useCallback } from 'react';
import useSWR from 'swr';
import { DashboardLayout } from '@/components/dashboard/layout';
import {
  Search, Filter, TrendingUp, Users, Music2, Globe, Star, CheckCircle2, AlertCircle,
  Sparkles, RefreshCw, RotateCcw, Phone, Mail, Plus, BrainCircuit, MessageCircle, Eye, EyeOff,
  Grid3X3, List, Columns3,
} from 'lucide-react';

const fetcher = (url: string) => fetch(url).then(res => {
  if (!res.ok) throw new Error(`Error ${res.status}`);
  return res.json();
});

const formatListeners = (n: number): string => {
  if (n >= 1_000_000) return (n / 1_000_000).toFixed(1) + 'M';
  if (n >= 1_000) return (n / 1_000).toFixed(n >= 10_000 ? 0 : 1) + 'K';
  return n.toString();
};

const formatGrowth = (n: number): string => {
  const sign = n >= 0 ? '+' : '';
  return `${sign}${n.toFixed(0)}%`;
};

const statusConfig: Record<string, { icon: React.ElementType; color: string }> = {
  breakout: { icon: TrendingUp, color: 'text-rose-500 bg-rose-500/10 border-rose-500/20' },
  monitoring: { icon: Eye, color: 'text-amber-500 bg-amber-500/10 border-amber-500/20' },
  watchlist: { icon: Star, color: 'text-primary bg-primary/10 border-primary/20' },
  emerging: { icon: Sparkles, color: 'text-emerald-500 bg-emerald-500/10 border-emerald-500/20' },
  established: { icon: CheckCircle2, color: 'text-gray-500 bg-gray-500/10 border-gray-500/20' },
  signed: { icon: CheckCircle2, color: 'text-green-500 bg-green-500/10 border-green-500/20' },
};

const statusLabels: Record<string, string> = {
  breakout: 'Breakout', monitoring: 'Monitoring', watchlist: 'Watchlist',
  emerging: 'Emerging', established: 'Established', signed: 'Signed',
};

const parseContact = (contact: string): { type: 'phone' | 'email' | 'text'; value: string } => {
  if (contact.includes('@')) return { type: 'email', value: contact };
  if (contact.match(/[\d\s\-\(\)\+\.]{7,}/)) return { type: 'phone', value: contact };
  return { type: 'text', value: contact };
};

function ScoreGradientBar({ score }: { score: number }) {
  const pct = Math.min(score, 100);
  return (
    <div className="w-full h-1.5 rounded-full bg-muted overflow-hidden">
      <div
        className="h-full rounded-full transition-all duration-500"
        style={{
          width: `${pct}%`,
          background: pct >= 80
            ? 'linear-gradient(90deg, #3B82F6, #22c55e)'
            : pct >= 60
              ? 'linear-gradient(90deg, #f59e0b, #3B82F6)'
              : pct >= 40
                ? 'linear-gradient(90deg, #ef4444, #f59e0b)'
                : 'linear-gradient(90deg, #ef4444, #f97316)',
        }}
      />
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const config = statusConfig[status];
  if (!config) return <span className="text-xs px-2 py-1 rounded-full bg-muted font-medium">{status}</span>;
  const Icon = config.icon;
  return (
    <span className={`inline-flex items-center gap-1 text-xs px-2 py-1 rounded-full font-medium border ${config.color}`}>
      <Icon className="h-3 w-3" />
      {statusLabels[status] || status}
    </span>
  );
}

export default function ArtistsPage() {
  const [search, setSearch] = useState('');
  const [activeGenre, setActiveGenre] = useState('All');
  const [sortBy, setSortBy] = useState<'score' | 'momentum' | 'listeners'>('momentum');
  const [viewMode, setViewMode] = useState<'table' | 'grid'>('table');

  const { data, error, isLoading, mutate, isValidating } = useSWR(
    `/api/v1/artists?genre=${encodeURIComponent(activeGenre)}&count=12`,
    fetcher,
    { revalidateOnFocus: false, refreshInterval: 30000 }
  );

  const artists = data?.artists ?? [];
  const genres = data?.genres ?? ['All'];
  const total = data?.total ?? 0;
  const updatedAt = data?.updatedAt ?? null;

  const filtered = useMemo(() => {
    let result = [...artists];
    if (search) {
      const q = search.toLowerCase();
      result = result.filter(a =>
        a.name.toLowerCase().includes(q) ||
        a.genres.some((g: string) => g.toLowerCase().includes(q)) ||
        a.city?.toLowerCase().includes(q) ||
        a.country?.toLowerCase().includes(q)
      );
    }
    result.sort((a, b) => {
      if (sortBy === 'score') return b.score - a.score;
      if (sortBy === 'listeners') return b.listeners - a.listeners;
      return b.momentum - a.momentum;
    });
    return result;
  }, [artists, search, sortBy]);

  const topProspects = useMemo(() => {
    return [...artists]
      .sort((a, b) => (b.momentum * 0.4 + b.score * 0.3 + (b.engagement ?? 0) * 0.3) - (a.momentum * 0.4 + a.score * 0.3 + (a.engagement ?? 0) * 0.3))
      .slice(0, 10);
  }, [artists]);

  const lastUpdated = updatedAt
    ? new Date(updatedAt).toLocaleString('es-ES', { dateStyle: 'short', timeStyle: 'short' })
    : null;

  const SkeletonRow = () => (
    <tr className="border-b border-border/50">
      {Array.from({ length: 7 }).map((_, i) => (
        <td key={i} className="p-4">
          <div className="h-4 rounded bg-muted animate-pulse" style={{ width: i === 0 ? '140px' : '60px' }} />
        </td>
      ))}
    </tr>
  );

  const SkeletonCard = () => (
    <div className="rounded-xl border bg-card overflow-hidden animate-pulse">
      <div className="aspect-[4/3] bg-muted" />
      <div className="p-4 space-y-2">
        <div className="h-4 w-3/4 bg-muted rounded" />
        <div className="h-3 w-1/2 bg-muted rounded" />
        <div className="h-2 w-full bg-muted rounded" />
      </div>
    </div>
  );

  return (
    <DashboardLayout>
      <div className="p-6 space-y-6 max-w-[1600px] mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between flex-wrap gap-3">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Artist Radar</h1>
            <p className="text-muted-foreground mt-1">
              {isLoading
                ? 'Loading prospects...'
                : `${total} artists tracked — ${(data as any)?.signedCount || 2} signed`
              }
              {data?.genres?.slice(0, 3).length ? ` · ${data.genres.slice(0, 3).join(', ')}` : ''}
            </p>
          </div>
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1 p-1 rounded-lg bg-muted">
              <button
                onClick={() => setViewMode('table')}
                className={`p-1.5 rounded ${viewMode === 'table' ? 'bg-background shadow-sm' : ''}`}
                title="Table view"
              >
                <List className="h-3.5 w-3.5" />
              </button>
              <button
                onClick={() => setViewMode('grid')}
                className={`p-1.5 rounded ${viewMode === 'grid' ? 'bg-background shadow-sm' : ''}`}
                title="Grid view"
              >
                <Grid3X3 className="h-3.5 w-3.5" />
              </button>
            </div>
            <button
              onClick={() => mutate()}
              disabled={isValidating}
              className="flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-full border bg-card hover:bg-accent transition-colors disabled:opacity-50"
            >
              <RefreshCw className={`h-3.5 w-3.5 ${isValidating ? 'animate-spin' : ''}`} />
              Refresh
            </button>
            {updatedAt && (
              <span className="text-[11px] text-muted-foreground hidden sm:block">
                Updated: {lastUpdated}
              </span>
            )}
          </div>
        </div>

        {/* Genre Tabs + Search */}
        <div className="flex items-center justify-between gap-4 flex-wrap">
          <div className="flex gap-1 p-1 rounded-xl bg-muted overflow-x-auto">
            {isLoading
              ? Array.from({ length: 4 }).map((_, i) => (
                  <div key={i} className="h-8 w-20 rounded-lg bg-muted animate-pulse" />
                ))
              : genres.map((genre: string) => (
                  <button
                    key={genre}
                    onClick={() => setActiveGenre(genre)}
                    className={`px-4 py-2 text-sm font-medium rounded-lg whitespace-nowrap transition-all ${
                      activeGenre === genre
                        ? 'bg-background text-foreground shadow-sm'
                        : 'text-muted-foreground hover:text-foreground'
                    }`}
                  >
                    {genre}
                  </button>
                ))}
          </div>
          <div className="relative max-w-xs flex-1 min-w-[200px]">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <input
              type="text"
              placeholder="Search by name, genre, city..."
              value={search}
              onChange={e => setSearch(e.target.value)}
              className="w-full pl-10 pr-4 py-2 rounded-lg border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
            />
          </div>
        </div>

        {/* Sort Controls */}
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-xs text-muted-foreground">Sort by:</span>
          {[
            { key: 'momentum' as const, label: 'Momentum' },
            { key: 'score' as const, label: 'Score' },
            { key: 'listeners' as const, label: 'Listeners' },
          ].map(opt => (
            <button
              key={opt.key}
              onClick={() => setSortBy(opt.key)}
              className={`text-xs px-3 py-1.5 rounded-full border transition-all ${
                sortBy === opt.key
                  ? 'bg-primary/10 text-primary border-primary/30'
                  : 'bg-card text-muted-foreground border-transparent hover:border-border'
              }`}
            >
              {opt.label}
            </button>
          ))}
        </div>

        {/* Error State */}
        {error && !isLoading && (
          <div className="rounded-xl border border-red-500/20 bg-red-500/5 p-6 text-center">
            <AlertCircle className="h-10 w-10 text-red-500 mx-auto mb-3" />
            <h3 className="text-lg font-semibold mb-1">Error loading artists</h3>
            <p className="text-sm text-muted-foreground mb-4">{error.message}</p>
            <button onClick={() => mutate()} className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-primary text-primary-foreground text-sm hover:opacity-90 transition-opacity">
              <RotateCcw className="h-4 w-4" /> Retry
            </button>
          </div>
        )}

        {/* Top 10 Prospects Bar */}
        {!isLoading && !error && topProspects.length > 0 && (
          <div className="rounded-xl border border-primary/20 bg-gradient-to-r from-primary/5 to-transparent p-4">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <Sparkles className="h-4 w-4 text-primary" />
                <h2 className="text-sm font-semibold">Top Prospects</h2>
              </div>
              <div className="flex items-center gap-2 text-[10px] text-muted-foreground">
                <span className="flex items-center gap-1"><TrendingUp className="h-3 w-3" /> Momentum</span>
                <span className="flex items-center gap-1"><Star className="h-3 w-3" /> Score</span>
              </div>
            </div>
            <div className="flex gap-2 overflow-x-auto pb-1">
              {topProspects.slice(0, 8).map((artist, i) => (
                <div key={artist.id} className="relative flex-shrink-0 w-32 p-3 rounded-lg bg-card border hover:border-primary/40 transition-all group">
                  <div className="absolute -top-1.5 -left-1.5 w-5 h-5 rounded-full bg-primary text-primary-foreground text-[9px] font-bold flex items-center justify-center shadow-lg">
                    {i + 1}
                  </div>
                  <div className="w-6 h-6 rounded-full bg-primary/10 flex items-center justify-center mb-1.5 overflow-hidden">
                    {artist.photoUrl ? (
                      <img src={artist.photoUrl} alt="" className="w-full h-full object-cover" />
                    ) : (
                      <span className="text-[9px] font-bold text-primary">{artist.name.charAt(0)}</span>
                    )}
                  </div>
                  <p className="text-xs font-semibold truncate">{artist.name}</p>
                  <p className="text-[9px] text-muted-foreground truncate">{artist.genres?.[0] || ''}</p>
                  <div className="mt-1.5">
                    <div className="flex items-center gap-1">
                      <div className="flex-1 h-1 rounded-full bg-muted overflow-hidden">
                        <div className="h-full rounded-full bg-primary" style={{ width: `${artist.momentum}%` }} />
                      </div>
                      <span className="text-[9px] font-medium text-primary">{artist.momentum}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Content: Table or Grid */}
        {!error && (
          <>
            {viewMode === 'table' ? (
              <div className="rounded-xl border bg-card overflow-hidden">
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b bg-muted/50">
                        <th className="text-left text-xs font-medium text-muted-foreground p-4">Artist</th>
                        <th className="text-left text-xs font-medium text-muted-foreground p-4">Score</th>
                        <th className="text-left text-xs font-medium text-muted-foreground p-4">Growth</th>
                        <th className="text-left text-xs font-medium text-muted-foreground p-4">Listeners</th>
                        <th className="text-left text-xs font-medium text-muted-foreground p-4">Status</th>
                        <th className="text-left text-xs font-medium text-muted-foreground p-4">Origin</th>
                        <th className="w-24"></th>
                      </tr>
                    </thead>
                    <tbody className="divide-y">
                      {isLoading
                        ? Array.from({ length: 5 }).map((_, i) => <SkeletonRow key={i} />)
                        : filtered.map(artist => (
                            <tr key={artist.id} className="data-row group cursor-pointer">
                              <td className="p-4">
                                <div className="flex items-center gap-3">
                                  <div className="w-9 h-9 rounded-full bg-primary/10 flex items-center justify-center text-sm font-bold overflow-hidden shrink-0 ring-1 ring-border">
                                    {artist.photoUrl ? (
                                      <img src={artist.photoUrl} alt="" className="w-full h-full object-cover" />
                                    ) : (
                                      artist.name.charAt(0)
                                    )}
                                  </div>
                                  <div className="min-w-0">
                                    <span className="font-medium text-sm block truncate">{artist.name}</span>
                                    <p className="text-[10px] text-muted-foreground truncate">{artist.genres?.slice(0, 2).join(' / ') || ''}</p>
                                  </div>
                                </div>
                              </td>
                              <td className="p-4">
                                <div className="flex items-center gap-2 min-w-[100px]">
                                  <span className={`text-sm font-bold tabular-nums ${artist.score >= 80 ? 'text-green-400' : artist.score >= 60 ? 'text-primary' : artist.score >= 40 ? 'text-amber-400' : 'text-rose-400'}`}>
                                    {artist.score}
                                  </span>
                                  <ScoreGradientBar score={artist.score} />
                                </div>
                              </td>
                              <td className="p-4">
                                <span className={`text-sm font-medium tabular-nums ${artist.growth >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                                  {formatGrowth(artist.growth)}
                                </span>
                              </td>
                              <td className="p-4 text-sm tabular-nums">{formatListeners(artist.listeners)}</td>
                              <td className="p-4">
                                <StatusBadge status={artist.status} />
                              </td>
                              <td className="p-4 text-sm text-muted-foreground truncate max-w-[120px]" title={`${artist.city}, ${artist.country}`}>
                                {artist.city}, {artist.country}
                              </td>
                              <td className="p-4">
                                <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                                  <button className="p-1.5 rounded hover:bg-surface-hover text-muted-foreground hover:text-primary transition-colors" title="View intelligence">
                                    <BrainCircuit className="h-3.5 w-3.5" />
                                  </button>
                                  <button className="p-1.5 rounded hover:bg-surface-hover text-muted-foreground hover:text-primary transition-colors" title="Contact">
                                    <MessageCircle className="h-3.5 w-3.5" />
                                  </button>
                                  <button className="p-1.5 rounded hover:bg-surface-hover text-muted-foreground hover:text-primary transition-colors" title="Add to pipeline">
                                    <Plus className="h-3.5 w-3.5" />
                                  </button>
                                </div>
                              </td>
                            </tr>
                          ))}
                    </tbody>
                  </table>
                </div>
              </div>
            ) : (
              /* Grid view */
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                {isLoading
                  ? Array.from({ length: 8 }).map((_, i) => <SkeletonCard key={i} />)
                  : filtered.map(artist => (
                      <div key={artist.id} className="rounded-xl border bg-card overflow-hidden group card-hover cursor-pointer">
                        <div className="aspect-[4/3] bg-muted relative flex items-center justify-center">
                          {artist.photoUrl ? (
                            <img src={artist.photoUrl} alt="" className="w-full h-full object-cover" />
                          ) : (
                            <Music2 className="h-10 w-10 text-muted-foreground/30" />
                          )}
                          <div className="absolute top-2 right-2">
                            <StatusBadge status={artist.status} />
                          </div>
                          <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
                            <button className="p-2 rounded-lg bg-white/10 hover:bg-white/20 transition-colors">
                              <Eye className="h-4 w-4 text-white" />
                            </button>
                            <button className="p-2 rounded-lg bg-white/10 hover:bg-white/20 transition-colors">
                              <Plus className="h-4 w-4 text-white" />
                            </button>
                            <button className="p-2 rounded-lg bg-white/10 hover:bg-white/20 transition-colors">
                              <MessageCircle className="h-4 w-4 text-white" />
                            </button>
                          </div>
                        </div>
                        <div className="p-4 space-y-2">
                          <div>
                            <h3 className="font-semibold text-sm truncate">{artist.name}</h3>
                            <p className="text-xs text-muted-foreground truncate">{artist.city}, {artist.country}</p>
                          </div>
                          <div className="flex items-center justify-between">
                            <span className={`text-lg font-bold ${artist.score >= 80 ? 'text-green-400' : artist.score >= 60 ? 'text-primary' : artist.score >= 40 ? 'text-amber-400' : 'text-rose-400'}`}>
                              {artist.score}
                            </span>
                            <span className="text-xs text-muted-foreground">{formatListeners(artist.listeners)} listeners</span>
                          </div>
                          <ScoreGradientBar score={artist.score} />
                        </div>
                      </div>
                    ))}
              </div>
            )}
          </>
        )}

        {/* Empty State */}
        {!isLoading && !error && filtered.length === 0 && (
          <div className="rounded-xl border bg-card p-12 text-center">
            <Music2 className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-1">No artists found</h3>
            <p className="text-sm text-muted-foreground">Try a different search or genre</p>
          </div>
        )}

        {/* Footer */}
        {!error && !isLoading && (
          <div className="flex items-center justify-between flex-wrap gap-3">
            <p className="text-sm text-muted-foreground">
              Showing {filtered.length} of {total} prospects ({(data as any)?.signedCount || 2} signed)
              {updatedAt && (
                <>
                  <span className="mx-2">·</span>
                  <span className="text-green-500">Updated: {lastUpdated}</span>
                </>
              )}
            </p>
            <div className="flex items-center gap-2">
              <button className="px-3 py-1.5 rounded border bg-card text-sm hover:bg-accent transition-colors disabled:opacity-50" disabled>Previous</button>
              <button className="px-3 py-1.5 rounded bg-primary text-primary-foreground text-sm">1</button>
              <button className="px-3 py-1.5 rounded border bg-card text-sm hover:bg-accent transition-colors disabled:opacity-50" disabled>Next</button>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
