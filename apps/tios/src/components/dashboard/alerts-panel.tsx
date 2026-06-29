'use client';

import { AlertTriangle, AlertCircle, Info, CheckCircle2 } from 'lucide-react';
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
    return (
      <div className="rounded-xl border bg-card p-5">
        <p className="text-destructive text-sm">Failed to load alerts</p>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="rounded-xl border bg-card animate-pulse">
        <div className="p-5 border-b flex items-center justify-between">
          <div className="space-y-2">
            <div className="h-5 w-28 bg-muted rounded" />
            <div className="h-3 w-20 bg-muted rounded" />
          </div>
          <div className="h-5 w-8 bg-muted rounded" />
        </div>
        <div className="divide-y">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="flex items-start gap-3 p-4">
              <div className="w-9 h-9 rounded-lg bg-muted" />
              <div className="flex-1 space-y-1">
                <div className="h-4 w-32 bg-muted rounded" />
                <div className="h-3 w-48 bg-muted rounded" />
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
      <div className="rounded-xl border bg-card p-5 text-center">
        <AlertTriangle className="h-8 w-8 text-muted-foreground mx-auto mb-2" />
        <p className="text-sm text-muted-foreground">No active alerts</p>
      </div>
    );
  }

  return (
    <div className="rounded-xl border bg-card">
      <div className="p-5 border-b flex items-center justify-between">
        <div>
          <h2 className="font-semibold">Active Alerts</h2>
          <p className="text-xs text-muted-foreground mt-0.5">Requires attention</p>
        </div>
        <div className="flex items-center gap-1">
          <AlertTriangle className="h-4 w-4 text-destructive" />
          <span className="text-sm font-bold text-destructive">{unread}</span>
        </div>
      </div>

      <div className="divide-y">
        {notifications.map((alert: {
          id: string;
          type: string;
          title: string;
          description: string;
          time: string;
          read: boolean;
        }) => {
          const config = typeConfig[alert.type] ?? typeConfig.info;
          const Icon = config.icon;
          return (
            <div key={alert.id} className={`flex items-start gap-3 p-4 hover:bg-accent/50 transition-colors cursor-pointer ${!alert.read ? 'bg-accent/30' : ''}`}>
              <div className={`p-1.5 rounded-lg ${config.containerClass}`}>
                <Icon className="h-3.5 w-3.5" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium">{alert.title}</p>
                <p className="text-xs text-muted-foreground">{alert.description}</p>
              </div>
              <span className="text-xs text-muted-foreground whitespace-nowrap">{alert.time}</span>
            </div>
          );
        })}
      </div>

      <div className="p-3 border-t">
        <button className="w-full text-center text-sm text-muted-foreground hover:text-foreground transition-colors">
          View All Alerts →
        </button>
      </div>
    </div>
  );
}
