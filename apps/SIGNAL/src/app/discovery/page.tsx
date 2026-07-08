'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { DashboardLayout } from '@/components/dashboard/layout';
import { Search, RefreshCw, AlertCircle, Loader2, Sparkles, Music2, Plus, Eye, MessageCircle, X, SlidersHorizontal } from 'lucide-react';

interface ArtistResult {
  id: string; name: string; genres: string[]; score: number; growth: number;
  listeners: number; city: string; country: string; contact: string;
  image: string; photoUrl?: string; discoveryScore: number; source: string;
  platforms: Record<string, number>; status: string;
}

interface DiscoveryResponse {
  results: ArtistResult[]; total: number; sources: string[]; genres: string[];
  discovered24h: number;
}

const formatListeners = (n: number): string => {
  if (n >= 1_000_000) return (n / 1_000_000).toFixed(1) + 'M';
  if (n >= 1_000) return (n / 1_000).toFixed(n >= 10_000 ? 0 : 1) + 'K';
  return n.toString();
};

export default function DiscoveryPage() {
  const [query, setQuery] = useState('');
  const [debouncedQuery, setDebouncedQuery] = useState('');
  const [genre, setGenre] = useState('');
  const [source, setSource] = useState('');
  const [data, setData] = useState<DiscoveryResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showFilters, setShowFilters] = useState(false);
  const hasFetched = useRef(false);

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedQuery(query), 400);
    return () => clearTimeout(timer);
  }, [query]);

  const fetchResults = useCallback(async (q: string, g: string, s: string) => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      if (q) params.set('q', q);
      if (g) params.set('genre', g);
      if (s) params.set('source', s);
      const res = await fetch(`/api/v1/discovery?${params}`);
      if (!res.ok) throw new Error('Failed to fetch discovery results');
      const json: DiscoveryResponse = await res.json();
      setData(json);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (!hasFetched.current) { hasFetched.current = true; fetchResults('', '', ''); return; }
    fetchResults(debouncedQuery, genre, source);
  }, [debouncedQuery, genre, source, fetchResults]);

  const handleRefresh = () => fetchResults(debouncedQuery, genre, source);

  return (
    <DashboardLayout>
      <div className="p-6 space-y-6 max-w-[1600px] mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold tracking-tight">Discovery Engine</h1>
            <p className="text-muted-foreground mt-1">Multi-platform artist discovery with AI-powered scoring</p>
          </div>
          {data && data.discovered24h > 0 && (
            <div className="flex items-center gap-2 px-4 py-2 rounded-lg bg-primary/10 text-primary text-sm font-medium whitespace-nowrap">
              <Sparkles className="h-4 w-4" />
              {data.discovered24h} new (24h)
            </div>
          )}
        </div>

        {/* Search + Filters */}
        <div className="rounded-xl border bg-card p-4">
          <div className="flex gap-3 flex-wrap">
            <div className="relative flex-1 min-w-[200px]">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Genre, keyword, location, or artist name..."
                className="w-full pl-10 pr-4 py-2.5 rounded-lg border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
              />
            </div>
            <button
              onClick={() => setShowFilters(!showFilters)}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-lg border text-sm transition-all ${showFilters ? 'bg-primary/10 text-primary border-primary/30' : 'bg-card hover:bg-accent'}`}
            >
              <SlidersHorizontal className="h-4 w-4" />
              Filters
            </button>
            <button
              onClick={handleRefresh}
              disabled={loading}
              className="flex items-center gap-2 px-4 py-2.5 rounded-lg bg-primary text-primary-foreground text-sm font-medium hover:opacity-90 transition-opacity disabled:opacity-50"
            >
              <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </button>
          </div>

          {/* Expandable filters */}
          {showFilters && (
            <div className="flex gap-3 mt-3 pt-3 border-t border-border animate-fade-in">
              {data && data.genres.length > 0 && (
                <select value={genre} onChange={(e) => setGenre(e.target.value)} className="px-3 py-2 rounded-lg border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary/50">
                  <option value="">All Genres</option>
                  {data.genres.sort().map((g) => <option key={g} value={g}>{g}</option>)}
                </select>
              )}
              {data && data.sources.length > 0 && (
                <select value={source} onChange={(e) => setSource(e.target.value)} className="px-3 py-2 rounded-lg border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary/50">
                  <option value="">All Sources</option>
                  {data.sources.sort().map((s) => <option key={s} value={s}>{s}</option>)}
                </select>
              )}
            </div>
          )}
        </div>

        {/* Loading */}
        {loading && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="rounded-xl border bg-card overflow-hidden animate-pulse">
                <div className="aspect-[4/3] bg-muted" />
                <div className="p-4 space-y-3">
                  <div className="h-5 w-3/4 bg-muted rounded" />
                  <div className="h-3 w-1/2 bg-muted rounded" />
                  <div className="flex gap-1">
                    <div className="h-5 w-16 bg-muted rounded-full" />
                    <div className="h-5 w-20 bg-muted rounded-full" />
                  </div>
                  <div className="grid grid-cols-3 gap-2">
                    <div className="h-14 bg-muted rounded-lg" />
                    <div className="h-14 bg-muted rounded-lg" />
                    <div className="h-14 bg-muted rounded-lg" />
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Error */}
        {error && !loading && (
          <div className="rounded-xl border border-red-500/20 bg-red-500/10 p-6 text-center">
            <AlertCircle className="h-8 w-8 text-red-500 mx-auto mb-2" />
            <p className="text-red-500 font-medium">{error}</p>
            <button onClick={handleRefresh} className="mt-2 text-sm text-muted-foreground hover:text-foreground underline">Try again</button>
          </div>
        )}

        {/* Empty */}
        {!loading && !error && data && data.results.length === 0 && (
          <div className="rounded-xl border bg-card p-12 text-center text-muted-foreground">
            <Music2 className="h-8 w-8 mx-auto mb-2 opacity-50" />
            <p className="font-medium">No artists found</p>
            <p className="text-sm mt-1">Try adjusting your search or filters</p>
          </div>
        )}

        {/* Results */}
        {!loading && !error && data && data.results.length > 0 && (
          <div>
            <div className="flex items-center justify-between mb-4">
              <p className="text-sm text-muted-foreground">{data.total} results</p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {data.results.map((artist) => (
                <div key={artist.id} className="rounded-xl border bg-card overflow-hidden group card-hover">
                  {/* Image area */}
                  <div className="aspect-[4/3] bg-muted relative overflow-hidden">
                    {(artist.photoUrl || artist.image) ? (
                      <img
                        src={artist.photoUrl || artist.image}
                        alt={artist.name}
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                        onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }}
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center text-muted-foreground">
                        <Music2 className="h-10 w-10 opacity-30" />
                      </div>
                    )}

                    {/* Hover overlay */}
                    <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
                      <button className="p-2.5 rounded-lg bg-white/10 hover:bg-white/20 transition-colors backdrop-blur-sm" title="Quick view">
                        <Eye className="h-4 w-4 text-white" />
                      </button>
                      <button className="p-2.5 rounded-lg bg-white/10 hover:bg-white/20 transition-colors backdrop-blur-sm" title="Add to pipeline">
                        <Plus className="h-4 w-4 text-white" />
                      </button>
                      <button className="p-2.5 rounded-lg bg-white/10 hover:bg-white/20 transition-colors backdrop-blur-sm" title="Contact">
                        <MessageCircle className="h-4 w-4 text-white" />
                      </button>
                    </div>

                    {/* Source badge */}
                    <div className="absolute top-2 right-2 px-2 py-0.5 rounded-full text-[10px] font-medium bg-background/80 backdrop-blur-sm border border-border/50">
                      {artist.source}
                    </div>

                    {/* Score badge */}
                    <div className="absolute bottom-2 left-2 flex items-center gap-1 px-2 py-0.5 rounded-full bg-background/80 backdrop-blur-sm border border-border/50">
                      <span className={`text-[10px] font-bold ${artist.score >= 80 ? 'text-green-400' : artist.score >= 60 ? 'text-primary' : 'text-amber-400'}`}>
                        {artist.score}
                      </span>
                      <span className="text-[8px] text-muted-foreground">score</span>
                    </div>
                  </div>

                  {/* Content */}
                  <div className="p-4 space-y-3">
                    <div>
                      <h3 className="font-semibold text-sm truncate group-hover:text-primary transition-colors">{artist.name}</h3>
                      <p className="text-xs text-muted-foreground truncate">{artist.city}, {artist.country}</p>
                    </div>

                    {/* Genre pills */}
                    <div className="flex flex-wrap gap-1">
                      {artist.genres.slice(0, 3).map((g) => (
                        <span key={g} className="px-2 py-0.5 rounded-full bg-accent text-[10px]">{g}</span>
                      ))}
                    </div>

                    {/* Stats grid */}
                    <div className="grid grid-cols-3 gap-2 text-center text-xs">
                      <div className="rounded-lg bg-muted/50 p-2">
                        <p className="font-semibold text-sm">{artist.score}</p>
                        <p className="text-muted-foreground text-[10px]">Score</p>
                      </div>
                      <div className="rounded-lg bg-muted/50 p-2">
                        <p className="font-semibold text-sm">{artist.discoveryScore}</p>
                        <p className="text-muted-foreground text-[10px]">Discovery</p>
                      </div>
                      <div className="rounded-lg bg-muted/50 p-2">
                        <p className="font-semibold text-sm">{formatListeners(artist.listeners)}</p>
                        <p className="text-muted-foreground text-[10px]">Listeners</p>
                      </div>
                    </div>

                    {/* Platforms */}
                    {artist.platforms && Object.keys(artist.platforms).length > 0 && (
                      <div className="flex flex-wrap gap-1">
                        {Object.entries(artist.platforms).slice(0, 4).map(([platform, count]) => (
                          <span key={platform} className="text-[9px] text-muted-foreground bg-muted/50 px-1.5 py-0.5 rounded">
                            {platform}: {count.toLocaleString()}
                          </span>
                        ))}
                      </div>
                    )}

                    {/* Contact */}
                    {artist.contact && (
                      <p className="text-[10px] text-muted-foreground truncate">Contact: {artist.contact}</p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
