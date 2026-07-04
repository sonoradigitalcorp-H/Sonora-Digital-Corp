'use client';

import { useState } from 'react';
import { CheckCircle2, Circle, XCircle, Clock, ChevronDown, ChevronRight, Loader2 } from 'lucide-react';

type Step = {
  id?: string;
  name: string;
  status: 'completed' | 'running' | 'failed' | 'pending' | 'in_progress';
  agent?: string;
};

const stepIcons: Record<string, React.ReactNode> = {
  completed: <CheckCircle2 className="h-5 w-5 text-green-500" />,
  running: <Loader2 className="h-5 w-5 text-blue-500 animate-spin" />,
  failed: <XCircle className="h-5 w-5 text-red-500" />,
  pending: <Circle className="h-5 w-5 text-muted-foreground" />,
};

const stepColors: Record<string, string> = {
  completed: 'border-green-500/30',
  running: 'border-blue-500/30',
  failed: 'border-red-500/30',
  pending: 'border-muted',
};

const bgColors: Record<string, string> = {
  completed: 'bg-green-500/5',
  running: 'bg-blue-500/5',
  failed: 'bg-red-500/5',
  pending: '',
};

export function ExecutionTimeline({ steps }: { steps: Step[] }) {
  const [expanded, setExpanded] = useState<Set<string>>(new Set());

  const toggle = (id: string) => {
    setExpanded(prev => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id); else next.add(id);
      return next;
    });
  };

  return (
    <div className="rounded-xl border bg-card p-6">
      <h3 className="font-semibold mb-6">Execution Timeline</h3>
      <div className="relative">
        {steps.map((step, idx) => {
          const stepId = step.id || `step-${idx}`;
          const isExpanded = expanded.has(stepId);
          const isLast = idx === steps.length - 1;

          return (
            <div key={stepId} className={`relative pl-8 pb-6 ${isLast ? 'pb-0' : ''}`}>
              {/* Connector line */}
              {!isLast && (
                <div className={`absolute left-[11px] top-6 bottom-0 w-0.5 ${stepColors[step.status] || 'border-muted'}`} />
              )}

              {/* Status dot */}
              <div className="absolute left-0 top-0.5">
                {stepIcons[step.status] || <Circle className="h-5 w-5 text-muted-foreground" />}
              </div>

              {/* Step card */}
              <div
                className={`rounded-lg border p-3 cursor-pointer transition-colors hover:border-primary/30 ${bgColors[step.status] || ''}`}
                onClick={() => toggle(stepId)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-sm">{step.name}</span>
                    {step.agent && (
                      <span className="text-xs text-muted-foreground">— {step.agent}</span>
                    )}
                  </div>
                  <div className="flex items-center gap-3">
                    {isExpanded ? <ChevronDown className="h-4 w-4 text-muted-foreground" /> : <ChevronRight className="h-4 w-4 text-muted-foreground" />}
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
