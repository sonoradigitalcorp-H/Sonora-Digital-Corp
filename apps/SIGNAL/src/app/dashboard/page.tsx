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
      <div className="space-y-5 p-5 animate-fade-in">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-xl font-semibold tracking-tight">Mission Control</h1>
              <span className="badge badge-live">
                <span className="live-dot" />
                Live
              </span>
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Real-time intelligence overview
            </p>
          </div>
          <div className="hidden md:flex items-center gap-1.5 text-[11px] text-muted-foreground">
            <span className="w-1.5 h-1.5 rounded-full bg-primary/60" />
            {new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
          </div>
        </div>

        {/* KPIs */}
        <StatsGrid />

        {/* Main Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
          <div className="lg:col-span-2 space-y-5">
            <TopArtists />
            <ActivityChart />
          </div>
          <div className="space-y-5">
            <AlertsPanel />
            <MarketOverview />
          </div>
        </div>

        <DiscoveryFeed />
      </div>
    </DashboardLayout>
  );
}
