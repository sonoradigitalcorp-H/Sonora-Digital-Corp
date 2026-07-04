'use client';

import { DashboardLayout } from '@/components/dashboard/layout';
import { useMemo, useState, useCallback } from 'react';
import { ArrowLeft, TrendingUp, TrendingDown, Music2, Users, Globe, Share2, Star, Phone, Mail, ExternalLink, AlertTriangle, Loader2, Download, FileText, Scale, FileWarning, CheckCircle2, Clock, XCircle, Archive } from 'lucide-react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import useSWR from 'swr';
import { downloadReportAsPDF, downloadContractAsPDF, type ReportPDFData } from '@/lib/report-pdf';

const fetcher = (url: string) => fetch(url).then(r => {
  if (!r.ok) throw new Error('Failed to fetch');
  return r.json();
});

interface GrowthMonth {
  month: string;
  followers: number;
  streams: number;
  score: number;
}

interface PlatformMetric {
  name: string;
  followers: string;
  url: string;
}

interface DealBreakdown {
  label: string;
  value: string;
}

interface ArtistInsights {
  growth30d: string;
  growth90d: string;
  velocity: string;
  consistency: string;
  age18_24: string;
  age25_34: string;
  topCountry: string;
  engagementRate: string;
  signingPriority: string;
  competitionRisk: string;
  estimatedROI: string;
  recommendation: string;
}

interface Artist {
  id: string;
  name: string;
  image: string;
  photoUrl?: string;
  score: number;
  genres: string[];
  listeners: number;
  followers: number;
  growth: string;
  growthValue: number;
  engagement: number;
  momentum: number;
  status: string;
  city: string;
  country: string;
  phone: string;
  email: string;
  deal: string;
  dealEstimate: string;
  dealBreakdown: DealBreakdown[];
  platforms: PlatformMetric[];
  growthHistory: GrowthMonth[];
  insights: ArtistInsights;
}

const statusColors: Record<string, string> = {
  breakout: 'text-green-500 bg-green-500/10 border-green-500/20',
  monitoring: 'text-blue-500 bg-blue-500/10 border-blue-500/20',
  watchlist: 'text-amber-500 bg-amber-500/10 border-amber-500/20',
  emerging: 'text-purple-500 bg-purple-500/10 border-purple-500/20',
  established: 'text-muted-foreground bg-muted border-muted',
};

function formatNumber(n: number): string {
  if (n >= 1_000_000) return (n / 1_000_000).toFixed(1) + 'M';
  if (n >= 1_000) return (n / 1_000).toFixed(1) + 'K';
  return n.toLocaleString();
}

