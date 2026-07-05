'use client';

import { useState } from 'react';
import useSWR from 'swr';
import { DashboardLayout } from '@/components/dashboard/layout';
import { ScoreRing } from '@/components/ui/score-ring';
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
  BarChart3,
  ChevronDown,
  ExternalLink,
  Share2,
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
  artist: { id: string; name: string; genres: string[]; country: string | null; image: string | null };
  scores: ScoreItem[];
  aggregate: { score: number; confidence: number; scoresComputed: number; scoresSkipped: number };
  features: { platforms: { name: string; value: number; quality: number; provider: string; source: string }[]; summary: Record<string, unknown> };
  insights: { items: InsightItem[]; summary: string[] };
  metadata: { computedAt: string; version: string };
}

interface ScoreItem {
  id: string; name: string; category: string; version: string;
  score: number; confidence: number; summary: string;
  factors: { name: string; impact: number; direction: string; reasoning: string }[];
  recommendations: string[]; dataQuality: string; trend: string;
  volatility: number; valid: boolean; validationMessage: string;
}

interface InsightItem {
  type: 'growth' | 'risk' | 'opportunity' | 'achievement' | 'warning';
  message: string; severity: 'high' | 'medium' | 'low';
  category: string; source: string;
}

// ── Category configuration ──

const categoryConfig: Record<string, { icon: React.ElementType; color: string; bgClass: string; borderClass: string }> = {
  growth: { icon: TrendingUp, color: '#22c55e', bgClass: 'bg-green-500/5 border-green-500/20', borderClass: 'border-l-green-500' },
  audience: { icon: Users, color: '#3B82F6', bgClass: 'bg-primary/5 border-primary/20', borderClass: 'border-l-primary' },
  commercial: { icon: Wallet, color: '#f59e0b', bgClass: 'bg-amber-500/5 border-amber-500/20', borderClass: 'border-l-amber-500' },
  discovery: { icon: Search, color: '#8b5cf6', bgClass: 'bg-purple-500/5 border-purple-500/20', borderClass: 'border-l-purple-500' },
  performance: { icon: Zap, color: '#06b6d4', bgClass: 'bg-cyan-500/5 border-cyan-500/20', borderClass: 'border-l-cyan-500' },
};

const insightConfig: Record<string, { icon: React.ElementType; color: string }> = {
  growth: { icon: TrendingUp, color: 'text-green-400' },
  risk: { icon: AlertTriangle, color: 'text-rose-400' },
  opportunity: { icon: Lightbulb, color: 'text-amber-400' },
  achievement: { icon: Award, color: 'text-primary' },
  warning: { icon: AlertTriangle, color: 'text-amber-400' },
};

function severityClass(severity: string): string {
  return severity === 'high' ? 'bg-rose-500/10 text-rose-400'
    : severity === 'medium' ? 'bg-amber-500/10 text-amber-400'
    : 'bg-muted text-muted-foreground';
}

// ── Score Card ──

