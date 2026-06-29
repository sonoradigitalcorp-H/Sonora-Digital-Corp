'use client';

import { useState, useMemo, useCallback } from 'react';
import useSWR from 'swr';
import { DashboardLayout } from '@/components/dashboard/layout';
import Link from 'next/link';
import { Crosshair, Users, FileText, Calendar, TrendingUp, AlertCircle, RefreshCw, ArrowUpDown } from 'lucide-react';

interface WarRoom {
  id: string;
  name: string;
  stage: 'discovery' | 'initial_contact' | 'due_diligence' | 'negotiation' | 'closed';
  priority: 'low' | 'medium' | 'high' | 'critical';
  score: number;
  image: string;
  members: number;
  documents: number;
  meetings: number;
  deal: number;
  contact: string;
}

interface ApiResponse {
  warRooms: WarRoom[];
  total: number;
  totalValue: number;
  stages: { label: string; count: number }[];
}

const fetcher = (url: string) =>
  fetch(url).then(r => {
    if (!r.ok) throw new Error('Failed to load war rooms');
    return r.json();
  });

const priorityColors: Record<string, string> = {
  critical: 'text-red-500 bg-red-500/10 border-red-500/20',
  high: 'text-orange-500 bg-orange-500/10 border-orange-500/20',
  medium: 'text-blue-500 bg-blue-500/10 border-blue-500/20',
  low: 'text-muted-foreground bg-muted border-muted',
};

const stageColors: Record<string, string> = {
  negotiation: 'text-amber-500 bg-amber-500/10',
  due_diligence: 'text-purple-500 bg-purple-500/10',
  initial_contact: 'text-blue-500 bg-blue-500/10',
  discovery: 'text-muted-foreground bg-muted',
  closed: 'text-green-500 bg-green-500/10',
};

const stageLabels: Record<string, string> = {
  discovery: 'Discovery',
  initial_contact: 'Initial Contact',
  due_diligence: 'Due Diligence',
  negotiation: 'Negotiation',
  closed: 'Closed',
};

const stageKeyFromLabel: Record<string, string> = {
  Discovery: 'discovery',
  'Initial Contact': 'initial_contact',
  'Due Diligence': 'due_diligence',
  Negotiation: 'negotiation',
  Closed: 'closed',
};

const priorityOrder: Record<string, number> = {
  critical: 4,
  high: 3,
  medium: 2,
  low: 1,
};

type SortKey = 'priority' | 'score' | 'deal';

