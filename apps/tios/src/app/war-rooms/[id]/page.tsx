'use client';

import { DashboardLayout } from '@/components/dashboard/layout';
import { WarRoomHome } from '@/components/war-room/war-room-home';
import { DecisionCenter } from '@/components/war-room/decision-center';
import { NegotiationCenter } from '@/components/war-room/negotiation-center';
import { BoardMode } from '@/components/war-room/board-mode';
import { DocumentsHub } from '@/components/war-room/documents-hub';
import { MeetingsRoom } from '@/components/war-room/meetings-room';
import { use, useState } from 'react';

type Tab = 'overview' | 'decision' | 'negotiation' | 'documents' | 'meetings' | 'board';

export default function WarRoomDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const resolvedParams = use(params);
  const [activeTab, setActiveTab] = useState<Tab>('overview');

  const tabs: { id: Tab; label: string }[] = [
    { id: 'overview', label: 'War Room' },
    { id: 'decision', label: 'Decision Center' },
    { id: 'negotiation', label: 'Negotiation' },
    { id: 'documents', label: 'Documents' },
    { id: 'meetings', label: 'Meetings' },
    { id: 'board', label: 'Board Mode' },
  ];

  return (
    <DashboardLayout>
      <div className="border-b bg-card">
        <div className="px-6 flex items-center justify-between">
          <div className="flex items-center gap-1">
            <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
            <span className="text-xs text-muted-foreground font-mono mr-4">WAR-{resolvedParams.id.slice(0, 8).toUpperCase()}</span>
          </div>
          <nav className="flex -mb-px">
            {tabs.map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-5 py-3 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === tab.id
                    ? 'border-primary text-primary'
                    : 'border-transparent text-muted-foreground hover:text-foreground hover:border-muted-foreground/30'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </nav>
          <div className="flex items-center gap-2">
            <span className="flex items-center gap-1 text-xs text-muted-foreground">
              <span className="w-1.5 h-1.5 rounded-full bg-green-500" />
              {3} online
            </span>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto">
        {activeTab === 'overview' && <WarRoomHome warRoomId={resolvedParams.id} />}
        {activeTab === 'decision' && <DecisionCenter warRoomId={resolvedParams.id} />}
        {activeTab === 'negotiation' && <NegotiationCenter warRoomId={resolvedParams.id} />}
        {activeTab === 'board' && <BoardMode warRoomId={resolvedParams.id} />}
        {activeTab === 'documents' && <DocumentsHub warRoomId={resolvedParams.id} />}
        {activeTab === 'meetings' && <MeetingsRoom warRoomId={resolvedParams.id} />}
      </div>
    </DashboardLayout>
  );
}
