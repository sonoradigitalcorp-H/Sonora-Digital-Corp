'use client';

import { TrendingUp, TrendingDown, AlertTriangle, CheckCircle2, Lightbulb, Target, ArrowRight, Sparkles } from 'lucide-react';
import useSWR from 'swr';

const fetcher = (url: string) => fetch(url).then(r => r.json());

interface BriefMetric {
  label: string;
  value: string | number;
  trend: 'up' | 'down' | 'neutral';
  detail: string;
}

interface BriefBullet {
  text: string;
  icon: 'alert' | 'positive' | 'info';
}

function computeBrief(
  analytics: any,
  alerts: any,
): { metrics: BriefMetric[]; bullets: BriefBullet[]; highestOpportunity: string; recommendedAction: string; confidence: number } | null {
  if (!analytics) return null;

  const kpis = analytics.kpiMetrics ?? [];
  const artists = analytics.topForSigning ?? [];

  const findKPI = (label: string) => kpis.find((k: any) => k.label === label);

  // Portfolio Health: from Avg Discovery Score or average of artist scores
  const avgScore = artists.length > 0
    ? Math.round(artists.reduce((s: number, a: any) => s + (a.score || 0), 0) / artists.length)
    : 72;

  // Highest opportunity: artist with max score
  const topArtist = artists.length > 0
    ? artists.reduce((best: any, a: any) => (a.score || 0) > (best?.score || 0) ? a : best, artists[0])
    : null;

  // Alerts requiring attention
  const notifications = alerts?.notifications ?? [];
  const criticalCount = notifications.filter((n: any) => n.type === 'critical').length;
  const warningCount = notifications.filter((n: any) => n.type === 'warning').length;
  const totalActionable = criticalCount + warningCount;

  // Artists in high-growth (growth > 10)
  const highGrowthCount = artists.filter((a: any) => (a.growth || 0) > 10).length;

  // Artists near signing threshold (score > 80)
  const signingReady = artists.filter((a: any) => (a.score || 0) >= 80).length;

  // Momentum trend
  const avgGrowth = artists.length > 0
    ? Math.round(artists.reduce((s: number, a: any) => s + (a.growth || 0), 0) / artists.length)
    : 0;

  // Compute confidence from score distribution
  const scoreVariance = artists.length > 1
    ? Math.sqrt(artists.reduce((s: number, a: any) => s + Math.pow((a.score || 0) - avgScore, 2), 0) / artists.length)
    : 12;
  const confidence = Math.max(50, Math.min(98, Math.round(100 - scoreVariance / 2)));

  const bullets: BriefBullet[] = [];

  if (totalActionable > 0) {
    bullets.push({
      text: `${totalActionable} artist${totalActionable > 1 ? 's' : ''} require${totalActionable === 1 ? 's' : ''} immediate attention`,
      icon: 'alert',
    });
  }

  if (highGrowthCount > 0) {
    bullets.push({
      text: `${highGrowthCount} artist${highGrowthCount > 1 ? 's' : ''} entered high-growth territory`,
      icon: 'positive',
    });
  }

  if (avgGrowth > 0) {
    bullets.push({
      text: `Portfolio health ${avgGrowth > 5 ? 'improved' : 'remained stable'} this week`,
      icon: 'positive',
    });
  } else if (avgGrowth < 0) {
    bullets.push({
      text: `Portfolio health declined this week — review underperformers`,
      icon: 'alert',
    });
  }

  if (signingReady > 0) {
    bullets.push({
      text: `${signingReady} artist${signingReady > 1 ? 's' : ''} reached signing threshold`,
      icon: 'positive',
    });
  }

  if (!bullets.length) {
    bullets.push({
      text: 'Portfolio is stable — no urgent actions required',
      icon: 'info',
    });
  }

  const highestOpportunity = topArtist?.name ?? 'No data';
  const recommendedAction = signingReady > 0
    ? `Prioritize signing discussions for ${signingReady} qualified artist${signingReady > 1 ? 's' : ''}`
    : highGrowthCount > 0
      ? `Monitor ${highGrowthCount} high-growth artist${highGrowthCount > 1 ? 's' : ''} for investment potential`
      : totalActionable > 0
        ? `Review ${totalActionable} active risk${totalActionable > 1 ? 's' : ''} before proceeding`
        : 'Continue current strategy — portfolio is performing well';

  // Portfolio health metric
  const portfolioMetric: BriefMetric = {
    label: 'Portfolio Health',
    value: `${avgScore}/100`,
    trend: avgGrowth > 5 ? 'up' : avgGrowth < -5 ? 'down' : 'neutral',
    detail: `${avgGrowth > 0 ? '+' : ''}${avgGrowth}% vs last period`,
  };

  return {
    metrics: [
      portfolioMetric,
      {
        label: 'Highest Opportunity',
        value: highestOpportunity,
        trend: 'up',
        detail: `Score: ${topArtist?.score ?? 'N/A'} · Growth: ${topArtist?.growth != null ? (topArtist.growth > 0 ? '+' : '') + topArtist.growth + '%' : 'N/A'}`,
      },
      {
        label: 'Active Risks',
        value: totalActionable,
        trend: totalActionable > 3 ? 'down' : totalActionable === 0 ? 'up' : 'neutral',
        detail: `${criticalCount} critical · ${warningCount} warnings`,
      },
      {
        label: 'Signing Readiness',
        value: `${signingReady} artist${signingReady !== 1 ? 's' : ''}`,
        trend: signingReady > 0 ? 'up' : 'neutral',
        detail: `${artists.length} evaluated in portfolio`,
      },
    ],
    bullets,
    highestOpportunity,
    recommendedAction,
    confidence,
  };
}

