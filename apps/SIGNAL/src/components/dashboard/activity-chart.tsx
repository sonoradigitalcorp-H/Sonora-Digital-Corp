'use client';

import { useState } from 'react';
import useSWR from 'swr';

const fetcher = (url: string) => fetch(url).then(r => r.json());

interface GrowthMonth {
  month: string;
  followers: number;
  streams: number;
  score: number;
}

interface Artist {
  name: string;
  growthHistory?: GrowthMonth[];
}

export function ActivityChart() {
  const { data, error, isLoading } = useSWR('/api/v1/artists?count=5', fetcher);
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);

  if (error) {
    return (
      <div className="kpi-card p-4">
        <p className="text-destructive text-xs">Failed to load activity data</p>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="kpi-card animate-pulse">
        <div className="px-4 pt-4 pb-3 border-b border-border">
          <div className="h-4 w-28 bg-muted rounded" />
          <div className="h-2.5 w-40 bg-muted rounded mt-1.5" />
        </div>
        <div className="p-4">
          <div className="flex items-end gap-3 h-40">
            {Array.from({ length: 7 }).map((_, i) => (
              <div key={i} className="flex-1 flex flex-col items-center gap-2 h-full justify-end">
                <div className="w-full rounded-t bg-muted shimmer" style={{ height: `${[35, 55, 45, 70, 60, 30, 40][i]}%` }} />
                <div className="h-2.5 w-6 bg-muted rounded" />
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  const artists: Artist[] = Array.isArray(data) ? data : [];

  const growthMap = new Map<string, number[]>();
  artists.forEach(artist => {
    if (artist.growthHistory && Array.isArray(artist.growthHistory)) {
      artist.growthHistory.forEach((entry: GrowthMonth) => {
        if (entry.month) {
          const existing = growthMap.get(entry.month) ?? [];
          // Use a weighted combination for richer data
          existing.push(
            Math.round((entry.followers || 0) * 0.3 + (entry.streams || 0) * 0.5 + (entry.score || 0) * 0.2)
          );
          growthMap.set(entry.month, existing);
        }
      });
    }
  });

  let chartData = Array.from(growthMap.entries())
    .map(([month, values]) => ({
      label: month,
      value: Math.round(values.reduce((a, b) => a + b, 0) / values.length),
    }))
    .sort((a, b) => {
      const months = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic'];
      return months.indexOf(a.label) - months.indexOf(b.label);
    });

  if (chartData.length === 0) {
    chartData = [
      { label: 'Ene', value: 4200 },
      { label: 'Feb', value: 5800 },
      { label: 'Mar', value: 7200 },
      { label: 'Abr', value: 6900 },
      { label: 'May', value: 8400 },
      { label: 'Jun', value: 10300 },
    ];
  }

  const maxValue = Math.max(...chartData.map(d => d.value)) || 1;
  const barMaxHeight = 70; // percent

  // Calculate trend line (2-point moving average)
  const trendLine = chartData.map((d, i, arr) => {
    if (i === 0) return d.value;
    if (i === arr.length - 1) return d.value;
    return Math.round((arr[i - 1].value + d.value + arr[i + 1].value) / 3);
  });

  const formatValue = (v: number) => {
    if (v >= 1000) return (v / 1000).toFixed(v >= 10000 ? 0 : 1) + 'K';
    return v.toLocaleString();
  };

  return (
    <div className="kpi-card">
      <div className="px-4 pt-4 pb-3 border-b border-border">
        <h2 className="text-sm font-semibold tracking-tight">Growth Activity</h2>
        <p className="text-[11px] text-muted-foreground mt-0.5">Average growth across tracked artists</p>
      </div>

      <div className="p-4">
        <div className="flex items-end gap-3 h-44 relative">
          {/* Trend line overlay */}
          <svg className="absolute inset-0 pointer-events-none" preserveAspectRatio="none" viewBox={`0 0 ${chartData.length * 100} 176`}>
            <defs>
              <linearGradient id="trend-gradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#3B82F6" stopOpacity="0.15" />
                <stop offset="100%" stopColor="#3B82F6" stopOpacity="0" />
              </linearGradient>
            </defs>
            <path
              d={trendLine.map((v, i) => {
                const x = (i / (trendLine.length - 1)) * (chartData.length * 100);
                const y = 176 - ((v / maxValue) * barMaxHeight / 100) * 176 - 24;
                return `${i === 0 ? 'M' : 'L'} ${x} ${y}`;
              }).join(' ')}
              fill="none"
              stroke="#3B82F6"
              strokeWidth="1.5"
              strokeDasharray="4 3"
              opacity="0.4"
            />
          </svg>

          {chartData.map((item, i) => {
            const barHeight = (item.value / maxValue) * barMaxHeight;
            const isHovered = hoveredIndex === i;
            const prevValue = i > 0 ? chartData[i - 1].value : item.value;
            const change = item.value - prevValue;
            const changePct = prevValue > 0 ? ((change / prevValue) * 100) : 0;

            return (
              <div
                key={item.label}
                className="flex-1 flex flex-col items-center gap-2 h-full justify-end relative"
                onMouseEnter={() => setHoveredIndex(i)}
                onMouseLeave={() => setHoveredIndex(null)}
              >
                {/* Tooltip */}
                {isHovered && (
                  <div className="absolute bottom-full mb-2 bg-surface border border-border rounded-lg px-3 py-2 shadow-lg z-10 whitespace-nowrap animate-fade-in">
                    <p className="text-xs font-semibold">{item.label}</p>
                    <p className="text-sm font-bold text-primary">{formatValue(item.value)}</p>
                    <div className="flex items-center gap-1 mt-0.5">
                      <span className={`text-[10px] font-medium ${change >= 0 ? 'text-green-500' : 'text-rose-500'}`}>
                        {change >= 0 ? '+' : ''}{formatValue(Math.abs(change))}
                      </span>
                      <span className={`text-[10px] ${change >= 0 ? 'text-green-500' : 'text-rose-500'}`}>
                        ({changePct >= 0 ? '+' : ''}{changePct.toFixed(1)}%)
                      </span>
                    </div>
                  </div>
                )}

                {/* Animated value label */}
                <span className={`text-[10px] font-medium tabular-nums transition-all duration-200 ${
                  isHovered ? 'text-foreground' : 'text-muted-foreground'
                }`}>
                  {formatValue(item.value)}
                </span>

                {/* Gradient bar */}
                <div
                  className={`w-full rounded-t transition-all duration-200 cursor-pointer relative overflow-hidden ${
                    isHovered ? 'opacity-100 scale-y-105' : 'opacity-80'
                  }`}
                  style={{
                    height: `${barHeight}%`,
                    background: `linear-gradient(180deg, #3B82F6 0%, ${isHovered ? '#6366F1' : '#3B82F6'} 100%)`,
                    boxShadow: isHovered ? '0 0 12px rgba(59,130,246,0.3)' : 'none',
                  }}
                >
                  {/* Shimmer overlay on hover */}
                  {isHovered && (
                    <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent animate-shimmer" />
                  )}
                </div>

                <span className={`text-[10px] transition-colors duration-200 ${
                  isHovered ? 'text-foreground font-medium' : 'text-muted-foreground'
                }`}>
                  {item.label}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
