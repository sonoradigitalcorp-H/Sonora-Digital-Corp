'use client';

import { useState } from 'react';
import useSWR from 'swr';
import { DashboardLayout } from '@/components/dashboard/layout';
import {
  BrainCircuit,
  TrendingUp,
  Users,
  Music2,
  Target,
  AlertTriangle,
  Lightbulb,
  Award,
  Loader2,
  ChevronRight,
  Zap,
  Globe,
  Radio,
  Wallet,
  Star,
  Search,
} from 'lucide-react';

const fetcher = (url: string) => fetch(url).then(r => r.json());

// ── Types ──

interface ArtistListItem {
  id: string;
  name: string;
  genres?: string[];
  country?: string;
  image?: string;
  score?: number;
  growth?: number;
}

interface IntelligenceArtist {
  artist: {
    id: string;
    name: string;
    genres: string[];
    country: string | null;
    image: string | null;
  };
  scores: ScoreItem[];
  aggregate: {
    score: number;
    confidence: number;
    scoresComputed: number;
    scoresSkipped: number;
  };
  features: {
    platforms: { name: string; value: number; quality: number; provider: string; source: string }[];
    summary: Record<string, unknown>;
  };
  insights: {
    items: InsightItem[];
    summary: string[];
  };
  metadata: {
    computedAt: string;
    version: string;
  };
}

interface ScoreItem {
  id: string;
  name: string;
  category: string;
  score: number;
  confidence: number;
  summary: string;
  factors: { name: string; impact: number; direction: string; reasoning: string }[];
  recommendations: string[];
  dataQuality: string;
  trend: string;
  volatility: number;
  valid: boolean;
  validationMessage: string;
}

interface InsightItem {
  type: 'growth' | 'risk' | 'opportunity' | 'achievement' | 'warning';
  message: string;
  severity: 'high' | 'medium' | 'low';
  category: string;
  source: string;
}

// ── Helpers ──

function scoreColor(score: number): string {
  if (score >= 80) return 'text-green-400';
  if (score >= 60) return 'text-primary';
  if (score >= 40) return 'text-amber-400';
  return 'text-rose-400';
}

function scoreBgColor(score: number): string {
  if (score >= 80) return 'bg-green-500/10 border-green-500/20';
  if (score >= 60) return 'bg-primary/10 border-primary/20';
  if (score >= 40) return 'bg-amber-500/10 border-amber-500/20';
  return 'bg-rose-500/10 border-rose-500/20';
}

function confidenceBar(confidence: number): string {
  if (confidence >= 70) return 'bg-green-500';
  if (confidence >= 40) return 'bg-primary';
  return 'bg-amber-500';
}

function insightIcon(type: string) {
  switch (type) {
    case 'growth': return <TrendingUp className="w-3.5 h-3.5 text-green-400" />;
    case 'risk': return <AlertTriangle className="w-3.5 h-3.5 text-rose-400" />;
    case 'opportunity': return <Lightbulb className="w-3.5 h-3.5 text-amber-400" />;
    case 'achievement': return <Award className="w-3.5 h-3.5 text-primary" />;
    case 'warning': return <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />;
    default: return <Lightbulb className="w-3.5 h-3.5 text-muted-foreground" />;
  }
}

function insightBorder(type: string): string {
  switch (type) {
    case 'growth': return 'border-l-green-500/40';
    case 'risk': return 'border-l-rose-500/40';
    case 'opportunity': return 'border-l-amber-500/40';
    case 'achievement': return 'border-l-primary/40';
    case 'warning': return 'border-l-amber-500/40';
    default: return 'border-l-muted';
  }
}

function ScoreIcon({ category }: { category: string }) {
  switch (category) {
    case 'growth': return <TrendingUp className="w-4 h-4" />;
    case 'audience': return <Users className="w-4 h-4" />;
    case 'commercial': return <Wallet className="w-4 h-4" />;
    case 'discovery': return <Search className="w-4 h-4" />;
    case 'performance': return <Zap className="w-4 h-4" />;
    default: return <BrainCircuit className="w-4 h-4" />;
  }
}

// ── Score Card ──

