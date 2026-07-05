'use client';

import {
  TrendingUp, TrendingDown, ArrowRight, Target, Shield, Activity, AlertTriangle,
  Users, DollarSign, Loader2, Eye, Sparkles
} from 'lucide-react';
import useSWR from 'swr';

const fetcher = (url: string) => fetch(url).then(r => r.json());

interface DecisionCardData {
  title: string;
  value: string | number;
  why: string;
  trend: 'up' | 'down' | 'neutral';
  trendValue: string;
  priority: 'high' | 'medium' | 'low';
  icon: typeof Target;
  color: string;
  bgClass: string;
}

function computeDecisionCards(analytics: any, alerts: any): DecisionCardData[] {
  const kpis = analytics?.kpiMetrics ?? [];
  const artists = analytics?.topForSigning ?? [];
  const notifications = alerts?.notifications ?? [];

  const findKPI = (label: string) => kpis.find((k: any) => k.label === label);

  const artistsTracked = findKPI('Artists Tracked');
  const avgScore = findKPI('Avg Discovery Score');
  const activePipeline = findKPI('Active Pipeline');
  const alertsActive = findKPI('Alerts Active');
  const prospectRadar = findKPI('Prospect Radar');
  const signingReadiness = findKPI('Signing Readiness');

  // Compute derived metrics
  const highPriorityCount = artists.filter((a: any) => (a.score || 0) >= 75 && (a.growth || 0) > 5).length;
  const signingReadyCount = artists.filter((a: any) => (a.score || 0) >= 80).length;
  const avgArtistScore = artists.length > 0
    ? Math.round(artists.reduce((s: number, a: any) => s + (a.score || 0), 0) / artists.length)
    : 0;
  const avgGrowth = artists.length > 0
    ? Math.round(artists.reduce((s: number, a: any) => s + (a.growth || 0), 0) / artists.length)
    : 0;
  const activeRiskCount = notifications.filter((n: any) => n.type === 'critical' || n.type === 'warning').length;
  const totalMomentum = artists.reduce((s: number, a: any) => s + (a.momentum || 0), 0);
  const avgMomentum = artists.length > 0 ? Math.round(totalMomentum / artists.length) : 0;

  // Confidence from score consistency
  const scoreVariance = artists.length > 1
    ? Math.sqrt(artists.reduce((s: number, a: any) => s + Math.pow((a.score || 0) - avgArtistScore, 2), 0) / artists.length)
    : 15;
  const confidence = Math.max(50, Math.min(98, Math.round(100 - scoreVariance / 2)));

  return [
    {
      title: 'High Priority Opportunities',
      value: highPriorityCount,
      why: `${highPriorityCount} artist${highPriorityCount !== 1 ? 's' : ''} with strong scores and positive growth`,
      trend: highPriorityCount > 2 ? 'up' : 'neutral',
      trendValue: `${highPriorityCount} active`,
      priority: highPriorityCount > 0 ? 'high' : 'low',
      icon: Target,
      color: 'text-primary',
      bgClass: 'bg-primary/5 border-primary/10',
    },
    {
      title: 'Artists Ready to Sign',
      value: signingReadyCount,
      why: `${signingReadyCount} artist${signingReadyCount !== 1 ? 's' : ''} exceeded score threshold of 80`,
      trend: signingReadyCount > 0 ? 'up' : 'neutral',
      trendValue: `${signingReadyCount} qualified`,
      priority: signingReadyCount > 0 ? 'high' : 'medium',
      icon: Users,
      color: 'text-green-500',
      bgClass: 'bg-green-500/5 border-green-500/10',
    },
    {
      title: 'Portfolio Health',
      value: `${avgArtistScore}/100`,
      why: `Average score across ${artists.length} evaluated artists`,
      trend: avgGrowth > 5 ? 'up' : avgGrowth < -5 ? 'down' : 'neutral',
      trendValue: `${avgGrowth > 0 ? '+' : ''}${avgGrowth}%`,
      priority: 'medium',
      icon: Shield,
      color: 'text-emerald-400',
      bgClass: 'bg-emerald-500/5 border-emerald-500/10',
    },
    {
      title: 'Growth Outlook',
      value: `${avgMomentum}%`,
      why: `Average momentum across ${artists.length} artists in portfolio`,
      trend: avgMomentum > 50 ? 'up' : avgMomentum < 30 ? 'down' : 'neutral',
      trendValue: `${artists.filter((a: any) => (a.momentum || 0) > 50).length} accelerating`,
      priority: avgMomentum > 50 ? 'high' : 'medium',
      icon: TrendingUp,
      color: 'text-purple-400',
      bgClass: 'bg-purple-500/5 border-purple-500/10',
    },
    {
      title: 'Active Risks',
      value: activeRiskCount,
      why: `${notifications.filter((n: any) => n.type === 'critical').length} critical, ${notifications.filter((n: any) => n.type === 'warning').length} warnings requiring attention`,
      trend: activeRiskCount > 3 ? 'down' : activeRiskCount === 0 ? 'up' : 'neutral',
      trendValue: activeRiskCount === 0 ? 'All clear' : `${activeRiskCount} open`,
      priority: activeRiskCount > 0 ? 'high' : 'low',
      icon: AlertTriangle,
      color: 'text-amber-400',
      bgClass: 'bg-amber-500/5 border-amber-500/10',
    },
    {
      title: 'Confidence Index',
      value: `${confidence}%`,
      why: `Based on score consistency across ${artists.length} artists — higher is more reliable`,
      trend: confidence >= 80 ? 'up' : confidence < 65 ? 'down' : 'neutral',
      trendValue: confidence >= 80 ? 'Strong signal' : confidence >= 65 ? 'Moderate' : 'Low confidence',
      priority: 'medium',
      icon: Activity,
      color: 'text-cyan-400',
      bgClass: 'bg-cyan-500/5 border-cyan-500/10',
    },
  ];
}

