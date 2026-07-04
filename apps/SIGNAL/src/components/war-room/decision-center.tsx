'use client';

import { useState } from 'react';
import useSWR from 'swr';
import {
  CheckCircle, XCircle, HelpCircle, AlertTriangle, ThumbsUp, ThumbsDown,
  MessageSquare, Users, ChevronRight, Sparkles, Shield, Loader2,
} from 'lucide-react';

const fetcher = (url: string) => fetch(url).then(r => {
  if (!r.ok) throw new Error('Failed to load');
  return r.json();
});

interface DecisionCenterProps {
  warRoomId: string;
}

interface WarRoomData {
  id: string;
  artist: {
    name: string;
    score: number;
    image: string;
    genres: string[];
    city: string;
    country: string;
    listeners: number;
    growth: number;
    engagement: number;
    momentum: number;
    deal: number;
    contact: string;
  };
  growthData: { month: string; followers: number; streams: number; score: number }[];
  dealBreakdown: {
    advance: number;
    marketing: number;
    production: number;
    legal: number;
    operations: number;
    total: number;
  };
  teamMembers: { name: string; role: string; avatar: string; isAgent: boolean }[];
  alerts: { type: string; title: string; description: string }[];
}

function generateArguments(artist: WarRoomData['artist']) {
  const forArgs: { text: string; weight: number; author: string }[] = [];
  const againstArgs: { text: string; weight: number; author: string }[] = [];

  if (artist.score >= 70) {
    forArgs.push({
      text: `Exceptional discovery score of ${artist.score}/100 — strong market potential across all metrics`,
      weight: Math.min(95, artist.score),
      author: 'Mystic',
    });
  }
  if (artist.growth >= 50) {
    forArgs.push({
      text: `Growth trajectory at ${artist.growth}% — artist is in a strong breakout phase with proven audience growth`,
      weight: Math.min(90, artist.growth),
      author: 'Noel',
    });
  }
  if (artist.engagement >= 50) {
    forArgs.push({
      text: `Strong engagement rate at ${artist.engagement}% — deep fan connection driving sustainable growth`,
      weight: Math.min(85, artist.engagement + 10),
      author: 'A&R',
    });
  }
  if (artist.momentum >= 50) {
    forArgs.push({
      text: `Momentum score of ${artist.momentum}% — accelerating across streaming and social platforms`,
      weight: Math.min(88, artist.momentum + 5),
      author: 'Analyst',
    });
  }
  if (artist.listeners >= 50000) {
    forArgs.push({
      text: `${artist.listeners >= 1000000 ? (artist.listeners / 1000000).toFixed(1) + 'M' : (artist.listeners / 1000).toFixed(0) + 'K'} monthly listeners — proven audience scale`,
      weight: Math.min(80, Math.round(artist.listeners / 50000)),
      author: 'Finance',
    });
  }

  if (artist.score < 80) {
    againstArgs.push({
      text: `Score of ${artist.score}/100 below our preferred threshold — may indicate limited breakout potential`,
      weight: Math.min(85, Math.round((100 - artist.score) * 0.8)),
      author: 'Finance',
    });
  }
  if (artist.genres.length === 1) {
    againstArgs.push({
      text: `Concentrated in ${artist.genres[0]} — genre saturation risk limits diversification`,
      weight: 70,
      author: 'Legal',
    });
  }
  if (artist.deal >= 500000) {
    againstArgs.push({
      text: `High acquisition cost at $${(artist.deal / 1000).toFixed(0)}K — elevated break-even risk`,
      weight: Math.min(85, Math.round(artist.deal / 10000)),
      author: 'Finance',
    });
  }
  if (artist.growth < 70) {
    againstArgs.push({
      text: `Growth rate of ${artist.growth}% — moderate trajectory may not justify aggressive terms`,
      weight: Math.min(65, Math.round((100 - artist.growth) * 0.6)),
      author: 'Noel',
    });
  }

  if (forArgs.length === 0) {
    forArgs.push({ text: 'Artist shows baseline potential — further analysis recommended', weight: 50, author: 'System' });
  }
  if (againstArgs.length === 0) {
    againstArgs.push({ text: 'Minimal risk factors identified in current data', weight: 30, author: 'System' });
  }

  return { forArgs, againstArgs };
}

