'use client';

import {
  TrendingUp, TrendingDown, Minus, Plus, BrainCircuit, MessageCircle,
  ArrowUpRight, AlertTriangle, CheckCircle2, Target, Sparkles, Zap
} from 'lucide-react';
import useSWR from 'swr';

const fetcher = (url: string) => fetch(url).then(r => r.json());

function ScoreBar({ score, maxScore = 100 }: { score: number; maxScore?: number }) {
  const pct = Math.min((score / maxScore) * 100, 100);
  return (
    <div className="w-full h-1 rounded-full bg-muted overflow-hidden">
      <div
        className="h-full rounded-full transition-all duration-500"
        style={{
          width: `${pct}%`,
          background: pct >= 80
            ? 'linear-gradient(90deg, #3B82F6, #10b981)'
            : pct >= 60
              ? 'linear-gradient(90deg, #f59e0b, #3B82F6)'
              : 'linear-gradient(90deg, #ef4444, #f59e0b)',
        }}
      />
    </div>
  );
}

function TrendIndicator({ value }: { value: number }) {
  if (value > 0) return <TrendingUp className="h-3 w-3 text-green-500" />;
  if (value < 0) return <TrendingDown className="h-3 w-3 text-rose-500" />;
  return <Minus className="h-3 w-3 text-muted-foreground" />;
}

function getRecommendation(artist: any): { text: string; icon: typeof Zap; color: string } {
  const score = artist.score || 0;
  const growth = artist.growth || 0;
  const momentum = artist.momentum || 0;

  if (score >= 80 && growth > 5) {
    return { text: 'Initiate signing discussions', icon: Target, color: 'text-green-500' };
  }
  if (score >= 70 && growth > 0) {
    return { text: 'Schedule investment review', icon: TrendingUp, color: 'text-primary' };
  }
  if (score >= 60 && momentum > 40) {
    return { text: 'Monitor for growth acceleration', icon: Eye, color: 'text-amber-400' };
  }
  if (growth < -10) {
    return { text: 'Review performance strategy', icon: AlertTriangle, color: 'text-rose-500' };
  }
  return { text: 'Continue current cadence', icon: CheckCircle2, color: 'text-muted-foreground' };
}

function getOneSentenceSummary(artist: any): string {
  const score = artist.score || 0;
  const growth = artist.growth || 0;
  const momentum = artist.momentum || 0;

  const scoreDesc = score >= 80 ? 'Exceptional' : score >= 65 ? 'Strong' : score >= 50 ? 'Developing' : 'Early-stage';
  const growthDesc = growth > 15 ? 'rapid growth' : growth > 5 ? 'steady growth' : growth > -5 ? 'stable performance' : 'declining metrics';
  const momentumDesc = momentum > 60 ? 'with strong upward trajectory.' : momentum > 40 ? 'with positive momentum.' : '— maintaining position.';

  return `${scoreDesc} artist showing ${growthDesc} ${momentumDesc}`;
}

const Eye = ({ className }: { className?: string }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z" />
    <circle cx="12" cy="12" r="3" />
  </svg>
);