function DecisionCard({ card, index }: { card: DecisionCardData; index: number }) {
  const Icon = card.icon;
  const isPositive = card.trend === 'up';

  return (
    <div
      className="kpi-card card-hover relative overflow-hidden group animate-fade-in-up"
      style={{ animationDelay: `${index * 60}ms` }}
    >
      {/* Colored top accent */}
      <div className={`absolute top-0 left-0 right-0 h-0.5 ${card.bgClass.replace('bg-', 'bg-').replace('border-', '')}`} style={{ background: card.color.replace('text-', '').includes('primary') ? '#3B82F6' : undefined }} />

      <div className="flex items-start justify-between mb-3">
        <div className={`p-2 rounded-lg ${card.bgClass}`}>
          <Icon className={`h-4 w-4 ${card.color}`} />
        </div>
        <div className="flex items-center gap-1">
          {isPositive ? (
            <TrendingUp className="h-3.5 w-3.5 text-green-500" />
          ) : card.trend === 'down' ? (
            <TrendingDown className="h-3.5 w-3.5 text-rose-500" />
          ) : null}
          <span className={`text-[10px] font-medium tabular-nums ${isPositive ? 'text-green-500' : card.trend === 'down' ? 'text-rose-500' : 'text-muted-foreground'}`}>
            {card.trendValue}
          </span>
        </div>
      </div>

      <p className="kpi-value mb-1">{card.value}</p>
      <p className="kpi-label">{card.title}</p>

      {/* WHY explanation */}
      <div className="mt-3 pt-3 border-t border-border/50">
        <div className="flex items-start gap-1.5">
          <Sparkles className="h-3 w-3 text-muted-foreground/40 shrink-0 mt-0.5" />
          <p className="text-[10px] text-muted-foreground/60 leading-relaxed">
            {card.why}
          </p>
        </div>
      </div>
    </div>
  );
}

export function DecisionCards() {
  const { data: analytics, error: analyticsError, isLoading: analyticsLoading } = useSWR('/api/v1/analytics', fetcher);
  const { data: alerts, error: alertsError, isLoading: alertsLoading } = useSWR('/api/v1/notifications', fetcher);

  const isLoading = analyticsLoading || alertsLoading;
  const hasError = analyticsError || alertsError;

  if (hasError) {
    return (
      <div className="kpi-card">
        <p className="text-destructive text-xs flex items-center gap-2">
          <AlertTriangle className="h-3.5 w-3.5" />
          Failed to load decision data
        </p>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-3">
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="kpi-card animate-pulse">
            <div className="flex items-start justify-between mb-4">
              <div className="h-8 w-8 bg-muted rounded-lg" />
              <div className="h-3 w-14 bg-muted rounded" />
            </div>
            <div className="h-7 w-16 bg-muted rounded mb-1" />
            <div className="h-3 w-20 bg-muted rounded mb-4" />
            <div className="h-px bg-muted mb-3" />
            <div className="h-2.5 w-32 bg-muted rounded" />
          </div>
        ))}
      </div>
    );
  }

  const cards = computeDecisionCards(analytics, alerts);

  if (!cards.length) {
    return (
      <div className="kpi-card text-center py-8">
        <div className="p-2 rounded-lg bg-muted inline-block mb-3">
          <Eye className="h-5 w-5 text-muted-foreground" />
        </div>
        <p className="text-sm font-medium mb-1">No Decision Data</p>
        <p className="text-xs text-muted-foreground max-w-sm mx-auto">
          Decision intelligence is computed as artist and portfolio data becomes available.
          Start by adding artists to your portfolio.
        </p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-3">
      {cards.map((card, i) => (
        <DecisionCard key={card.title} card={card} index={i} />
      ))}
    </div>
  );
}
