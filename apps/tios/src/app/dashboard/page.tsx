'use client';

import { DashboardLayout } from '@/components/dashboard/layout';
import { StatsGrid } from '@/components/dashboard/stats-grid';
import { TopArtists } from '@/components/dashboard/top-artists';
import { DiscoveryFeed } from '@/components/dashboard/discovery-feed';
import { MarketOverview } from '@/components/dashboard/market-overview';
import { AlertsPanel } from '@/components/dashboard/alerts-panel';
import { ActivityChart } from '@/components/dashboard/activity-chart';

export default function DashboardPage() {
  return (
    <DashboardLayout>
      <div className="space-y-6 p-6 animate-fade-in">
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-3xl font-bold tracking-tight">Mission Control</h1>
              <span className="flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-green-500/10 border border-green-500/20 text-green-500 text-[10px] font-semibold uppercase tracking-wider">
                <span className="live-dot" />
                Live
              </span>
            </div>
            <p className="text-muted-foreground mt-1.5">
              Real-time intelligence overview for Abe Music Group
            </p>
          </div>
          <div className="hidden md:flex items-center gap-2 text-xs text-muted-foreground">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-muted/50">
              <span className="w-1.5 h-1.5 rounded-full bg-amber-500" />
              {new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
            </span>
          </div>
        </div>

        <StatsGrid />

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <TopArtists />
            <ActivityChart />
          </div>
          <div className="space-y-6">
            <AlertsPanel />
            <MarketOverview />
          </div>
        </div>

        <DiscoveryFeed />
      </div>
    </DashboardLayout>
  );
}
