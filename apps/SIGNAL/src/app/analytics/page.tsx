'use client';

import { useState } from 'react';
import { DashboardLayout } from '@/components/dashboard/layout';
import {
  BarChart3, TrendingUp, ArrowUp, ArrowDown, Star, Users, AlertTriangle,
  Target, Loader2, AlertCircle, Music2, Eye, Bell,
} from 'lucide-react';
import useSWR from 'swr';

const fetcher = (url: string) => fetch(url).then(r => r.json());

const kpiIcons: Record<string, React.ElementType> = {
  'Artists Tracked': Users,
  'Avg Discovery Score': Star,
  'Active Pipeline': Music2,
  'Alerts Active': Bell,
  'Prospect Radar': Eye,
  'Signing Readiness': Target,
};

function formatCurrency(n: number) {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', notation: 'compact', maximumFractionDigits: 0 }).format(n);
}

function formatNumber(n: number) {
  return new Intl.NumberFormat('en-US', { notation: 'compact', maximumFractionDigits: 0 }).format(n);
}

function SkeletonCard() {
  return <div className="rounded-xl border bg-card p-5 space-y-3 animate-pulse"><div className="h-3 w-24 bg-muted rounded" /><div className="h-7 w-16 bg-muted rounded" /><div className="h-3 w-20 bg-muted rounded" /></div>;
}

function AnimatedBar({ pct, color, delay = 0 }: { pct: number; color: string; delay?: number }) {
  const [width, setWidth] = useState(0);
  useState(() => { setTimeout(() => setWidth(pct), 50); });
  return (
    <div className="h-2 rounded-full bg-muted overflow-hidden">
      <div
        className="h-full rounded-full transition-all duration-700"
        style={{
          width: `${width}%`,
          background: `linear-gradient(90deg, ${color}, ${color}88)`,
          transitionDelay: `${delay}ms`,
        }}
      />
    </div>
  );
}

export default function AnalyticsPage() {
  const [range, setRange] = useState<'7d' | '30d' | '90d'>('30d');
  const { data, error, isLoading } = useSWR(`/api/v1/analytics?range=${range}`, fetcher, { revalidateOnFocus: false });

  return (
    <DashboardLayout>
      <div className="p-6 space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold tracking-tight">Analytics</h1>
            <p className="text-muted-foreground mt-1">Comprehensive performance metrics and trends</p>
          </div>
          {/* Date range picker */}
          <div className="flex items-center gap-1 p-1 rounded-lg bg-muted">
            {(['7d', '30d', '90d'] as const).map(opt => (
              <button
                key={opt}
                onClick={() => setRange(opt)}
                className={`px-3 py-1.5 text-xs font-medium rounded-md transition-all ${
                  range === opt ? 'bg-background text-foreground shadow-sm' : 'text-muted-foreground hover:text-foreground'
                }`}
              >
                {opt}
              </button>
            ))}
          </div>
        </div>

        {error && (
          <div className="flex items-center gap-2 p-4 rounded-xl border border-red-500/20 bg-red-500/5 text-red-500">
            <AlertCircle className="h-4 w-4 shrink-0" />
            <div>
              <p className="text-sm font-medium">Failed to load analytics data</p>
              <p className="text-xs text-red-400/80 mt-0.5">{error.message}</p>
            </div>
          </div>
        )}

        {isLoading && (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {[...Array(4)].map((_, i) => <SkeletonCard key={i} />)}
            </div>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="rounded-xl border bg-card p-5 space-y-3 animate-pulse">
                <div className="h-4 w-32 bg-muted rounded mb-4" />
                {[...Array(6)].map((_, i) => (
                  <div key={i} className="space-y-1">
                    <div className="flex justify-between"><div className="h-3 w-24 bg-muted rounded" /><div className="h-3 w-12 bg-muted rounded" /></div>
                    <div className="h-2 rounded-full bg-muted" style={{ width: `${60 + Math.random() * 40}%` }} />
                  </div>
                ))}
              </div>
              <div className="rounded-xl border bg-card p-5 space-y-3 animate-pulse">
                <div className="h-4 w-32 bg-muted rounded mb-4" />
                {[...Array(8)].map((_, i) => (
                  <div key={i} className="flex items-center justify-between p-2"><div className="h-3 w-28 bg-muted rounded" /><div className="h-3 w-16 bg-muted rounded" /></div>
                ))}
              </div>
            </div>
          </>
        )}

        {data && (
          <>
            {/* KPI Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {data.kpiMetrics.map((m: any, i: number) => {
                const Icon = kpiIcons[m.label] || BarChart3;
                return (
                  <div key={i} className="rounded-xl border bg-card p-5 card-hover">
                    <div className="flex items-center justify-between mb-2">
                      <p className="text-sm text-muted-foreground">{m.label}</p>
                      <Icon className="h-4 w-4 text-primary" />
                    </div>
                    <p className="text-2xl font-bold tabular-nums">{m.value}</p>
                    <div className={`flex items-center gap-1 mt-1 text-xs font-medium ${m.trend === 'up' ? 'text-green-500' : 'text-red-500'}`}>
                      {m.trend === 'up' ? <ArrowUp className="h-3 w-3" /> : <ArrowDown className="h-3 w-3" />}
                      {m.change}
                    </div>
                  </div>
                );
              })}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Genre Distribution */}
              <div className="rounded-xl border bg-card p-5">
                <h2 className="font-semibold mb-4 flex items-center gap-2">
                  <BarChart3 className="h-4 w-4 text-primary" />
                  Genre Distribution
                </h2>
                <div className="space-y-4">
                  {data.genreDistribution.map((g: any, i: number) => (
                    <div key={i}>
                      <div className="flex items-center justify-between text-sm mb-1">
                        <span className="font-medium">{g.genre}</span>
                        <span className="text-xs text-muted-foreground tabular-nums">{g.percentage}%</span>
                      </div>
                      <AnimatedBar pct={g.percentage} color={g.color || '#3B82F6'} delay={i * 50} />
                    </div>
                  ))}
                </div>
              </div>

              {/* Top 10 for Signing */}
              <div className="rounded-xl border bg-card p-5">
                <h2 className="font-semibold mb-4 flex items-center gap-2">
                  <TrendingUp className="h-4 w-4 text-primary" />
                  Top 10 for Signing
                </h2>
                <div className="space-y-1 max-h-[500px] overflow-y-auto pr-1">
                  {data.topForSigning.map((a: any, i: number) => (
                    <div key={i} className="flex items-center justify-between p-3 rounded-lg data-row group">
                      <div className="flex items-center gap-3 min-w-0">
                        <span className="text-sm font-medium text-muted-foreground w-6 shrink-0 text-right">{a.rank}.</span>
                        <div className="min-w-0">
                          <p className="text-sm font-medium truncate">{a.name}</p>
                          <p className="text-xs text-muted-foreground truncate">{a.contact}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-3 shrink-0">
                        <div className="text-right">
                          <p className="text-sm font-semibold tabular-nums">{a.score}</p>
                          <p className="text-xs text-muted-foreground tabular-nums">{formatCurrency(a.dealEstimate)}</p>
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
