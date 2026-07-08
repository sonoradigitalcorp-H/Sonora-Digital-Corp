'use client';

import { useState } from 'react';
import useSWR, { mutate } from 'swr';
import {
  Send, History, Target, AlertTriangle, TrendingUp, FileText,
  MessageSquare, Calendar, Clock, ChevronRight, Sparkles, CheckCircle,
  XCircle, ArrowLeft, ArrowRight, Loader2, X, DollarSign, HelpCircle,
} from 'lucide-react';

const fetcher = (url: string) => fetch(url).then(r => r.json());

interface NegotiationCenterProps {
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

function generateRiskAnalysis(artist: WarRoomData['artist']) {
  const risks: { risk: string; severity: string; mitigation: string }[] = [];
  if (artist.deal >= 400000) {
    risks.push({ risk: 'High Acquisition Cost', severity: 'high', mitigation: `Set hard walk-away at $${(artist.deal * 1.3 / 1000).toFixed(0)}K` });
  }
  if (artist.score < 80) {
    risks.push({ risk: 'Moderate Score', severity: 'medium', mitigation: 'Consider structured earn-out terms' });
  }
  if (artist.genres.length <= 1) {
    risks.push({ risk: 'Genre Concentration', severity: 'medium', mitigation: 'Include genre diversification in development plan' });
  }
  if (artist.momentum < 60) {
    risks.push({ risk: 'Weakening Momentum', severity: 'medium', mitigation: 'Insert performance-based escalators' });
  }
  if (artist.growth < 50) {
    risks.push({ risk: 'Slow Growth Trajectory', severity: 'high', mitigation: 'Require marketing commitment from artist' });
  }
  if (risks.length === 0) {
    risks.push({ risk: 'Standard Market Risk', severity: 'low', mitigation: 'Standard deal terms apply' });
  }
  return risks;
}

function generateDealStrategy(artist: WarRoomData['artist']) {
  const advanceBase = artist.deal;
  const royaltyBase = Math.min(20, Math.max(10, Math.round(artist.score / 6)));
  return {
    opening: `$${Math.round(advanceBase * 0.75 / 1000)}K advance, ${royaltyBase}% royalty, 3 options`,
    walkAway: `Max $${Math.round(advanceBase * 1.3 / 1000)}K or ${royaltyBase + 4}%+ royalty`,
    approach: artist.score >= 85
      ? `Aggressive but structured. Move quickly with competitive opening offer. Leverage speed and decisive action.`
      : `Measured approach. Focus on value-aligned terms with performance-based upside.`,
    approachEs: artist.score >= 85
      ? `Agresiva pero estructurada. Muévase rápido con una oferta competitiva.`
      : `Enfoque medido. Céntrese en términos alineados con el valor.`,
  };
}

function generateComparableDeals(artist: WarRoomData['artist']) {
  const deals = [];
  const adv = artist.deal;
  deals.push({ name: `${artist.genres[0] || 'Market'} Average`, advance: `$${Math.round(adv * 0.65 / 1000)}K`, royalty: `${Math.round(artist.score / 7)}%`, outcome: '2.5x ROI (24mo)' });
  deals.push({ name: `Similar Artist A (${artist.genres[0] || 'Genre'})`, advance: `$${Math.round(adv * 0.9 / 1000)}K`, royalty: `${Math.min(18, Math.round(artist.score / 5.5))}%`, outcome: '3x ROI (18mo)' });
  deals.push({ name: `Similar Artist B`, advance: `$${Math.round(adv * 1.15 / 1000)}K`, royalty: `${Math.min(20, Math.round(artist.score / 5))}%`, outcome: '4x ROI (24mo)' });
  if (artist.score >= 80) {
    deals.push({ name: 'Competing Label Estimate', advance: `$${Math.round(adv * 1.25 / 1000)}K`, royalty: `${Math.min(22, Math.round(artist.score / 4.5))}%`, outcome: 'Estimated' });
  }
  return deals;
}

function generateAcceptanceProbability(artist: WarRoomData['artist']) {
  const base = Math.round(
    (artist.score * 0.3) +
    (artist.momentum * 0.2) +
    (Math.min(100, artist.growth * 1.2) * 0.2) +
    ((100 - Math.min(100, Math.max(0, (artist.deal - 150000) / 10000))) * 0.3)
  );
  return Math.min(95, Math.max(30, base));
}

function generateAIRecommendation(artist: WarRoomData['artist']) {
  const recommendedAdvance = Math.round(artist.deal * 0.85 / 1000) * 1000;
  const recommendedRoyalty = Math.min(18, Math.max(12, Math.round(artist.score / 6)));
  const escalatorThreshold = Math.round(artist.listeners * 1.3);
  return {
    recommendation: `Counter at $${(recommendedAdvance / 1000).toFixed(0)}K with ${recommendedRoyalty}% royalty. Add performance escalator to ${recommendedRoyalty + 2}% if artist achieves ${escalatorThreshold >= 1000000 ? (escalatorThreshold / 1000000).toFixed(1) + 'M' : (escalatorThreshold / 1000).toFixed(0) + 'K'} monthly listeners within 12 months.`,
    counterAdvance: `$${(recommendedAdvance / 1000).toFixed(0)}K`,
    royalty: `${recommendedRoyalty}%`,
    escalator: `${recommendedRoyalty + 2}% @ ${escalatorThreshold >= 1000000 ? (escalatorThreshold / 1000000).toFixed(1) + 'M' : (escalatorThreshold / 1000).toFixed(0) + 'K'} listeners`,
    walkAway: `$${Math.round(artist.deal * 1.3 / 1000)}K / ${recommendedRoyalty + 4}%`,
    alternatives: [
      `Option A: $${Math.round(artist.deal * 0.8 / 1000)}K advance + ${recommendedRoyalty + 1}% royalty (lower advance, higher royalty)`,
      `Option B: $${Math.round(artist.deal * 0.9 / 1000)}K advance + ${recommendedRoyalty - 1}% royalty + $${Math.round(artist.deal * 0.12 / 1000)}K marketing guarantee`,
      `Option C: $${Math.round(artist.deal * 0.7 / 1000)}K advance + ${recommendedRoyalty}% royalty + 50/50 net profit split`,
    ],
  };
}

export function NegotiationCenter({ warRoomId }: NegotiationCenterProps) {
  const [activeView, setActiveView] = useState<'offers' | 'strategy' | 'timeline' | 'ai'>('offers');

  const { data, error, isLoading } = useSWR<WarRoomData>(
    `/api/v1/war-rooms/${warRoomId}`,
    fetcher,
    { refreshInterval: 15000 }
  );
  const { data: offersData } = useSWR<{ offers: any[] }>(
    `/api/v1/war-rooms/${warRoomId}?section=offers`,
    fetcher,
    { refreshInterval: 10000 }
  );

  const views = [
    { id: 'offers' as const, label: 'Offers' },
    { id: 'strategy' as const, label: 'Strategy' },
    { id: 'timeline' as const, label: 'Timeline' },
    { id: 'ai' as const, label: 'AI Assistant' },
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
            <p className="font-semibold text-red-500">Failed to load negotiation data</p>
            <p className="text-sm text-muted-foreground mt-1">{error.message}</p>
          </div>
        </div>
      </div>
    );
  }

