'use client';

import { DashboardLayout } from '@/components/dashboard/layout';
import { BarChart3, TrendingUp, ArrowUp, ArrowDown, Star, Users, AlertTriangle, Target, Loader2, AlertCircle } from 'lucide-react';
import useSWR from 'swr';

const fetcher = (url: string) => fetch(url).then(r => r.json());

function formatCurrency(n: number) {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', notation: 'compact', maximumFractionDigits: 0 }).format(n);
}

function formatNumber(n: number) {
  return new Intl.NumberFormat('en-US', { notation: 'compact', maximumFractionDigits: 0 }).format(n);
}

const t = (es: string, en: string) => `${es} / ${en}`;

function SkeletonCard() {
  return <div className="rounded-xl border bg-card p-5 space-y-3 animate-pulse"><div className="h-3 w-24 bg-muted rounded" /><div className="h-7 w-16 bg-muted rounded" /><div className="h-3 w-20 bg-muted rounded" /></div>;
}

function SkeletonBar() {
  return <div className="space-y-3"><div className="h-4 w-32 bg-muted rounded mb-4" />{[...Array(6)].map((_, i) => <div key={i} className="space-y-1"><div className="flex justify-between"><div className="h-3 w-24 bg-muted rounded" /><div className="h-3 w-12 bg-muted rounded" /></div><div className="h-2 rounded-full bg-muted overflow-hidden"><div className="h-full rounded-full bg-muted" style={{ width: `${60 + Math.random() * 40}%` }} /></div></div>)}</div>;
}

function SkeletonTable() {
  return <div className="space-y-3"><div className="h-4 w-32 bg-muted rounded mb-4" />{[...Array(8)].map((_, i) => <div key={i} className="flex items-center justify-between p-3"><div className="flex items-center gap-3"><div className="h-3 w-6 bg-muted rounded" /><div className="h-3 w-28 bg-muted rounded" /></div><div className="flex items-center gap-4"><div className="h-3 w-16 bg-muted rounded" /><div className="h-3 w-12 bg-muted rounded" /></div></div>)}</div>;
}

export default function AnalyticsPage() {
  const { data, error, isLoading } = useSWR('/api/v1/analytics', fetcher, { revalidateOnFocus: false });

  return (
    <DashboardLayout>
      <div className="p-6 space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">{t('Analíticas', 'Analytics')}</h1>
          <p className="text-muted-foreground mt-1">{t('Métricas de rendimiento y tendencias', 'Comprehensive performance metrics and trends')}</p>
        </div>

        {error && (
          <div className="flex items-center gap-2 p-4 rounded-xl border border-red-500/20 bg-red-500/5 text-red-500">
            <AlertCircle className="h-4 w-4 shrink-0" />
            <div>
              <p className="text-sm font-medium">{t('Error al cargar datos', 'Failed to load analytics data')}</p>
              <p className="text-xs text-red-400/80 mt-0.5">{error.message}</p>
            </div>
          </div>
        )}

        {isLoading && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {[...Array(4)].map((_, i) => <SkeletonCard key={i} />)}
          </div>
        )}

        {isLoading && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <SkeletonBar />
            <SkeletonTable />
          </div>
        )}

        {data && (
          <>
            {/* KPI Metric Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {data.kpiMetrics.map((m: any, i: number) => (
                <div key={i} className="rounded-xl border bg-card p-5 hover:border-primary/30 transition-colors">
                  <div className="flex items-center justify-between mb-2">
                    <p className="text-sm text-muted-foreground">{m.label}</p>
                    {i === 0 && <Users className="h-4 w-4 text-primary" />}
                    {i === 1 && <Star className="h-4 w-4 text-primary" />}
                    {i === 2 && <Target className="h-4 w-4 text-primary" />}
                    {i === 3 && <AlertTriangle className="h-4 w-4 text-primary" />}
                  </div>
                  <p className="text-2xl font-bold">{m.value}</p>
                  <div className={`flex items-center gap-1 mt-1 text-xs font-medium ${m.trend === 'up' ? 'text-green-500' : 'text-red-500'}`}>
                    {m.trend === 'up' ? <ArrowUp className="h-3 w-3" /> : <ArrowDown className="h-3 w-3" />}
                    {m.change}
                  </div>
                </div>
              ))}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Genre Distribution */}
              <div className="rounded-xl border bg-card p-5">
                <h2 className="font-semibold mb-4 flex items-center gap-2">
                  <BarChart3 className="h-4 w-4 text-primary" />
                  {t('Distribución por Género', 'Genre Distribution')}
                </h2>
                <div className="space-y-4">
                  {data.genreDistribution.map((g: any, i: number) => (
                    <div key={i}>
                      <div className="flex items-center justify-between text-sm mb-1">
                        <span className="font-medium">{g.genre}</span>
                        <span className="text-xs text-muted-foreground">{g.percentage}%</span>
                      </div>
                      <div className="h-2 rounded-full bg-muted overflow-hidden">
                        <div
                          className="h-full rounded-full transition-all duration-500"
                          style={{ width: `${g.percentage}%`, backgroundColor: g.color || 'var(--primary)' }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Top 10 For Signing */}
              <div className="rounded-xl border bg-card p-5">
                <h2 className="font-semibold mb-4 flex items-center gap-2">
                  <TrendingUp className="h-4 w-4 text-primary" />
                  {t('Top 10 para Fichar', 'Top 10 for Signing')}
                </h2>
                <div className="space-y-1 max-h-[500px] overflow-y-auto pr-1">
                  {data.topForSigning.map((a: any, i: number) => (
                    <div key={i} className="flex items-center justify-between p-3 rounded-lg hover:bg-accent/50 transition-colors group">
                      <div className="flex items-center gap-3 min-w-0">
                        <span className="text-sm font-medium text-muted-foreground w-6 shrink-0">{a.rank}.</span>
                        <div className="min-w-0">
                          <p className="text-sm font-medium truncate">{a.name}</p>
                          <p className="text-xs text-muted-foreground truncate">{a.contact}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-3 shrink-0">
                        <div className="text-right">
                          <p className="text-sm font-semibold">{a.score}</p>
                          <p className="text-xs text-muted-foreground">{formatCurrency(a.dealEstimate)}</p>
                        </div>
                        <span className={`text-xs font-medium flex items-center gap-1 ${a.growth >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                          {a.growth >= 0 ? <ArrowUp className="h-3 w-3" /> : <ArrowDown className="h-3 w-3" />}
                          {Math.abs(a.growth)}%
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </DashboardLayout>
  );
}
