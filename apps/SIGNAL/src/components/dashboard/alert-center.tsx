'use client';

import { AlertTriangle, AlertCircle, Info, CheckCircle2, ArrowRight, Target, TrendingUp, TrendingDown, Eye, X } from 'lucide-react';
import useSWR from 'swr';

const fetcher = (url: string) => fetch(url).then(r => r.json());

interface ActionableAlert {
  id: string;
  type: string;
  priority: 'critical' | 'high' | 'medium' | 'low';
  title: string;
  reason: string;
  recommendedAction: string;
  expectedImpact: string;
  confidence: number;
  time: string;
  read: boolean;
}

const typeConfig: Record<string, { icon: typeof AlertTriangle; label: string; containerClass: string }> = {
  critical: { icon: AlertTriangle, label: 'Critical Priority', containerClass: 'text-red-500 bg-red-500/10 border-red-500/20' },
  warning: { icon: AlertCircle, label: 'High Priority', containerClass: 'text-orange-500 bg-orange-500/10 border-orange-500/20' },
  success: { icon: CheckCircle2, label: 'Resolved', containerClass: 'text-green-500 bg-green-500/10 border-green-500/20' },
  info: { icon: Info, label: 'Information', containerClass: 'text-blue-500 bg-blue-500/10 border-blue-500/20' },
};

function computeActionableAlerts(notifications: any[]): ActionableAlert[] {
  if (!notifications || !notifications.length) return [];

  const typeToPriority: Record<string, string> = {
    critical: 'critical',
    warning: 'high',
    success: 'low',
    info: 'medium',
  };

  return notifications.map((n: any) => {
    const type = n.type || 'info';
    const priority = typeToPriority[type] || 'medium';

    // Generate recommended action based on alert type and content
    let recommendedAction = 'Monitor situation for changes';
    let expectedImpact = 'Low — informational only';
    let confidence = 65;

    if (type === 'critical') {
      recommendedAction = 'Schedule immediate review with leadership team';
      expectedImpact = 'High — prevents potential portfolio risk escalation';
      confidence = 85;
    } else if (type === 'warning') {
      recommendedAction = 'Assign team member to investigate within 48 hours';
      expectedImpact = 'Medium — early intervention reduces future risk';
      confidence = 72;
    } else if (type === 'success') {
      recommendedAction = 'Document outcomes and update portfolio records';
      expectedImpact = 'Positive — strengthens portfolio position';
      confidence = 90;
    }

    // Try to extract a better reason from description
    let reason = n.description || 'System-generated notification';
    if (n.title?.toLowerCase().includes('score')) {
      reason = `Score change detected: ${n.description || n.title}`;
    } else if (n.title?.toLowerCase().includes('growth')) {
      reason = `Growth metric triggered: ${n.description || n.title}`;
    } else if (n.title?.toLowerCase().includes('alert')) {
      reason = n.description || 'Threshold breach detected';
    }

    return {
      id: n.id,
      type: n.type,
      priority,
      title: n.title || 'Notification',
      reason,
      recommendedAction,
      expectedImpact,
      confidence,
      time: n.time,
      read: n.read,
    };
  });
}