function ScoreCard({ score }: { score: ScoreItem }) {
  const [expanded, setExpanded] = useState(false);
  const cat = categoryConfig[score.category] || categoryConfig.growth;

  return (
    <div
      className={`rounded-lg border ${cat.bgClass} p-3.5 transition-all duration-200 cursor-pointer ${
        expanded ? 'ring-1 ring-primary/20 shadow-md' : 'card-hover'
      }`}
      onClick={() => setExpanded(!expanded)}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <cat.icon className="w-4 h-4" style={{ color: cat.color }} />
          <span className="text-[10px] font-medium text-muted-foreground uppercase tracking-wider">{score.category}</span>
        </div>
        <div className="flex items-center gap-2">
          {score.valid && (
            <div className="flex items-center gap-1">
              <ScoreRing score={score.score} size={28} strokeWidth={2.5} animated={false} />
            </div>
          )}
          <ChevronRight className={`w-3.5 h-3.5 text-muted-foreground transition-transform ${expanded ? 'rotate-90' : ''}`} />
        </div>
      </div>

      {/* Name & confidence */}
      <div className="flex items-end justify-between">
        <div>
          <span className="text-sm font-semibold text-foreground">{score.name}</span>
          <div className="flex items-center gap-2 mt-0.5">
            <span className="text-[10px] text-muted-foreground">v{score.version}</span>
            <span className="text-[10px] text-muted-foreground">·</span>
            <span className="text-[10px] text-muted-foreground">{score.confidence}% confidence</span>
          </div>
        </div>
      </div>

      {/* Summary (collapsed) */}
      {!expanded && score.valid && (
        <p className="text-[11px] text-muted-foreground mt-2 line-clamp-2">{score.summary}</p>
      )}

      {/* Expanded content */}
      {expanded && score.valid && (
        <div className="mt-3 pt-3 border-t border-white/5 space-y-3 animate-fade-in">
          {/* Confidence bar */}
          <div className="flex items-center gap-2">
            <span className="text-[10px] text-muted-foreground">Data quality</span>
            <div className="flex-1 h-1 rounded-full bg-muted overflow-hidden">
              <div
                className="h-full rounded-full transition-all"
                style={{
                  width: `${score.confidence}%`,
                  background: score.confidence >= 70
                    ? 'linear-gradient(90deg, #22c55e, #10b981)'
                    : score.confidence >= 40
                      ? 'linear-gradient(90deg, #f59e0b, #eab308)'
                      : 'linear-gradient(90deg, #ef4444, #f97316)',
                }}
              />
            </div>
            <span className="text-[10px] font-medium tabular-nums">{score.confidence}%</span>
          </div>

          {/* Summary */}
          <p className="text-[11px] text-muted-foreground leading-relaxed">{score.summary}</p>

          {/* Factors */}
          {score.factors.length > 0 && (
            <div>
              <span className="text-[10px] font-medium text-muted-foreground uppercase tracking-wider">Key Factors</span>
              <div className="space-y-1.5 mt-1.5">
                {score.factors.map((f, i) => (
                  <div key={i} className="flex items-center gap-2">
                    {/* Factor bar */}
                    <div className="flex-1 h-5 rounded bg-muted/50 relative overflow-hidden">
                      <div
                        className={`h-full rounded transition-all duration-500 ${
                          f.direction === 'positive' ? 'bg-green-500/20' : 'bg-rose-500/20'
                        }`}
                        style={{ width: `${Math.abs(f.impact) * 10}%` }}
                      />
                      <span className="absolute inset-0 flex items-center px-2 text-[10px] text-foreground/70 truncate">
                        {f.name}
                      </span>
                    </div>
                    <span className={`text-[10px] font-bold tabular-nums shrink-0 ${
                      f.direction === 'positive' ? 'text-green-400' : 'text-rose-400'
                    }`}>
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
                    <span className="text-primary mt-0.5 shrink-0">·</span>
                    <span>{r}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Metadata */}
          <div className="flex items-center gap-3 text-[10px] text-muted-foreground pt-1">
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

// ── Insight Row ──

function InsightRow({ insight }: { insight: InsightItem }) {
  const config = insightConfig[insight.type] || insightConfig.opportunity;
  const Icon = config.icon;

  return (
    <div className="flex items-start gap-2.5 p-3 rounded-lg border-l-4 bg-white/[0.015] hover:bg-white/[0.03] transition-colors cursor-pointer"
      style={{ borderLeftColor: config.color === 'text-primary' ? 'hsl(217, 91%, 60%)' : config.color.replace('text-', '').includes('green') ? '#22c55e' : config.color.replace('text-', '').includes('rose') ? '#f43f5e' : '#f59e0b' }}
    >
      <div className="mt-0.5 shrink-0">
        <Icon className={`w-4 h-4 ${config.color}`} />
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className="text-[10px] font-medium uppercase tracking-wider text-muted-foreground">{insight.category}</span>
          <span className={`text-[10px] px-1.5 py-0.5 rounded-full ${severityClass(insight.severity)}`}>
            {insight.severity}
          </span>
        </div>
        <p className="text-xs text-foreground/80 mt-0.5 leading-relaxed">{insight.message}</p>
      </div>
    </div>
  );
}

// ── Main Dashboard Page ──

export default function IntelligenceDashboard() {
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  const { data: artistsData, error: artistsError, isLoading: artistsLoading } = useSWR('/api/v1/artists', fetcher);
  const { data: intelligenceData, error: intelligenceError, isLoading: intelligenceLoading } = useSWR(
    selectedId ? `/api/v1/intelligence/${selectedId}` : null,
    fetcher,
    { revalidateOnFocus: false }
  );

  const artists: ArtistListItem[] = artistsData?.artists ?? artistsData ?? [];
  const filteredArtists = searchQuery
    ? artists.filter((a: ArtistListItem) => a.name.toLowerCase().includes(searchQuery.toLowerCase()))
    : artists;
  const selectedArtist = artists.find((a: ArtistListItem) => a.id === selectedId);

  return (
    <DashboardLayout>
      <div className="flex h-full">
        {/* ── Artist List (Left Panel) ── */}
        <div className="w-72 border-r border-border flex flex-col flex-shrink-0">
          <div className="p-4 border-b border-border">
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
                className="w-full bg-muted/50 rounded-md pl-8 pr-3 py-1.5 text-xs text-foreground placeholder:text-muted-foreground/40 focus:outline-none focus:ring-1 focus:ring-primary/30 transition-all"
              />
            </div>
          </div>

          <div className="flex-1 overflow-y-auto">
            {artistsLoading && (
              <div className="flex items-center justify-center py-8"><Loader2 className="w-4 h-4 animate-spin text-muted-foreground" /></div>
            )}
            {artistsError && <p className="text-[11px] text-rose-400 p-4">Failed to load artists</p>}
            {!artistsLoading && !artistsError && filteredArtists.length === 0 && (
              <p className="text-[11px] text-muted-foreground p-4">No artists found</p>
            )}
            {!artistsLoading && !artistsError && filteredArtists.map((artist: ArtistListItem) => (
              <button
                key={artist.id}
                onClick={() => setSelectedId(artist.id)}
                className={`w-full text-left px-4 py-3 border-b border-white/[0.03] transition-all data-row ${
                  selectedId === artist.id ? 'bg-primary/5 border-l-2 border-l-primary' : ''
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2.5 min-w-0">
                    <div className="w-7 h-7 rounded-full bg-primary/10 flex items-center justify-center text-[10px] font-bold text-primary shrink-0 overflow-hidden ring-1 ring-border">
                      {artist.image ? (
                        <img src={artist.image} alt="" className="w-full h-full object-cover" />
                      ) : (
                        artist.name.charAt(0)
                      )}
                    </div>
                    <span className="text-[13px] font-medium text-foreground truncate">{artist.name}</span>
                  </div>
                  {artist.score && (
                    <ScoreRing score={artist.score} size={28} strokeWidth={2.5} animated={false} />
                  )}
                </div>
                <div className="flex items-center gap-2 mt-1 ml-9">
                  <span className="text-[10px] text-muted-foreground truncate">
                    {artist.genres?.slice(0, 2).join(', ') ?? 'Unknown'}
                  </span>
                  {artist.country && (
                    <>
                      <span className="text-[10px] text-muted-foreground">·</span>
                      <span className="text-[10px] text-muted-foreground">{artist.country}</span>
                    </>
                  )}
                  {artist.growth !== undefined && (
                    <>
                      <span className="text-[10px] text-muted-foreground">·</span>
                      <span className={`text-[10px] font-medium ${artist.growth >= 0 ? 'text-green-500' : 'text-rose-500'}`}>
                        {artist.growth >= 0 ? '+' : ''}{artist.growth}%
                      </span>
                    </>
                  )}
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* ── Intelligence Detail (Right Panel) ── */}
        <div className="flex-1 overflow-y-auto p-6">
          {!selectedId && (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <BrainCircuit className="w-12 h-12 text-muted-foreground/20 mb-4" />
              <h3 className="text-sm font-semibold text-muted-foreground">Select an artist</h3>
              <p className="text-[11px] text-muted-foreground/60 mt-1 max-w-[240px]">
                Choose an artist from the list to view their complete intelligence profile with scores, insights, and feature analysis
              </p>
            </div>
          )}

          {intelligenceLoading && selectedId && (
            <div className="flex items-center justify-center h-full">
              <Loader2 className="w-6 h-6 animate-spin text-primary" />
            </div>
          )}

          {intelligenceError && selectedId && (
            <div className="flex flex-col items-center justify-center h-full">
              <AlertTriangle className="w-8 h-8 text-rose-400 mb-3" />
              <p className="text-sm text-rose-400">Failed to load intelligence data</p>
            </div>
          )}

          {intelligenceData && !intelligenceLoading && (
            <div className="space-y-6 max-w-5xl">
              {/* ── Artist Header with Score Ring ── */}
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-4">
                  <ScoreRing
                    score={intelligenceData.aggregate.score}
                    size={88}
                    strokeWidth={5}
                    sublabel="/100"
                  />
                  <div>
                    <h1 className="text-2xl font-bold tracking-tight">
                      {intelligenceData.artist.name}
                    </h1>
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
                </div>
                <div className="flex items-center gap-2">
                  <button className="p-2 rounded-lg border border-border hover:bg-surface-hover transition-colors text-muted-foreground hover:text-foreground" title="Share">
                    <Share2 className="h-3.5 w-3.5" />
                  </button>
                  <div className="text-right text-[10px] text-muted-foreground leading-tight">
                    <p>v{intelligenceData.metadata.version}</p>
                    <p className="text-[9px]">{new Date(intelligenceData.metadata.computedAt).toLocaleDateString()}</p>
                  </div>
                </div>
              </div>

              {/* ── Aggregate Stats ── */}
              <div className="grid grid-cols-4 gap-3">
                <div className="rounded-lg bg-white/[0.02] border border-border p-3">
                  <span className="text-[10px] uppercase tracking-wider text-muted-foreground">Overall Score</span>
                  <p className={`text-lg font-bold mt-1 ${intelligenceData.aggregate.score >= 80 ? 'text-green-400' : intelligenceData.aggregate.score >= 60 ? 'text-primary' : intelligenceData.aggregate.score >= 40 ? 'text-amber-400' : 'text-rose-400'}`}>
                    {intelligenceData.aggregate.score}
                    <span className="text-xs text-muted-foreground font-normal">/100</span>
                  </p>
                </div>
                <div className="rounded-lg bg-white/[0.02] border border-border p-3">
                  <span className="text-[10px] uppercase tracking-wider text-muted-foreground">Confidence</span>
                  <p className="text-lg font-bold mt-1 text-primary">{intelligenceData.aggregate.confidence}%</p>
                  <div className="w-full h-1 rounded-full bg-muted mt-1.5 overflow-hidden">
                    <div className="h-full rounded-full bg-primary transition-all" style={{ width: `${intelligenceData.aggregate.confidence}%` }} />
                  </div>
                </div>
                <div className="rounded-lg bg-white/[0.02] border border-border p-3">
                  <span className="text-[10px] uppercase tracking-wider text-muted-foreground">Scores Active</span>
                  <p className="text-lg font-bold mt-1 text-foreground">{intelligenceData.aggregate.scoresComputed}</p>
                  <div className="flex items-center gap-1 mt-1">
                    <BarChart3 className="h-3 w-3 text-muted-foreground" />
                    <span className="text-[10px] text-muted-foreground">of {intelligenceData.aggregate.scoresComputed + intelligenceData.aggregate.scoresSkipped} total</span>
                  </div>
                </div>
                <div className="rounded-lg bg-white/[0.02] border border-border p-3">
                  <span className="text-[10px] uppercase tracking-wider text-muted-foreground">Scores Skipped</span>
                  <p className="text-lg font-bold mt-1 text-muted-foreground">{intelligenceData.aggregate.scoresSkipped}</p>
                  {intelligenceData.aggregate.scoresSkipped > 0 && (
                    <p className="text-[10px] text-amber-400 mt-1">Incomplete data</p>
                  )}
                </div>
              </div>

              {/* ── Score Cards Grid ── */}
              <div>
                <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3 flex items-center gap-2">
                  <Zap className="h-3.5 w-3.5 text-primary" />
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
                  <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3 flex items-center gap-2">
                    <Lightbulb className="h-3.5 w-3.5 text-primary" />
                    Intelligence Insights
                  </h3>
                  {intelligenceData.insights.summary.length > 0 && (
                    <div className="mb-3 p-3 rounded-lg bg-primary/5 border border-primary/10">
                      {intelligenceData.insights.summary.map((s: string, i: number) => (
                        <p key={i} className="text-xs text-foreground/80 leading-relaxed">{s}</p>
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

              {/* ── Feature Sources ── */}
              {intelligenceData.features.platforms.length > 0 && (
                <div>
                  <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3 flex items-center gap-2">
                    <Globe className="h-3.5 w-3.5 text-primary" />
                    Feature Sources
                  </h3>
                  <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2">
                    {intelligenceData.features.platforms.map((f: { name: string; value: number; quality: number; provider: string; source: string }) => (
                      <div key={f.name} className="rounded-md bg-white/[0.02] border border-border p-3 card-hover">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-[10px] font-medium text-muted-foreground capitalize">{f.name}</span>
                          <span className="text-[11px] font-bold tabular-nums text-foreground/80">{f.value.toLocaleString()}</span>
                        </div>
                        <div className="flex items-center gap-1.5">
                          <div className="flex-1 h-1.5 rounded-full bg-muted overflow-hidden">
                            <div
                              className="h-full rounded-full transition-all"
                              style={{
                                width: `${f.quality * 100}%`,
                                background: f.quality >= 0.7
                                  ? 'linear-gradient(90deg, #3B82F6, #22c55e)'
                                  : f.quality >= 0.4
                                    ? 'linear-gradient(90deg, #f59e0b, #eab308)'
                                    : 'linear-gradient(90deg, #ef4444, #f97316)',
                              }}
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