export function OpportunityPanel() {
  const { data, error, isLoading } = useSWR('/api/v1/analytics', fetcher);

  if (error) {
    return (
      <div className="kpi-card p-4">
        <p className="text-destructive text-xs flex items-center gap-2">
          <AlertTriangle className="h-3.5 w-3.5" />
          Failed to load opportunities
        </p>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="kpi-card animate-pulse overflow-hidden">
        <div className="px-4 pt-4 pb-3 border-b border-border">
          <div className="h-4 w-44 bg-muted rounded" />
          <div className="h-2.5 w-32 bg-muted rounded mt-1.5" />
        </div>
        <div>
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="flex items-center gap-4 px-4 py-3">
              <div className="w-5 h-3 bg-muted rounded" />
              <div className="w-9 h-9 rounded-full bg-muted" />
              <div className="flex-1 space-y-1">
                <div className="h-3.5 w-28 bg-muted rounded" />
                <div className="h-2.5 w-40 bg-muted rounded" />
              </div>
              <div className="h-3 w-14 bg-muted rounded" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  const artists = data?.topForSigning ?? [];

  if (!artists.length) {
    return (
      <div className="kpi-card text-center py-10">
        <div className="p-3 rounded-xl bg-muted inline-block mb-3">
          <Eye className="h-6 w-6 text-muted-foreground" />
        </div>
        <p className="text-sm font-medium mb-1">No Opportunities Yet</p>
        <p className="text-xs text-muted-foreground max-w-sm mx-auto leading-relaxed">
          Opportunities appear when SIGNAL identifies artists with strong scores,
          positive growth, and actionable potential. Start exploring the Discovery
          engine to build your portfolio.
        </p>
      </div>
    );
  }

  return (
    <div className="kpi-card overflow-hidden">
      <div className="px-4 pt-4 pb-3 border-b border-border">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-sm font-semibold tracking-tight">Top Opportunities</h2>
            <p className="text-[11px] text-muted-foreground mt-0.5">
              Ranked by investment potential across portfolio
            </p>
          </div>
          <span className="badge badge-blue text-[10px] gap-1">
            <Zap className="h-3 w-3" />
            {artists.length} active
          </span>
        </div>
      </div>

      <div>
        {artists.slice(0, 5).map((artist: {
          rank: number;
          name: string;
          score: number;
          growth: number;
          listeners?: number;
          dealEstimate?: number;
          momentum?: number;
          reason?: string;
          image?: string;
          photoUrl?: string;
          contact?: string;
        }, idx: number) => {
          const rec = getRecommendation(artist);
          const summary = getOneSentenceSummary(artist);
          const riskLevel = (artist.growth || 0) < -10 ? 'high' : (artist.score || 0) < 50 ? 'medium' : 'low';

          return (
            <div
              key={artist.rank}
              className="flex items-start gap-3 px-4 py-3 data-row group cursor-pointer animate-fade-in-up"
              style={{ animationDelay: `${idx * 80}ms` }}
            >
              {/* Rank */}
              <div className="flex flex-col items-center gap-0.5 w-6 shrink-0 pt-1">
                <span className="text-xs font-bold text-muted-foreground">{artist.rank}</span>
              </div>

              {/* Avatar */}
              <div className="w-9 h-9 rounded-full bg-primary/10 flex items-center justify-center text-xs font-bold overflow-hidden shrink-0 ring-1 ring-border">
                {(artist.photoUrl || artist.image) ? (
                  <img src={artist.photoUrl || artist.image} alt={artist.name} className="w-full h-full object-cover" />
                ) : (
                  <span className="text-sm font-bold text-primary">{artist.name.charAt(0)}</span>
                )}
              </div>

              {/* Content */}
              <div className="flex-1 min-w-0">
                {/* Name + badges row */}
                <div className="flex items-center gap-2 flex-wrap">
                  <p className="text-sm font-medium truncate">{artist.name}</p>
                  <span className={`text-[10px] font-medium tabular-nums ${
                    (artist.growth || 0) > 0 ? 'text-green-500' : (artist.growth || 0) < 0 ? 'text-rose-500' : 'text-muted-foreground'
                  }`}>
                    {(artist.growth || 0) > 0 ? '+' : ''}{artist.growth}%
                  </span>
                  {riskLevel === 'high' && (
                    <span className="badge badge-rose text-[9px] py-0 px-1.5">Risk</span>
                  )}
                </div>

                {/* One sentence summary */}
                <p className="text-[11px] text-muted-foreground mt-0.5 leading-relaxed">
                  {summary}
                </p>

                {/* Score bar + metrics row */}
                <div className="flex items-center gap-4 mt-2">
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-0.5">
                      <span className="text-[9px] text-muted-foreground uppercase tracking-wider">Potential</span>
                      <span className="text-[10px] font-semibold tabular-nums">{artist.score}</span>
                    </div>
                    <ScoreBar score={artist.score} />
                  </div>
                </div>

                {/* Recommendation + Next Action */}
                <div className="flex items-center gap-3 mt-2 flex-wrap">
                  <div className="flex items-center gap-1">
                    <rec.icon className={`h-3 w-3 ${rec.color}`} />
                    <span className={`text-[10px] font-medium ${rec.color}`}>{rec.text}</span>
                  </div>
                  {(artist.momentum || 0) > 0 && (
                    <div className="flex items-center gap-1">
                      <TrendIndicator value={artist.momentum || 0} />
                      <span className="text-[10px] text-muted-foreground">
                        Momentum: {artist.momentum}%
                      </span>
                    </div>
                  )}
                </div>
              </div>

              {/* Quick actions */}
              <div className="flex items-center gap-0.5 shrink-0 opacity-0 group-hover:opacity-100 transition-opacity pt-1">
                <button className="p-1.5 rounded-md hover:bg-surface-hover text-muted-foreground hover:text-primary transition-all" title="View intelligence">
                  <BrainCircuit className="h-3.5 w-3.5" />
                </button>
                <button className="p-1.5 rounded-md hover:bg-surface-hover text-muted-foreground hover:text-primary transition-all" title="Contact">
                  <MessageCircle className="h-3.5 w-3.5" />
                </button>
                <button className="p-1.5 rounded-md hover:bg-surface-hover text-muted-foreground hover:text-primary transition-all" title="Add to portfolio">
                  <Plus className="h-3.5 w-3.5" />
                </button>
              </div>
            </div>
          );
        })}
      </div>

      <div className="p-3 border-t border-border">
        <button className="w-full text-center text-xs text-muted-foreground hover:text-foreground transition-colors group flex items-center justify-center gap-1">
          View Full Portfolio <ArrowUpRight className="h-3 w-3 inline-block transition-transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5" />
        </button>
      </div>
    </div>
  );
}