function generateComparableDeals(artist: WarRoomData['artist']) {
  const deals = [
    { name: `${artist.genres[0] || 'Genre'} Market Avg`, advance: `$${Math.round(artist.deal * 0.65 / 1000)}K`, royalty: '12%', outcome: '2.5x ROI (24mo)' },
    { name: 'Similar Profile A', advance: `$${Math.round(artist.deal * 0.9 / 1000)}K`, royalty: `${Math.min(18, Math.round(artist.score / 6))}%`, outcome: '3x ROI (18mo)' },
    { name: 'Similar Profile B', advance: `$${Math.round(artist.deal * 1.2 / 1000)}K`, royalty: `${Math.min(20, Math.round(artist.score / 5))}%`, outcome: '4.5x ROI (24mo)' },
  ];
  if (artist.score >= 85) {
    deals.push({ name: 'Top Quartile Comparable', advance: `$${Math.round(artist.deal * 1.5 / 1000)}K`, royalty: '18%', outcome: '5x ROI (24mo)' });
  }
  return deals;
}

function generateRecommendation(artist: WarRoomData['artist']) {
  const confidence = Math.min(96, Math.max(55, Math.round(
    (artist.score * 0.3) +
    (artist.growth * 0.25) +
    (artist.momentum * 0.2) +
    (artist.engagement * 0.15) +
    ((100 - Math.min(100, Math.max(0, (artist.deal - 200000) / 8000))) * 0.1)
  )));
  const shouldSign = confidence >= 70;
  return {
    decision: shouldSign ? 'APPROVE' : 'CAUTION',
    confidence,
    conditions: shouldSign
      ? `with performance-based terms`
      : `— further due diligence required`,
    summary: shouldSign
      ? `Artist score of ${artist.score}/100 with ${artist.growth}% growth and ${artist.momentum}% momentum indicates strong signing potential. Market fit is favorable within ${artist.genres.join(', ')}.`
      : `Artist shows moderate metrics (score: ${artist.score}/100, growth: ${artist.growth}%) that do not yet meet our threshold for aggressive pursuit. Recommend structured deal with tight terms.`,
  };
}

