// ───────────────────────────────────────────────
// SIGNAL — Public Intelligence Report
// THE product surface of SIGNAL.
// URL: /intelligence/[artistId]
// Public, shareable, zero-code understandable.
// ───────────────────────────────────────────────
'use client';

import { use, useEffect, useState } from 'react';
import useSWR from 'swr';

// ── Icons ──
const Icons = {
  spotify: () => (
    <svg viewBox="0 0 24 24" className="w-4 h-4 fill-current"><path d="M12 0C5.4 0 0 5.4 0 12s5.4 12 12 12 12-5.4 12-12S18.66 0 12 0zm5.521 17.34c-.24.359-.66.48-1.021.24-2.82-1.74-6.36-2.101-10.561-1.141-.418.122-.779-.179-.899-.539-.12-.421.18-.78.54-.9 4.56-1.021 8.52-.6 11.64 1.32.42.18.479.659.301 1.02zm1.44-3.3c-.301.42-.841.6-1.262.3-3.239-1.98-8.159-2.58-11.939-1.38-.479.12-1.02-.12-1.14-.6-.12-.48.12-1.021.6-1.141C9.6 9.9 15 10.561 18.72 12.84c.361.181.54.78.241 1.2zm.12-3.36C15.24 8.4 8.82 8.16 5.16 9.301c-.6.179-1.2-.181-1.38-.721-.18-.601.18-1.2.72-1.381 4.26-1.26 11.28-1.02 15.721 1.621.539.3.719 1.02.419 1.56-.299.421-1.02.599-1.559.3z"/></svg>
  ),
  youtube: () => (
    <svg viewBox="0 0 24 24" className="w-4 h-4 fill-current"><path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/></svg>
  ),
  instagram: () => (
    <svg viewBox="0 0 24 24" className="w-4 h-4 fill-current"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 1 0 0 12.324 6.162 6.162 0 0 0 0-12.324zM12 16a4 4 0 1 1 0-8 4 4 0 0 1 0 8zm6.406-11.845a1.44 1.44 0 1 0 0 2.881 1.44 1.44 0 0 0 0-2.881z"/></svg>
  ),
  tiktok: () => (
    <svg viewBox="0 0 24 24" className="w-4 h-4 fill-current"><path d="M12.525.02c1.31-.02 2.61-.01 3.91-.02.08 1.53.63 3.09 1.75 4.17 1.12 1.11 2.7 1.62 4.24 1.79v4.03c-1.44-.05-2.89-.35-4.2-.97-.57-.26-1.1-.59-1.62-.93-.01 2.92.01 5.84-.02 8.75-.08 1.4-.54 2.79-1.35 3.94-1.31 1.92-3.58 3.17-5.91 3.21-1.43.08-2.86-.31-4.08-1.03-2.02-1.19-3.44-3.37-3.65-5.71-.02-.5-.03-1-.01-1.49.18-1.9 1.12-3.72 2.58-4.96 1.66-1.44 3.98-2.13 6.15-1.72.02 1.48-.04 2.96-.04 4.44-.99-.32-2.15-.23-3.02.37-.63.41-1.11 1.04-1.36 1.75-.21.51-.15 1.07-.14 1.61.24 1.64 1.82 3.02 3.5 2.87 1.12-.01 2.19-.66 2.77-1.61.19-.33.4-.67.41-1.06.1-1.79.06-3.57.07-5.36.01-4.03-.01-8.05.02-12.07z"/></svg>
  ),
  appleMusic: () => (
    <svg viewBox="0 0 24 24" className="w-4 h-4 fill-current"><path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm4.5 17.66a.75.75 0 0 1-.75.75c-.06 0-.12-.01-.18-.03a10.5 10.5 0 0 0-3.12-.5c-1.4 0-2.78.27-4.06.79a.75.75 0 0 1-.6-1.37c1.5-.66 3.1-1 4.66-1 .97 0 1.94.13 2.88.38a.75.75 0 0 1-.83.98zm1.28-3.14a.75.75 0 0 1-.75.75c-.06 0-.12-.01-.18-.03A15 15 0 0 0 12 14.25c-1.85 0-3.68.28-5.44.84a.75.75 0 0 1-.5-1.41c1.97-.7 3.99-1.05 5.94-1.05 1.2 0 2.4.14 3.57.42a.75.75 0 0 1-.83.98zm.12-3.27a.75.75 0 0 1-.75.75h-.01c-.06 0-.12-.01-.18-.03a18 18 0 0 0-4.02-.47c-2.3 0-4.57.4-6.75 1.2a.75.75 0 0 1-.5-1.41c2.4-.86 4.9-1.29 7.25-1.29 1.55 0 3.1.17 4.63.52a.75.75 0 0 1-.67.73z"/></svg>
  ),
  link: () => (
    <svg viewBox="0 0 24 24" className="w-3.5 h-3.5 fill-current"><path d="M15 7h3a5 5 0 0 1 0 10h-3m-6 0H6a5 5 0 0 1 0-10h3m-1 5h8" stroke="currentColor" strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round"/></svg>
  ),
  check: () => (
    <svg viewBox="0 0 24 24" className="w-3.5 h-3.5 fill-none" stroke="currentColor" strokeWidth="2.5"><polyline points="20 6 9 17 4 12"/></svg>
  ),
};

