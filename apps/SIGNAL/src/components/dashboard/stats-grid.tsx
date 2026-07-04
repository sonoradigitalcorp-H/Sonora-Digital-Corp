'use client';

import { Users, TrendingUp, Music2, Activity, Eye, Target, Loader2 } from 'lucide-react';
import useSWR from 'swr';

const fetcher = (url: string) => fetch(url).then(r => r.json());

const kpiConfig: Record<string, { icon: typeof Users; color: string }> = {
  'Artists Tracked': { icon: Users, color: 'text-primary' },
  'Avg Discovery Score': { icon: TrendingUp, color: 'text-green-500' },
  'Active Pipeline': { icon: Music2, color: 'text-purple-400' },
  'Alerts Active': { icon: Activity, color: 'text-amber-400' },
  'Prospect Radar': { icon: Eye, color: 'text-cyan-400' },
  'Signing Readiness': { icon: Target, color: 'text-rose-400' },
};

export function StatsGrid() {
  const { data, error, isLoading } = useSWR('/api/v1/analytics', fetcher);

  if (error) {
    return <div className="text-destructive text-xs p-3">Failed to load KPIs</div>;
  }

  if (isLoading) {
    return (
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="kpi-card animate-pulse">
            <div className="h-4 w-4 bg-muted rounded mb-3" />
            <div className="h-6 w-14 bg-muted rounded mb-1" />
            <div className="h-2.5 w-16 bg-muted rounded" />
          </div>
        ))}
      </div>
    );
  }

  const kpis = data?.kpiMetrics ?? [];

  if (!kpis.length) {
    return <div className="text-muted-foreground text-xs p-3">No KPI data available</div>;
  }

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
      {kpis.map((kpi: { label: string; value: number | string; change: string; trend: string }) => {
        const config = kpiConfig[kpi.label];
        const Icon = config?.icon;
        const colorClass = config?.color ?? 'text-muted-foreground';
        const isPositive = String(kpi.change).startsWith('+');

        return (
          <div key={kpi.label} className="kpi-card">
            <div className="flex items-center justify-between mb-2">
              {Icon && <Icon className={`h-4 w-4 ${colorClass}`} />}
              <span className={`text-[10px] font-medium ${isPositive ? 'text-green-500' : 'text-rose-500'}`}>
                {kpi.change}
              </span>
            </div>
            <p className="kpi-value">{kpi.value}</p>
            <p className="kpi-label">{kpi.label}</p>
          </div>
        );
      })}
    </div>
  );
}
