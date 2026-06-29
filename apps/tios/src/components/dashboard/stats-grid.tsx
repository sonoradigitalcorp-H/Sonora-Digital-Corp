'use client';

import { Users, TrendingUp, Music2, Activity, Eye, Target, Loader2 } from 'lucide-react';
import useSWR from 'swr';

const fetcher = (url: string) => fetch(url).then(r => r.json());

const kpiConfig: Record<string, { icon: typeof Users; color: string }> = {
  'Artists Tracked': { icon: Users, color: 'text-blue-500' },
  'Avg Discovery Score': { icon: TrendingUp, color: 'text-green-500' },
  'Active Pipeline': { icon: Music2, color: 'text-purple-500' },
  'Alerts Active': { icon: Activity, color: 'text-orange-500' },
  'Prospect Radar': { icon: Eye, color: 'text-cyan-500' },
  'Signing Readiness': { icon: Target, color: 'text-rose-500' },
};

export function StatsGrid() {
  const { data, error, isLoading } = useSWR('/api/v1/analytics', fetcher);

  if (error) {
    return <div className="text-destructive text-sm p-4">Failed to load KPIs</div>;
  }

  if (isLoading) {
    return (
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="rounded-xl border bg-card p-4 animate-pulse">
            <div className="h-5 w-5 bg-muted rounded mb-3" />
            <div className="h-7 w-16 bg-muted rounded mb-1" />
            <div className="h-3 w-20 bg-muted rounded" />
          </div>
        ))}
      </div>
    );
  }

  const kpis = data?.kpiMetrics ?? [];

  if (!kpis.length) {
    return <div className="text-muted-foreground text-sm p-4">No KPI data available</div>;
  }

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
      {kpis.map((kpi: { label: string; value: number | string; change: string; trend: string }) => {
        const config = kpiConfig[kpi.label];
        const Icon = config?.icon;
        const colorClass = config?.color ?? 'text-muted-foreground';
        const isPositive = String(kpi.change).startsWith('+');

        return (
          <div key={kpi.label} className="rounded-xl border bg-card p-4 hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between mb-3">
              {Icon && <Icon className={`h-5 w-5 ${colorClass}`} />}
              <span className={`text-xs font-medium ${isPositive ? 'text-green-500' : 'text-orange-500'}`}>
                {kpi.change}
              </span>
            </div>
            <p className="text-2xl font-bold">{kpi.value}</p>
            <p className="text-xs text-muted-foreground mt-1">{kpi.label}</p>
          </div>
        );
      })}
    </div>
  );
}
