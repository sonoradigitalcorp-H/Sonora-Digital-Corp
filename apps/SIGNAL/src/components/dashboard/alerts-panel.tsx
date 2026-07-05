'use client';

import { AlertTriangle, AlertCircle, Info, CheckCircle2, TrendingUp } from 'lucide-react';
import useSWR from 'swr';

const fetcher = (url: string) => fetch(url).then(r => r.json());

const typeConfig: Record<string, { icon: typeof AlertTriangle; containerClass: string }> = {
  critical: { icon: AlertTriangle, containerClass: 'text-red-500 bg-red-500/10' },
  warning: { icon: AlertCircle, containerClass: 'text-orange-500 bg-orange-500/10' },
  success: { icon: CheckCircle2, containerClass: 'text-green-500 bg-green-500/10' },
  info: { icon: Info, containerClass: 'text-blue-500 bg-blue-500/10' },
};

export function AlertsPanel() {
  const { data, error, isLoading } = useSWR('/api/v1/notifications', fetcher);

  if (error) {
    return <div className="kpi-card p-4"><p className="text-destructive text-xs">Failed to load alerts</p></div>;
  }

  if (isLoading) {
    return (
      <div className="kpi-card animate-pulse">
        <div className="px-4 pt-4 pb-3 border-b border-border flex items-center justify-between">
          <div className="space-y-1.5">
            <div className="h-4 w-24 bg-muted rounded" />
            <div className="h-2.5 w-16 bg-muted rounded" />
          </div>
          <div className="h-4 w-6 bg-muted rounded" />
        </div>
        <div>
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="flex items-start gap-3 px-4 py-3">
              <div className="w-7 h-7 rounded-md bg-muted" />
              <div className="flex-1 space-y-1">
                <div className="h-3.5 w-28 bg-muted rounded" />
                <div className="h-2.5 w-40 bg-muted rounded" />
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  const notifications = data?.notifications ?? [];
  const unread = data?.unread ?? 0;

  if (!notifications.length) {
    return (
      <div className="kpi-card p-6 text-center">
        <CheckCircle2 className="h-6 w-6 text-green-500 mx-auto mb-2" />
        <p className="text-xs text-muted-foreground">No active alerts</p>
      </div>
    );
  }

  return (
    <div className="kpi-card">
      <div className="px-4 pt-4 pb-3 border-b border-border flex items-center justify-between">
        <div>
          <h2 className="text-sm font-semibold tracking-tight">Active Alerts</h2>
          <p className="text-[11px] text-muted-foreground mt-0.5">Requires attention</p>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="relative flex h-5 w-5 items-center justify-center">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-destructive/20" />
            <span className="relative inline-flex rounded-full h-2 w-2 bg-destructive" />
          </span>
          <span className="text-sm font-bold text-destructive tabular-nums">{unread}</span>
        </div>
      </div>

      <div>
        {notifications.map((alert: { id: string; type: string; title: string; description: string; time: string; read: boolean }) => {
          const config = typeConfig[alert.type] ?? typeConfig.info;
          const Icon = config.icon;
          return (
            <div key={alert.id} className={`flex items-start gap-3 px-4 py-3 data-row cursor-pointer ${!alert.read ? 'bg-primary/[0.02] border-l-2 border-l-primary' : ''}`}>
              <div className={`p-1.5 rounded-md ${config.containerClass} shrink-0`}>
                <Icon className="h-3 w-3" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-xs font-medium">{alert.title}</p>
                <p className="text-[11px] text-muted-foreground">{alert.description}</p>
                <p className="text-[10px] text-muted-foreground mt-0.5">{alert.time}</p>
              </div>
            </div>
          );
        })}
      </div>

      <div className="p-3 border-t border-border">
        <button className="w-full text-center text-xs text-muted-foreground hover:text-foreground transition-colors group">
          View All Alerts <span className="inline-block transition-transform group-hover:translate-x-0.5">→</span>
        </button>
      </div>
    </div>
  );
}
