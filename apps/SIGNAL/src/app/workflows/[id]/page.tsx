'use client';

import { useParams } from 'next/navigation';
import useSWR from 'swr';
import { DashboardLayout } from '@/components/dashboard/layout';
import { WorkflowDetail } from '@/components/workflows/workflow-detail';
import { WorkflowControls } from '@/components/workflows/workflow-controls';
import { ExecutionTimeline } from '@/components/workflows/execution-timeline';
import { ApprovalGate } from '@/components/workflows/approval-gate';
import { ArrowLeft, Loader2 } from 'lucide-react';
import Link from 'next/link';

const fetcher = (url: string) => fetch(url).then(r => r.json());

type StepData = {
  name: string;
  status: 'completed' | 'running' | 'failed' | 'pending' | 'in_progress';
  agent?: string;
};

type WorkflowData = {
  id: string;
  name: string;
  type: string;
  status: 'running' | 'paused' | 'failed' | 'completed' | 'waiting_approval';
  priority: 'low' | 'medium' | 'high' | 'critical';
  progress: number;
  steps_total: number;
  steps_completed: number;
  created: string;
  steps: StepData[];
};

export default function WorkflowDetailPage() {
  const params = useParams();
  const id = params.id as string;

  const { data: workflow, error, isLoading } = useSWR<WorkflowData>(
    `/api/v1/workflows/${id}`,
    fetcher,
  );

  if (error) {
    return (
      <DashboardLayout>
        <div className="p-6">
          <div className="rounded-xl border bg-card p-8 text-center">
            <p className="text-destructive font-medium">Failed to load workflow</p>
            <p className="text-sm text-muted-foreground mt-1">The workflow may not exist or the server is unavailable.</p>
            <Link href="/workflows" className="inline-flex items-center gap-1 mt-4 text-sm text-primary hover:underline">
              <ArrowLeft className="h-4 w-4" />
              Back to Workflows
            </Link>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  if (isLoading || !workflow) {
    return (
      <DashboardLayout>
        <div className="p-6">
          <div className="flex items-center justify-center h-64">
            <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
          </div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="p-6 space-y-6">
        {/* Back link */}
        <Link href="/workflows" className="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground transition-colors">
          <ArrowLeft className="h-4 w-4" />
          Back to Workflows
        </Link>

        {/* Detail Panel */}
        <WorkflowDetail workflow={workflow} />

        {/* Controls */}
        <WorkflowControls workflowId={workflow.id} status={workflow.status} />

        {/* Approval Gate */}
        <ApprovalGate workflowId={workflow.id} />

        {/* Execution Timeline */}
        <ExecutionTimeline steps={workflow.steps} />
      </div>
    </DashboardLayout>
  );
}
