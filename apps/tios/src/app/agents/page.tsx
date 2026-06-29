'use client';

import useSWR from 'swr';
import { DashboardLayout } from '@/components/dashboard/layout';
import { AgentCard } from '@/components/agents/agent-card';
import { AgentPerformance } from '@/components/agents/agent-performance';
import { AgentNetwork } from '@/components/agents/agent-network';
import { ConsensusViewer } from '@/components/agents/consensus-viewer';
import { Loader2, AlertCircle } from 'lucide-react';

const API = process.env.NEXT_PUBLIC_API_URL || '';

const fetcher = (url: string) => fetch(url).then(res => {
  if (!res.ok) throw new Error('Failed to fetch');
  return res.json();
});

export default function AgentsPage() {
  const { data, error, isLoading } = useSWR(`${API}/api/v1/agents`, fetcher);

  return (
    <DashboardLayout>
      <div className="space-y-6 p-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Agent Performance</h1>
          <p className="text-muted-foreground mt-1">Multi-Agent Intelligence Monitoring</p>
        </div>

        {error && (
          <div className="flex items-center gap-2 p-4 rounded-xl border border-red-500/20 bg-red-500/5 text-red-500">
            <AlertCircle className="h-4 w-4" />
            <span className="text-sm">Failed to load agent data</span>
          </div>
        )}

        {isLoading && (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
          </div>
        )}

        {data && (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {data.agents.map((agent: any) => (
                <AgentCard key={agent.id} agent={agent} />
              ))}
            </div>

            <AgentPerformance agents={data.agents} />

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <AgentNetwork agents={data.agents} decisions={data.recentDecisions} />
              <ConsensusViewer decisions={data.recentDecisions} />
            </div>
          </>
        )}
      </div>
    </DashboardLayout>
  );
}