// ── Fetch ──
const fetcher = (url: string) => fetch(url).then(r => r.json());

// ── Score Color ──
function getScoreColor(score: number): string {
  if (score >= 75) return 'text-green-400';
  if (score >= 55) return 'text-yellow-400';
  return 'text-rose-400';
}

function getScoreRingColor(score: number): string {
  if (score >= 75) return '#22c55e';
  if (score >= 55) return '#eab308';
  return '#f43f5e';
}

function getScoreLabel(score: number): string {
  if (score >= 85) return 'Exceptional';
  if (score >= 75) return 'Strong';
  if (score >= 65) return 'Good';
  if (score >= 55) return 'Stable';
  if (score >= 40) return 'Developing';
  return 'Needs Attention';
}

// ── SVG Score Ring ──
function ScoreRing({ score, size = 180, strokeWidth = 10 }: { score: number; size?: number; strokeWidth?: number }) {
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const offset = circumference - (score / 100) * circumference;
  const color = getScoreRingColor(score);

  return (
    <svg width={size} height={size} className="transform -rotate-90 drop-shadow-[0_0_20px_rgba(59,130,246,0.15)]">
      {/* Background ring */}
      <circle
        cx={size / 2}
        cy={size / 2}
        r={radius}
        stroke="currentColor"
        strokeWidth={strokeWidth}
        fill="none"
        className="text-white/5"
      />
      {/* Progress ring */}
      <circle
        cx={size / 2}
        cy={size / 2}
        r={radius}
        stroke={color}
        strokeWidth={strokeWidth}
        fill="none"
        strokeDasharray={circumference}
        strokeDashoffset={offset}
        strokeLinecap="round"
        className="transition-all duration-1000 ease-out"
        style={{ filter: `drop-shadow(0 0 8px ${color}40)` }}
      />
    </svg>
  );
}

// ── Helper: Platform Icons ──
function PlatformIcon({ name }: { name: string }) {
  const key = name.toLowerCase();
  if (key === 'spotify') return <Icons.spotify />;
  if (key === 'youtube') return <Icons.youtube />;
  if (key === 'instagram') return <Icons.instagram />;
  if (key === 'tiktok') return <Icons.tiktok />;
  if (key === 'applemusic' || key === 'appleMusic') return <Icons.appleMusic />;
  return null;
}

function PlatformTag({ name }: { name: string }) {
  const display = name === 'appleMusic' ? 'Apple Music' : name.charAt(0).toUpperCase() + name.slice(1);
  return (
    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-white/[0.04] border border-white/[0.06] text-[11px] font-medium text-muted-foreground">
      <PlatformIcon name={name} />
      {display}
    </span>
  );
}

// ── Skeleton ──
function Skeleton({ className = '' }: { className?: string }) {
  return <div className={`animate-pulse rounded-md bg-white/[0.04] ${className}`} />;
}