function Skeleton() {
  return (
    <div className="space-y-4">
      {Array.from({ length: 4 }).map((_, i) => (
        <div key={i} className="rounded-xl border bg-card p-5 animate-pulse">
          <div className="flex items-start justify-between mb-3">
            <div className="flex items-center gap-4">
              <div className="h-10 w-10 rounded-lg bg-muted" />
              <div className="space-y-2">
                <div className="h-5 w-48 rounded bg-muted" />
                <div className="h-4 w-72 rounded bg-muted" />
              </div>
            </div>
            <div className="flex gap-2">
              <div className="h-6 w-16 rounded-full bg-muted" />
              <div className="h-6 w-24 rounded-full bg-muted" />
            </div>
          </div>
          <div className="flex gap-6">
            {Array.from({ length: 5 }).map((_, j) => (
              <div key={j} className="h-4 w-20 rounded bg-muted" />
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

export default function WarRoomsPage() {
  const { data, error, isLoading, mutate } = useSWR<ApiResponse>(
    '/api/v1/war-rooms',
    fetcher
  );
  const [stageFilter, setStageFilter] = useState<string>('all');
  const [sortKey, setSortKey] = useState<SortKey>('priority');
  const [sortAsc, setSortAsc] = useState(false);

  const toggleSort = (key: SortKey) => {
    if (sortKey === key) {
      setSortAsc(!sortAsc);
    } else {
      setSortKey(key);
      setSortAsc(false);
    }
  };

  const stats = useMemo(() => {
    if (!data) return { highPriority: 0, totalDocs: 0 };
    return {
      highPriority: data.warRooms.filter(
        r => r.priority === 'critical' || r.priority === 'high'
      ).length,
      totalDocs: data.warRooms.reduce((a, r) => a + r.documents, 0),
    };
  }, [data]);

  const filtered = useMemo(() => {
    if (!data) return [];
    let rooms = data.warRooms;
    if (stageFilter !== 'all') {
      rooms = rooms.filter(r => r.stage === stageFilter);
    }
    return [...rooms].sort((a, b) => {
      let cmp = 0;
      if (sortKey === 'priority') {
        cmp = priorityOrder[a.priority] - priorityOrder[b.priority];
      } else if (sortKey === 'score') {
        cmp = a.score - b.score;
      } else if (sortKey === 'deal') {
        cmp = a.deal - b.deal;
      }
      return sortAsc ? cmp : -cmp;
    });
  }, [data, stageFilter, sortKey, sortAsc]);

  if (error) {
    return (
      <DashboardLayout>
        <div className="p-6 max-w-[1600px] mx-auto">
          <div className="flex flex-col items-center justify-center py-20 text-muted-foreground">
            <AlertCircle className="h-12 w-12 mb-3 text-red-500" />
            <p className="text-lg font-medium text-foreground">Failed to load war rooms</p>
            <p className="text-sm mt-1 mb-4">{error.message}</p>
            <button
              onClick={() => mutate()}
              className="px-4 py-2 text-sm font-medium rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 transition-colors"
            >
              Try again
            </button>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="p-6 space-y-6 max-w-[1600px] mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">War Rooms</h1>
            <p className="text-muted-foreground mt-1">
              Active deal negotiations with unsigned prospects
            </p>
          </div>
          <div className="flex items-center gap-3">
            {data && (
              <div className="flex gap-1 p-1 rounded-xl bg-muted">
                <button
                  onClick={() => setStageFilter('all')}
                  className={`px-4 py-2 text-sm font-medium rounded-lg capitalize transition-all ${
                    stageFilter === 'all'
                      ? 'bg-background text-foreground shadow-sm'
                      : 'text-muted-foreground hover:text-foreground'
                  }`}
                >
                  All ({data.total})
                </button>
                {data.stages.map(s => (
                  <button
                    key={s.label}
                    onClick={() => setStageFilter(stageKeyFromLabel[s.label] || s.label)}
                    className={`px-4 py-2 text-sm font-medium rounded-lg capitalize transition-all ${
                      stageFilter === (stageKeyFromLabel[s.label] || s.label)
                        ? 'bg-background text-foreground shadow-sm'
                        : 'text-muted-foreground hover:text-foreground'
                    }`}
                  >
                    {s.label} ({s.count})
                  </button>
                ))}
              </div>
            )}
            <button
              onClick={() => mutate()}
              disabled={isLoading}
              className="p-2 rounded-lg hover:bg-muted transition-colors text-muted-foreground hover:text-foreground disabled:opacity-50"
              title="Refresh"
            >
              <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-4 gap-4">
          <div className="rounded-xl border bg-card p-4">
            <p className="text-2xl font-bold">{data ? data.total : '-'}</p>
            <p className="text-xs text-muted-foreground">Active Deals</p>
          </div>
          <div className="rounded-xl border bg-card p-4">
            <p className="text-2xl font-bold">{data ? stats.highPriority : '-'}</p>
            <p className="text-xs text-muted-foreground">High Priority</p>
          </div>
          <div className="rounded-xl border bg-card p-4">
            <p className="text-2xl font-bold">{data ? stats.totalDocs : '-'}</p>
            <p className="text-xs text-muted-foreground">Total Documents</p>
          </div>
          <div className="rounded-xl border bg-card p-4">
            <p className="text-2xl font-bold">
              {data ? `$${Intl.NumberFormat().format(data.totalValue)}` : '-'}
            </p>
            <p className="text-xs text-muted-foreground">Total Offer Value</p>
          </div>
        </div>

        {/* Sort Controls */}
        {data && (
          <div className="flex items-center gap-2 text-sm">
            <span className="text-muted-foreground">Sort by:</span>
            {(['priority', 'score', 'deal'] as const).map(key => (
              <button
                key={key}
                onClick={() => toggleSort(key)}
                className={`flex items-center gap-1 px-3 py-1.5 rounded-lg border transition-all ${
                  sortKey === key
                    ? 'bg-primary/10 border-primary/30 text-primary font-medium'
                    : 'bg-card text-muted-foreground hover:text-foreground'
                }`}
              >
                {key.charAt(0).toUpperCase() + key.slice(1)}
                {sortKey === key && (
                  <ArrowUpDown
                    className={`h-3 w-3 transition-transform ${
                      sortAsc ? '' : 'rotate-180'
                    }`}
                  />
                )}
              </button>
            ))}
          </div>
        )}

        {/* War Room Cards */}
        {isLoading ? (
          <Skeleton />
        ) : (
          <div className="grid gap-4">
            {filtered.map(room => (
              <Link
                key={room.id}
                href={`/war-rooms/${room.id}`}
                className="rounded-xl border bg-card p-5 hover:shadow-md hover:border-primary/30 transition-all group"
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-4">
                    <div className="p-2.5 rounded-lg bg-primary/10 text-primary">
                      <Crosshair className="h-5 w-5" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-lg group-hover:text-primary transition-colors">
                        {room.name}
                      </h3>
                      <p className="text-sm text-muted-foreground">{room.contact}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <span
                      className={`text-xs px-2.5 py-1 rounded-full border font-medium ${
                        priorityColors[room.priority]
                      }`}
                    >
                      {room.priority}
                    </span>
                    <span
                      className={`text-xs px-2.5 py-1 rounded-full font-medium ${
                        stageColors[room.stage] || 'bg-muted text-muted-foreground'
                      }`}
                    >
                      {stageLabels[room.stage] || room.stage}
                    </span>
                  </div>
                </div>

                <div className="flex items-center gap-6 text-sm text-muted-foreground flex-wrap">
                  <span className="flex items-center gap-1.5">
                    <TrendingUp className="h-3.5 w-3.5" />
                    Score {room.score}
                  </span>
                  <span className="flex items-center gap-1.5">
                    <Users className="h-3.5 w-3.5" />
                    {room.members}
                  </span>
                  <span className="flex items-center gap-1.5">
                    <FileText className="h-3.5 w-3.5" />
                    {room.documents} docs
                  </span>
                  <span className="flex items-center gap-1.5">
                    <Calendar className="h-3.5 w-3.5" />
                    {room.meetings} meetings
                  </span>
                  <span className="flex items-center gap-1.5">
                    <TrendingUp className="h-3.5 w-3.5" />
                    ${Intl.NumberFormat().format(room.deal)}
                  </span>
                </div>
              </Link>
            ))}
          </div>
        )}

        {!isLoading && filtered.length === 0 && (
          <div className="text-center py-20 text-muted-foreground">
            <Crosshair className="h-12 w-12 mx-auto mb-3 opacity-30" />
            <p className="text-lg font-medium">No war rooms found</p>
            <p className="text-sm mt-1">Try a different filter or start a new deal.</p>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
