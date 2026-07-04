'use client';

import { useState, useMemo, useCallback } from 'react';
import useSWR from 'swr';
import { DashboardLayout } from '@/components/dashboard/layout';
import { Search, Filter, TrendingUp, Users, Music2, Globe, Star, CheckCircle2, AlertCircle, Sparkles, RefreshCw, RotateCcw, Phone, Mail } from 'lucide-react';

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

const getScoreColor = (score: number): string => {
  if (score >= 90) return 'text-green-500';
  if (score >= 80) return 'text-blue-500';
  if (score >= 70) return 'text-amber-500';
  return 'text-muted-foreground';
};

const getScoreBarColor = (score: number): string => {
  if (score >= 90) return 'bg-green-500';
  if (score >= 80) return 'bg-blue-500';
  if (score >= 70) return 'bg-amber-500';
  return 'bg-muted-foreground';
};

const statusColors: Record<string, string> = {
  breakout: 'text-red-500 bg-red-500/10 border-red-500/20',
  monitoring: 'text-amber-500 bg-amber-500/10 border-amber-500/20',
  watchlist: 'text-blue-500 bg-blue-500/10 border-blue-500/20',
  emerging: 'text-green-500 bg-green-500/10 border-green-500/20',
  established: 'text-gray-500 bg-gray-500/10 border-gray-500/20',
  signed: 'text-emerald-500 bg-emerald-500/10 border-emerald-500/20',
};

const statusLabels: Record<string, { en: string; es: string }> = {
  breakout: { en: 'Breakout', es: 'Explosivo' },
  monitoring: { en: 'Monitoring', es: 'Monitoreo' },
  watchlist: { en: 'Watchlist', es: 'Observación' },
  emerging: { en: 'Emerging', es: 'Emergente' },
  established: { en: 'Established', es: 'Establecido' },
  signed: { en: 'SIGNED', es: 'FIRMADO' },
};

const parseContact = (contact: string): { type: 'phone' | 'email' | 'text'; value: string } => {
  if (contact.includes('@')) return { type: 'email', value: contact };
  if (contact.match(/[\d\s\-\(\)\+\.]{7,}/)) return { type: 'phone', value: contact };
  return { type: 'text', value: contact };
};

