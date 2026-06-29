'use client';

import { useState, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import useSWR from 'swr';
import { Search, Filter, ArrowUpDown, ChevronUp, ChevronDown } from 'lucide-react';

type Workflow = {
  id: string;
  name: string;
  type: string;
  status: 'running' | 'paused' | 'failed' | 'completed';
  priority: 'low' | 'medium' | 'high' | 'critical';
  created: string;
  steps_total: number;
  steps_completed: number;
};

const fetcher = (url: string) => fetch(url).then(r => r.json());

const statusColors: Record<string, string> = {
  running: 'text-green-500 bg-green-500/10 border-green-500/20',
  paused: 'text-amber-500 bg-amber-500/10 border-amber-500/20',
  failed: 'text-red-500 bg-red-500/10 border-red-500/20',
  completed: 'text-blue-500 bg-blue-500/10 border-blue-500/20',
};

const priorityColors: Record<string, string> = {
  low: 'text-muted-foreground',
  medium: 'text-blue-500',
  high: 'text-amber-500',
  critical: 'text-red-500',
};

const typeOptions = ['All', 'onboarding', 'discovery', 'contract', 'marketing', 'compliance'];

type SortKey = 'name' | 'status' | 'priority' | 'created';

export function WorkflowList() {
  const router = useRouter();
  const [statusFilter, setStatusFilter] = useState<string>('All');
  const [typeFilter, setTypeFilter] = useState<string>('All');
  const [search, setSearch] = useState('');
  const [sortKey, setSortKey] = useState<SortKey>('created');
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('desc');

  const { data, error, isLoading } = useSWR<{ workflows: Workflow[] }>('/api/v1/workflows', fetcher);

  const filtered = useMemo(() => {
    if (!data?.workflows) return [];
    let list = [...data.workflows];

    if (statusFilter !== 'All') list = list.filter(w => w.status === statusFilter.toLowerCase());
    if (typeFilter !== 'All') list = list.filter(w => w.type === typeFilter.toLowerCase());
    if (search) {
      const q = search.toLowerCase();
      list = list.filter(w => w.name.toLowerCase().includes(q));
    }

    list.sort((a, b) => {
      let cmp = 0;
      if (sortKey === 'name') cmp = a.name.localeCompare(b.name);
      else if (sortKey === 'status') cmp = a.status.localeCompare(b.status);
      else if (sortKey === 'priority') {
        const order = { critical: 0, high: 1, medium: 2, low: 3 };
        cmp = (order[a.priority] ?? 0) - (order[b.priority] ?? 0);
      } else cmp = new Date(a.created).getTime() - new Date(b.created).getTime();
      return sortDir === 'asc' ? cmp : -cmp;
    });

    return list;
  }, [data, statusFilter, typeFilter, search, sortKey, sortDir]);

  const toggleSort = (key: SortKey) => {
    if (sortKey === key) setSortDir(d => (d === 'asc' ? 'desc' : 'asc'));
    else { setSortKey(key); setSortDir('asc'); }
  };

  const SortIcon = ({ column }: { column: SortKey }) => {
    if (sortKey !== column) return <ArrowUpDown className="h-3 w-3 ml-1 inline" />;
    return sortDir === 'asc' ? <ChevronUp className="h-3 w-3 ml-1 inline" /> : <ChevronDown className="h-3 w-3 ml-1 inline" />;
  };

  if (error) return <div className="rounded-xl border bg-card p-8 text-center text-destructive">Failed to load workflows</div>;

  return (
    <div className="space-y-4">
      {/* Filters */}
      <div className="flex flex-wrap items-center gap-3">
        <div className="relative flex-1 min-w-[200px] max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search workflows..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2 rounded-lg border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
          />
        </div>
        <select
          value={statusFilter}
          onChange={e => setStatusFilter(e.target.value)}
          className="px-3 py-2 rounded-lg border bg-card text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
        >
          {['All', 'Running', 'Paused', 'Failed', 'Completed'].map(s => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
        <select
          value={typeFilter}
          onChange={e => setTypeFilter(e.target.value)}
          className="px-3 py-2 rounded-lg border bg-card text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
        >
          {typeOptions.map(t => (
            <option key={t} value={t}>{t.charAt(0).toUpperCase() + t.slice(1)}</option>
          ))}
        </select>
        <button className="flex items-center gap-2 px-3 py-2 rounded-lg border bg-card text-sm hover:bg-accent transition-colors">
          <Filter className="h-4 w-4" />
          Filter
        </button>
      </div>

      {/* Table */}
      <div className="rounded-xl border bg-card overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b bg-muted/50">
              <th className="text-left text-xs font-medium text-muted-foreground p-4 cursor-pointer hover:text-foreground" onClick={() => toggleSort('name')}>
                Name <SortIcon column="name" />
              </th>
              <th className="text-left text-xs font-medium text-muted-foreground p-4">Type</th>
              <th className="text-left text-xs font-medium text-muted-foreground p-4 cursor-pointer hover:text-foreground" onClick={() => toggleSort('status')}>
                Status <SortIcon column="status" />
              </th>
              <th className="text-left text-xs font-medium text-muted-foreground p-4 cursor-pointer hover:text-foreground" onClick={() => toggleSort('priority')}>
                Priority <SortIcon column="priority" />
              </th>
              <th className="text-left text-xs font-medium text-muted-foreground p-4 cursor-pointer hover:text-foreground" onClick={() => toggleSort('created')}>
                Created <SortIcon column="created" />
              </th>
              <th className="text-left text-xs font-medium text-muted-foreground p-4">Steps</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {isLoading ? (
              Array.from({ length: 5 }).map((_, i) => (
                <tr key={i} className="animate-pulse">
                  {Array.from({ length: 6 }).map((_, j) => (
                    <td key={j} className="p-4"><div className="h-4 bg-muted rounded w-3/4" /></td>
                  ))}
                </tr>
              ))
            ) : filtered.length === 0 ? (
              <tr>
                <td colSpan={6} className="p-8 text-center text-muted-foreground">No workflows found</td>
              </tr>
            ) : (
              filtered.map(w => (
                <tr
                  key={w.id}
                  onClick={() => router.push(`/workflows/${w.id}`)}
                  className="hover:bg-accent/50 transition-colors cursor-pointer"
                >
                  <td className="p-4">
                    <span className="font-medium text-sm">{w.name}</span>
                  </td>
                  <td className="p-4">
                    <span className="text-sm text-muted-foreground">{w.type}</span>
                  </td>
                  <td className="p-4">
                    <span className={`text-xs px-2 py-1 rounded-full border font-medium ${statusColors[w.status]}`}>
                      {w.status}
                    </span>
                  </td>
                  <td className="p-4">
                    <span className={`text-xs font-medium ${priorityColors[w.priority]}`}>
                      {w.priority.toUpperCase()}
                    </span>
                  </td>
                  <td className="p-4 text-sm text-muted-foreground">
                    {new Date(w.created).toLocaleDateString()}
                  </td>
                  <td className="p-4">
                    <div className="flex items-center gap-2">
                      <div className="flex-1 h-2 rounded-full bg-muted overflow-hidden max-w-[100px]">
                        <div
                          className="h-full rounded-full bg-primary transition-all"
                          style={{ width: `${(w.steps_completed / w.steps_total) * 100}%` }}
                        />
                      </div>
                      <span className="text-xs text-muted-foreground">{w.steps_completed}/{w.steps_total}</span>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">
          {isLoading ? 'Loading...' : `Showing ${filtered.length} of ${data?.workflows?.length ?? 0} workflows`}
        </p>
      </div>
    </div>
  );
}
