'use client';

import { DashboardLayout } from '@/components/dashboard/layout';
import { ExecutiveBrief } from '@/components/dashboard/executive-brief';
import { DecisionCards } from '@/components/dashboard/decision-cards';
import { OpportunityPanel } from '@/components/dashboard/opportunity-panel';
import { AlertCenter } from '@/components/dashboard/alert-center';
import { MarketOverview } from '@/components/dashboard/market-overview';
import { ActivityChart } from '@/components/dashboard/activity-chart';
import { DiscoveryFeed } from '@/components/dashboard/discovery-feed';

export default function DashboardPage() {
  return (
    <DashboardLayout>
      <div className="space-y-5 p-3 sm:p-5 animate-fade-in">
        {/* ===== SECTION 1: EXECUTIVE BRIEF ===== */}
        {/* What happened? Why? What should I do? */}
        <section>
          <ExecutiveBrief />
        </section>

        {/* ===== SECTION 2: DECISION CARDS ===== */}
        {/* Executive KPIs — actionable, not passive */}
        <section>
          <div className="flex items-center justify-between mb-3">
            <div>
              <h2 className="text-sm font-semibold tracking-tight">Executive KPIs</h2>
              <p className="text-[11px] text-muted-foreground mt-0.5">
                Actionable metrics driving portfolio decisions
              </p>
            </div>
            <span className="badge badge-blue text-[10px]">
              Priority Weighted
            </span>
          </div>
          <DecisionCards />
        </section>

        {/* ===== SECTION 3: OPPORTUNITIES + ALERTS ===== */}
        {/* Top Opportunities (primary) + Critical Alerts (secondary) */}
        <section className="grid grid-cols-1 lg:grid-cols-3 gap-5">
          <div className="lg:col-span-2 space-y-5">
            <OpportunityPanel />
          </div>
          <div className="space-y-5">
            <AlertCenter />
          </div>
        </section>

        {/* ===== SECTION 4: MARKET + PERFORMANCE ===== */}
        {/* Supporting context */}
        <section className="grid grid-cols-1 lg:grid-cols-2 gap-5">
          <MarketOverview />
          <ActivityChart />
        </section>

        {/* ===== SECTION 5: DISCOVERY ===== */}
        {/* Pipeline for future opportunities */}
        <section>
          <div className="flex items-center justify-between mb-3">
            <div>
              <h2 className="text-sm font-semibold tracking-tight">Opportunity Pipeline</h2>
              <p className="text-[11px] text-muted-foreground mt-0.5">
                Emerging talent and new investment candidates
              </p>
            </div>
          </div>
          <DiscoveryFeed />
        </section>
      </div>
    </DashboardLayout>
  );
}