const trendIcon = (t: string) => {
  if (t === 'up') return <TrendingUp className="h-3.5 w-3.5 text-green-500" />;
  if (t === 'down') return <TrendingDown className="h-3.5 w-3.5 text-rose-500" />;
  return null;
};

function ExecutiveBriefSkeleton() {
  return (
    <div className="kpi-card animate-pulse">
      <div className="flex items-start justify-between mb-5">
        <div className="space-y-2">
          <div className="h-5 w-40 bg-muted rounded" />
          <div className="h-3 w-56 bg-muted rounded" />
        </div>
        <div className="h-8 w-24 bg-muted rounded-full" />
      </div>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-5">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="space-y-2">
            <div className="h-2.5 w-20 bg-muted rounded" />
            <div className="h-7 w-24 bg-muted rounded" />
            <div className="h-2 w-16 bg-muted rounded" />
          </div>
        ))}
      </div>
      <div className="space-y-2">
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="flex items-center gap-2">
            <div className="h-4 w-4 bg-muted rounded-full" />
            <div className="h-3 w-64 bg-muted rounded" />
          </div>
        ))}
      </div>
    </div>
  );
}

export function ExecutiveBrief() {
  const { data: analytics, error: analyticsError, isLoading: analyticsLoading } = useSWR('/api/v1/analytics', fetcher);
  const { data: alerts, error: alertsError, isLoading: alertsLoading } = useSWR('/api/v1/notifications', fetcher);

  const isLoading = analyticsLoading || alertsLoading;
  const hasError = analyticsError || alertsError;

  if (hasError) {
    return (
      <div className="kpi-card">
        <div className="flex items-center gap-3">
          <AlertTriangle className="h-5 w-5 text-amber-400" />
          <div>
            <p className="text-sm font-medium">Unable to load Executive Brief</p>
            <p className="text-xs text-muted-foreground mt-0.5">Data source unavailable — check connectivity</p>
          </div>
        </div>
      </div>
    );
  }

  if (isLoading) {
    return <ExecutiveBriefSkeleton />;
  }

  const brief = computeBrief(analytics, alerts);

  if (!brief) {
    return (
      <div className="kpi-card">
        <div className="flex items-center gap-3">
          <Lightbulb className="h-5 w-5 text-muted-foreground" />
          <div>
            <p className="text-sm font-medium">Executive Brief</p>
            <p className="text-xs text-muted-foreground mt-0.5">Awaiting data to generate portfolio summary</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="kpi-card relative overflow-hidden">
      {/* Subtle gradient background accent */}
      <div className="absolute top-0 right-0 w-64 h-64 bg-primary/5 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-0 left-0 w-48 h-48 bg-green-500/5 rounded-full blur-3xl pointer-events-none" />

      <div className="relative">
        {/* Header */}
        <div className="flex items-start justify-between gap-4 mb-5">
          <div>
            <div className="flex items-center gap-2.5">
              <h2 className="text-base font-semibold tracking-tight">Executive Brief</h2>
              <span className="badge badge-blue text-[10px]">
                <Sparkles className="h-3 w-3" />
                AI-Powered
              </span>
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Portfolio intelligence summary — updated in real-time
            </p>
          </div>
          <div className="flex items-center gap-2 shrink-0">
            <span className="status-dot status-dot-green" />
            <span className="text-[11px] text-muted-foreground font-medium">Live</span>
          </div>
        </div>

        {/* Key metrics row */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-5">
          {brief.metrics.map((m) => (
            <div key={m.label} className="p-3 rounded-lg bg-background/40 border border-border/50">
              <div className="flex items-center justify-between mb-1">
                <p className="text-[10px] font-medium text-muted-foreground uppercase tracking-wider">{m.label}</p>
                {trendIcon(m.trend)}
              </div>
              <p className="text-lg font-bold tracking-tight truncate">{m.value}</p>
              <p className="text-[10px] text-muted-foreground mt-0.5 truncate">{m.detail}</p>
            </div>
          ))}
        </div>

        {/* Bullet points */}
        <div className="space-y-1.5 mb-4">
          {brief.bullets.map((b, i) => (
            <div key={i} className="flex items-center gap-2 text-xs">
              {b.icon === 'alert' ? (
                <AlertTriangle className="h-3.5 w-3.5 text-amber-400 shrink-0" />
              ) : b.icon === 'positive' ? (
                <CheckCircle2 className="h-3.5 w-3.5 text-green-500 shrink-0" />
              ) : (
                <Lightbulb className="h-3.5 w-3.5 text-primary shrink-0" />
              )}
              <span className="text-muted-foreground">{b.text}</span>
            </div>
          ))}
        </div>

        {/* Recommended Action + Confidence */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-3 rounded-lg bg-primary/5 border border-primary/10">
          <div className="flex items-center gap-2">
            <div className="p-1.5 rounded-md bg-primary/10">
              <Target className="h-3.5 w-3.5 text-primary" />
            </div>
            <div>
              <p className="text-[10px] text-muted-foreground uppercase tracking-wider">Recommended Action</p>
              <p className="text-xs font-medium">{brief.recommendedAction}</p>
            </div>
          </div>
          <div className="flex items-center gap-2 shrink-0">
            <div className="flex items-center gap-1.5">
              <span className="text-[10px] text-muted-foreground">Confidence</span>
              <div className="flex items-center gap-1">
                <div className="w-16 h-1.5 rounded-full bg-muted overflow-hidden">
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-primary to-green-500 transition-all duration-500"
                    style={{ width: `${brief.confidence}%` }}
                  />
                </div>
                <span className="text-xs font-semibold tabular-nums text-green-500">{brief.confidence}%</span>
              </div>
            </div>
          </div>
        </div>

        {/* Context hint */}
        <div className="mt-3 flex items-center justify-end">
          <p className="text-[10px] text-muted-foreground/50 flex items-center gap-1">
            <span>Highest opportunity today:</span>
            <span className="font-medium text-muted-foreground/70">{brief.highestOpportunity}</span>
          </p>
        </div>
      </div>
    </div>
  );
}
