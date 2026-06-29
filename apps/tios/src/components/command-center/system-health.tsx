'use client';

import { Activity, CheckCircle2, AlertTriangle, XCircle, Loader2, RefreshCw } from 'lucide-react';

interface Service {
  name: string;
  status: 'healthy' | 'degraded' | 'critical';
  uptime: string;
  version: string;
}

interface HealthData {
  overallStatus: 'healthy' | 'degraded' | 'critical';
  services: Service[];
  lastUpdated: string;
}

interface Props {
  data?: HealthData;
  isLoading: boolean;
}

const statusConfig: Record<string, { label: string; icon: typeof CheckCircle2; color: string; bg: string }> = {
  healthy: { label: 'Healthy', icon: CheckCircle2, color: 'text-emerald-500', bg: 'bg-emerald-500/10' },
  degraded: { label: 'Degraded', icon: AlertTriangle, color: 'text-amber-500', bg: 'bg-amber-500/10' },
  critical: { label: 'Critical', icon: XCircle, color: 'text-red-500', bg: 'bg-red-500/10' },
};

function Skeleton() {
  return (
    <div className="rounded-xl border bg-card">
      <div className="p-5 border-b">
        <div className="h-5 w-32 bg-muted rounded animate-pulse" />
      </div>
      <div className="p-5 space-y-3">
        {[1, 2, 3, 4].map(i => (
          <div key={i} className="h-14 bg-muted rounded-lg animate-pulse" />
        ))}
      </div>
    </div>
  );
}

export function SystemHealth({ data, isLoading }: Props) {
  if (isLoading) return <Skeleton />;
  if (!data) return null;

  const overall = statusConfig[data.overallStatus];
  const OverallIcon = overall.icon;

  return (
    <div className="rounded-xl border bg-card">
      <div className="p-5 border-b flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Activity className="h-5 w-5 text-primary" />
          <div>
            <h2 className="font-semibold">System Health</h2>
            <p className="text-xs text-muted-foreground mt-0.5">Service status overview</p>
          </div>
        </div>
        <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
          <RefreshCw className="h-3 w-3 animate-spin" />
          <span>Auto-refresh</span>
        </div>
      </div>

      <div className="p-5 space-y-4">
        <div className="flex items-center justify-between p-3 rounded-lg border">
          <span className="text-sm font-medium">Overall Status</span>
          <div className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${overall.bg} ${overall.color}`}>
            <OverallIcon className="h-3.5 w-3.5" />
            <span>{overall.label}</span>
          </div>
        </div>

        <div className="space-y-2">
          {data.services.map((service, i) => {
            const svc = statusConfig[service.status];
            const SvcIcon = svc.icon;
            return (
              <div
                key={i}
                className="flex items-center justify-between p-3 rounded-lg border hover:bg-accent/50 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <div className={`p-1 rounded-full ${svc.bg}`}>
                    <SvcIcon className={`h-3.5 w-3.5 ${svc.color}`} />
                  </div>
                  <div>
                    <p className="text-sm font-medium">{service.name}</p>
                    <p className="text-xs text-muted-foreground">
                      v{service.version} &middot; {service.uptime}
                    </p>
                  </div>
                </div>
                <span className={`text-xs font-medium ${svc.color}`}>
                  {svc.label}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