  const artist = data?.artist;
  const offers = offersData?.offers ?? [];

  return (
    <div className="p-6 max-w-[1600px] mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Negotiation Center</h1>
          <p className="text-muted-foreground mt-1">
            {artist ? `${artist.name} — ` : ''}Track offers, strategy, and negotiation timeline
          </p>
        </div>
        {artist && (
          <div className="flex items-center gap-2">
            <span className="text-sm text-muted-foreground">Status:</span>
            <span className="flex items-center gap-1.5 text-sm font-medium text-amber-500">
              <div className="w-2 h-2 rounded-full bg-amber-500 animate-pulse" />
              In Negotiation
            </span>
          </div>
        )}
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

      {activeView === 'offers' && <OffersView warRoomId={warRoomId} artist={artist} offers={offers} />}
      {activeView === 'strategy' && artist && <StrategyView artist={artist} />}
      {activeView === 'timeline' && (artist ? <TimelineView artist={artist} /> : <TimelineFallback />)}
      {activeView === 'ai' && artist && <AiAssistantView artist={artist} />}
    </div>
  );
}

function OffersView({ warRoomId, artist, offers }: { warRoomId: string; artist?: WarRoomData['artist']; offers: any[] }) {
  const [sending, setSending] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [showCounter, setShowCounter] = useState(false);
  const [counterAmount, setCounterAmount] = useState(artist ? String(artist.deal) : '350000');
  const [counterRoyalty, setCounterRoyalty] = useState(artist ? String(Math.min(18, Math.max(12, Math.round(artist.score / 6)))) : '15');
  const [counterNote, setCounterNote] = useState('');

  const latestOffer = offers.length > 0 ? offers[offers.length - 1] : null;

  const sendCounter = async () => {
    setSending(true);
    await fetch(`/api/v1/war-rooms/${warRoomId}/offers`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: 'send_counter',
        amount: parseInt(counterAmount),
        royalty: parseFloat(counterRoyalty),
        notes: counterNote,
      }),
    });
    setSending(false);
    setShowCounter(false);
    mutate(`/api/v1/war-rooms/${warRoomId}/offers`);
  };

  const generateOfferDoc = async () => {
    setGenerating(true);
    await fetch(`/api/v1/war-rooms/${warRoomId}/documents`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: 'Offer_Document.pdf', type: 'pdf', category: 'contract' }),
    });
    setGenerating(false);
    mutate(`/api/v1/war-rooms/${warRoomId}/documents`);
  };

  const dealTerms = artist ? [
    { label: 'Advance Amount', value: `$${(artist.deal / 1000).toFixed(0)}K` },
    { label: 'Target Royalty', value: `${Math.min(18, Math.max(12, Math.round(artist.score / 6)))}%` },
    { label: 'Publishing Share', value: '50%' },
    { label: 'Merchandising', value: '70/30 (Label)' },
    { label: 'Touring', value: '80/20 (Artist)' },
    { label: 'Options', value: '3 albums' },
    { label: 'Exclusivity', value: 'Worldwide' },
    { label: 'Contract Duration', value: '48 months' },
  ] : [];

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div className="lg:col-span-2 rounded-xl border bg-card overflow-hidden">
        <div className="p-4 border-b bg-gradient-to-r from-primary/5 to-transparent">
          <h2 className="font-semibold flex items-center gap-2">
            <Target className="h-4 w-4 text-primary" />
            {latestOffer ? `Current Offer — Version ${latestOffer.version || '1'}` : 'Proposed Terms'}
          </h2>
          <p className="text-xs text-muted-foreground mt-0.5">
            {latestOffer ? `Last updated ${latestOffer.date || 'recently'} • Status: ${latestOffer.status || 'draft'}` : 'Based on artist discovery analysis'}
          </p>
        </div>
        {artist ? (
          <div className="p-5">
            <div className="grid grid-cols-2 gap-6">
              {dealTerms.map(item => (
                <div key={item.label} className="flex justify-between p-3 rounded-lg bg-accent/30">
                  <span className="text-sm text-muted-foreground">{item.label}</span>
                  <span className="text-sm font-medium">{item.value}</span>
                </div>
              ))}
            </div>
            {latestOffer?.notes && (
              <div className="mt-4 p-3 rounded-lg bg-accent/50">
                <p className="text-xs text-muted-foreground">Notes</p>
                <p className="text-sm mt-1">{latestOffer.notes}</p>
              </div>
            )}
            {!latestOffer && (
              <div className="mt-4 p-3 rounded-lg bg-accent/50">
                <p className="text-xs text-muted-foreground">Suggested Approach</p>
                <p className="text-sm mt-1">
                  Opening offer at ${(artist.deal * 0.75 / 1000).toFixed(0)}K with {Math.min(18, Math.max(12, Math.round(artist.score / 6)))}% royalty.
                  Room to move to ${(artist.deal / 1000).toFixed(0)}K with performance escalators.
                </p>
              </div>
            )}
          </div>
        ) : (
          <div className="p-8 text-center text-muted-foreground">
            <HelpCircle className="h-8 w-8 mx-auto mb-2" />
            <p className="text-sm">No artist data available</p>
          </div>
        )}
      </div>

      <div className="rounded-xl border bg-card overflow-hidden">
        <div className="p-4 border-b">
          <h3 className="font-semibold flex items-center gap-2">
            <History className="h-4 w-4 text-muted-foreground" />
            Offer History
          </h3>
        </div>
        {offers.length === 0 ? (
          <div className="p-4 text-center text-muted-foreground">
            <p className="text-sm">No offers yet</p>
            <p className="text-xs mt-1">Send the first counter-offer to begin.</p>
          </div>
        ) : (
          <div className="divide-y">
            {offers.slice().reverse().map((offer: any, i: number) => (
              <div key={i} className="p-4 hover:bg-accent/30 transition-colors">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-medium">v{offer.version || offers.length - i}</span>
                  <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                    offer.status === 'countered' ? 'bg-amber-500/10 text-amber-500' :
                    offer.status === 'rejected' ? 'bg-red-500/10 text-red-500' :
                    offer.status === 'accepted' ? 'bg-emerald-500/10 text-emerald-500' :
                    'bg-blue-500/10 text-blue-500'
                  }`}>{offer.status || 'draft'}</span>
                </div>
                <p className="text-lg font-bold">{typeof offer.amount === 'number' ? `$${(offer.amount / 1000).toFixed(0)}K` : offer.amount}</p>
                <div className="flex items-center justify-between mt-1">
                  <span className="text-xs text-muted-foreground">by {offer.by || 'System'}</span>
                  <span className="text-xs text-muted-foreground">{offer.date || 'N/A'}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="lg:col-span-3 flex items-center gap-3">
        <button onClick={() => setShowCounter(true)} className="flex items-center gap-2 px-4 py-2.5 rounded-lg bg-primary text-primary-foreground text-sm font-medium hover:opacity-90 transition-all">
          <Send className="h-4 w-4" />
          Send Counter-Offer
        </button>
        <button onClick={generateOfferDoc} disabled={generating} className="flex items-center gap-2 px-4 py-2.5 rounded-lg border bg-card text-sm font-medium hover:bg-accent transition-all disabled:opacity-50">
          {generating ? <Loader2 className="h-4 w-4 animate-spin" /> : <FileText className="h-4 w-4" />}
          {generating ? 'Generating...' : 'Generate Offer Document'}
        </button>
        <button className="flex items-center gap-2 px-4 py-2.5 rounded-lg border bg-card text-sm font-medium hover:bg-accent transition-all">
          <MessageSquare className="h-4 w-4" />
          Schedule Meeting
        </button>
      </div>

      {showCounter && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm" onClick={() => !sending && setShowCounter(false)}>
          <div className="rounded-xl border bg-card p-6 max-w-md w-full mx-4 shadow-2xl" onClick={e => e.stopPropagation()}>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">Send Counter-Offer</h3>
              <button onClick={() => setShowCounter(false)} disabled={sending} className="p-1 rounded-lg hover:bg-accent transition-colors disabled:opacity-50"><X className="h-5 w-5" /></button>
            </div>
            <div className="space-y-4">
              <div>
                <label className="text-xs font-medium text-muted-foreground mb-1.5 block">Advance Amount ($)</label>
                <input type="number" value={counterAmount} onChange={e => setCounterAmount(e.target.value)} className="w-full px-3 py-2 rounded-lg border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary/50" />
              </div>
              <div>
                <label className="text-xs font-medium text-muted-foreground mb-1.5 block">Royalty Rate (%)</label>
                <input type="number" step="0.1" value={counterRoyalty} onChange={e => setCounterRoyalty(e.target.value)} className="w-full px-3 py-2 rounded-lg border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary/50" />
              </div>
              <div>
                <label className="text-xs font-medium text-muted-foreground mb-1.5 block">Notes</label>
                <textarea value={counterNote} onChange={e => setCounterNote(e.target.value)} rows={3} className="w-full px-3 py-2 rounded-lg border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 resize-none" placeholder="Optional notes for the artist team..." />
              </div>
            </div>
            <div className="flex items-center justify-end gap-3 mt-6">
              <button onClick={() => setShowCounter(false)} disabled={sending} className="px-4 py-2 rounded-lg border bg-card text-sm hover:bg-accent transition-colors disabled:opacity-50">Cancel</button>
              <button onClick={sendCounter} disabled={sending || !counterAmount} className="flex items-center gap-2 px-4 py-2 rounded-lg bg-primary text-primary-foreground text-sm font-medium hover:opacity-90 transition-all disabled:opacity-50">
                {sending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
                {sending ? 'Sending...' : 'Send Counter-Offer'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function StrategyView({ artist }: { artist: WarRoomData['artist'] }) {
  const strategy = generateDealStrategy(artist);
  const risks = generateRiskAnalysis(artist);
  const acceptanceProb = generateAcceptanceProbability(artist);
  const factors = [
    artist.score >= 75 ? 'Strong discovery score driving confidence' : 'Moderate score — terms should reflect risk',
    artist.momentum >= 60 ? 'Positive momentum increases leverage' : 'Building momentum — be patient on timeline',
    artist.deal >= 400000 ? 'Premium deal requires stronger justification' : 'Reasonable deal range — good alignment',
  ];

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div className="lg:col-span-2 space-y-6">
        <div className="rounded-xl border bg-card p-5">
          <h2 className="font-semibold mb-4">Negotiation Strategy</h2>
          <div className="space-y-4">
            <div className="p-4 rounded-xl bg-gradient-to-r from-primary/5 to-transparent border border-primary/10">
              <p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">Approach</p>
              <p className="text-sm leading-relaxed">{strategy.approach}</p>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="p-3 rounded-lg bg-accent/30">
                <p className="text-xs text-muted-foreground uppercase mb-1">Opening Position</p>
                <p className="text-sm">{strategy.opening}</p>
              </div>
              <div className="p-3 rounded-lg bg-accent/30">
                <p className="text-xs text-muted-foreground uppercase mb-1">Walk-Away Point</p>
                <p className="text-sm">{strategy.walkAway}</p>
              </div>
            </div>
            <div>
              <p className="text-xs text-muted-foreground uppercase tracking-wider mb-2">Key Terms</p>
              <div className="space-y-1.5">
                {[
                  'Performance-based royalty structure with escalators',
                  'Exclusive negotiation period: 14 days',
                  'Marketing commitment with upside sharing',
                  'Artist retains 80% creative approval',
                  'Territory: Worldwide all-inclusive',
                ].map((term, i) => (
                  <div key={i} className="flex items-center gap-2 text-sm">
                    <CheckCircle className="h-3.5 w-3.5 text-emerald-500" />
                    <span className="text-muted-foreground">{term}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        <div className="rounded-xl border bg-card p-5">
          <h2 className="font-semibold mb-4">Talking Points</h2>
          <div className="space-y-3">
            {[
              { topic: 'Artist Vision & Alignment', priority: 'High', points: ['Understand 3-5 year vision', 'Present label alignment strategy', `Share ${artist.genres[0] || 'genre'} success stories`] },
              { topic: 'Commercial Opportunity', priority: 'High', points: [`${artist.growth}% growth trajectory data`, 'Distribution and marketing advantages', `Revenue projection based on ${artist.listeners >= 1000000 ? (artist.listeners / 1000000).toFixed(1) + 'M' : (artist.listeners / 1000).toFixed(0) + 'K'} listeners`] },
              { topic: 'Competitive Differentiation', priority: 'Medium', points: ['Unique value proposition', 'A&R philosophy and roster synergies', `Deal structured at $${(artist.deal / 1000).toFixed(0)}K`] },
            ].map(section => (
              <div key={section.topic} className="p-3 rounded-lg bg-accent/30">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-sm font-medium">{section.topic}</p>
                  <span className="text-xs px-2 py-0.5 rounded-full bg-primary/10 text-primary">{section.priority}</span>
                </div>
                <ul className="space-y-1">
                  {section.points.map((point, i) => (
                    <li key={i} className="flex items-center gap-2 text-sm text-muted-foreground">
                      <ChevronRight className="h-3 w-3" />
                      {point}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="space-y-6">
        <div className="rounded-xl border bg-card p-5">
          <h3 className="font-semibold mb-4">Risk Analysis</h3>
          <div className="space-y-3">
            {risks.map((r, i) => (
              <div key={i} className="p-3 rounded-lg bg-accent/30">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">{r.risk}</span>
                  <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                    r.severity === 'high' ? 'bg-red-500/10 text-red-500' :
                    r.severity === 'medium' ? 'bg-amber-500/10 text-amber-500' :
                    'bg-emerald-500/10 text-emerald-500'
                  }`}>{r.severity}</span>
                </div>
                <p className="text-xs text-muted-foreground mt-1">{r.mitigation}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-xl border bg-card p-5">
          <h3 className="font-semibold mb-4">Acceptance Probability</h3>
          <div className="text-center">
            <p className="text-4xl font-bold text-primary">{acceptanceProb}%</p>
            <p className="text-sm text-muted-foreground mt-1">Probability of acceptance</p>
            <div className="mt-3 h-2 rounded-full bg-muted overflow-hidden">
              <div className="h-full rounded-full bg-primary" style={{ width: `${acceptanceProb}%` }} />
            </div>
            <div className="mt-4 text-left space-y-1">
              <p className="text-xs text-muted-foreground">Key factors:</p>
              {factors.map((f, i) => (
                <div key={i} className="flex items-center gap-2 text-xs">
                  <CheckCircle className="h-3 w-3 text-emerald-500" />
                  <span>{f}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function TimelineView({ artist }: { artist: WarRoomData['artist'] }) {
  const daysAgo = (n: number) => {
    const d = new Date();
    d.setDate(d.getDate() - n);
    return d.toLocaleDateString();
  };

  const events = [
    { date: 'Today', event: `${artist.name} — active negotiation phase`, type: 'action' as const, by: 'System' },
    { date: `${daysAgo(1)}`, event: `Strategy review for ${artist.name}`, type: 'action' as const, by: 'Mystic' },
    { date: `${daysAgo(3)}`, event: `Data analysis completed — score: ${artist.score}/100`, type: 'system' as const, by: 'Analyst' },
    { date: `${daysAgo(5)}`, event: `War Room created for ${artist.name}`, type: 'system' as const, by: 'System' },
  ];

  return (
    <div className="rounded-xl border bg-card p-5">
      <h2 className="font-semibold mb-6">Negotiation Timeline</h2>
      <div className="relative">
        {events.map((item, i) => (
          <div key={i} className="flex items-start gap-4 pb-6 relative">
            <div className="flex flex-col items-center">
              <div className={`w-3 h-3 rounded-full ${
                item.type === 'system' ? 'bg-muted-foreground' :
                item.type === 'action' ? 'bg-primary' :
                'bg-amber-500'
              }`} />
              {i < events.length - 1 && <div className="w-0.5 h-full bg-border absolute top-3" />}
            </div>
            <div className="flex-1 -mt-1">
              <div className="flex items-center justify-between">
                <p className="text-sm">{item.event}</p>
                <span className="text-xs text-muted-foreground">{item.date}</span>
              </div>
              <p className="text-xs text-muted-foreground mt-0.5">by {item.by}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function TimelineFallback() {
  return (
    <div className="rounded-xl border bg-card p-5">
      <div className="text-center py-8 text-muted-foreground">
        <Clock className="h-8 w-8 mx-auto mb-2 opacity-30" />
        <p className="text-sm">Timeline data will appear once negotiations begin</p>
      </div>
    </div>
  );
}

function AiAssistantView({ artist }: { artist: WarRoomData['artist'] }) {
  const recommendation = generateAIRecommendation(artist);
  const deals = generateComparableDeals(artist);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div className="rounded-xl border bg-card p-5">
        <h2 className="font-semibold mb-4 flex items-center gap-2">
          <Sparkles className="h-4 w-4 text-primary" />
          AI Negotiation Assistant
        </h2>
        <div className="space-y-4">
          <div className="p-4 rounded-xl bg-gradient-to-r from-primary/5 to-transparent border border-primary/10">
            <p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">Recommendation</p>
            <p className="text-sm">{recommendation.recommendation}</p>
          </div>

          <div className="grid grid-cols-2 gap-3">
            {[
              { label: 'Counter at', value: recommendation.counterAdvance },
              { label: 'Royalty', value: recommendation.royalty },
              { label: 'Escalator', value: recommendation.escalator },
              { label: 'Walk-away', value: recommendation.walkAway },
            ].map(item => (
              <div key={item.label} className="p-3 rounded-lg bg-accent/30">
                <p className="text-xs text-muted-foreground">{item.label}</p>
                <p className="text-sm font-bold mt-0.5">{item.value}</p>
              </div>
            ))}
          </div>

          <div>
            <h3 className="text-sm font-medium mb-2">Alternative Structures</h3>
            <div className="space-y-2">
              {recommendation.alternatives.map((alt, i) => (
                <div key={i} className="flex items-start gap-2 text-sm text-muted-foreground p-2 rounded-lg hover:bg-accent/50">
                  <ChevronRight className="h-3.5 w-3.5 mt-0.5 shrink-0" />
                  <span>{alt}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      <div className="rounded-xl border bg-card p-5">
        <h2 className="font-semibold mb-4 flex items-center gap-2">
          <FileText className="h-4 w-4 text-muted-foreground" />
          Comparable Deals
        </h2>
        <div className="space-y-3">
          {deals.map((deal, i) => (
            <div key={i} className="flex items-center justify-between p-3 rounded-lg bg-accent/30 hover:bg-accent/50 transition-colors">
              <div>
                <p className="text-sm font-medium">{deal.name}</p>
                <p className="text-xs text-muted-foreground">{deal.advance} advance | {deal.royalty} royalty</p>
              </div>
              <span className="text-xs text-muted-foreground">{deal.outcome}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