// ── Loading State ──
function LoadingPage() {
  return (
    <main className="min-h-screen bg-[#080808]">
      {/* Nav skeleton */}
      <div className="flex items-center justify-between px-5 py-4 border-b border-white/[0.04]">
        <div className="flex items-center gap-2.5">
          <Skeleton className="w-7 h-7 rounded-lg" />
          <Skeleton className="w-20 h-4" />
        </div>
        <Skeleton className="w-24 h-8 rounded-full" />
      </div>

      <div className="max-w-4xl mx-auto px-5 py-12 space-y-16">
        {/* Hero skeleton */}
        <div className="flex flex-col items-center text-center space-y-4">
          <Skeleton className="w-24 h-24 rounded-full" />
          <Skeleton className="w-48 h-8" />
          <Skeleton className="w-64 h-4" />
          <div className="flex gap-2"><Skeleton className="w-20 h-6 rounded-full" /><Skeleton className="w-24 h-6 rounded-full" /></div>
        </div>

        {/* Score ring skeleton */}
        <div className="flex flex-col items-center space-y-4">
          <Skeleton className="w-44 h-44 rounded-full" />
          <Skeleton className="w-32 h-6" />
          <Skeleton className="w-48 h-4" />
        </div>

        {/* Score cards skeleton */}
        <div className="space-y-4">
          <Skeleton className="w-36 h-5" />
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="rounded-xl border border-white/[0.06] p-4 space-y-3">
                <Skeleton className="w-20 h-3" />
                <div className="flex justify-between">
                  <Skeleton className="w-24 h-4" />
                  <Skeleton className="w-10 h-6" />
                </div>
                <Skeleton className="w-full h-2" />
              </div>
            ))}
          </div>
        </div>

        {/* Insights skeleton */}
        <div className="space-y-4">
          <Skeleton className="w-32 h-5" />
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="rounded-xl border border-white/[0.06] p-4 space-y-2">
              <Skeleton className="w-20 h-3" />
              <Skeleton className="w-full h-4" />
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}

// ── Error State ──
function ErrorPage({ artistId, error }: { artistId: string; error: Error }) {
  return (
    <main className="min-h-screen bg-[#080808] flex items-center justify-center p-5">
      <div className="text-center max-w-md">
        <div className="w-16 h-16 mx-auto mb-6 rounded-full bg-rose-500/10 border border-rose-500/20 flex items-center justify-center">
          <svg className="w-7 h-7 text-rose-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
        </div>
        <h1 className="text-xl font-semibold text-foreground mb-2">Intelligence Report Unavailable</h1>
        <p className="text-sm text-muted-foreground mb-6">
          We could not load the intelligence profile for this artist. The report may not exist or the service is temporarily unavailable.
        </p>
        <div className="flex items-center justify-center gap-3">
          <button
            onClick={() => window.location.reload()}
            className="px-5 py-2.5 rounded-full bg-primary text-white text-sm font-medium hover:bg-primary/90 transition-colors"
          >
            Try Again
          </button>
          <a
            href="/"
            className="px-5 py-2.5 rounded-full border border-white/[0.1] text-sm text-muted-foreground hover:text-foreground transition-colors"
          >
            Go Home
          </a>
        </div>
        {process.env.NODE_ENV === 'development' && (
          <p className="mt-6 text-[11px] text-muted-foreground/50 font-mono">{error.message}</p>
        )}
      </div>
    </main>
  );
}

// ── Main Page ──

