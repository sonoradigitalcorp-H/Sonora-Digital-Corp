'use client';

import { useMemo } from 'react';
import { Activity, Play, Pause, Clock, AlertTriangle, ArrowRight, Loader2, BarChart3 } from 'lucide-react';
import Link from 'next/link';
import { generateWorkflowStatusBreakdown } from '@/lib/data-generator';

interface Metrics {
  activeWorkflows: number;
  pendingApprovals: number;
  successRate: number;
}

interface Props {
  data?: Metrics;
  isLoading: boolean;
}

function Skeleton() {
  return (
    <div className="rounded-xl border bg-card">
      <div className="p-5 border-b">
        <div className="h-5 w-40 bg-muted rounded animate-pulse" />
      </div>
      <div className="p-5 space-y-4">
        <div className="h-8 bg-muted rounded animate-pulse" />
        <div className="h-8 bg-muted rounded animate-pulse" />
        <div className="h-8 bg-muted rounded animate-pulse" />
        <div className="h-8 bg-muted rounded animate-pulse" />
      </div>
    </div>
  );
}

export function ActiveWorkflows({ data, isLoading }: Props) {
  const breakdown = useMemo(() => generateWorkflowStatusBreakdown(), []);
  const statusConfig = useMemo(() => [
    { key: 'running', label: 'Running', value: breakdown.running, color: 'bg-emerald-500', icon: Play },
    { key: 'paused', label: 'Paused', value: breakdown.paused, color: 'bg-amber-500', icon: Pause },
    { key: 'waiting_approval', label: 'Waiting Approval', value: breakdown.waiting_approval, color: 'bg-blue-500', icon: Clock },
    { key: 'failed', label: 'Failed', value: breakdown.failed, color: 'bg-red-500', icon: AlertTriangle },
  ], [breakdown]);

  if (isLoading) return <Skeleton />;

  const maxValue = Math.max(...statusConfig.map(s => s.value));

  return (
    <div className="rounded-xl border bg-card">
      <div className="p-5 border-b flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Activity className="h-5 w-5 text-primary" />
          <div>
            <h2 className="font-semibold">Active Workflows</h2>
            <p className="text-xs text-muted-foreground mt-0.5">
              {data ? `${data.activeWorkflows} running across all pipelines` : 'Pipeline activity'}
            </p>
          </div>
        </div>
        <Link
          href="/workflows"
          className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground transition-colors"
        >
          View all
          <ArrowRight className="h-3 w-3" />
        </Link>
      </div>

      <div className="p-5 space-y-4">
        {statusConfig.map(({ key, label, value, color, icon: Icon }) => (
          <div key={key} className="space-y-1.5">
            <div className="flex items-center justify-between text-sm">
              <div className="flex items-center gap-2">
                <Icon className="h-3.5 w-3.5 text-muted-foreground" />
                <span>{label}</span>
              </div>
              <span className="font-bold">{value}</span>
            </div>
            <div className="h-2 rounded-full bg-muted overflow-hidden">
              <div
                className={`h-full rounded-full transition-all duration-500 ${color}`}
                style={{ width: `${(value / maxValue) * 100}%` }}
              />
            </div>
          </div>
        ))}
      </div>

      <div className="p-3 border-t flex justify-center">
        <Link
          href="/workflows"
          className="flex items-center gap-2 px-4 py-2 rounded-lg border bg-card text-sm hover:bg-accent transition-colors"
        >
          <BarChart3 className="h-4 w-4" />
          <span>Go to Workflows</span>
        </Link>
      </div>
    </div>
  );
}
