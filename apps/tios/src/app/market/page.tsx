'use client';

import { DashboardLayout } from '@/components/dashboard/layout';
import { TrendingUp, Globe, MapPin, ArrowUp, ArrowDown, Target, Lightbulb, ExternalLink, Loader2, AlertCircle } from 'lucide-react';
import useSWR from 'swr';

const fetcher = (url: string) => fetch(url).then(r => r.json());

const t = (es: string, en: string) => `${es} / ${en}`;

const potentialColors: Record<string, string> = {
  Alta: 'bg-green-500/10 text-green-500',
  Alto: 'bg-green-500/10 text-green-500',
  Crítica: 'bg-red-500/10 text-red-500',
  Media: 'bg-amber-500/10 text-amber-500',
  Medio: 'bg-amber-500/10 text-amber-500',
};

function SkeletonCard() {
  return <div className="rounded-xl border bg-card p-4 space-y-3 animate-pulse"><div className="h-3 w-20 bg-muted rounded" /><div className="h-6 w-16 bg-muted rounded" /><div className="h-3 w-24 bg-muted rounded" /></div>;
}

function SkeletonBar() {
  return <div className="space-y-3"><div className="h-4 w-36 bg-muted rounded mb-4" />{[...Array(6)].map((_, i) => <div key={i} className="flex gap-4 p-2"><div className="h-4 w-4 bg-muted rounded shrink-0" /><div className="flex-1 space-y-1"><div className="flex justify-between"><div className="h-3 w-28 bg-muted rounded" /><div className="h-3 w-16 bg-muted rounded" /></div><div className="h-1.5 rounded-full bg-muted" /></div></div>)}</div>;
}

function SkeletonOpps() {
  return <div className="space-y-3"><div className="h-4 w-32 bg-muted rounded mb-4" />{[...Array(4)].map((_, i) => <div key={i} className="p-3 rounded-lg border space-y-2"><div className="h-3 w-40 bg-muted rounded" /><div className="h-3 w-full bg-muted rounded" /><div className="h-3 w-24 bg-muted rounded" /></div>)}</div>;
}

