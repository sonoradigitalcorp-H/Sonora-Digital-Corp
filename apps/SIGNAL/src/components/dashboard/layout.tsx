'use client';

import dynamic from 'next/dynamic';
import { Sidebar } from './sidebar';
import { TopBar } from './topbar';

const ChatAgent = dynamic(
  () => import('@/components/chat-agent').then(m => ({ default: m.ChatAgent })),
  { ssr: false }
);

export function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-screen overflow-hidden bg-background">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <TopBar />
        <main className="flex-1 overflow-y-auto">
          {children}
        </main>
      </div>
      <ChatAgent />
    </div>
  );
}
