'use client';

import { Users, TrendingUp, Music2, Activity, Eye, Target, Loader2, ArrowUp, ArrowDown } from 'lucide-react';
import useSWR from 'swr';

const fetcher = (url: string) => fetch(url).then(r => r.json());

const kpiConfig: Record<string, { icon: typeof Users; color: string; chartColor: string }> = {
  'Artists Tracked': { icon: Users, color: 'text-primary', chartColor: '#3B82F6' },
  'Avg Discovery Score': { icon: TrendingUp, color: 'text-green-500', chartColor: '#10b981' },
  'Active Pipeline': { icon: Music2, color: 'text-purple-400', chartColor: '#a78bfa' },
  'Alerts Active': { icon: Activity, color: 'text-amber-400', chartColor: '#f59e0b' },
  'Prospect Radar': { icon: Eye, color: 'text-cyan-400', chartColor: '#22d3ee' },
  'Signing Readiness': { icon: Target, color: 'text-rose-400', chartColor: '#f43f5e' },
};

// Mini sparkline SVG component
function Sparkline({ data, color, height = 28 }: { data?: number[]; color: string; height?: number }) {
  const points = data && data.length > 0
    ? data
    : [30, 45, 38, 52, 48, 60, 55, 62, 58, 70, 68, 75];

  const max = Math.max(...points) || 1;
  const min = Math.min(...points) || 0;
  const range = max - min || 1;

  const width = points.length * 8;
  const pathD = points.map((p, i) => {
    const x = (i / (points.length - 1)) * width;
    const y = height - ((p - min) / range) * (height - 4) - 2;
    return `${i === 0 ? 'M' : 'L'} ${x} ${y}`;
  }).join(' ');

  return (
    <svg width={width} height={height} className="w-full h-full" viewBox={`0 0 ${width} ${height}`} preserveAspectRatio="none">
      <defs>
        <linearGradient id={`grad-${color.replace('#', '')}`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={color} stopOpacity="0.2" />
          <stop offset="100%" stopColor={color} stopOpacity="0" />
        </linearGradient>
      </defs>
      <path d={pathD} fill="none" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
      <path d={`${pathD} L ${width} ${height} L 0 ${height} Z`} fill={`url(#grad-${color.replace('#', '')})`} />
    </svg>
  );
}

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
      {kpis.map((kpi: { label: string; value: number | string; change: string; trend: string; history?: number[] }) => {
        const config = kpiConfig[kpi.label];
        const Icon = config?.icon;
        const colorClass = config?.color ?? 'text-muted-foreground';
        const isPositive = String(kpi.change).startsWith('+');
        const chartColor = config?.chartColor ?? '#3B82F6';

        return (
          <div key={kpi.label} className="kpi-card relative overflow-hidden group">
            <div className="flex items-center justify-between mb-2">
              {Icon && <Icon className={`h-4 w-4 ${colorClass}`} />}
              <span className={`flex items-center gap-0.5 text-[10px] font-medium ${isPositive ? 'text-green-500' : 'text-rose-500'}`}>
                {isPositive ? <ArrowUp className="h-3 w-3" /> : <ArrowDown className="h-3 w-3" />}
                {kpi.change}
              </span>
            </div>
            <p className="kpi-value">{kpi.value}</p>
            <p className="kpi-label">{kpi.label}</p>

            {/* Sparkline at bottom */}
            <div className="absolute bottom-0 left-0 right-0 h-8 opacity-30 group-hover:opacity-50 transition-opacity pointer-events-none">
              <Sparkline data={kpi.history} color={chartColor} />
            </div>
          </div>
        );
      })}
    </div>
  );
}