export default function MarketPage() {
  const { data, error, isLoading } = useSWR('/api/v1/market', fetcher, { revalidateOnFocus: false });

  return (
    <DashboardLayout>
      <div className="p-6 space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">{t('Inteligencia de Mercado', 'Market Intelligence')}</h1>
          <p className="text-muted-foreground mt-1">{t('Análisis regional y oportunidades de crecimiento', 'Regional market analysis and growth opportunities')}</p>
        </div>

        {error && (
          <div className="flex items-center gap-2 p-4 rounded-xl border border-red-500/20 bg-red-500/5 text-red-500">
            <AlertCircle className="h-4 w-4 shrink-0" />
            <div>
              <p className="text-sm font-medium">{t('Error al cargar datos', 'Failed to load market data')}</p>
              <p className="text-xs text-red-400/80 mt-0.5">{error.message}</p>
            </div>
          </div>
        )}

        {isLoading && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {[...Array(4)].map((_, i) => <SkeletonCard key={i} />)}
          </div>
        )}

        {isLoading && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <SkeletonBar />
            <SkeletonOpps />
          </div>
        )}

        {data && (
          <>
            {/* Market Summary */}
            {data.summary && (
              <div className="rounded-xl border bg-card p-4 flex flex-wrap items-center gap-4 text-sm">
                <span className="text-muted-foreground">{t('Mercado', 'Market')}:</span>
                <span className="font-medium">{data.summary.totalMarketSize}</span>
                <span className="text-muted-foreground">|</span>
                <span className="text-muted-foreground">{t('Top', 'Top')}:</span>
                <span className="font-medium text-primary">{data.summary.topGenre}</span>
                <span className="text-green-500">{data.summary.genreGrowth}</span>
              </div>
            )}

            {/* Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              {data.metrics.map((m: any, i: number) => (
                <div key={i} className="rounded-xl border bg-card p-4 hover:border-primary/30 transition-colors">
                  <p className="text-xs text-muted-foreground mb-1">{m.label}</p>
                  <p className="text-xl font-bold">{m.value}</p>
                  <p className={`text-xs mt-1 flex items-center gap-1 ${m.trend === 'up' ? 'text-green-500' : m.trend === 'down' ? 'text-red-500' : 'text-muted-foreground'}`}>
                    {m.trend === 'up' && <ArrowUp className="h-3 w-3" />}
                    {m.trend === 'down' && <ArrowDown className="h-3 w-3" />}
                    {m.change}
                  </p>
                </div>
              ))}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Genre Breakdown */}
              <div className="rounded-xl border bg-card p-5">
                <h2 className="font-semibold mb-4 flex items-center gap-2">
                  <Globe className="h-4 w-4 text-primary" />
                  {t('Distribución por Género', 'Genre Distribution')}
                </h2>
                <div className="space-y-3">
                  {data.genres.map((g: any, i: number) => (
                    <div key={i} className="flex items-center gap-4 p-2 rounded-lg hover:bg-accent/50 transition-colors">
                      <MapPin className="h-4 w-4 text-muted-foreground shrink-0" />
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between text-sm mb-1">
                          <span className="font-medium truncate">{g.genre}</span>
                          <div className="flex items-center gap-3 shrink-0">
                            <span className="text-xs text-muted-foreground">{t('Share', 'Share')}: {g.marketShare}</span>
                            <span className={`text-xs font-medium ${g.growth.startsWith('+') ? 'text-green-500' : 'text-red-500'}`}>{g.growth}</span>
                          </div>
                        </div>
                        <div className="flex items-center gap-2 text-xs text-muted-foreground">
                          <span>{t('Indie', 'Indie')}: {g.avgIndieListeners}</span>
                          <span>·</span>
                          <span className={`px-1.5 py-0.5 rounded text-[10px] font-medium ${potentialColors[g.unsignedOpportunity] || 'bg-muted text-muted-foreground'}`}>
                            {g.unsignedOpportunity}
                          </span>
                        </div>
                        {g.keyMarkets && g.keyMarkets.length > 0 && (
                          <div className="flex flex-wrap gap-1 mt-1.5">
                            {g.keyMarkets.map((m: string, mi: number) => (
                              <span key={mi} className="text-[10px] px-1.5 py-0.5 rounded-full bg-primary/10 text-primary/80">{m}</span>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Opportunities */}
              <div className="rounded-xl border bg-card p-5">
                <h2 className="font-semibold mb-4 flex items-center gap-2">
                  <Lightbulb className="h-4 w-4 text-primary" />
                  {t('Oportunidades', 'Opportunities')}
                </h2>
                <div className="space-y-3">
                  {data.opportunities.map((o: any, i: number) => (
                    <div key={i} className="p-3 rounded-lg border hover:border-primary/30 transition-colors">
                      <div className="flex items-start justify-between gap-2">
                        <div className="min-w-0">
                          <p className="text-sm font-medium">{o.market}</p>
                          <p className="text-xs text-muted-foreground mt-0.5">{o.reason}</p>
                        </div>
                        <span className={`text-[10px] px-2 py-0.5 rounded-full font-medium shrink-0 ${potentialColors[o.potential] || 'bg-muted text-muted-foreground'}`}>
                          {o.potential}
                        </span>
                      </div>
                      <div className="flex items-center gap-1 mt-2 text-xs text-primary">
                        <Target className="h-3 w-3" />
                        <span>{o.action}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Sources */}
            {data.sources && data.sources.length > 0 && (
              <div className="rounded-xl border bg-card p-4">
                <p className="text-xs text-muted-foreground mb-2">{t('Fuentes', 'Sources')}</p>
                <div className="flex flex-wrap gap-2">
                  {data.sources.map((s: string, i: number) => (
                    <span key={i} className="flex items-center gap-1 text-xs px-2 py-1 rounded-md bg-muted">
                      <ExternalLink className="h-3 w-3 text-muted-foreground" />
                      {s}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </DashboardLayout>
  );
}
