'use client';

import { BarChart3, Target } from 'lucide-react';

function parseAccuracy(acc: string | number): number {
  if (typeof acc === 'number') return acc;
  return parseInt(acc.replace('%', ''), 10) || 0;
}

function tierColor(acc: number): string {
  if (acc >= 80) return 'bg-green-500';
  if (acc >= 60) return 'bg-yellow-500';
  return 'bg-red-500';
}

function tierText(acc: number): string {
  if (acc >= 80) return 'text-green-500';
  if (acc >= 60) return 'text-yellow-500';
  return 'text-red-500';
}

export function AgentPerformance({ agents }: { agents: any[] }) {
  const parsed = agents.map((a: any) => ({ ...a, accuracyNum: parseAccuracy(a.accuracy) }));
  const maxAccuracy = Math.max(...parsed.map((a: any) => a.accuracyNum));
  const maxTools = Math.max(...parsed.map((a: any) => a.tools));

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Accuracy Comparison */}
      <div className="rounded-xl border bg-card p-5">
        <div className="flex items-center justify-between mb-5">
          <div>
            <h2 className="font-semibold flex items-center gap-2">
              <BarChart3 className="h-4 w-4 text-primary" />
              Accuracy Comparison
            </h2>
            <p className="text-xs text-muted-foreground mt-0.5">Agent performance tier by accuracy</p>
          </div>
          <div className="flex items-center gap-2 text-xs">
            <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-green-500" /> Elite</span>
            <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-yellow-500" /> Strong</span>
            <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-red-500" /> Needs Review</span>
          </div>
        </div>

        <div className="space-y-3">
          {parsed.map((agent: any) => (
            <div key={agent.id} className="group">
              <div className="flex items-center justify-between text-sm mb-1">
                <span className="font-medium truncate">{agent.name}</span>
                <span className={`font-mono text-xs font-bold ${tierText(agent.accuracyNum)}`}>{agent.accuracyNum}%</span>
              </div>
              <div className="relative h-5 rounded-full bg-muted overflow-hidden">
                <div
                  className={`h-full rounded-full ${tierColor(agent.accuracyNum)} transition-all duration-500 group-hover:opacity-80`}
                  style={{ width: maxAccuracy > 0 ? `${(agent.accuracyNum / maxAccuracy) * 100}%` : '0%' }}
                />
                <div
                  className="absolute inset-y-0 left-0 h-full rounded-full bg-white/10"
                  style={{ width: `${agent.accuracyNum}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Tool Weight vs Accuracy */}
      <div className="rounded-xl border bg-card p-5">
        <div className="flex items-center justify-between mb-5">
          <div>
            <h2 className="font-semibold flex items-center gap-2">
              <Target className="h-4 w-4 text-primary" />
              Tools & Accuracy
            </h2>
            <p className="text-xs text-muted-foreground mt-0.5">Tool count vs accuracy by agent</p>
          </div>
        </div>

        <div className="space-y-4">
          {parsed.map((agent: any) => {
            const toolWeight = Math.round((agent.tools / maxTools) * 100);
            const calibrationDiff = Math.abs(toolWeight - agent.accuracyNum);
            const isCalibrated = calibrationDiff <= 15;

            return (
              <div key={agent.id} className="p-3 rounded-lg bg-accent/30">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium">{agent.name}</span>
                  <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                    isCalibrated ? 'bg-green-500/10 text-green-500' : 'bg-amber-500/10 text-amber-500'
                  }`}>
                    {isCalibrated ? 'Balanced' : `Gap: ${calibrationDiff}%`}
                  </span>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <div className="flex items-center justify-between text-xs mb-1">
                      <span className="text-muted-foreground">Tools</span>
                      <span className="font-mono">{agent.tools} ({toolWeight}%)</span>
                    </div>
                    <div className="h-1.5 rounded-full bg-muted overflow-hidden">
                      <div className="h-full rounded-full bg-primary" style={{ width: `${toolWeight}%` }} />
                    </div>
                  </div>
                  <div>
                    <div className="flex items-center justify-between text-xs mb-1">
                      <span className="text-muted-foreground">Accuracy</span>
                      <span className={`font-mono ${tierText(agent.accuracyNum)}`}>{agent.accuracyNum}%</span>
                    </div>
                    <div className="h-1.5 rounded-full bg-muted overflow-hidden">
                      <div className={`h-full rounded-full ${tierColor(agent.accuracyNum)}`} style={{ width: `${agent.accuracyNum}%` }} />
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