function ScoreCard({ score }: { score: ScoreItem }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className={`rounded-lg border ${scoreBgColor(score.score)} p-3.5 transition-all duration-200 ${expanded ? 'ring-1 ring-primary/20' : ''}`}>
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full text-left"
      >
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <ScoreIcon category={score.category} />
            <span className="text-xs font-medium text-muted-foreground uppercase tracking-wider">{score.category}</span>
          </div>
          <ChevronRight className={`w-3.5 h-3.5 text-muted-foreground transition-transform ${expanded ? 'rotate-90' : ''}`} />
        </div>
        <div className="flex items-end justify-between">
          <div>
            <span className="text-sm font-semibold text-foreground">{score.name}</span>
            <div className="flex items-center gap-2 mt-0.5">
              <span className="text-[10px] text-muted-foreground">v{score.version}</span>
              <span className="text-[10px] text-muted-foreground">·</span>
              <span className="text-[10px] text-muted-foreground">{score.confidence}% confidence</span>
            </div>
          </div>
          <div className="text-right">
            <span className={`text-2xl font-bold ${scoreColor(score.score)}`}>
              {score.valid ? score.score : '—'}
            </span>
            <span className="text-[10px] text-muted-foreground ml-0.5">/100</span>
          </div>
        </div>
        {!expanded && score.valid && (
          <p className="text-[11px] text-muted-foreground mt-2 line-clamp-2">{score.summary}</p>
        )}
      </button>

      {expanded && score.valid && (
        <div className="mt-3 pt-3 border-t border-white/5 space-y-3 animate-fade-in">
          {/* Summary */}
          <p className="text-[11px] text-muted-foreground leading-relaxed">{score.summary}</p>

          {/* Factors */}
          {score.factors.length > 0 && (
            <div>
              <span className="text-[10px] font-medium text-muted-foreground uppercase tracking-wider">Factors</span>
              <div className="space-y-1.5 mt-1.5">
                {score.factors.map((f, i) => (
                  <div key={i} className="flex items-center justify-between text-[11px]">
                    <span className="text-foreground/80">{f.name}</span>
                    <span className={f.direction === 'positive' ? 'text-green-400' : 'text-rose-400'}>
                      {f.direction === 'positive' ? '+' : ''}{f.impact.toFixed(1)}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Recommendations */}
          {score.recommendations.length > 0 && (
            <div>
              <span className="text-[10px] font-medium text-muted-foreground uppercase tracking-wider">Recommendations</span>
              <ul className="space-y-1 mt-1.5">
                {score.recommendations.map((r, i) => (
                  <li key={i} className="text-[11px] text-foreground/60 flex items-start gap-1.5">
                    <span className="text-primary mt-0.5">·</span>
                    {r}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Data Quality / Trend */}
          <div className="flex items-center gap-3 text-[10px] text-muted-foreground">
            <span>Quality: {score.dataQuality}</span>
            <span>·</span>
            <span>Trend: {score.trend}</span>
            {score.volatility > 0 && (
              <>
                <span>·</span>
                <span>Volatility: {score.volatility}%</span>
              </>
            )}
          </div>
        </div>
      )}

      {expanded && !score.valid && (
        <div className="mt-3 pt-3 border-t border-white/5">
          <p className="text-[11px] text-rose-400">{score.validationMessage}</p>
        </div>
      )}
    </div>
  );
}

// ── Insight Item ──

function InsightRow({ insight }: { insight: InsightItem }) {
  return (
    <div className={`flex items-start gap-2.5 p-2.5 rounded-md border-l-2 ${insightBorder(insight.type)} bg-white/[0.02]`}>
      <div className="mt-0.5">{insightIcon(insight.type)}</div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className="text-[10px] font-medium uppercase tracking-wider text-muted-foreground">{insight.category}</span>
          <span className={`text-[10px] px-1.5 py-0.5 rounded-full ${
            insight.severity === 'high' ? 'bg-rose-500/10 text-rose-400' :
            insight.severity === 'medium' ? 'bg-amber-500/10 text-amber-400' :
            'bg-muted text-muted-foreground'
          }`}>
            {insight.severity}
          </span>
        </div>
        <p className="text-[12px] text-foreground/80 mt-0.5 leading-relaxed">{insight.message}</p>
      </div>
    </div>
  );
}

// ── Main Dashboard Page ──

export default function IntelligenceDashboard() {
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  // Fetch artist list
  const { data: artistsData, error: artistsError, isLoading: artistsLoading } = useSWR(
    '/api/v1/artists',
    fetcher
  );

  // Fetch intelligence for selected artist
  const { data: intelligenceData, error: intelligenceError, isLoading: intelligenceLoading } = useSWR(
    selectedId ? `/api/v1/intelligence/${selectedId}` : null,
    fetcher,
    { revalidateOnFocus: false }
  );

  const artists: ArtistListItem[] = artistsData?.artists ?? artistsData ?? [];

  // Filter artists by search
  const filteredArtists = searchQuery
    ? artists.filter((a: ArtistListItem) =>
        a.name.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : artists;

  const selectedArtist = artists.find((a: ArtistListItem) => a.id === selectedId);

  return (
    <DashboardLayout>
      <div className="flex h-full">
        {/* ── Artist List (Left Panel) ── */}
        <div className="w-72 border-r border-white/5 flex flex-col flex-shrink-0">
          {/* Header */}
          <div className="p-4 border-b border-white/5">
            <div className="flex items-center gap-2 mb-3">
              <BrainCircuit className="w-4 h-4 text-primary" />
              <h2 className="text-sm font-semibold tracking-tight">Artist Intelligence</h2>
            </div>
            <div className="relative">
              <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-muted-foreground" />
              <input
                type="text"
                placeholder="Search artists..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-muted rounded-md pl-8 pr-3 py-1.5 text-xs text-foreground placeholder:text-muted-foreground/50 focus:outline-none focus:ring-1 focus:ring-primary/30"
              />
            </div>
          </div>

          {/* Artist list */}
          <div className="flex-1 overflow-y-auto">
            {artistsLoading && (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="w-4 h-4 animate-spin text-muted-foreground" />
              </div>
            )}
            {artistsError && (
              <p className="text-[11px] text-rose-400 p-4">Failed to load artists</p>
            )}
            {!artistsLoading && !artistsError && filteredArtists.length === 0 && (
              <p className="text-[11px] text-muted-foreground p-4">No artists found</p>
            )}
            {!artistsLoading && !artistsError && filteredArtists.map((artist: ArtistListItem) => (
              <button
                key={artist.id}
                onClick={() => setSelectedId(artist.id)}
                className={`w-full text-left px-4 py-2.5 border-b border-white/[0.03] transition-colors hover:bg-white/[0.03] ${
                  selectedId === artist.id ? 'bg-primary/5 border-l-2 border-l-primary' : ''
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="text-[13px] font-medium text-foreground truncate">{artist.name}</span>
                  {artist.score && (
                    <span className={`text-xs font-bold ml-2 ${scoreColor(artist.score)}`}>
                      {artist.score}
                    </span>
                  )}
                </div>
                <div className="flex items-center gap-2 mt-0.5">
                  <span className="text-[10px] text-muted-foreground truncate">
                    {artist.genres?.slice(0, 2).join(', ') ?? 'Unknown'}
                  </span>
                  {artist.country && (
                    <>
                      <span className="text-[10px] text-muted-foreground">·</span>
                      <span className="text-[10px] text-muted-foreground">{artist.country}</span>
                    </>
                  )}
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* ── Intelligence Detail (Right Panel) ── */}
        <div className="flex-1 overflow-y-auto p-5">
          {!selectedId && (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <BrainCircuit className="w-10 h-10 text-muted-foreground/20 mb-4" />
              <h3 className="text-sm font-semibold text-muted-foreground">Select an artist</h3>
              <p className="text-[11px] text-muted-foreground/60 mt-1">
                Choose an artist from the list to view their intelligence profile
              </p>
            </div>
          )}

          {intelligenceLoading && selectedId && (
            <div className="flex items-center justify-center h-full">
              <Loader2 className="w-5 h-5 animate-spin text-primary" />
            </div>
          )}

          {intelligenceError && selectedId && (
            <div className="flex flex-col items-center justify-center h-full">
              <AlertTriangle className="w-8 h-8 text-rose-400 mb-3" />
              <p className="text-sm text-rose-400">Failed to load intelligence data</p>
            </div>
          )}

          {intelligenceData && !intelligenceLoading && (
            <div className="space-y-5 max-w-4xl">
              {/* ── Artist Header ── */}
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-3">
                    <h1 className="text-xl font-bold tracking-tight">
                      {intelligenceData.artist.name}
                    </h1>
                    <span className={`text-2xl font-black ${scoreColor(intelligenceData.aggregate.score)}`}>
                      {intelligenceData.aggregate.score}
                      <span className="text-xs text-muted-foreground font-normal">/100</span>
                    </span>
                  </div>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-xs text-muted-foreground">
                      {intelligenceData.artist.genres?.slice(0, 3).join(', ') ?? 'Unknown genre'}
                    </span>
                    {intelligenceData.artist.country && (
                      <>
                        <span className="text-xs text-muted-foreground">·</span>
                        <span className="text-xs text-muted-foreground">{intelligenceData.artist.country}</span>
                      </>
                    )}
                    <span className="text-xs text-muted-foreground">·</span>
                    <span className="text-xs text-muted-foreground">
                      {intelligenceData.aggregate.scoresComputed} scores computed
                    </span>
                  </div>
                </div>
                <div className="text-right text-[10px] text-muted-foreground">
                  <p>v{intelligenceData.metadata.version}</p>
                  <p>{new Date(intelligenceData.metadata.computedAt).toLocaleString()}</p>
                </div>
              </div>

              {/* ── Aggregate Stats ── */}
              <div className="grid grid-cols-4 gap-3">
                <div className="rounded-lg bg-white/[0.03] border border-white/5 p-3">
                  <span className="text-[10px] uppercase tracking-wider text-muted-foreground">Overall Score</span>
                  <p className={`text-lg font-bold ${scoreColor(intelligenceData.aggregate.score)}`}>
                    {intelligenceData.aggregate.score}
                    <span className="text-xs text-muted-foreground font-normal">/100</span>
                  </p>
                </div>
                <div className="rounded-lg bg-white/[0.03] border border-white/5 p-3">
                  <span className="text-[10px] uppercase tracking-wider text-muted-foreground">Confidence</span>
                  <p className="text-lg font-bold text-primary">{intelligenceData.aggregate.confidence}%</p>
                </div>
                <div className="rounded-lg bg-white/[0.03] border border-white/5 p-3">
                  <span className="text-[10px] uppercase tracking-wider text-muted-foreground">Scores Active</span>
                  <p className="text-lg font-bold text-foreground">{intelligenceData.aggregate.scoresComputed}</p>
                </div>
                <div className="rounded-lg bg-white/[0.03] border border-white/5 p-3">
                  <span className="text-[10px] uppercase tracking-wider text-muted-foreground">Scores Skipped</span>
                  <p className="text-lg font-bold text-foreground">{intelligenceData.aggregate.scoresSkipped}</p>
                </div>
              </div>

              {/* ── Score Cards Grid ── */}
              <div>
                <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">
                  Intelligence Scores
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                  {intelligenceData.scores.map((score: ScoreItem) => (
                    <ScoreCard key={score.id} score={score} />
                  ))}
                </div>
              </div>

              {/* ── Insights ── */}
              {intelligenceData.insights.items.length > 0 && (
                <div>
                  <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">
                    Intelligence Insights
                  </h3>
                  {intelligenceData.insights.summary.length > 0 && (
                    <div className="mb-3 p-3 rounded-lg bg-primary/5 border border-primary/10">
                      {intelligenceData.insights.summary.map((s: string, i: number) => (
                        <p key={i} className="text-[12px] text-foreground/80 leading-relaxed">{s}</p>
                      ))}
                    </div>
                  )}
                  <div className="space-y-1.5">
                    {intelligenceData.insights.items.map((insight: InsightItem, i: number) => (
                      <InsightRow key={i} insight={insight} />
                    ))}
                  </div>
                </div>
              )}

              {/* ── Feature Summary ── */}
              {intelligenceData.features.platforms.length > 0 && (
                <div>
                  <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">
                    Feature Sources
                  </h3>
                  <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2">
                    {intelligenceData.features.platforms.map((f: { name: string; value: number; quality: number; provider: string; source: string }) => (
                      <div key={f.name} className="rounded-md bg-white/[0.02] border border-white/5 p-2.5">
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-[10px] font-medium text-muted-foreground capitalize">{f.name}</span>
                          <span className="text-[10px] text-foreground/80">{f.value.toLocaleString()}</span>
                        </div>
                        <div className="flex items-center gap-1.5">
                          <div className="flex-1 h-1 rounded-full bg-muted">
                            <div
                              className={`h-full rounded-full ${confidenceBar(f.quality * 100)}`}
                              style={{ width: `${f.quality * 100}%` }}
                            />
                          </div>
                          <span className="text-[9px] text-muted-foreground">{f.provider}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </DashboardLayout>
  );
}