function GrowthBars({ data }: { data: GrowthMonth[] }) {
  const maxFollowers = Math.max(...data.map(d => d.followers), 1);
  const maxStreams = Math.max(...data.map(d => d.streams), 1);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div className="rounded-xl border bg-card p-5">
        <h3 className="font-semibold mb-1">Growth Trajectory</h3>
        <p className="text-xs text-muted-foreground mb-4">Followers & streams over time</p>
        <div className="flex items-end gap-3 h-56">
          {data.map((d) => (
            <div key={d.month} className="flex-1 flex flex-col items-center gap-1 h-full justify-end">
              <span className="text-[9px] text-muted-foreground font-mono">{d.streams >= 1000000 ? (d.streams / 1000000).toFixed(1) + 'M' : d.streams >= 1000 ? (d.streams / 1000).toFixed(0) + 'K' : d.streams}</span>
              <div className="w-full flex gap-0.5 h-3/4 items-end">
                <div
                  className="flex-1 bg-primary/80 rounded-t-sm transition-all duration-500 min-h-[2px]"
                  style={{ height: `${(d.streams / maxStreams) * 100}%` }}
                />
                <div
                  className="flex-1 bg-chart-1/80 rounded-t-sm transition-all duration-500 min-h-[2px]"
                  style={{ height: `${(d.followers / maxFollowers) * 100}%` }}
                />
              </div>
              <span className="text-[10px] text-muted-foreground mt-1">{d.month}</span>
            </div>
          ))}
        </div>
        <div className="flex items-center justify-center gap-4 mt-3 text-[10px] text-muted-foreground">
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-sm bg-primary/80" />
            Streams
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-sm bg-chart-1/80" />
            Followers
          </span>
        </div>
      </div>

      <div className="rounded-xl border bg-card p-5">
        <h3 className="font-semibold mb-1">Score Breakdown</h3>
        <p className="text-xs text-muted-foreground mb-4">Component scores over time</p>
        <div className="flex items-end gap-3 h-56">
          {data.map((d) => (
            <div key={d.month} className="flex-1 flex flex-col items-center gap-1 h-full justify-end">
              <span className="text-[10px] font-mono font-medium text-chart-3">{d.score}</span>
              <div
                className="w-full bg-chart-3/80 rounded-t-sm transition-all duration-500 min-h-[2px]"
                style={{ height: `${d.score}%` }}
              />
              <span className="text-[10px] text-muted-foreground mt-1">{d.month}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function Skeleton() {
  return (
    <DashboardLayout>
      <div className="p-6 space-y-6">
        <div className="h-4 w-32 rounded bg-muted animate-pulse" />
        <div className="flex items-start justify-between animate-pulse">
          <div className="flex items-center gap-5">
            <div className="w-20 h-20 rounded-2xl bg-muted" />
            <div className="space-y-3">
              <div className="h-8 w-48 rounded bg-muted" />
              <div className="flex gap-2">
                <div className="h-4 w-24 rounded bg-muted" />
                <div className="h-4 w-1 rounded-full bg-muted" />
                <div className="h-4 w-20 rounded bg-muted" />
              </div>
            </div>
          </div>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 animate-pulse">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="rounded-xl border bg-card p-4 space-y-2">
              <div className="h-3 w-20 rounded bg-muted" />
              <div className="h-8 w-16 rounded bg-muted" />
              <div className="h-3 w-12 rounded bg-muted" />
            </div>
          ))}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 animate-pulse">
          <div className="rounded-xl border bg-card p-5">
            <div className="h-5 w-40 rounded bg-muted mb-1" />
            <div className="h-3 w-56 rounded bg-muted mb-4" />
            <div className="h-56 rounded bg-muted" />
          </div>
          <div className="rounded-xl border bg-card p-5">
            <div className="h-5 w-40 rounded bg-muted mb-1" />
            <div className="h-3 w-56 rounded bg-muted mb-4" />
            <div className="h-56 rounded bg-muted" />
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}

// Report API type
interface ReportAPI {
  id: string;
  name: string;
  type: string;
  status: 'final' | 'draft';
  created: string;
  author: string;
  description: string;
  artistName: string;
  agentActions: string[];
}

interface ContractAPI {
  id: string;
  artistName: string;
  artistGenre: string;
  artistScore: number;
  type: string;
  subType: string;
  status: string;
  amount: number;
  advance: number;
  royaltyRate: string;
  revenueShare: string;
  recoupableItems: string[];
  term: string;
  territory: string;
  albumCommitment: number;
  mastersOwnership: string;
  publishingSplit: string;
  creativeControl: string;
  marketingCommitment: string;
  syncRights: string;
  riskLevel: 'low' | 'medium' | 'high';
  reviewedBy: string;
  clauses: string[];
  agentAlert: string;
  createdAt: string;
  expiryDate: string;
  signedDate: string | null;
  notes: string;
}

export default function ArtistDetailPage() {
  const params = useParams();
  const id = params.id as string;

  const { data, error, isLoading } = useSWR<{ artists?: Artist[] } | Artist[]>(
    '/api/v1/artists?count=20',
    fetcher,
  );
  const { data: contractsData } = useSWR<{ contracts: ContractAPI[] }>('/api/v1/contracts', fetcher);
  const { data: reportsData } = useSWR<{ reports: ReportAPI[] }>('/api/v1/reports', fetcher);

  const [downloading, setDownloading] = useState<string | null>(null);
  const [downloadingAll, setDownloadingAll] = useState(false);

  const artist = useMemo(() => {
    if (!data) return null;
    const list = Array.isArray(data) ? data : data.artists;
    if (!list) return null;
    return list.find((a: Artist) => a.id === id) || null;
  }, [data, id]);

  // Filter contracts and reports for this artist
  const artistContracts = useMemo(() => {
    if (!contractsData?.contracts || !artist) return [];
    return contractsData.contracts.filter(c =>
      c.artistName.toLowerCase().includes(artist.name.toLowerCase()) ||
      artist.name.toLowerCase().includes(c.artistName.toLowerCase())
    );
  }, [contractsData, artist]);

  const artistReports = useMemo(() => {
    if (!reportsData?.reports || !artist) return [];
    return reportsData.reports.filter(r =>
      r.artistName.toLowerCase().includes(artist.name.toLowerCase()) ||
      artist.name.toLowerCase().includes(r.artistName.toLowerCase())
    );
  }, [reportsData, artist]);

  // Download individual report
  const handleDownloadReport = useCallback(async (report: ReportAPI) => {
    setDownloading('report-' + report.id);
    try {
      const pdfData: ReportPDFData = {
        id: report.id,
        name: report.name,
        type: report.type,
        status: report.status,
        created: report.created,
        author: report.author,
        description: report.description,
        artistName: report.artistName,
        agentActions: report.agentActions,
        artist: artist ? {
          score: artist.score,
          growth: artist.growthValue || 0,
          listeners: artist.listeners,
          followers: artist.followers,
          genres: artist.genres || [],
          city: artist.city || '',
          country: artist.country || '',
          deal: artist.deal ? parseInt(artist.deal.replace(/[^0-9]/g, '')) || 0 : 0,
          engagement: artist.engagement || 0,
          momentum: artist.momentum || 0,
          platforms: {},
          growthHistory: artist.growthHistory || [],
        } : undefined,
      };
      await downloadReportAsPDF(pdfData);
    } catch (err) {
      console.error('Download failed:', err);
    } finally {
      setDownloading(null);
    }
  }, [artist]);

  // Download individual contract
  const handleDownloadContract = useCallback(async (contract: ContractAPI) => {
    setDownloading('contract-' + contract.id);
    try {
      downloadContractAsPDF(contract);
    } catch (err) {
      console.error('Download failed:', err);
    } finally {
      setDownloading(null);
    }
  }, []);

  // Download all agent outputs for this artist
  const handleDownloadAll = useCallback(async () => {
    setDownloadingAll(true);
    try {
      // Download all reports one by one
      for (const report of artistReports) {
        const pdfData: ReportPDFData = {
          id: report.id,
          name: report.name,
          type: report.type,
          status: report.status,
          created: report.created,
          author: report.author,
          description: report.description,
          artistName: report.artistName,
          agentActions: report.agentActions,
          artist: artist ? {
            score: artist.score,
            growth: artist.growthValue || 0,
            listeners: artist.listeners,
            followers: artist.followers,
            genres: artist.genres || [],
            city: artist.city || '',
            country: artist.country || '',
            deal: artist.deal ? parseInt(artist.deal.replace(/[^0-9]/g, '')) || 0 : 0,
            engagement: artist.engagement || 0,
            momentum: artist.momentum || 0,
            platforms: {},
            growthHistory: artist.growthHistory || [],
          } : undefined,
        };
        await downloadReportAsPDF(pdfData);
        // Small delay between downloads
        await new Promise(r => setTimeout(r, 500));
      }
    } catch (err) {
      console.error('Download all failed:', err);
    } finally {
      setDownloadingAll(false);
    }
  }, [artistReports, artist]);

  if (error) {
    return (
      <DashboardLayout>
        <div className="p-6">
          <div className="rounded-xl border bg-card p-8 text-center">
            <AlertTriangle className="h-8 w-8 text-destructive mx-auto mb-3" />
            <h2 className="text-lg font-semibold mb-1">Failed to load artist</h2>
            <p className="text-sm text-muted-foreground mb-4">The artist data could not be fetched. Please try again.</p>
            <Link href="/artists" className="inline-flex items-center gap-1 text-sm text-primary hover:underline">
              <ArrowLeft className="h-4 w-4" />
              Back to Artists
            </Link>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  if (isLoading || !data) return <Skeleton />;

  if (!artist) {
    return (
      <DashboardLayout>
        <div className="p-6">
          <div className="rounded-xl border bg-card p-8 text-center">
            <Music2 className="h-8 w-8 text-muted-foreground mx-auto mb-3" />
            <h2 className="text-lg font-semibold mb-1">Artist not found</h2>
            <p className="text-sm text-muted-foreground mb-4">No artist matches the ID &quot;{id}&quot;.</p>
            <Link href="/artists" className="inline-flex items-center gap-1 text-sm text-primary hover:underline">
              <ArrowLeft className="h-4 w-4" />
              Back to Artists
            </Link>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="p-6 space-y-6">
        {/* Back + Header */}
        <div>
          <Link href="/artists" className="flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground mb-4 transition-colors">
            <ArrowLeft className="h-4 w-4" />
            Back to Artists
          </Link>

          <div className="flex items-start justify-between">
            <div className="flex items-center gap-5">
              <div className="w-20 h-20 rounded-2xl bg-primary/10 flex items-center justify-center text-3xl font-bold overflow-hidden shrink-0">
                {artist.photoUrl ? (
                  <img src={artist.photoUrl} alt={artist.name} className="w-full h-full object-cover" />
                ) : (
                  artist.image || artist.name.slice(0, 2).toUpperCase()
                )}
              </div>
              <div>
                <h1 className="text-3xl font-bold">{artist.name}</h1>
                <div className="flex items-center gap-3 mt-1 flex-wrap">
                  <span className="text-sm text-muted-foreground">
                    {Array.isArray(artist.genres) ? artist.genres.join(', ') : artist.genres || '—'}
                  </span>
                  <span className="w-1 h-1 rounded-full bg-muted-foreground" />
                  <span className="text-sm text-muted-foreground">
                    {artist.city}{artist.country ? `, ${artist.country}` : ''}
                  </span>
                  <span className="w-1 h-1 rounded-full bg-muted-foreground" />
                  <span className={`text-xs px-2 py-0.5 rounded-full font-medium border ${statusColors[artist.status] || statusColors.emerging}`}>
                    {artist.status}
                  </span>
                </div>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <button className="flex items-center gap-2 px-4 py-2 rounded-lg border bg-card text-sm hover:bg-accent transition-colors">
                <Star className="h-4 w-4" />
                Watchlist
              </button>
              <button className="flex items-center gap-2 px-4 py-2 rounded-lg border bg-card text-sm hover:bg-accent transition-colors">
                <Share2 className="h-4 w-4" />
                Share
              </button>
            </div>
          </div>
        </div>

        {/* Score badge */}
        <div className="flex items-center gap-2">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-primary/10 text-primary text-sm font-medium">
            <Star className="h-3.5 w-3.5" />
            Score {artist.score}/100
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div className="rounded-xl border bg-card p-4">
            <p className="text-xs text-muted-foreground mb-1">Monthly Listeners</p>
            <p className="text-3xl font-bold">{formatNumber(artist.listeners)}</p>
            <p className="text-xs text-green-500 mt-1">Active audience</p>
          </div>
          <div className="rounded-xl border bg-card p-4">
            <p className="text-xs text-muted-foreground mb-1">Followers</p>
            <p className="text-3xl font-bold">{formatNumber(artist.followers)}</p>
            <p className="text-xs text-muted-foreground mt-1">Total following</p>
          </div>
          <div className="rounded-xl border bg-card p-4">
            <p className="text-xs text-muted-foreground mb-1">Growth</p>
            <p className="text-3xl font-bold text-green-500">{artist.growth}</p>
            <p className="text-xs text-green-500/80 mt-1">Monthly change</p>
          </div>
          <div className="rounded-xl border bg-card p-4">
            <p className="text-xs text-muted-foreground mb-1">Engagement</p>
            <p className="text-3xl font-bold">{artist.engagement}%</p>
            <p className="text-xs text-muted-foreground mt-1">Rate</p>
          </div>
          <div className="rounded-xl border bg-card p-4">
            <p className="text-xs text-muted-foreground mb-1">Momentum</p>
            <p className="text-3xl font-bold">{artist.momentum}</p>
            <p className="text-xs text-muted-foreground mt-1">Score</p>
          </div>
        </div>

        {/* Growth History Chart */}
        {artist.growthHistory && artist.growthHistory.length > 1 && (
          <GrowthBars data={artist.growthHistory} />
        )}

        {/* Contact + Deal */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="rounded-xl border bg-card p-5">
            <h3 className="font-semibold mb-4">Contact Information</h3>
            <div className="space-y-3">
              <div className="flex items-center gap-3 text-sm">
                <Phone className="h-4 w-4 text-muted-foreground shrink-0" />
                <span>{artist.phone || '—'}</span>
              </div>
              <div className="flex items-center gap-3 text-sm">
                <Mail className="h-4 w-4 text-muted-foreground shrink-0" />
                <span>{artist.email || '—'}</span>
              </div>
            </div>
          </div>

          <div className="rounded-xl border bg-card p-5">
            <h3 className="font-semibold mb-4">Deal Estimate</h3>
            <p className="text-2xl font-bold text-primary mb-1">{artist.dealEstimate || '—'}</p>
            <p className="text-xs text-muted-foreground mb-3">{artist.deal || '—'}</p>
            {artist.dealBreakdown && artist.dealBreakdown.length > 0 && (
              <div className="space-y-2 pt-2 border-t">
                {artist.dealBreakdown.map((item, i) => (
                  <div key={i} className="flex justify-between text-sm">
                    <span className="text-muted-foreground">{item.label}</span>
                    <span className="font-medium">{item.value}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Platform Metrics */}
        {artist.platforms && artist.platforms.length > 0 && (
          <div className="rounded-xl border bg-card p-5">
            <h3 className="font-semibold mb-4">Platform Presence</h3>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              {artist.platforms.map(platform => (
                <div key={platform.name} className="p-3 rounded-lg bg-accent/50">
                  <p className="text-xs text-muted-foreground">{platform.name}</p>
                  <p className="font-medium mt-0.5">{platform.followers}</p>
                  {platform.url && (
                    <a
                      href={platform.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-0.5 text-[10px] text-primary hover:underline mt-1"
                    >
                      Visit <ExternalLink className="h-3 w-3" />
                    </a>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Intelligence Breakdown */}
        {artist.insights && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="rounded-xl border bg-card p-5">
              <div className="flex items-center gap-2 mb-4">
                <TrendingUp className="h-4 w-4 text-green-500" />
                <h3 className="font-semibold">Growth Analysis</h3>
              </div>
              <div className="space-y-3">
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">30-day growth</span>
                  <span className="font-medium text-green-500">{artist.insights.growth30d || '—'}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">90-day growth</span>
                  <span className="font-medium text-green-500">{artist.insights.growth90d || '—'}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Velocity</span>
                  <span className="font-medium text-green-500">{artist.insights.velocity || '—'}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Consistency</span>
                  <span className="font-medium">{artist.insights.consistency || '—'}</span>
                </div>
              </div>
            </div>

            <div className="rounded-xl border bg-card p-5">
              <div className="flex items-center gap-2 mb-4">
                <Users className="h-4 w-4 text-purple-500" />
                <h3 className="font-semibold">Audience Insights</h3>
              </div>
              <div className="space-y-3">
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Age 18-24</span>
                  <span className="font-medium">{artist.insights.age18_24 || '—'}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Age 25-34</span>
                  <span className="font-medium">{artist.insights.age25_34 || '—'}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Top country</span>
                  <span className="font-medium">{artist.insights.topCountry || '—'}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Engagement rate</span>
                  <span className="font-medium">{artist.insights.engagementRate || '—'}</span>
                </div>
              </div>
            </div>

            <div className="rounded-xl border bg-card p-5">
              <div className="flex items-center gap-2 mb-4">
                <AlertTriangle className="h-4 w-4 text-amber-500" />
                <h3 className="font-semibold">Signing Assessment</h3>
              </div>
              <div className="space-y-3">
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Signing priority</span>
                  <span className="font-medium text-green-500">{artist.insights.signingPriority || '—'}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Competition risk</span>
                  <span className="font-medium text-amber-500">{artist.insights.competitionRisk || '—'}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Estimated ROI</span>
                  <span className="font-medium text-green-500">{artist.insights.estimatedROI || '—'}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Recommendation</span>
                  <span className="font-medium text-green-500">{artist.insights.recommendation || '—'}</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ════════════════════════════════════════
            CONTRACTS SECTION
            ════════════════════════════════════════ */}
        {artistContracts.length > 0 && (
          <div className="rounded-xl border bg-card overflow-hidden">
            <div className="p-5 border-b flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Scale className="h-5 w-5 text-primary" />
                <h3 className="font-semibold">Contracts ({artistContracts.length})</h3>
              </div>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b bg-muted/50">
                    <th className="text-left text-xs font-medium text-muted-foreground p-3">Type</th>
                    <th className="text-left text-xs font-medium text-muted-foreground p-3">Status</th>
                    <th className="text-right text-xs font-medium text-muted-foreground p-3">Amount</th>
                    <th className="text-left text-xs font-medium text-muted-foreground p-3">Term</th>
                    <th className="text-left text-xs font-medium text-muted-foreground p-3">Risk</th>
                    <th className="text-right text-xs font-medium text-muted-foreground p-3">Download</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {artistContracts.map((c) => {
                    const riskDot = c.riskLevel === 'low' ? 'bg-green-500' : c.riskLevel === 'medium' ? 'bg-amber-500' : 'bg-red-500';
                    const statusLabel = c.status.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
                    return (
                      <tr key={c.id} className="hover:bg-accent/50 transition-colors">
                        <td className="p-3 text-sm">{c.type}</td>
                        <td className="p-3">
                          <span className={`text-xs px-2 py-0.5 rounded-full border font-medium ${
                            c.status === 'signed' ? 'text-green-500 bg-green-500/10 border-green-500/20' :
                            c.status === 'pending_review' ? 'text-red-500 bg-red-500/10 border-red-500/20' :
                            c.status === 'draft' ? 'text-amber-500 bg-amber-500/10 border-amber-500/20' :
                            c.status === 'negotiation' ? 'text-blue-500 bg-blue-500/10 border-blue-500/20' :
                            'text-gray-500 bg-gray-500/10 border-gray-500/20'
                          }`}>
                            {statusLabel}
                          </span>
                        </td>
                        <td className="p-3 text-right text-sm font-medium">
                          ${c.amount.toLocaleString()}
                        </td>
                        <td className="p-3 text-sm text-muted-foreground">{c.term}</td>
                        <td className="p-3">
                          <span className={`inline-flex items-center gap-1.5 text-xs px-2 py-0.5 rounded-full font-medium ${
                            c.riskLevel === 'low' ? 'text-green-600 bg-green-50' :
                            c.riskLevel === 'medium' ? 'text-amber-600 bg-amber-50' :
                            'text-red-600 bg-red-50'
                          }`}>
                            <span className={`w-1.5 h-1.5 rounded-full ${riskDot}`} />
                            {c.riskLevel}
                          </span>
                        </td>
                        <td className="p-3 text-right">
                          <button
                            onClick={() => handleDownloadContract(c)}
                            disabled={downloading === 'contract-' + c.id}
                            className="inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg border bg-card text-xs font-medium hover:bg-accent transition-all disabled:opacity-50"
                          >
                            {downloading === 'contract-' + c.id ? (
                              <Loader2 className="h-3 w-3 animate-spin" />
                            ) : (
                              <Download className="h-3 w-3" />
                            )}
                            PDF
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* ════════════════════════════════════════
            AGENT OUTPUTS SECTION
            ════════════════════════════════════════ */}
        {artistReports.length > 0 && (
          <div className="rounded-xl border bg-card overflow-hidden">
            <div className="p-5 border-b flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Archive className="h-5 w-5 text-primary" />
                <h3 className="font-semibold">Agent Outputs ({artistReports.length})</h3>
                <span className="text-xs text-muted-foreground">
                  — Everything generated by agents for {artist.name}
                </span>
              </div>
              <button
                onClick={handleDownloadAll}
                disabled={downloadingAll}
                className="flex items-center gap-2 px-4 py-2 rounded-lg bg-primary text-primary-foreground text-sm font-medium hover:opacity-90 transition-opacity disabled:opacity-50"
              >
                {downloadingAll ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Archive className="h-4 w-4" />
                )}
                {downloadingAll ? 'Downloading...' : 'Download All'}
              </button>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b bg-muted/50">
                    <th className="text-left text-xs font-medium text-muted-foreground p-3">Report</th>
                    <th className="text-left text-xs font-medium text-muted-foreground p-3">Type</th>
                    <th className="text-left text-xs font-medium text-muted-foreground p-3">Author</th>
                    <th className="text-left text-xs font-medium text-muted-foreground p-3">Status</th>
                    <th className="text-left text-xs font-medium text-muted-foreground p-3">Actions</th>
                    <th className="text-right text-xs font-medium text-muted-foreground p-3">Download</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {artistReports.map((r) => (
                    <tr key={r.id} className="hover:bg-accent/50 transition-colors">
                      <td className="p-3">
                        <span className="text-sm font-medium">{r.name}</span>
                        <p className="text-[10px] text-muted-foreground mt-0.5 truncate max-w-[200px]">{r.description}</p>
                      </td>
                      <td className="p-3">
                        <span className="text-xs px-2 py-0.5 rounded-full bg-muted font-medium">{r.type}</span>
                      </td>
                      <td className="p-3 text-sm text-muted-foreground">{r.author}</td>
                      <td className="p-3">
                        <span className={`inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded-full font-medium ${
                          r.status === 'final' ? 'text-green-500 bg-green-500/10' : 'text-amber-500 bg-amber-500/10'
                        }`}>
                          {r.status === 'final' ? <CheckCircle2 className="h-3 w-3" /> : <Clock className="h-3 w-3" />}
                          {r.status}
                        </span>
                      </td>
                      <td className="p-3">
                        <div className="flex gap-1 flex-wrap">
                          {r.agentActions.slice(0, 2).map((a, i) => (
                            <span key={i} className="text-[9px] px-1.5 py-0.5 rounded bg-accent text-muted-foreground">
                              {a.length > 30 ? a.slice(0, 30) + '...' : a}
                            </span>
                          ))}
                          {r.agentActions.length > 2 && (
                            <span className="text-[9px] text-muted-foreground">+{r.agentActions.length - 2}</span>
                          )}
                        </div>
                      </td>
                      <td className="p-3 text-right">
                        <button
                          onClick={() => handleDownloadReport(r)}
                          disabled={downloading === 'report-' + r.id}
                          className="inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg border bg-card text-xs font-medium hover:bg-accent transition-all disabled:opacity-50"
                        >
                          {downloading === 'report-' + r.id ? (
                            <Loader2 className="h-3 w-3 animate-spin" />
                          ) : (
                            <Download className="h-3 w-3" />
                          )}
                          PDF
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Empty state for no agent outputs */}
        {artist && artistReports.length === 0 && (
          <div className="rounded-xl border bg-card p-8 text-center text-muted-foreground">
            <FileText className="h-8 w-8 mx-auto mb-2 opacity-50" />
            <p className="font-medium">No agent outputs yet</p>
            <p className="text-sm mt-1">
              Agents haven&apos;t generated reports for {artist.name} yet.
              Start a workflow to begin analysis.
            </p>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