export default function IntelligencePage({
  params,
}: {
  params: Promise<{ artistId: string }>;
}) {
  const { artistId } = use(params);
  const [copied, setCopied] = useState(false);

  const { data, error, isLoading } = useSWR(
    `/api/v1/intelligence/${artistId}`,
    fetcher,
    { revalidateOnFocus: false, revalidateOnReconnect: false }
  );

  // ── Copy Link ──
  const handleCopyLink = () => {
    if (typeof window === 'undefined') return;
    navigator.clipboard.writeText(window.location.href).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  // Loading
  if (isLoading) return <LoadingPage />;
  // Error
  if (error) return <ErrorPage artistId={artistId} error={error} />;
  // No data
  if (!data) return <LoadingPage />;

  const { artist, aggregate, scores, insights, features, metadata } = data;

  // Derive platforms from features summary
  const platforms: string[] = features?.summary?.platforms ?? [];
  const followers = features?.summary?.followers ?? 0;
  const monthlyListeners = features?.summary?.monthlyListeners ?? 0;

  // Derived stats
  const totalScores = scores?.length ?? 0;
  const validScores = scores?.filter((s: { valid: boolean }) => s.valid).length ?? 0;

  // ── Render ──
  return (
    <main className="min-h-screen bg-[#080808] text-foreground antialiased">
      {/* ═══════ NAV ═══════ */}
      <nav className="sticky top-0 z-50 backdrop-blur-xl bg-[#080808]/80 border-b border-white/[0.04]">
        <div className="max-w-4xl mx-auto flex items-center justify-between px-5 py-3.5">
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded-lg signal-gradient flex items-center justify-center">
              <span className="text-white text-xs font-black tracking-tight">S</span>
            </div>
            <span className="font-semibold text-sm tracking-tight">SIGNAL</span>
          </div>
          <button
            onClick={handleCopyLink}
            className="inline-flex items-center gap-1.5 px-4 py-2 rounded-full border border-white/[0.1] text-xs font-medium text-muted-foreground hover:text-foreground hover:border-white/20 transition-all active:scale-95"
          >
            {copied ? (
              <><Icons.check /> Copied</>
            ) : (
              <><Icons.link /> Copy Link</>
            )}
          </button>
        </div>
      </nav>

      {/* ═══════ CONTENT ═══════ */}
      <div className="max-w-4xl mx-auto px-5 pt-12 pb-24 space-y-20">

        {/* ─── 1. HERO ─── */}
        <section className="flex flex-col items-center text-center animate-fade-in">
          {/* Avatar */}
          {artist.image ? (
            <img
              src={artist.image}
              alt={artist.name}
              className="w-24 h-24 rounded-full object-cover ring-2 ring-white/[0.08] mb-5 shadow-2xl"
            />
          ) : (
            <div className="w-24 h-24 rounded-full bg-white/[0.04] border border-white/[0.08] flex items-center justify-center mb-5">
              <span className="text-3xl font-bold text-muted-foreground/30">{artist.name.charAt(0)}</span>
            </div>
          )}

          <h1 className="text-3xl sm:text-4xl font-bold tracking-tight text-foreground">{artist.name}</h1>

          <div className="flex flex-wrap items-center justify-center gap-2 mt-3">
            {artist.genres?.slice(0, 4).map((g: string) => (
              <span key={g} className="px-3 py-1 rounded-full bg-white/[0.04] border border-white/[0.06] text-[12px] text-muted-foreground">
                {g}
              </span>
            ))}
          </div>

          {/* Platform tags */}
          {platforms.length > 0 && (
            <div className="flex flex-wrap items-center justify-center gap-2 mt-4">
              {platforms.map((p: string) => (
                <PlatformTag key={p} name={p} />
              ))}
            </div>
          )}

          {/* Metadata */}
          <p className="text-[11px] text-muted-foreground/50 mt-4">
            Report generated {metadata?.computedAt ? new Date(metadata.computedAt).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit' }) : 'recently'}
          </p>
        </section>

        {/* ─── 2. CORE SCORE ─── */}
        <section className="flex flex-col items-center text-center animate-fade-in-up">
          <div className="relative">
            <ScoreRing score={aggregate.score} size={200} strokeWidth={12} />
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <span className={`text-5xl sm:text-6xl font-black tracking-tight ${getScoreColor(aggregate.score)}`}>
                {aggregate.score}
              </span>
              <span className="text-[11px] text-muted-foreground mt-1">/ 100</span>
            </div>
          </div>

          <h2 className={`text-lg font-semibold mt-4 ${getScoreColor(aggregate.score)}`}>
            {getScoreLabel(aggregate.score)}
          </h2>

          <p className="text-sm text-muted-foreground mt-1 max-w-md">
            Overall intelligence score across {aggregate.scoresComputed} dimensions
            {aggregate.scoresSkipped > 0 && ` (${aggregate.scoresSkipped} unavailable)`}
          </p>

          {/* Mini stats */}
          <div className="flex items-center gap-6 mt-5">
            <div className="text-center">
              <span className="text-sm font-semibold text-foreground">{aggregate.confidence}%</span>
              <p className="text-[10px] text-muted-foreground uppercase tracking-wider mt-0.5">Confidence</p>
            </div>
            <div className="w-px h-8 bg-white/[0.06]" />
            <div className="text-center">
              <span className="text-sm font-semibold text-foreground">{validScores}/{totalScores}</span>
              <p className="text-[10px] text-muted-foreground uppercase tracking-wider mt-0.5">Scores Active</p>
            </div>
            {followers > 0 && (
              <>
                <div className="w-px h-8 bg-white/[0.06]" />
                <div className="text-center">
                  <span className="text-sm font-semibold text-foreground">{followers.toLocaleString()}</span>
                  <p className="text-[10px] text-muted-foreground uppercase tracking-wider mt-0.5">Followers</p>
                </div>
              </>
            )}
          </div>
        </section>

        {/* ─── 3. SCORE BREAKDOWN ─── */}
        <section className="animate-fade-in-up">
          <div className="mb-6">
            <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-[0.15em]">Intelligence Scores</h3>
            <p className="text-sm text-muted-foreground/70 mt-1">10 AI-powered scores evaluating the artist across growth, audience, commercial, discovery, and performance dimensions.</p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {scores?.map((score: {
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
            }) => {
              const barColor = score.valid ? getScoreRingColor(score.score) : '#ffffff10';

              return (
                <div
                  key={score.id}
                  className="group rounded-xl border border-white/[0.06] bg-white/[0.015] p-4 hover:bg-white/[0.025] hover:border-white/[0.1] transition-all duration-200"
                >
                  {/* Header */}
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-[10px] font-medium text-muted-foreground uppercase tracking-wider">{score.category}</span>
                    {score.valid && score.trend && (
                      <span className={`text-[10px] ${
                        score.trend === 'up' ? 'text-green-400' :
                        score.trend === 'down' ? 'text-rose-400' :
                        'text-muted-foreground'
                      }`}>
                        {score.trend === 'up' ? '↑' : score.trend === 'down' ? '↓' : '→'}
                      </span>
                    )}
                  </div>

                  {/* Score value + name */}
                  <div className="flex items-end justify-between mb-2">
                    <span className="text-sm font-semibold text-foreground">{score.name}</span>
                    <span className={`text-xl font-bold ${score.valid ? getScoreColor(score.score) : 'text-muted-foreground/30'}`}>
                      {score.valid ? score.score : '—'}
                    </span>
                  </div>

                  {/* Mini bar */}
                  <div className="w-full h-1.5 rounded-full bg-white/[0.04] mb-2 overflow-hidden">
                    <div
                      className="h-full rounded-full transition-all duration-700 ease-out"
                      style={{ width: `${score.valid ? score.score : 0}%`, backgroundColor: barColor }}
                    />
                  </div>

                  {/* Summary */}
                  {score.valid && (
                    <p className="text-[11px] text-muted-foreground/70 leading-relaxed line-clamp-2 group-hover:line-clamp-3 transition-all">
                      {score.summary}
                    </p>
                  )}
                  {!score.valid && (
                    <p className="text-[11px] text-rose-400/70 italic">{score.validationMessage || 'Unavailable'}</p>
                  )}

                  {/* Hover detail: factors */}
                  {score.valid && score.factors && score.factors.length > 0 && (
                    <div className="mt-2 pt-2 border-t border-white/[0.04] hidden group-hover:block animate-fade-in">
                      <span className="text-[9px] font-medium text-muted-foreground uppercase tracking-wider">Key Factors</span>
                      <div className="space-y-1 mt-1">
                        {score.factors.slice(0, 3).map((f, i) => (
                          <div key={i} className="flex items-center justify-between text-[10px]">
                            <span className="text-foreground/60 truncate mr-2">{f.name}</span>
                            <span className={`shrink-0 ${f.direction === 'positive' ? 'text-green-400' : 'text-rose-400'}`}>
                              {f.direction === 'positive' ? '+' : ''}{f.impact.toFixed(1)}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Confidence indicator */}
                  <div className="flex items-center gap-1.5 mt-2">
                    <div className="flex-1 h-0.5 rounded-full bg-white/[0.04]">
                      <div
                        className="h-full rounded-full bg-primary/40"
                        style={{ width: `${score.confidence}%` }}
                      />
                    </div>
                    <span className="text-[9px] text-muted-foreground">{score.confidence}%</span>
                  </div>
                </div>
              );
            })}
          </div>
        </section>

        {/* ─── 4. INSIGHTS PANEL ─── */}
        {insights?.items?.length > 0 && (
          <section className="animate-fade-in-up">
            <div className="mb-6">
              <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-[0.15em]">AI Insights</h3>
              <p className="text-sm text-muted-foreground/70 mt-1">Key signals detected across the artist&apos;s intelligence profile.</p>
            </div>

            {/* Summary highlight */}
            {insights.summary?.length > 0 && (
              <div className="mb-4 p-4 rounded-xl bg-primary/5 border border-primary/10">
                <div className="flex items-start gap-3">
                  <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center shrink-0 mt-0.5">
                    <svg className="w-4 h-4 text-primary" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/>
                    </svg>
                  </div>
                  <div className="space-y-1">
                    {insights.summary.map((s: string, i: number) => (
                      <p key={i} className="text-sm text-foreground/90 leading-relaxed">{s}</p>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Insight items */}
            <div className="space-y-2">
              {insights.items.map((item: {
                type: string;
                message: string;
                severity: string;
                category: string;
                source: string;
              }, i: number) => {
                const borderColor =
                  item.type === 'growth' ? 'border-l-green-500/40' :
                  item.type === 'risk' ? 'border-l-rose-500/40' :
                  item.type === 'opportunity' ? 'border-l-amber-500/40' :
                  item.type === 'achievement' ? 'border-l-primary/40' :
                  'border-l-amber-500/40';

                const dotColor =
                  item.type === 'growth' ? 'bg-green-400' :
                  item.type === 'risk' ? 'bg-rose-400' :
                  item.type === 'opportunity' ? 'bg-amber-400' :
                  item.type === 'achievement' ? 'bg-primary' :
                  'bg-amber-400';

                return (
                  <div
                    key={i}
                    className={`flex items-start gap-3 p-3.5 rounded-xl border border-white/[0.04] bg-white/[0.015] border-l-2 ${borderColor}`}
                  >
                    <div className={`w-2 h-2 rounded-full ${dotColor} mt-1.5 shrink-0`} />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-0.5">
                        <span className="text-[10px] font-medium uppercase tracking-wider text-muted-foreground">{item.category}</span>
                        <span className={`text-[9px] px-1.5 py-0.5 rounded-full ${
                          item.severity === 'high' ? 'bg-rose-500/10 text-rose-400' :
                          item.severity === 'medium' ? 'bg-amber-500/10 text-amber-400' :
                          'bg-muted text-muted-foreground'
                        }`}>
                          {item.severity}
                        </span>
                      </div>
                      <p className="text-sm text-foreground/80 leading-relaxed">{item.message}</p>
                    </div>
                  </div>
                );
              })}
            </div>
          </section>
        )}

        {/* ─── 5. FEATURE IMPACT ─── */}
        {features?.platforms?.length > 0 && (
          <section className="animate-fade-in-up">
            <div className="mb-6">
              <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-[0.15em]">Feature Sources</h3>
              <p className="text-sm text-muted-foreground/70 mt-1">Data quality and provenance for each feature used in scoring.</p>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2">
              {features.platforms.map((f: {
                name: string;
                value: number;
                quality: number;
                provider: string;
                source: string;
              }) => (
                <div key={f.name} className="rounded-xl border border-white/[0.04] bg-white/[0.015] p-3">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-[10px] font-medium text-muted-foreground capitalize">{f.name.replace(/([A-Z])/g, ' $1').trim()}</span>
                    <span className="text-[10px] font-semibold text-foreground/80">
                      {f.value >= 1000000
                        ? `${(f.value / 1000000).toFixed(1)}M`
                        : f.value >= 1000
                          ? `${(f.value / 1000).toFixed(1)}K`
                          : f.value.toLocaleString()}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="flex-1 h-1.5 rounded-full bg-white/[0.04]">
                      <div
                        className="h-full rounded-full transition-all"
                        style={{
                          width: `${f.quality * 100}%`,
                          backgroundColor: f.quality >= 0.7 ? '#22c55e' : f.quality >= 0.4 ? '#eab308' : '#f43f5e',
                        }}
                      />
                    </div>
                    <span className="text-[9px] text-muted-foreground capitalize">{f.provider}</span>
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* ─── 6. FOOTER ─── */}
        <footer className="border-t border-white/[0.04] pt-10 animate-fade-in">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2.5">
              <div className="w-6 h-6 rounded-md signal-gradient flex items-center justify-center">
                <span className="text-white text-[9px] font-black tracking-tight">S</span>
              </div>
              <div>
                <span className="text-xs font-semibold text-foreground">SIGNAL</span>
                <p className="text-[10px] text-muted-foreground">Music Intelligence by Abe Music Group</p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <button
                onClick={handleCopyLink}
                className="inline-flex items-center gap-1.5 px-4 py-2 rounded-full border border-white/[0.1] text-xs font-medium text-muted-foreground hover:text-foreground hover:border-white/20 transition-all active:scale-95"
              >
                {copied ? (
                  <><Icons.check /> Copied</>
                ) : (
                  <><Icons.link /> Copy Report Link</>
                )}
              </button>
            </div>
          </div>

          <p className="text-center text-[10px] text-muted-foreground/40 mt-6">
            SIGNAL v{metadata?.version ?? '3.5.0'} · AI-Powered Music Intelligence
          </p>
        </footer>

      </div>
    </main>
  );
}
