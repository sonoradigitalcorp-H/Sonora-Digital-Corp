'use client';

import { Sidebar } from './sidebar';
import { TopBar } from './topbar';
import { ChatAgent } from '@/components/chat-agent';

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