export default function ArtistsPage() {
  const [search, setSearch] = useState('');
  const [activeGenre, setActiveGenre] = useState('All');
  const [sortBy, setSortBy] = useState<'score' | 'momentum' | 'listeners'>('momentum');

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
        a.city.toLowerCase().includes(q) ||
        a.country.toLowerCase().includes(q)
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
      {Array.from({ length: 9 }).map((_, i) => (
        <td key={i} className="p-4">
          <div className="h-4 rounded bg-muted animate-pulse" style={{ width: i === 0 ? '140px' : i === 7 ? '80px' : '60px' }} />
        </td>
      ))}
    </tr>
  );

  const SkeletonCard = () => (
    <div className="relative p-3 rounded-lg bg-card border animate-pulse">
      <div className="w-6 h-6 rounded-full bg-muted mb-2" />
      <div className="h-5 w-5 bg-muted rounded mb-1" />
      <div className="h-4 w-24 bg-muted rounded mb-1" />
      <div className="h-3 w-16 bg-muted rounded mb-2" />
      <div className="h-1.5 w-full bg-muted rounded" />
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
                : `${total} artists tracked — ${(data as any)?.signedCount || 2} signed (ABE Music Group) · ${data?.genres?.slice(0, 3).join(', ') ?? ''}`
              }
            </p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => mutate()}
              disabled={isValidating}
              className="flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-full border bg-card hover:bg-accent transition-colors disabled:opacity-50"
            >
              <RefreshCw className={`h-3.5 w-3.5 ${isValidating ? 'animate-spin' : ''}`} />
              Refresh / Actualizar
            </button>
            {updatedAt && (
              <span className="text-[11px] text-muted-foreground hidden sm:block">
                Updated: {lastUpdated}
              </span>
            )}
          </div>
        </div>

        {/* Top 10 Prospects Banner */}
        <div className="rounded-xl border border-primary/20 bg-gradient-to-r from-primary/5 to-transparent p-5">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-primary" />
              <h2 className="font-semibold">Top 10 Prospects — <span className="text-muted-foreground font-normal">Top Prospects</span></h2>
            </div>
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <span className="flex items-center gap-1"><TrendingUp className="h-3 w-3" /> Momentum</span>
              <span className="flex items-center gap-1"><Star className="h-3 w-3" /> Score</span>
              <span className="flex items-center gap-1"><Users className="h-3 w-3" /> Engagement</span>
            </div>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
            {isLoading
              ? Array.from({ length: 5 }).map((_, i) => <SkeletonCard key={i} />)
              : topProspects.map((artist, i) => (
                  <div key={artist.id} className="relative p-3 rounded-lg bg-card border hover:border-primary/40 transition-all group">
                    <div className="absolute -top-2 -left-2 w-6 h-6 rounded-full bg-primary text-primary-foreground text-xs font-bold flex items-center justify-center shadow-lg">
                      {i + 1}
                    </div>
                    <div className="text-lg mb-1">
                      {artist.photoUrl ? (
                        <img src={artist.photoUrl} alt="" className="w-6 h-6 rounded-full object-cover" />
                      ) : (
                        artist.image || '🎵'
                      )}
                    </div>
                    <p className="text-sm font-semibold truncate">{artist.name}</p>
                    <p className="text-[10px] text-muted-foreground truncate">{artist.genres?.join(', ') || ''}</p>
                    <div className="flex items-center gap-1 mt-1.5">
                      <div className="flex-1 h-1 rounded-full bg-muted overflow-hidden">
                        <div className="h-full rounded-full bg-primary" style={{ width: `${artist.momentum}%` }} />
                      </div>
                      <span className="text-[10px] font-medium text-primary">{artist.momentum}</span>
                    </div>
                  </div>
                ))}
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
              placeholder="Search / Buscar by name, genre, city..."
              value={search}
              onChange={e => setSearch(e.target.value)}
              className="w-full pl-10 pr-4 py-2 rounded-lg border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
            />
          </div>
        </div>

        {/* Sort Controls */}
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-xs text-muted-foreground">Sort by / Ordenar:</span>
          {[
            { key: 'momentum' as const, label: 'Momentum' },
            { key: 'score' as const, label: 'Score / Puntaje' },
            { key: 'listeners' as const, label: 'Listeners / Oyentes' },
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
            <button
              onClick={() => mutate()}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-primary text-primary-foreground text-sm hover:opacity-90 transition-opacity"
            >
              <RotateCcw className="h-4 w-4" /> Retry / Reintentar
            </button>
          </div>
        )}

        {/* Table */}
        {!error && (
          <div className="rounded-xl border bg-card overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b bg-muted/50">
                    <th className="text-left text-xs font-medium text-muted-foreground p-4">Artist / Artista</th>
                    <th className="text-left text-xs font-medium text-muted-foreground p-4">Score / Puntaje</th>
                    <th className="text-left text-xs font-medium text-muted-foreground p-4">Growth / Crec.</th>
                    <th className="text-left text-xs font-medium text-muted-foreground p-4">Listeners / Oyentes</th>
                    <th className="text-left text-xs font-medium text-muted-foreground p-4">Genre / Género</th>
                    <th className="text-left text-xs font-medium text-muted-foreground p-4">Status / Estado</th>
                    <th className="text-left text-xs font-medium text-muted-foreground p-4">Contact / Contacto</th>
                    <th className="text-left text-xs font-medium text-muted-foreground p-4">Origin / Origen</th>
                    <th className="w-10"></th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {isLoading
                    ? Array.from({ length: 5 }).map((_, i) => <SkeletonRow key={i} />)
                    : filtered.map(artist => {
                        const contact = parseContact(artist.contact || '');
                        return (
                          <tr key={artist.id} className="hover:bg-accent/50 transition-colors cursor-pointer group">
                            <td className="p-4">
                              <div className="flex items-center gap-3">
                                <div className="w-9 h-9 rounded-full bg-primary/10 flex items-center justify-center text-lg shrink-0 overflow-hidden">
                                  {artist.photoUrl ? (
                                    <img src={artist.photoUrl} alt="" className="w-full h-full object-cover" />
                                  ) : (
                                    artist.image || '🎵'
                                  )}
                                </div>
                                <div className="min-w-0">
                                  <span className="font-medium text-sm block truncate">{artist.name}</span>
                                  <p className="text-[10px] text-muted-foreground truncate">{artist.genres?.slice(0, 2).join(' / ') || ''}</p>
                                </div>
                              </div>
                            </td>
                            <td className="p-4">
                              <div className="flex items-center gap-2">
                                <span className={`text-sm font-bold ${getScoreColor(artist.score)}`}>{artist.score}</span>
                                <div className="w-12 h-1.5 rounded-full bg-muted overflow-hidden hidden sm:block">
                                  <div className={`h-full rounded-full ${getScoreBarColor(artist.score)}`} style={{ width: `${artist.score}%` }} />
                                </div>
                              </div>
                            </td>
                            <td className="p-4">
                              <span className={`text-sm font-medium ${artist.growth >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                                {formatGrowth(artist.growth)}
                              </span>
                            </td>
                            <td className="p-4 text-sm whitespace-nowrap">{formatListeners(artist.listeners)}</td>
                            <td className="p-4">
                              <span className="text-xs text-muted-foreground">{artist.genres?.[0] || ''}</span>
                            </td>
                            <td className="p-4">
                              <span className={`text-xs px-2 py-1 rounded-full font-medium border whitespace-nowrap ${statusColors[artist.status] || statusColors.established}`}>
                                {statusLabels[artist.status]?.en || artist.status}
                              </span>
                            </td>
                            <td className="p-4">
                              <div className="flex items-center gap-1.5 text-xs text-muted-foreground min-w-0 max-w-[160px]">
                                {contact.type === 'phone' ? (
                                  <Phone className="h-3 w-3 shrink-0" />
                                ) : contact.type === 'email' ? (
                                  <Mail className="h-3 w-3 shrink-0" />
                                ) : null}
                                <span className="truncate" title={contact.value}>{contact.value}</span>
                              </div>
                            </td>
                            <td className="p-4 text-sm text-muted-foreground truncate max-w-[120px]" title={`${artist.city}, ${artist.country}`}>
                              {artist.city}, {artist.country}
                            </td>
                            <td className="p-4 opacity-0 group-hover:opacity-100 transition-opacity">
                              <button className="p-1.5 hover:bg-accent rounded-lg transition-colors">
                                <span className="text-xs">→</span>
                              </button>
                            </td>
                          </tr>
                        );
                      })}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Empty State */}
        {!isLoading && !error && filtered.length === 0 && (
          <div className="rounded-xl border bg-card p-12 text-center">
            <Music2 className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-1">No artists found / Sin resultados</h3>
            <p className="text-sm text-muted-foreground">
              Try a different search or genre / Prueba otra búsqueda o género
            </p>
          </div>
        )}

        {/* Footer */}
        {!error && (
          <div className="flex items-center justify-between flex-wrap gap-3">
            <p className="text-sm text-muted-foreground">
              {isLoading
                ? 'Loading...'
                : `Showing / Mostrando ${filtered.length} of / de ${total} prospects (${(data as any)?.signedCount || 2} signed)`
              }
              {updatedAt && (
                <>
                  <span className="mx-2">·</span>
                  <span className="text-green-500">Updated / Actualizado: {lastUpdated}</span>
                </>
              )}
            </p>
            <div className="flex items-center gap-2">
              <button className="px-3 py-1.5 rounded border bg-card text-sm hover:bg-accent transition-colors disabled:opacity-50" disabled>Previous / Anterior</button>
              <button className="px-3 py-1.5 rounded bg-primary text-primary-foreground text-sm">1</button>
              <button className="px-3 py-1.5 rounded border bg-card text-sm hover:bg-accent transition-colors disabled:opacity-50" disabled>Next / Siguiente</button>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
