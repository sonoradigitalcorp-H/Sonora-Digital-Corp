'use client';

import { FileText, Target, Brain, TrendingUp } from 'lucide-react';

type WorkflowData = {
  id: string;
  name: string;
  type: string;
  status: 'running' | 'paused' | 'failed' | 'completed' | 'waiting_approval';
  priority: 'low' | 'medium' | 'high' | 'critical';
  steps_completed: number;
  steps_total: number;
  progress?: number;
  created: string;
};

const statusConfig: Record<string, { color: string; label: string }> = {
  running: { color: 'text-green-500', label: 'Running' },
  paused: { color: 'text-amber-500', label: 'Paused' },
  failed: { color: 'text-red-500', label: 'Failed' },
  completed: { color: 'text-blue-500', label: 'Completed' },
  waiting_approval: { color: 'text-purple-500', label: 'Waiting Approval' },
};

const priorityColors: Record<string, string> = {
  low: 'text-muted-foreground',
  medium: 'text-blue-500',
  high: 'text-amber-500',
  critical: 'text-red-500',
};

export function WorkflowDetail({ workflow }: { workflow: WorkflowData }) {
  const sc = statusConfig[workflow.status] || { color: 'text-muted-foreground', label: workflow.status };
  const progress = workflow.steps_total > 0 ? (workflow.steps_completed / workflow.steps_total) * 100 : 0;

  return (
    <div className="rounded-xl border bg-card p-6 space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="space-y-1">
          <div className="flex items-center gap-3">
            <h2 className="text-2xl font-bold">{workflow.name}</h2>
            <span className={`text-xs px-2 py-1 rounded-full border font-medium bg-card ${sc.color}`}>
              {sc.label}
            </span>
          </div>
          <p className="text-sm text-muted-foreground">Type: {workflow.type}</p>
        </div>
        <span className={`text-xs font-medium ${priorityColors[workflow.priority]}`}>
          {workflow.priority.toUpperCase()} PRIORITY
        </span>
      </div>

      {/* Metadata grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="flex items-start gap-3 p-3 rounded-lg bg-muted/50">
          <Brain className="h-4 w-4 text-primary mt-0.5" />
          <div>
            <p className="text-xs text-muted-foreground">Type</p>
            <p className="text-sm font-medium">{workflow.type}</p>
          </div>
        </div>
        <div className="flex items-start gap-3 p-3 rounded-lg bg-muted/50">
          <Target className="h-4 w-4 text-primary mt-0.5" />
          <div>
            <p className="text-xs text-muted-foreground">Priority</p>
            <p className="text-sm font-medium capitalize">{workflow.priority}</p>
          </div>
        </div>
        <div className="flex items-start gap-3 p-3 rounded-lg bg-muted/50">
          <FileText className="h-4 w-4 text-primary mt-0.5" />
          <div>
            <p className="text-xs text-muted-foreground">Created</p>
            <p className="text-sm font-medium">{new Date(workflow.created).toLocaleString()}</p>
          </div>
        </div>
        <div className="flex items-start gap-3 p-3 rounded-lg bg-muted/50">
          <FileText className="h-4 w-4 text-primary mt-0.5" />
          <div>
            <p className="text-xs text-muted-foreground">Progress</p>
            <p className="text-sm font-medium">{workflow.steps_completed}/{workflow.steps_total} steps</p>
          </div>
        </div>
      </div>

      {/* Progress */}
      <div className="space-y-2">
        <div className="flex items-center justify-between text-sm">
          <span className="text-muted-foreground">Progress</span>
          <span className="font-medium">Step {workflow.steps_completed} of {workflow.steps_total}</span>
        </div>
        <div className="h-2.5 rounded-full bg-muted overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-500 ${
              workflow.status === 'failed' ? 'bg-destructive' :
              workflow.status === 'completed' ? 'bg-green-500' :
              'bg-primary'
            }`}
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>
    </div>
  );
}
