'use client';

import { useState } from 'react';
import { Network, Share2, Activity, Users } from 'lucide-react';

const typeColors: Record<string, string> = {
  analyst: 'border-blue-500 bg-blue-500/20 text-blue-500',
  strategist: 'border-purple-500 bg-purple-500/20 text-purple-500',
  specialist: 'border-emerald-500 bg-emerald-500/20 text-emerald-500',
  operations: 'border-orange-500 bg-orange-500/20 text-orange-500',
  legal: 'border-red-500 bg-red-500/20 text-red-500',
  gateway: 'border-cyan-500 bg-cyan-500/20 text-cyan-500',
  memory: 'border-indigo-500 bg-indigo-500/20 text-indigo-500',
  streaming: 'border-amber-500 bg-amber-500/20 text-amber-500',
};

const typeBadges: Record<string, { label: string; color: string }> = {
  analyst: { label: 'Analysts', color: 'bg-blue-500' },
  strategist: { label: 'Strategists', color: 'bg-purple-500' },
  specialist: { label: 'Specialists', color: 'bg-emerald-500' },
  operations: { label: 'Operations', color: 'bg-orange-500' },
  legal: { label: 'Legal', color: 'bg-red-500' },
  gateway: { label: 'Gateway', color: 'bg-cyan-500' },
  memory: { label: 'Memory', color: 'bg-indigo-500' },
  streaming: { label: 'Streaming', color: 'bg-amber-500' },
};

function roleToType(role: string): string {
  const r = role.toLowerCase();
  if (r.includes('analyst') || r.includes('data')) return 'analyst';
  if (r.includes('writer') || r.includes('content')) return 'strategist';
  if (r.includes('legal') || r.includes('compliance') || r.includes('contract')) return 'legal';
  if (r.includes('orchestrator')) return 'strategist';
  if (r.includes('memory') || r.includes('engram') || r.includes('rag')) return 'memory';
  if (r.includes('gateway') || r.includes('openclaw') || r.includes('http')) return 'gateway';
  if (r.includes('streaming') || r.includes('live')) return 'streaming';
  if (r.includes('auto') || r.includes('hermes') || r.includes('improve')) return 'analyst';
  return 'operations';
}

export function AgentNetwork({ agents, decisions }: { agents: any[]; decisions: any[] }) {
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);

  // Build co-participation connections from decisions
  const pairs = (decisions || []).flatMap((d: any) => {
    const names: string[] = d.agents || [];
    const result: { from: string; to: string; strength: string }[] = [];
    for (let i = 0; i < names.length; i++) {
      for (let j = i + 1; j < names.length; j++) {
        result.push({ from: names[i], to: names[j], strength: 'strong' });
      }
    }
    return result;
  });

  const selectedConnections = selectedAgent
    ? pairs.filter((p: any) => p.from === selectedAgent || p.to === selectedAgent)
    : [];

  return (
    <div className="rounded-xl border bg-card p-5">
      <div className="flex items-center justify-between mb-5">
        <div>
          <h2 className="font-semibold flex items-center gap-2">
            <Share2 className="h-4 w-4 text-primary" />
            Agent Network
          </h2>
          <p className="text-xs text-muted-foreground mt-0.5">Communication & consensus patterns</p>
        </div>
        <div className="flex items-center gap-2 text-xs">
          <Activity className="h-3 w-3 text-muted-foreground" />
          <span className="text-muted-foreground">{agents.length} agents</span>
        </div>
      </div>

      <div className="relative aspect-[4/3] bg-accent/20 rounded-lg border border-dashed p-4 mb-4">
        <div className="grid grid-cols-3 gap-3 h-full items-center">
          {agents.map((agent: any, i: number) => {
            const isSelected = selectedAgent === agent.name;
            return (
              <button
                key={agent.id}
                onClick={() => setSelectedAgent(isSelected ? null : agent.name)}
                className={`relative flex flex-col items-center justify-center p-3 rounded-xl border-2 transition-all ${
                  typeColors[roleToType(agent.role)] || typeColors.operations
                } ${isSelected ? 'scale-110 shadow-lg ring-2 ring-primary/30 z-10' : 'hover:scale-105'}`}
                style={{ gridColumn: ((i % 3) + 1).toString(), gridRow: (Math.floor(i / 3) + 1).toString() }}
              >
                <Network className="h-5 w-5 mb-1" />
                <span className="text-[10px] font-medium leading-tight text-center">{agent.name}</span>
                {isSelected && (
                  <span className="absolute -top-1 -right-1 w-3 h-3 rounded-full bg-primary border-2 border-background" />
                )}
              </button>
            );
          })}
        </div>

        {selectedAgent && (
          <div className="absolute bottom-2 left-2 right-2 p-2 rounded-lg bg-background/95 backdrop-blur border text-xs">
            <p className="font-medium mb-1">{selectedAgent}</p>
            <p className="text-muted-foreground">{selectedConnections.length} consensus connections</p>
          </div>
        )}
      </div>

      <div className="flex flex-wrap gap-3">
        {Object.entries(typeBadges).map(([key, badge]) => (
          <div key={key} className="flex items-center gap-1.5 text-xs text-muted-foreground">
            <span className={`w-2.5 h-2.5 rounded-full ${badge.color}`} />
            {badge.label}
          </div>
        ))}
      </div>
    </div>
  );
}