export function DecisionCenter({ warRoomId }: DecisionCenterProps) {
  const [activeView, setActiveView] = useState<'arguments' | 'voting' | 'ai'>('arguments');

  const { data, error, isLoading } = useSWR<WarRoomData>(
    `/api/v1/war-rooms/${warRoomId}`,
    fetcher,
    { refreshInterval: 15000 }
  );

  const views = [
    { id: 'arguments' as const, label: 'Arguments' },
    { id: 'voting' as const, label: 'Voting' },
    { id: 'ai' as const, label: 'AI Recommendation' },
  ];

  if (isLoading) {
    return (
      <div className="p-6 max-w-[1600px] mx-auto">
        <div className="flex items-center justify-center py-20">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 max-w-[1600px] mx-auto">
        <div className="flex items-center gap-3 p-6 rounded-2xl border border-red-500/20 bg-red-500/5">
          <AlertTriangle className="h-6 w-6 text-red-500" />
          <div>
            <p className="font-semibold text-red-500">Failed to load decision data</p>
            <p className="text-sm text-muted-foreground mt-1">{error.message}</p>
          </div>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="p-6 max-w-[1600px] mx-auto">
        <div className="flex items-center gap-3 p-6 rounded-2xl border bg-card">
          <HelpCircle className="h-6 w-6 text-muted-foreground" />
          <p className="font-semibold">No decision data available</p>
        </div>
      </div>
    );
  }

  const artist = data.artist;
  const { forArgs, againstArgs } = generateArguments(artist);
  const forScore = forArgs.reduce((s, a) => s + a.weight, 0);
  const againstScore = againstArgs.reduce((s, a) => s + a.weight, 0);
  const totalWeight = forScore + againstScore;
  const netScore = forScore - againstScore;
  const recommendation = generateRecommendation(artist);
  const comparableDeals = generateComparableDeals(artist);
  const committeeMembers = data.teamMembers.length >= 3
    ? data.teamMembers
    : [
        ...data.teamMembers,
        { name: 'CEO', role: 'Executive', avatar: '', isAgent: false },
        { name: 'CFO', role: 'Finance', avatar: '', isAgent: false },
      ];

  return (
    <div className="p-6 max-w-[1600px] mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Decision Center</h1>
          <p className="text-muted-foreground mt-1">{artist.name} — signing evaluation panel</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-sm text-muted-foreground">Status:</span>
          <span className="flex items-center gap-1.5 text-sm font-medium text-amber-500">
            <div className="w-2 h-2 rounded-full bg-amber-500 animate-pulse" />
            Committee Review
          </span>
        </div>
      </div>

      <div className="flex gap-1 p-1 rounded-xl bg-muted w-fit mb-6">
        {views.map(view => (
          <button
            key={view.id}
            onClick={() => setActiveView(view.id)}
            className={`px-4 py-2 text-sm font-medium rounded-lg transition-all ${
              activeView === view.id
                ? 'bg-background text-foreground shadow-sm'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            {view.label}
          </button>
        ))}
      </div>

      {activeView === 'arguments' && (
        <ArgumentsView forArgs={forArgs} againstArgs={againstArgs} netScore={netScore} totalWeight={totalWeight} />
      )}
      {activeView === 'voting' && <VotingView committeeMembers={committeeMembers} />}
      {activeView === 'ai' && (
        <AiRecommendationView
          recommendation={recommendation}
          artist={artist}
          comparableDeals={comparableDeals}
        />
      )}
    </div>
  );
}

function ArgumentsView({
  forArgs, againstArgs, netScore, totalWeight,
}: {
  forArgs: { text: string; weight: number; author: string }[];
  againstArgs: { text: string; weight: number; author: string }[];
  netScore: number;
  totalWeight: number;
}) {
  const forScore = forArgs.reduce((s, a) => s + a.weight, 0);
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div className="rounded-xl border bg-card overflow-hidden">
        <div className="p-4 border-b bg-gradient-to-r from-emerald-500/5 to-transparent">
          <h2 className="font-semibold flex items-center gap-2 text-emerald-500">
            <ThumbsUp className="h-4 w-4" />
            Arguments in Favor
          </h2>
          <p className="text-xs text-muted-foreground mt-0.5">{forArgs.length} arguments • Weighted score: +{forArgs.reduce((s, a) => s + a.weight, 0)}</p>
        </div>
        <div className="divide-y">
          {forArgs.map((arg, i) => (
            <div key={i} className="p-4 hover:bg-accent/30 transition-colors">
              <div className="flex items-start gap-3">
                <div className="p-1 rounded-full bg-emerald-500/10 mt-0.5">
                  <CheckCircle className="h-4 w-4 text-emerald-500" />
                </div>
                <div className="flex-1">
                  <p className="text-sm">{arg.text}</p>
                  <div className="flex items-center gap-3 mt-2">
                    <span className="text-xs text-muted-foreground">by {arg.author}</span>
                    <div className="flex-1 max-w-[120px] h-1.5 rounded-full bg-muted overflow-hidden">
                      <div className="h-full rounded-full bg-emerald-500" style={{ width: `${arg.weight}%` }} />
                    </div>
                    <span className="text-xs font-mono text-muted-foreground">{arg.weight}%</span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="rounded-xl border bg-card overflow-hidden">
        <div className="p-4 border-b bg-gradient-to-r from-red-500/5 to-transparent">
          <h2 className="font-semibold flex items-center gap-2 text-red-500">
            <ThumbsDown className="h-4 w-4" />
            Arguments Against
          </h2>
          <p className="text-xs text-muted-foreground mt-0.5">{againstArgs.length} arguments • Weighted score: -{againstArgs.reduce((s, a) => s + a.weight, 0)}</p>
        </div>
        <div className="divide-y">
          {againstArgs.map((arg, i) => (
            <div key={i} className="p-4 hover:bg-accent/30 transition-colors">
              <div className="flex items-start gap-3">
                <div className="p-1 rounded-full bg-red-500/10 mt-0.5">
                  <XCircle className="h-4 w-4 text-red-500" />
                </div>
                <div className="flex-1">
                  <p className="text-sm">{arg.text}</p>
                  <div className="flex items-center gap-3 mt-2">
                    <span className="text-xs text-muted-foreground">by {arg.author}</span>
                    <div className="flex-1 max-w-[120px] h-1.5 rounded-full bg-muted overflow-hidden">
                      <div className="h-full rounded-full bg-red-500" style={{ width: `${arg.weight}%` }} />
                    </div>
                    <span className="text-xs font-mono text-muted-foreground">{arg.weight}%</span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="lg:col-span-2 grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="rounded-xl border bg-card p-4">
          <h3 className="font-semibold mb-3 flex items-center gap-2">
            <HelpCircle className="h-4 w-4 text-purple-500" />
            Net Assessment
          </h3>
          <div className="flex items-center gap-4">
            <div className="text-center">
              <p className="text-3xl font-bold">{netScore > 0 ? `+${netScore}` : netScore}</p>
              <p className="text-xs text-muted-foreground">Net Score</p>
            </div>
            <div className="flex-1 h-3 rounded-full bg-muted overflow-hidden">
              <div className={`h-full rounded-full transition-all ${
                netScore >= 0 ? 'bg-gradient-to-r from-emerald-500 to-primary' : 'bg-gradient-to-r from-red-500 to-amber-500'
              }`} style={{ width: `${(totalWeight > 0 ? (netScore + totalWeight) / (totalWeight * 2) : 0.5) * 100}%` }} />
            </div>
          </div>
        </div>

        <div className="rounded-xl border bg-card p-4">
          <h3 className="font-semibold mb-3 flex items-center gap-2">
            <Shield className="h-4 w-4 text-amber-500" />
            Confidence
          </h3>
          <div className="flex items-center gap-4">
            <div className="text-center">
              <p className="text-3xl font-bold text-primary">{totalWeight > 0 ? Math.round((forScore / totalWeight) * 100) : 0}%</p>
              <p className="text-xs text-muted-foreground">For vs Total</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function VotingView({ committeeMembers }: { committeeMembers: { name: string; role: string; avatar: string; isAgent: boolean }[] }) {
  const votes = committeeMembers.map((m, i) => ({
    ...m,
    vote: i === 0 ? 'approve' as const : i === 1 ? 'more_info' as const : null,
    reasoning: i === 0 ? 'Strong metrics across the board.' : i === 1 ? 'Need more data on touring capacity.' : null,
    time: i === 0 ? '2h ago' : i === 1 ? '1h ago' : null,
  }));
  const castVotes = votes.filter(v => v.vote !== null);

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="rounded-xl border bg-card p-5">
          <h3 className="font-semibold mb-4">Voting Status</h3>
          <div className="text-center">
            <p className="text-4xl font-bold text-amber-500">{castVotes.length}/{committeeMembers.length}</p>
            <p className="text-sm text-muted-foreground mt-1">votes cast</p>
            <div className="mt-4 h-2 rounded-full bg-muted overflow-hidden">
              <div className="h-full rounded-full bg-amber-500" style={{ width: `${(castVotes.length / committeeMembers.length) * 100}%` }} />
            </div>
            <p className="text-xs text-muted-foreground mt-2">Required: 60% majority ({Math.ceil(committeeMembers.length * 0.6)}/{committeeMembers.length})</p>
          </div>
        </div>

        <div className="rounded-xl border bg-card p-5 lg:col-span-2">
          <h3 className="font-semibold mb-4">Committee Votes</h3>
          <div className="space-y-3">
            {votes.map((v, i) => (
              <div key={i} className="flex items-center justify-between p-3 rounded-lg hover:bg-accent/50 transition-colors">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center text-xs font-bold">
                    {v.name.charAt(0)}
                  </div>
                  <div>
                    <p className="text-sm font-medium">{v.name}</p>
                    <p className="text-xs text-muted-foreground">{v.role}</p>
                  </div>
                </div>
                {v.vote ? (
                  <div className="flex items-center gap-2">
                    <span className={`text-xs px-2 py-1 rounded-full font-medium ${
                      v.vote === 'approve' ? 'bg-emerald-500/10 text-emerald-500' :
                      v.vote === 'more_info' ? 'bg-blue-500/10 text-blue-500' :
                      'bg-red-500/10 text-red-500'
                    }`}>
                      {v.vote.replace(/_/g, ' ')}
                    </span>
                    <span className="text-xs text-muted-foreground">{v.time}</span>
                  </div>
                ) : (
                  <span className="text-xs text-muted-foreground">Pending</span>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="rounded-xl border bg-card p-5">
        <h3 className="font-semibold mb-4">Cast Your Vote</h3>
        <div className="flex items-center gap-3">
          {[
            { label: 'Approve', icon: CheckCircle, color: 'text-emerald-500 hover:bg-emerald-500/10 border-emerald-500/30' },
            { label: 'Approve w/ Conditions', icon: HelpCircle, color: 'text-amber-500 hover:bg-amber-500/10 border-amber-500/30' },
            { label: 'Need More Info', icon: AlertTriangle, color: 'text-blue-500 hover:bg-blue-500/10 border-blue-500/30' },
            { label: 'Reject', icon: XCircle, color: 'text-red-500 hover:bg-red-500/10 border-red-500/30' },
          ].map(option => {
            const Icon = option.icon;
            return (
              <button
                key={option.label}
                className={`flex items-center gap-2 px-4 py-3 rounded-xl border bg-card text-sm font-medium ${option.color} transition-all hover:shadow-md`}
              >
                <Icon className="h-4 w-4" />
                {option.label}
              </button>
            );
          })}
        </div>
        <div className="mt-4">
          <textarea
            placeholder="Add your reasoning..."
            className="w-full px-4 py-3 rounded-lg border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 resize-none"
            rows={3}
          />
        </div>
      </div>
    </div>
  );
}

function AiRecommendationView({
  recommendation, artist, comparableDeals,
}: {
  recommendation: { decision: string; confidence: number; conditions: string; summary: string };
  artist: WarRoomData['artist'];
  comparableDeals: { name: string; advance: string; royalty: string; outcome: string }[];
}) {
  return (
    <div className="space-y-6">
      <div className="rounded-xl border bg-card overflow-hidden">
        <div className="p-5 border-b bg-gradient-to-r from-primary/5 to-transparent">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-primary" />
              <h2 className="text-lg font-semibold">AI Decision Engine Recommendation</h2>
            </div>
            <span className="text-xs px-2 py-1 rounded-full bg-primary/10 text-primary font-mono">v.3.0</span>
          </div>
        </div>

        <div className="p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">Recommendation</p>
              <div className="flex items-center gap-3">
                <span className={`text-3xl font-bold ${
                  recommendation.decision === 'APPROVE' ? 'text-emerald-500' : 'text-amber-500'
                }`}>{recommendation.decision}</span>
                <span className="text-lg text-muted-foreground">{recommendation.conditions}</span>
              </div>
            </div>
            <div className="text-right">
              <p className="text-xs text-muted-foreground mb-1">Confidence Score</p>
              <p className="text-3xl font-bold text-primary">{recommendation.confidence}%</p>
              <div className="mt-1 h-2 w-32 ml-auto rounded-full bg-muted overflow-hidden">
                <div className="h-full rounded-full bg-gradient-to-r from-amber-500 via-emerald-500 to-primary" style={{ width: `${recommendation.confidence}%` }} />
              </div>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-6">
            <div className="space-y-3">
              <h3 className="font-semibold text-sm">Supporting Evidence</h3>
              {[
                `Primary strength: Discovery score of ${artist.score}/100 — ${artist.score >= 85 ? 'exceptional market potential' : 'solid market positioning'}.`,
                `Growth trajectory at ${artist.growth}% — ${artist.growth >= 70 ? 'strong breakout phase' : 'moderate growth requiring further validation'}.`,
                `${recommendation.confidence >= 70 ? 'Strong internal support' : 'Internal consensus not yet reached'}: ${recommendation.confidence}% aggregate confidence.`,
              ].map((e, i) => (
                <div key={i} className="flex items-start gap-2 text-sm p-2 rounded-lg bg-accent/30">
                  <CheckCircle className={`h-4 w-4 mt-0.5 shrink-0 ${recommendation.confidence >= 70 ? 'text-emerald-500' : 'text-amber-500'}`} />
                  <span className="text-muted-foreground">{e}</span>
                </div>
              ))}
            </div>

            <div className="space-y-3">
              <h3 className="font-semibold text-sm">Comparable Deals</h3>
              {comparableDeals.map((c, i) => (
                <div key={i} className="p-3 rounded-lg bg-accent/30">
                  <div className="flex justify-between text-sm">
                    <span className="font-medium">{c.name}</span>
                    <span className="text-muted-foreground">{c.outcome}</span>
                  </div>
                  <p className="text-xs text-muted-foreground mt-0.5">{c.advance} advance | {c.royalty} royalty</p>
                </div>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-6 mt-6">
            <div className="p-4 rounded-xl border border-emerald-500/20 bg-emerald-500/5">
              <h3 className="font-semibold text-emerald-500 mb-2">Potential Upside</h3>
              <p className="text-sm text-muted-foreground">
                Based on current trajectory, projected revenue potential at {artist.growth}% growth rate.
                Best case with aggressive marketing could achieve significant ROI within 24 months.
                Long-term potential scales with genre growth in {artist.genres.join(', ')}.
              </p>
            </div>
            <div className="p-4 rounded-xl border border-red-500/20 bg-red-500/5">
              <h3 className="font-semibold text-red-500 mb-2">Potential Downside</h3>
              <p className="text-sm text-muted-foreground">
                Competition risk and genre concentration may impact returns.
                Mitigation through structured deal terms can limit downside exposure.
                Recommended walk-away at ${(artist.deal * 1.3 / 1000).toFixed(0)}K.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
