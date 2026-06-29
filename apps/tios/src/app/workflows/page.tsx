'use client';

import { DashboardLayout } from '@/components/dashboard/layout';
import { WorkflowList } from '@/components/workflows/workflow-list';
import useSWR from 'swr';
import { Activity, CheckCircle2, XCircle, Play, Loader2 } from 'lucide-react';

const fetcher = (url: string) => fetch(url).then(r => r.json());

export default function WorkflowsPage() {
  const { data, error, isLoading } = useSWR<{
    workflows: { status: string }[];
    total: number;
    summary: { running: number; completed: number; failed: number };
  }>('/api/v1/workflows', fetcher);

  const s = data?.summary;
  const stats = [
    { label: 'Total', value: data?.total ?? data?.workflows?.length ?? 0, icon: Activity, color: 'text-blue-500' },
    { label: 'Running', value: s?.running ?? 0, icon: Play, color: 'text-green-500' },
    { label: 'Completed', value: s?.completed ?? 0, icon: CheckCircle2, color: 'text-blue-500' },
    { label: 'Failed', value: s?.failed ?? 0, icon: XCircle, color: 'text-red-500' },
  ];

  return (
    <DashboardLayout>
      <div className="p-6 space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Workflow Automation</h1>
          <p className="text-muted-foreground mt-1">
            Automated agent workflows and orchestration
          </p>
        </div>

        {/* Summary Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {stats.map(stat => {
            const Icon = stat.icon;
            return (
              <div key={stat.label} className="rounded-xl border bg-card p-4">
                <div className="flex items-center gap-2 mb-2">
                  <Icon className={`h-4 w-4 ${stat.color}`} />
                  <span className="text-xs text-muted-foreground">{stat.label}</span>
                </div>
                {isLoading ? (
                  <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
                ) : (
                  <p className="text-2xl font-bold">{stat.value}</p>
                )}
              </div>
            );
          })}
        </div>

        <WorkflowList />
      </div>
    </DashboardLayout>
  );
}
