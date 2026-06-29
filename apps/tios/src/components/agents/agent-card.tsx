'use client';

import { Brain, Network, Target, ListChecks, Gavel, Radio, Shield, Cpu } from 'lucide-react';

const typeConfig: Record<string, { label: string; color: string; icon: any }> = {
  analyst: { label: 'Analyst', color: 'text-blue-500 bg-blue-500/10', icon: Brain },
  strategist: { label: 'Strategist', color: 'text-purple-500 bg-purple-500/10', icon: Target },
  specialist: { label: 'Specialist', color: 'text-emerald-500 bg-emerald-500/10', icon: Cpu },
  operations: { label: 'Operations', color: 'text-orange-500 bg-orange-500/10', icon: ListChecks },
  legal: { label: 'Legal', color: 'text-red-500 bg-red-500/10', icon: Gavel },
  gateway: { label: 'Gateway', color: 'text-cyan-500 bg-cyan-500/10', icon: Radio },
  memory: { label: 'Memory', color: 'text-indigo-500 bg-indigo-500/10', icon: Shield },
  streaming: { label: 'Streaming', color: 'text-amber-500 bg-amber-500/10', icon: Network },
};

function roleToConfig(role: string): string {
  const r = role.toLowerCase();
  if (r.includes('analyst') || r.includes('data')) return 'analyst';
  if (r.includes('writer') || r.includes('content')) return 'strategist';
  if (r.includes('legal') || r.includes('compliance') || r.includes('contract')) return 'legal';
  if (r.includes('orchestrator') || r.includes('gbrain')) return 'strategist';
  if (r.includes('memory') || r.includes('engram') || r.includes('rag')) return 'memory';
  if (r.includes('gateway') || r.includes('openclaw') || r.includes('http')) return 'gateway';
  if (r.includes('streaming') || r.includes('live')) return 'streaming';
  if (r.includes('auto') || r.includes('hermes') || r.includes('improve')) return 'analyst';
  return 'operations';
}

function accuracyColor(acc: number): string {
  if (acc >= 80) return 'text-green-500';
  if (acc >= 60) return 'text-yellow-500';
  return 'text-red-500';
}

function accuracyBarColor(acc: number): string {
  if (acc >= 80) return 'bg-green-500';
  if (acc >= 60) return 'bg-yellow-500';
  return 'bg-red-500';
}

function parseAccuracy(acc: string | number): number {
  if (typeof acc === 'number') return acc;
  return parseInt(acc.replace('%', ''), 10) || 0;
}

export function AgentCard({ agent }: { agent: any }) {
  const typeKey = roleToConfig(agent.role || agent.name || '');
  const cfg = typeConfig[typeKey] || typeConfig.operations;
  const Icon = cfg.icon;
  const accuracy = parseAccuracy(agent.accuracy);
  const weight = Math.min(Math.round((agent.tools / 10) * 100), 100);

  return (
    <div className="rounded-xl border bg-card p-5 hover:shadow-md transition-all cursor-pointer group" id={`agent-${agent.id}`}>
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-lg ${cfg.color}`}>
            <Icon className="h-5 w-5" />
          </div>
          <div>
            <p className="font-semibold text-sm">{agent.name}</p>
            <span className={`text-xs font-medium ${cfg.color.split(' ')[0]}`}>{cfg.label} — {agent.role}</span>
          </div>
        </div>
        <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
          agent.status === 'active' ? 'bg-green-500/10 text-green-500' :
          agent.status === 'idle' ? 'bg-amber-500/10 text-amber-500' :
          'bg-red-500/10 text-red-500'
        }`}>
          {agent.status}
        </span>
      </div>

      <div className="space-y-3">
        <div>
          <div className="flex items-center justify-between text-sm mb-1">
            <span className="text-muted-foreground">Tools</span>
            <span className="font-mono font-medium">{agent.tools}</span>
          </div>
          <div className="h-2 rounded-full bg-muted overflow-hidden">
            <div className="h-full rounded-full bg-primary transition-all" style={{ width: `${weight}%` }} />
          </div>
        </div>

        <div>
          <div className="flex items-center justify-between text-sm mb-1">
            <span className="text-muted-foreground">Accuracy</span>
            <span className={`font-mono font-medium ${accuracyColor(accuracy)}`}>{accuracy}%</span>
          </div>
          <div className="h-2 rounded-full bg-muted overflow-hidden">
            <div className={`h-full rounded-full transition-all ${accuracyBarColor(accuracy)}`} style={{ width: `${accuracy}%` }} />
          </div>
        </div>

        <div className="flex items-center justify-between pt-1 border-t">
          <span className="text-xs text-muted-foreground">Tasks Completed</span>
          <span className="text-sm font-mono font-bold">{agent.tasksCompleted.toLocaleString()}</span>
        </div>
      </div>
    </div>
  );
}
