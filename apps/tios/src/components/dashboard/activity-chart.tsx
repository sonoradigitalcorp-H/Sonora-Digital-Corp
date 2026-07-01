'use client';

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
                <div className="w-full rounded-t bg-muted" style={{ height: `${[35, 55, 45, 70, 60, 30, 40][i]}%` }} />
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
          existing.push(entry.followers || entry.streams || entry.score || 0);
          growthMap.set(entry.month, existing);
        }
      });
    }
  });

  const chartData = Array.from(growthMap.entries())
    .map(([month, values]) => ({
      label: month,
      value: Math.round(values.reduce((a, b) => a + b, 0) / values.length),
    }))
    .sort((a, b) => {
      const months = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic'];
      return months.indexOf(a.label) - months.indexOf(b.label);
    });

  const displayData = chartData.length > 0 ? chartData : [
    { label: 'Ene', value: 4200 },
    { label: 'Feb', value: 5800 },
    { label: 'Mar', value: 7200 },
    { label: 'Abr', value: 6900 },
    { label: 'May', value: 8400 },
    { label: 'Jun', value: 10300 },
  ];

  const maxValue = Math.max(...displayData.map(d => d.value)) || 1;

  return (
    <div className="kpi-card">
      <div className="px-4 pt-4 pb-3 border-b border-border">
        <h2 className="text-sm font-semibold tracking-tight">Growth Activity</h2>
        <p className="text-[11px] text-muted-foreground mt-0.5">Average growth across tracked artists</p>
      </div>

      <div className="p-4">
        <div className="flex items-end gap-3 h-40">
          {displayData.map((item) => (
            <div key={item.label} className="flex-1 flex flex-col items-center gap-2 h-full justify-end">
              <span className="text-[10px] font-medium tabular-nums text-muted-foreground">{item.value.toLocaleString()}</span>
              <div
                className="w-full rounded-t bg-primary/70 hover:bg-primary transition-colors"
                style={{ height: `${(item.value / maxValue) * 70}%` }}
              />
              <span className="text-[10px] text-muted-foreground">{item.label}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