export function AlertCenter() {
  const { data, error, isLoading } = useSWR('/api/v1/notifications', fetcher);

  if (error) {
    return (
      <div className="kpi-card">
        <div className="flex items-center gap-2">
          <AlertTriangle className="h-4 w-4 text-amber-400" />
          <p className="text-destructive text-xs">Alert system unavailable</p>
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="kpi-card animate-pulse">
        <div className="px-4 pt-4 pb-3 border-b border-border flex items-center justify-between">
          <div className="space-y-1.5">
            <div className="h-4 w-28 bg-muted rounded" />
            <div className="h-2.5 w-20 bg-muted rounded" />
          </div>
          <div className="h-5 w-5 bg-muted rounded-full" />
        </div>
        <div>
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="px-4 py-3">
              <div className="flex items-start gap-3">
                <div className="w-7 h-7 rounded-md bg-muted" />
                <div className="flex-1 space-y-2">
                  <div className="h-3.5 w-32 bg-muted rounded" />
                  <div className="h-2.5 w-48 bg-muted rounded" />
                  <div className="flex gap-2">
                    <div className="h-2 w-16 bg-muted rounded" />
                    <div className="h-2 w-20 bg-muted rounded" />
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  const rawNotifications = data?.notifications ?? [];
  const unreadCount = data?.unread ?? 0;
  const alerts = computeActionableAlerts(rawNotifications);

  if (!alerts.length) {
    return (
      <div className="kpi-card text-center py-10">
        <div className="p-3 rounded-xl bg-green-500/5 border border-green-500/10 inline-block mb-3">
          <CheckCircle2 className="h-6 w-6 text-green-500" />
        </div>
        <p className="text-sm font-medium mb-1">All Clear</p>
        <p className="text-xs text-muted-foreground max-w-xs mx-auto leading-relaxed">
          No active alerts requiring your attention. Your portfolio is operating within expected parameters.
        </p>
      </div>
    );
  }

  return (
    <div className="kpi-card">
      <div className="px-4 pt-4 pb-3 border-b border-border flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-sm font-semibold tracking-tight">Critical Alerts</h2>
            {unreadCount > 0 && (
              <span className="relative flex h-2.5 w-2.5">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-destructive/30" />
                <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-destructive" />
              </span>
            )}
          </div>
          <p className="text-[11px] text-muted-foreground mt-0.5">
            {unreadCount > 0
              ? `${unreadCount} alert${unreadCount > 1 ? 's' : ''} require${unreadCount === 1 ? 's' : ''} your decision`
              : 'No unresolved alerts'
            }
          </p>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="text-sm font-bold tabular-nums">
            {alerts.filter(a => a.priority === 'critical' || a.priority === 'high').length}
          </span>
          <span className="text-[10px] text-muted-foreground">actionable</span>
        </div>
      </div>

      <div>
        {alerts.map((alert) => {
          const config = typeConfig[alert.type] ?? typeConfig.info;
          const Icon = config.icon;

          return (
            <div
              key={alert.id}
              className={`px-4 py-3 data-row cursor-pointer transition-all ${
                !alert.read ? 'border-l-2 border-l-primary bg-primary/[0.02]' : ''
              }`}
            >
              <div className="flex items-start gap-3">
                {/* Icon */}
                <div className={`p-1.5 rounded-md ${config.containerClass} shrink-0 mt-0.5`}>
                  <Icon className="h-3 w-3" />
                </div>

                <div className="flex-1 min-w-0">
                  {/* Title + Priority */}
                  <div className="flex items-center gap-2 flex-wrap">
                    <p className="text-xs font-semibold">{alert.title}</p>
                    <span className={`text-[9px] font-medium px-1.5 py-0.5 rounded-full uppercase tracking-wider ${
                      alert.priority === 'critical'
                        ? 'text-red-500 bg-red-500/10'
                        : alert.priority === 'high'
                          ? 'text-orange-500 bg-orange-500/10'
                          : alert.priority === 'medium'
                            ? 'text-primary bg-primary/10'
                            : 'text-muted-foreground bg-muted'
                    }`}>
                      {alert.priority}
                    </span>
                  </div>

                  {/* Reason */}
                  <p className="text-[11px] text-muted-foreground mt-0.5 leading-relaxed">
                    <span className="text-foreground/60 font-medium">Why: </span>
                    {alert.reason}
                  </p>

                  {/* Action + Impact row */}
                  <div className="flex flex-wrap items-center gap-3 mt-1.5">
                    <div className="flex items-center gap-1">
                      <Target className="h-3 w-3 text-primary" />
                      <span className="text-[10px] text-muted-foreground">{alert.recommendedAction}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <ArrowRight className="h-3 w-3 text-muted-foreground/60" />
                      <span className="text-[10px] text-muted-foreground/60">Impact: {alert.expectedImpact}</span>
                    </div>
                  </div>

                  {/* Confidence + Time */}
                  <div className="flex items-center gap-3 mt-1.5">
                    <div className="flex items-center gap-1">
                      <span className="text-[9px] text-muted-foreground/50">Confidence:</span>
                      <div className="w-12 h-1 rounded-full bg-muted overflow-hidden">
                        <div
                          className="h-full rounded-full bg-gradient-to-r from-primary to-green-500"
                          style={{ width: `${alert.confidence}%` }}
                        />
                      </div>
                      <span className="text-[9px] font-medium tabular-nums text-green-500">{alert.confidence}%</span>
                    </div>
                    {alert.time && (
                      <span className="text-[9px] text-muted-foreground/50">{alert.time}</span>
                    )}
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="p-3 border-t border-border">
        <button className="w-full text-center text-xs text-muted-foreground hover:text-foreground transition-colors group flex items-center justify-center gap-1">
          View Alert History <ArrowRight className="h-3 w-3 inline-block transition-transform group-hover:translate-x-0.5" />
        </button>
      </div>
    </div>
  );
}
