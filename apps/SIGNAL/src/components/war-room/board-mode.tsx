'use client';

import { useState } from 'react';
import useSWR from 'swr';
import {
  Monitor, ArrowLeft, ArrowRight, Maximize2, Minimize2, Download,
  FileText, Star, TrendingUp, Target, Shield, Sparkles,
  CheckCircle, AlertTriangle, X, Menu, Loader2, HelpCircle,
} from 'lucide-react';

const fetcher = (url: string) => fetch(url).then(r => {
  if (!r.ok) throw new Error('Failed to load');
  return r.json();
});

interface BoardModeProps {
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

function generateSlides(data: WarRoomData) {
  const { artist, dealBreakdown, growthData, teamMembers, alerts } = data;

  const projectedRevenue = Math.round(artist.listeners * 0.004 * 12 * (1 + artist.growth / 100));
  const totalInvestment = dealBreakdown.total;
  const roi = totalInvestment > 0 ? Math.round((projectedRevenue - totalInvestment) / totalInvestment * 100) : 0;
  const breakEvenMonths = projectedRevenue > 0 ? Math.ceil(totalInvestment / (projectedRevenue / 12)) : 0;
  const genreGrowth = growthData.length >= 2
    ? Math.round(((growthData[growthData.length - 1].score - growthData[0].score) / growthData[0].score) * 100)
    : 25;

  return [
    {
      id: 'cover',
      title: 'Executive Summary',
      subtitle: `${artist.name} — Signing Recommendation`,
      layout: 'cover' as const,
      content: {
        artist: artist.name,
        recommendation: roi >= 200 ? 'APPROVE' : roi >= 100 ? 'CONSIDER' : 'CAUTION',
        confidence: Math.min(96, Math.max(50, Math.round(
          (artist.score * 0.35) + (artist.growth * 0.25) + (artist.momentum * 0.2) + (artist.engagement * 0.2)
        ))),
        stage: roi >= 200 ? 'Committee Review' : roi >= 100 ? 'Due Diligence' : 'Further Analysis',
        date: new Date().toLocaleDateString(),
        score: artist.score,
      },
    },
    {
      id: 'market',
      title: 'Market Opportunity',
      subtitle: `Why now is the right time for ${artist.name}`,
      layout: 'split' as const,
      content: {
        genreGrowth: `${genreGrowth}%`,
        marketSize: `$${(projectedRevenue / 1000000).toFixed(1)}M projected Y1`,
        competition: `${Math.min(5, Math.max(2, Math.round(artist.score / 20)))} labels pursuing`,
        timing: artist.momentum >= 70 ? 'Peak discovery window' : 'Developing opportunity',
        audienceReach: `${artist.listeners >= 1000000 ? (artist.listeners / 1000000).toFixed(1) + 'M' : (artist.listeners / 1000).toFixed(0) + 'K'} monthly listeners`,
        primaryGenre: artist.genres[0] || 'N/A',
      },
    },
    {
      id: 'intelligence',
      title: 'Artist Intelligence',
      subtitle: 'Key metrics dashboard',
      layout: 'grid' as const,
      content: {
        discoveryScore: artist.score,
        growthTrajectory: `${artist.growth}%`,
        audienceQuality: `${Math.min(99, Math.round(artist.engagement * 1.1))}/100`,
        commercialScore: Math.min(99, Math.round((artist.score * 0.4 + artist.momentum * 0.3 + artist.growth * 0.3))),
        momentum: artist.momentum,
        genreFit: artist.score >= 85 ? 'Exceptional' : artist.score >= 70 ? 'Strong' : 'Moderate',
      },
    },
    {
      id: 'financial',
      title: 'Financial Analysis',
      subtitle: 'Investment thesis and returns',
      layout: 'chart' as const,
      content: {
        investment: `$${(totalInvestment / 1000).toFixed(0)}K`,
        revenueY1: `$${(projectedRevenue / 1000000).toFixed(1)}M`,
        roi: `${roi}%`,
        breakEven: `${breakEvenMonths} months`,
        bestCase: `${Math.round(roi * 1.5)}% ROI`,
        worstCase: `${Math.round(roi * 0.5)}% ROI`,
        advance: `$${(dealBreakdown.advance / 1000).toFixed(0)}K`,
        marketing: `$${(dealBreakdown.marketing / 1000).toFixed(0)}K`,
        production: `$${(dealBreakdown.production / 1000).toFixed(0)}K`,
        legal: `$${(dealBreakdown.legal / 1000).toFixed(0)}K`,
        operations: `$${(dealBreakdown.operations / 1000).toFixed(0)}K`,
        totalCost: `$${(dealBreakdown.total / 1000).toFixed(0)}K`,
        revenueCalc: `${(artist.listeners / 1000).toFixed(0)}K listeners × $0.004 avg stream × 12 months × ${1 + artist.growth / 100}x growth`,
        roiCalc: `( $${(projectedRevenue / 1000000).toFixed(1)}M — $${(totalInvestment / 1000000).toFixed(2)}M ) ÷ $${(totalInvestment / 1000000).toFixed(2)}M = ${roi}%`,
        breakEvenCalc: `$${(totalInvestment / 1000).toFixed(0)}K ÷ ( $${(projectedRevenue / 1000 / 12).toFixed(0)}K/mo ) = ${breakEvenMonths} months`,
      },
    },
    {
      id: 'risks',
      title: 'Risk Assessment',
      subtitle: 'Key risks and mitigation strategies',
      layout: 'split' as const,
      content: {
        overallRisk: artist.score >= 85 ? 'LOW-MODERATE' : artist.score >= 70 ? 'MODERATE' : 'MODERATE-HIGH',
        scoreRisk: `${Math.max(5, 100 - artist.score)}% score gap to target`,
        genreRisk: artist.genres.length <= 1 ? 'Concentration risk' : 'Diversified genres',
        momentumRisk: artist.momentum >= 70 ? 'Strong trajectory' : 'Building phase',
        dealRisk: `$${(dealBreakdown.total / 1000).toFixed(0)}K total investment at risk`,
        mitigations: [
          'Structured deal terms with performance milestones',
          artist.momentum >= 70 ? 'Capitalize on current momentum with rapid execution' : 'Include growth milestones in contract terms',
          `Right of refusal on ${artist.genres.length} option albums`,
          artist.score >= 80 ? 'Aggressive marketing to maximize breakout window' : 'Test market with targeted campaigns before full commitment',
        ],
      },
    },
    {
      id: 'recommendation',
      title: 'Recommendation',
      subtitle: 'Motion for committee vote',
      layout: 'cover' as const,
      content: {
        decision: roi >= 200 ? 'Approve signing with conditions' : roi >= 100 ? 'Consider with structured terms' : 'Further due diligence required',
        terms: `$${(dealBreakdown.advance / 1000).toFixed(0)}K advance, ${Math.min(18, Math.max(10, Math.round(artist.score / 6)))}% royalty, 3 options`,
        nextSteps: roi >= 100
          ? ['Finalize contract terms', 'Schedule signing ceremony', `Announcement Q${Math.ceil((new Date().getMonth() + 2) / 3)}`]
          : ['Conduct deeper market analysis', 'Monitor artist trajectory for 60 days', 'Revisit if growth accelerates'],
        committeeAction: 'Vote now in Decision Center',
        projectedROI: `${roi}%`,
        breakEvenPeriod: `${breakEvenMonths} months`,
      },
    },
  ];
}

export function BoardMode({ warRoomId }: BoardModeProps) {
  const [currentSlide, setCurrentSlide] = useState(0);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [showThumbnails, setShowThumbnails] = useState(true);

  const { data, error, isLoading } = useSWR<WarRoomData>(
    `/api/v1/war-rooms/${warRoomId}`,
    fetcher,
    { refreshInterval: 30000 }
  );

  if (isLoading) {
    return (
      <div className={`${isFullscreen ? 'fixed inset-0 z-50 bg-background' : ''}`}>
        <div className="flex items-center justify-between px-6 py-3 border-b bg-card rounded-t-xl">
          <div className="flex items-center gap-3">
            <Monitor className="h-4 w-4 text-primary" />
            <span className="text-sm font-semibold">Board Mode</span>
          </div>
        </div>
        <div className="flex items-center justify-center py-32">
          <div className="text-center">
            <Loader2 className="h-10 w-10 animate-spin text-muted-foreground mx-auto mb-3" />
            <p className="text-sm text-muted-foreground">Loading board presentation...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className={`${isFullscreen ? 'fixed inset-0 z-50 bg-background' : ''}`}>
        <div className="flex items-center justify-between px-6 py-3 border-b bg-card rounded-t-xl">
          <div className="flex items-center gap-3">
            <Monitor className="h-4 w-4 text-primary" />
            <span className="text-sm font-semibold">Board Mode</span>
          </div>
        </div>
        <div className="flex items-center justify-center py-32">
          <div className="text-center max-w-md">
            <HelpCircle className="h-12 w-12 text-muted-foreground mx-auto mb-3 opacity-30" />
            <p className="text-lg font-medium text-muted-foreground">No board data available</p>
            <p className="text-sm text-muted-foreground mt-1">
              {error ? error.message : 'No war room data found for this ID.'}
            </p>
          </div>
        </div>
      </div>
    );
  }

  const slides = generateSlides(data);
  const totalSlides = slides.length;
  const slide = slides[currentSlide];

  const goNext = () => setCurrentSlide(Math.min(currentSlide + 1, totalSlides - 1));
  const goPrev = () => setCurrentSlide(Math.max(currentSlide - 1, 0));

  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen();
      setIsFullscreen(false);
    }
  };

  const formatLabel = (key: string) => key.replace(/([A-Z])/g, ' $1').replace(/^./, s => s.toUpperCase());

  return (
    <div className={`${isFullscreen ? 'fixed inset-0 z-50 bg-background' : ''}`}>
      <div className={`flex items-center justify-between px-6 py-3 border-b bg-card ${isFullscreen ? '' : 'rounded-t-xl'}`}>
        <div className="flex items-center gap-3">
          <Monitor className="h-4 w-4 text-primary" />
          <span className="text-sm font-semibold">Board Mode</span>
          <span className="text-xs text-muted-foreground font-mono">
            Slide {currentSlide + 1} / {totalSlides}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <button onClick={toggleFullscreen} className="p-2 rounded-lg hover:bg-accent transition-colors">
            {isFullscreen ? <Minimize2 className="h-4 w-4" /> : <Maximize2 className="h-4 w-4" />}
          </button>
          <button className="p-2 rounded-lg hover:bg-accent transition-colors">
            <Download className="h-4 w-4" />
          </button>
        </div>
      </div>

      <div className={`flex ${isFullscreen ? 'h-[calc(100vh-56px)]' : ''}`}>
        {showThumbnails && (
          <div className="w-48 border-r bg-card overflow-y-auto p-2 space-y-2">
            {slides.map((s, i) => (
              <button
                key={s.id}
                onClick={() => setCurrentSlide(i)}
                className={`w-full p-2 rounded-lg text-left transition-all ${
                  i === currentSlide
                    ? 'bg-primary/10 ring-1 ring-primary/30'
                    : 'hover:bg-accent'
                }`}
              >
                <p className={`text-xs font-medium truncate ${i === currentSlide ? 'text-primary' : 'text-muted-foreground'}`}>
                  {s.title}
                </p>
                <p className="text-[10px] text-muted-foreground truncate mt-0.5">{s.subtitle}</p>
              </button>
            ))}
          </div>
        )}

        <div className="flex-1 flex flex-col">
          <div className={`flex-1 p-8 lg:p-16 overflow-y-auto ${isFullscreen ? '' : ''}`}>
            <div className="max-w-4xl mx-auto">
              {slide.layout === 'cover' && (
                <div className="text-center py-16">
                  <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-primary/10 text-primary text-sm font-medium mb-8">
                    <Sparkles className="h-4 w-4" />
                    SIGNAL Board Presentation
                  </div>
                  <h1 className="text-5xl lg:text-6xl font-bold tracking-tight mb-4">{slide.title}</h1>
                  <p className="text-xl text-muted-foreground mb-8">{slide.subtitle}</p>

                  {slide.id === 'cover' && (
                    <>
                      <div className="grid grid-cols-2 gap-6 max-w-2xl mx-auto mt-12">
                        <div className="p-6 rounded-2xl border bg-card">
                          <p className="text-sm text-muted-foreground">Recommendation</p>
                          <p className={`text-3xl font-bold mt-1 ${
                            String(slide.content.recommendation) === 'APPROVE' ? 'text-emerald-500' :
                            String(slide.content.recommendation) === 'CONSIDER' ? 'text-amber-500' : 'text-red-500'
                          }`}>{String(slide.content.recommendation)}</p>
                          <p className="text-sm text-muted-foreground mt-1">Confidence: {String(slide.content.confidence)}%</p>
                        </div>
                        <div className="p-6 rounded-2xl border bg-card">
                          <p className="text-sm text-muted-foreground">Artist</p>
                          <p className="text-3xl font-bold mt-1">{String(slide.content.artist)}</p>
                          <p className="text-sm text-muted-foreground mt-1">{String(slide.content.stage)}</p>
                        </div>
                      </div>
                      <div className="mt-8 flex items-center justify-center gap-2">
                        <Star className="h-5 w-5 text-amber-500" />
                        <span className="text-lg font-semibold">Score: {String(slide.content.score)}/100</span>
                      </div>
                    </>
                  )}

                  {slide.id === 'recommendation' && (
                    <div className="max-w-2xl mx-auto mt-12 space-y-6">
                      <div className="p-6 rounded-2xl border bg-card">
                        <p className="text-sm text-muted-foreground">Decision</p>
                        <p className="text-2xl font-bold mt-1">{String(slide.content.decision)}</p>
                      </div>
                      <div className="p-6 rounded-2xl border bg-card">
                        <p className="text-sm text-muted-foreground">Terms</p>
                        <p className="text-xl font-bold mt-1">{String(slide.content.terms)}</p>
                      </div>
                      <div className="grid grid-cols-2 gap-6">
                        <div className="p-4 rounded-xl border border-emerald-500/20 bg-emerald-500/5">
                          <p className="text-sm text-muted-foreground">Projected ROI</p>
                          <p className="text-2xl font-bold text-emerald-500">{String(slide.content.projectedROI)}</p>
                        </div>
                        <div className="p-4 rounded-xl border border-amber-500/20 bg-amber-500/5">
                          <p className="text-sm text-muted-foreground">Break-even</p>
                          <p className="text-2xl font-bold text-amber-500">{String(slide.content.breakEvenPeriod)}</p>
                        </div>
                      </div>
                      <div className="p-6 rounded-xl border bg-card">
                        <p className="text-sm text-muted-foreground mb-3">Next Steps</p>
                        <ul className="space-y-2 text-left">
                          {(slide.content.nextSteps as string[]).map((step, i) => (
                            <li key={i} className="flex items-center gap-2 text-sm">
                              <CheckCircle className="h-4 w-4 text-emerald-500 shrink-0" />
                              <span>{step}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                      <p className="text-sm text-muted-foreground">{String(slide.content.committeeAction)}</p>
                    </div>
                  )}
                </div>
              )}

              {slide.layout === 'split' && (
                <div className="py-8">
                  <div className="mb-8 text-center">
                    <h1 className="text-4xl lg:text-5xl font-bold tracking-tight mb-2">{slide.title}</h1>
                    <p className="text-lg text-muted-foreground">{slide.subtitle}</p>
                  </div>
                  <div className="grid grid-cols-2 gap-8">
                    {Object.entries(slide.content).map(([key, value]) => (
                      <div key={key} className="p-6 rounded-xl border bg-card">
                        <p className="text-sm text-muted-foreground uppercase tracking-wider mb-1">{formatLabel(key)}</p>
                        {key === 'mitigations' ? (
                          <ul className="mt-2 space-y-1">
                            {(value as string[]).map((v: string, i: number) => (
                              <li key={i} className="text-sm text-muted-foreground flex items-start gap-2">
                                <CheckCircle className="h-3.5 w-3.5 text-emerald-500 mt-0.5 shrink-0" />
                                <span>{v}</span>
                              </li>
                            ))}
                          </ul>
                        ) : (
                          <p className="text-3xl lg:text-4xl font-bold mt-1 text-primary">{String(value)}</p>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {slide.layout === 'grid' && (
                <div className="py-8">
                  <div className="mb-8 text-center">
                    <h1 className="text-4xl lg:text-5xl font-bold tracking-tight mb-2">{slide.title}</h1>
                    <p className="text-lg text-muted-foreground">{slide.subtitle}</p>
                  </div>
                  <div className="grid grid-cols-3 gap-6">
                    {Object.entries(slide.content).map(([key, value]) => (
                      <div key={key} className="p-6 rounded-xl border bg-card text-center">
                        <p className="text-sm text-muted-foreground uppercase tracking-wider mb-2">{formatLabel(key)}</p>
                        <p className="text-4xl lg:text-5xl font-bold text-primary">{String(value)}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {slide.layout === 'chart' && (
                <div className="py-8">
                  <div className="mb-8 text-center">
                    <h1 className="text-4xl lg:text-5xl font-bold tracking-tight mb-2">{slide.title}</h1>
                    <p className="text-lg text-muted-foreground">{slide.subtitle}</p>
                  </div>

                  <div className="grid grid-cols-3 gap-6 mb-8">
                    <div className="p-8 rounded-2xl border bg-gradient-to-br from-emerald-500/10 to-transparent text-center">
                      <p className="text-sm text-muted-foreground">Investment</p>
                      <p className="text-4xl font-bold mt-1">{String(slide.content.investment)}</p>
                    </div>
                    <div className="p-8 rounded-2xl border bg-gradient-to-br from-primary/10 to-transparent text-center">
                      <p className="text-sm text-muted-foreground">Y1 Revenue</p>
                      <p className="text-4xl font-bold mt-1">{String(slide.content.revenueY1)}</p>
                    </div>
                    <div className="p-8 rounded-2xl border bg-gradient-to-br from-amber-500/10 to-transparent text-center">
                      <p className="text-sm text-muted-foreground">ROI</p>
                      <p className="text-4xl font-bold mt-1">{String(slide.content.roi)}</p>
                    </div>
                  </div>

                  {/* Cost Breakdown with calculations */}
                  <div className="mb-8">
                    <h3 className="text-lg font-semibold mb-4 text-center">Cost Breakdown</h3>
                    <div className="grid grid-cols-5 gap-3">
                      {[
                        { label: 'Advance', value: String(slide.content.advance), calc: 'Direct signing payment to artist' },
                        { label: 'Marketing', value: String(slide.content.marketing), calc: 'Promo, PR, content, ads' },
                        { label: 'Production', value: String(slide.content.production), calc: 'Recording, mixing, mastering' },
                        { label: 'Legal', value: String(slide.content.legal), calc: 'Contracts, IP, compliance' },
                        { label: 'Operations', value: String(slide.content.operations), calc: 'A&R, mgmt, overhead' },
                      ].map(cat => (
                        <div key={cat.label} className="p-4 rounded-xl border bg-card text-center">
                          <p className="text-xs text-muted-foreground">{cat.label}</p>
                          <p className="text-xl font-bold mt-1">{cat.value}</p>
                          <p className="text-[10px] text-muted-foreground mt-1">{cat.calc}</p>
                        </div>
                      ))}
                    </div>
                    <div className="mt-4 p-4 rounded-xl border-2 border-primary/20 bg-primary/5 text-center">
                      <p className="text-xs text-muted-foreground">Total Investment (sum of all costs)</p>
                      <p className="text-3xl font-bold mt-1">{String(slide.content.totalCost)}</p>
                    </div>
                  </div>

                  {/* Calculation logic */}
                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold text-center">How Calculations Are Made</h3>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div className="p-5 rounded-xl border border-blue-500/20 bg-blue-500/5">
                        <p className="text-sm font-medium text-blue-500 mb-2">Revenue Projection</p>
                        <p className="text-xs text-muted-foreground leading-relaxed">{String(slide.content.revenueCalc)}</p>
                      </div>
                      <div className="p-5 rounded-xl border border-emerald-500/20 bg-emerald-500/5">
                        <p className="text-sm font-medium text-emerald-500 mb-2">ROI Formula</p>
                        <p className="text-xs text-muted-foreground leading-relaxed">{String(slide.content.roiCalc)}</p>
                      </div>
                      <div className="p-5 rounded-xl border border-amber-500/20 bg-amber-500/5">
                        <p className="text-sm font-medium text-amber-500 mb-2">Break-even</p>
                        <p className="text-xs text-muted-foreground leading-relaxed">{String(slide.content.breakEvenCalc)}</p>
                      </div>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-6 mt-8">
                    <div className="p-6 rounded-xl border border-emerald-500/20 bg-emerald-500/5">
                      <p className="text-sm text-muted-foreground">Best Case</p>
                      <p className="text-3xl font-bold text-emerald-500 mt-1">{String(slide.content.bestCase)}</p>
                      <p className="text-xs text-muted-foreground mt-1">With aggressive marketing & full momentum capture</p>
                    </div>
                    <div className="p-6 rounded-xl border border-red-500/20 bg-red-500/5">
                      <p className="text-sm text-muted-foreground">Worst Case</p>
                      <p className="text-3xl font-bold text-red-500 mt-1">{String(slide.content.worstCase)}</p>
                      <p className="text-xs text-muted-foreground mt-1">With conservative growth & market headwinds</p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>

          <div className="flex items-center justify-between px-6 py-4 border-t bg-card">
            <div className="flex items-center gap-4">
              <button
                onClick={goPrev}
                disabled={currentSlide === 0}
                className="flex items-center gap-2 px-4 py-2 rounded-lg border bg-card text-sm hover:bg-accent transition-colors disabled:opacity-30"
              >
                <ArrowLeft className="h-4 w-4" />
                Previous
              </button>
              <button
                onClick={goNext}
                disabled={currentSlide === totalSlides - 1}
                className="flex items-center gap-2 px-4 py-2 rounded-lg bg-primary text-primary-foreground text-sm hover:opacity-90 transition-all disabled:opacity-30"
              >
                Next
                <ArrowRight className="h-4 w-4" />
              </button>
            </div>

            <div className="flex items-center gap-3">
              <button
                onClick={() => setShowThumbnails(!showThumbnails)}
                className="p-2 rounded-lg hover:bg-accent transition-colors"
              >
                <Menu className="h-4 w-4" />
              </button>
              <div className="flex gap-1">
                {slides.map((_, i) => (
                  <button
                    key={i}
                    onClick={() => setCurrentSlide(i)}
                    className={`w-2.5 h-2.5 rounded-full transition-all ${
                      i === currentSlide ? 'bg-primary scale-125' : 'bg-muted-foreground/30 hover:bg-muted-foreground/50'
                    }`}
                  />
                ))}
              </div>
              <span className="text-sm text-muted-foreground font-mono">
                {currentSlide + 1} / {totalSlides}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
