'use client';

import { useMemo } from 'react';
import { TrendingDown, ArrowDown } from 'lucide-react';
import { generatePipelineFunnel } from '@/lib/data-generator';

function getConversionRate(current: number, previous: number): string {
  if (previous === 0) return '0%';
  return `${Math.round((current / previous) * 100)}%`;
}

export function PipelineFunnel() {
  const stages = useMemo(() => generatePipelineFunnel(), []);
  const maxCount = stages[0].count;

  return (
    <div className="rounded-xl border bg-card">
      <div className="p-5 border-b flex items-center justify-between">
        <div className="flex items-center gap-2">
          <TrendingDown className="h-5 w-5 text-primary" />
          <div>
            <h2 className="font-semibold">Signing Pipeline Funnel</h2>
            <p className="text-xs text-muted-foreground mt-0.5">
              Artist conversion through signing stages
            </p>
          </div>
        </div>
      </div>

      <div className="p-5 space-y-3">
        {stages.map((stage, i) => {
          const widthPercent = Math.max((stage.count / maxCount) * 100, 10);
          const conversion = i > 0 ? getConversionRate(stage.count, stages[i - 1].count) : null;

          return (
            <div key={stage.label} className="space-y-1">
              <div className="flex items-center justify-between text-sm">
                <span className="font-medium">{stage.label}</span>
                <div className="flex items-center gap-3">
                  {conversion && (
                    <span className="text-xs text-muted-foreground flex items-center gap-1">
                      <ArrowDown className="h-3 w-3" />
                      {conversion}
                    </span>
                  )}
                  <span className="font-bold tabular-nums">{stage.count}</span>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <div
                  className="h-4 rounded-full transition-all duration-500"
                  style={{
                    width: `${widthPercent}%`,
                    background: `linear-gradient(90deg, ${stage.color}, ${stage.color}88)`,
                  }}
                />
                <span className="text-[10px] text-muted-foreground w-16 shrink-0">
                  {stage.count} artists
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
