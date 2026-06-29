'use client';

import { Sparkles, ArrowRight, Clock, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';

interface Recommendation {
  title: string;
  description: string;
  severity: 'info' | 'warning' | 'critical';
}

interface Metrics {
  activeWorkflows: number;
  pendingApprovals: number;
  successRate: number;
}

interface BriefingData {
  executiveSummary: string;
  recommendations: Recommendation[];
  metrics: Metrics;
  generatedAt: string;
}

interface Props {
  data?: BriefingData;
  isLoading: boolean;
}

const severityStyles: Record<string, string> = {
  info: 'text-blue-500 bg-blue-500/10',
  warning: 'text-amber-500 bg-amber-500/10',
  critical: 'text-red-500 bg-red-500/10',
};

const severityIcons: Record<string, typeof AlertCircle> = {
  info: CheckCircle2,
  warning: AlertCircle,
  critical: AlertCircle,
};

function Skeleton() {
  return (
    <div className="rounded-xl border bg-card">
      <div className="p-5 border-b">
        <div className="h-5 w-48 bg-muted rounded animate-pulse" />
        <div className="h-3 w-64 bg-muted rounded mt-2 animate-pulse" />
      </div>
      <div className="p-5 space-y-4">
        <div className="h-4 w-full bg-muted rounded animate-pulse" />
        <div className="h-4 w-3/4 bg-muted rounded animate-pulse" />
        <div className="grid grid-cols-3 gap-4 mt-4">
          {[1, 2, 3].map(i => (
            <div key={i} className="h-20 bg-muted rounded-lg animate-pulse" />
          ))}
        </div>
        <div className="h-4 w-32 bg-muted rounded animate-pulse" />
      </div>
    </div>
  );
}

export function ExecutiveBriefing({ data, isLoading }: Props) {
  if (isLoading) return <Skeleton />;
  if (!data) return null;

  return (
    <div className="rounded-xl border bg-card">
      <div className="p-5 border-b flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Sparkles className="h-5 w-5 text-primary" />
          <div>
            <h2 className="font-semibold">Executive Briefing</h2>
            <p className="text-xs text-muted-foreground mt-0.5">
              AI-generated strategic overview
            </p>
          </div>
        </div>
        <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
          <Clock className="h-3.5 w-3.5" />
          <span>Generated {new Date(data.generatedAt).toLocaleString()}</span>
        </div>
      </div>

      <div className="p-5 space-y-5">
        <p className="text-sm text-muted-foreground leading-relaxed">
          {data.executiveSummary}
        </p>

        <div className="grid grid-cols-3 gap-4">
          {[
            { label: 'Active Workflows', value: data.metrics.activeWorkflows, color: 'text-blue-500' },
            { label: 'Pending Approvals', value: data.metrics.pendingApprovals, color: 'text-amber-500' },
            { label: 'Success Rate', value: `${data.metrics.successRate}%`, color: 'text-emerald-500' },
          ].map(metric => (
            <div key={metric.label} className="rounded-lg border bg-muted/30 p-3 text-center">
              <p className={`text-2xl font-bold ${metric.color}`}>{metric.value}</p>
              <p className="text-xs text-muted-foreground mt-1">{metric.label}</p>
            </div>
          ))}
        </div>

        {data.recommendations.length > 0 && (
          <div>
            <h3 className="text-sm font-medium mb-3">Top Recommendations</h3>
            <div className="space-y-2">
              {data.recommendations.map((rec, i) => {
                const Icon = severityIcons[rec.severity];
                return (
                  <div
                    key={i}
                    className="flex items-start gap-3 p-3 rounded-lg border hover:bg-accent/50 transition-colors cursor-pointer"
                  >
                    <div className={`p-1.5 rounded-lg ${severityStyles[rec.severity]}`}>
                      <Icon className="h-3.5 w-3.5" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium">{rec.title}</p>
                      <p className="text-xs text-muted-foreground mt-0.5">{rec.description}</p>
                    </div>
                    <ArrowRight className="h-4 w-4 text-muted-foreground shrink-0 mt-1" />
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
