'use client';

import { useState } from 'react';
import { Lightbulb, AlertTriangle, Info, ChevronDown, ChevronUp, Loader2 } from 'lucide-react';

interface Insight {
  title: string;
  description: string;
  severity: 'info' | 'warning' | 'critical';
}

interface Props {
  insights?: Insight[];
  isLoading: boolean;
}

const severityStyles: Record<string, string> = {
  info: 'text-blue-500 bg-blue-500/10 border-blue-500/20',
  warning: 'text-amber-500 bg-amber-500/10 border-amber-500/20',
  critical: 'text-red-500 bg-red-500/10 border-red-500/20',
};

const severityIcons: Record<string, typeof Lightbulb> = {
  info: Info,
  warning: AlertTriangle,
  critical: AlertTriangle,
};

function Skeleton() {
  return (
    <div className="rounded-xl border bg-card">
      <div className="p-5 border-b">
        <div className="h-5 w-28 bg-muted rounded animate-pulse" />
      </div>
      <div className="p-5 space-y-3">
        {[1, 2, 3].map(i => (
          <div key={i} className="h-16 bg-muted rounded-lg animate-pulse" />
        ))}
      </div>
    </div>
  );
}

export function AIInsights({ insights, isLoading }: Props) {
  const [expanded, setExpanded] = useState<number | null>(null);

  if (isLoading) return <Skeleton />;
  if (!insights || insights.length === 0) return null;

  return (
    <div className="rounded-xl border bg-card">
      <div className="p-5 border-b flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Lightbulb className="h-5 w-5 text-primary" />
          <div>
            <h2 className="font-semibold">AI Insights</h2>
            <p className="text-xs text-muted-foreground mt-0.5">
              Recommendations &amp; predictions
            </p>
          </div>
        </div>
        <span className="text-xs text-muted-foreground">{insights.length} items</span>
      </div>

      <div className="divide-y">
        {insights.map((insight, i) => {
          const Icon = severityIcons[insight.severity];
          const isExpanded = expanded === i;

          return (
            <div
              key={i}
              className="p-4 hover:bg-accent/50 transition-colors cursor-pointer"
              onClick={() => setExpanded(isExpanded ? null : i)}
            >
              <div className="flex items-start gap-3">
                <div className={`p-1.5 rounded-lg shrink-0 ${severityStyles[insight.severity]}`}>
                  <Icon className="h-3.5 w-3.5" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between gap-2">
                    <p className="text-sm font-medium">{insight.title}</p>
                    {isExpanded ? (
                      <ChevronUp className="h-4 w-4 text-muted-foreground shrink-0" />
                    ) : (
                      <ChevronDown className="h-4 w-4 text-muted-foreground shrink-0" />
                    )}
                  </div>
                  {isExpanded && (
                    <p className="text-sm text-muted-foreground mt-2 leading-relaxed">
                      {insight.description}
                    </p>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
