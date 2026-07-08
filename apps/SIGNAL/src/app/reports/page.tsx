'use client';

import { useState, useMemo, useCallback } from 'react';
import useSWR from 'swr';
import { DashboardLayout } from '@/components/dashboard/layout';
import {
  FileText, Loader2, AlertCircle, Plus, X, CheckCircle2, Clock, User,
  Layers, FileWarning, Download, BarChart3, TrendingUp, Scale, Target,
} from 'lucide-react';
import { downloadReportAsPDF, type ReportPDFData, type ReportArtistData } from '@/lib/report-pdf';

const fetcher = (url: string) => fetch(url).then(res => {
  if (!res.ok) throw new Error('Failed to fetch');
  return res.json();
});

interface Template { id: string; name: string; type: string; description: string; lastGenerated: string; }
interface Report { id: string; name: string; type: string; status: 'final' | 'draft'; pages: number; created: string; author: string; description: string; artistName: string; agentActions: string[]; }
interface ReportsResponse { templates: Template[]; reports: Report[]; }
interface ArtistAPI { id: string; name: string; score: number; growth: number; listeners: number; followers: number; genres: string[]; city: string; country: string; deal: number; engagement: number; momentum: number; platforms: Record<string, number>; growthHistory: { month: string; followers: number; streams: number; score: number }[]; }

const templateMeta: Record<string, { icon: React.ElementType; color: string; gradient: string }> = {
  'Analyst': { icon: BarChart3, color: 'from-blue-500/10 to-cyan-500/10', gradient: 'hover:border-blue-500/30' },
  'Writer': { icon: FileText, color: 'from-purple-500/10 to-pink-500/10', gradient: 'hover:border-purple-500/30' },
  'Legal': { icon: Scale, color: 'from-amber-500/10 to-orange-500/10', gradient: 'hover:border-amber-500/30' },
  'Market': { icon: TrendingUp, color: 'from-emerald-500/10 to-teal-500/10', gradient: 'hover:border-emerald-500/30' },
  'Strategy': { icon: Target, color: 'from-rose-500/10 to-purple-500/10', gradient: 'hover:border-rose-500/30' },
};

const statusConfig = {
  final: { icon: CheckCircle2, class: 'bg-green-500/10 text-green-500' },
  draft: { icon: Clock, class: 'bg-amber-500/10 text-amber-500' },
};

function findArtistData(artists: ArtistAPI[], artistName: string): ReportArtistData | undefined {
  const match = artists.find(a => a.name.toLowerCase().includes(artistName.toLowerCase()) || artistName.toLowerCase().includes(a.name.toLowerCase()));
  if (!match) return undefined;
  return {
    score: match.score, growth: match.growth, listeners: match.listeners, followers: match.followers,
    genres: match.genres, city: match.city, country: match.country, deal: match.deal,
    engagement: match.engagement, momentum: match.momentum, platforms: match.platforms, growthHistory: match.growthHistory,
  };
}

export default function ReportsPage() {
  const { data, error, isLoading, mutate } = useSWR<ReportsResponse>('/api/v1/reports', fetcher);
  const { data: artistsData } = useSWR<{ artists: ArtistAPI[] }>('/api/v1/artists?count=42', fetcher);
  const [showModal, setShowModal] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState<string | null>(null);
  const [generating, setGenerating] = useState(false);
  const [downloadingId, setDownloadingId] = useState<string | null>(null);
  const [filterType, setFilterType] = useState('All Types');
  const [filterStatus, setFilterStatus] = useState('All Statuses');

  const artists = artistsData?.artists ?? [];
  const filteredReports = useMemo(() => {
    if (!data?.reports) return [];
    return data.reports.filter(r => {
      if (filterType !== 'All Types' && r.type !== filterType) return false;
      if (filterStatus !== 'All Statuses' && r.status !== filterStatus) return false;
      return true;
    });
  }, [data?.reports, filterType, filterStatus]);

  const handleDownloadPDF = useCallback(async (report: Report) => {
    setDownloadingId(report.id);
    try {
      const pdfData: ReportPDFData = {
        id: report.id, name: report.name, type: report.type, status: report.status,
        created: report.created, author: report.author, description: report.description,
        artistName: report.artistName, agentActions: report.agentActions,
        artist: findArtistData(artists, report.artistName),
      };
      await downloadReportAsPDF(pdfData);
    } catch (err) { console.error('Failed to download PDF:', err); }
    finally { setDownloadingId(null); }
  }, [artists]);

  const handleGenerate = async () => {
    if (!selectedTemplate) return;
    setGenerating(true);
    try {
      await fetch('/api/v1/reports', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ templateId: selectedTemplate }) });
      setSelectedTemplate(null); setShowModal(false); mutate();
    } catch { /* handled */ }
    finally { setGenerating(false); }
  };

  return (
    <DashboardLayout>
      <div className="p-6 space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold tracking-tight">Reports</h1>
            <p className="text-muted-foreground mt-1">Generated reports and document templates</p>
          </div>
          <button
            onClick={() => setShowModal(true)}
            className="flex items-center gap-2 px-4 py-2.5 rounded-lg bg-primary text-primary-foreground text-sm font-medium hover:opacity-90 transition-opacity"
          >
            <Plus className="h-4 w-4" /> Generate
          </button>
        </div>

        {error && <div className="flex items-center gap-2 p-4 rounded-xl border border-red-500/20 bg-red-500/5 text-red-500"><AlertCircle className="h-4 w-4" /><span className="text-sm">Failed to load reports</span></div>}
        {isLoading && <div className="flex items-center justify-center py-20"><Loader2 className="h-8 w-8 animate-spin text-muted-foreground" /></div>}

        {data && (
          <>
            {/* Template cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {data.templates.map((t) => {
                const meta = templateMeta[t.type] || { icon: FileText, color: 'bg-muted', gradient: '' };
                const Icon = meta.icon;
                return (
                  <div
                    key={t.id}
                    onClick={() => { setSelectedTemplate(t.id); setShowModal(true); }}
                    className={`rounded-xl border bg-card p-4 cursor-pointer transition-all bg-gradient-to-br ${meta.color} ${meta.gradient} card-hover`}
                  >
                    <Icon className="h-8 w-8 text-primary mb-3" />
                    <h3 className="font-medium text-sm">{t.name}</h3>
                    <p className="text-xs text-muted-foreground mt-1">{t.description}</p>
                    {t.lastGenerated && (
                      <p className="text-[10px] text-muted-foreground mt-2">Last: {new Date(t.lastGenerated).toLocaleDateString()}</p>
                    )}
                  </div>
                );
              })}
            </div>

            {/* Filters */}
            <div className="flex items-center gap-3 flex-wrap">
              <select value={filterType} onChange={e => setFilterType(e.target.value)} className="px-3 py-2 rounded-lg border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary/50">
                <option>All Types</option>
                {Object.keys(templateMeta).map(t => <option key={t}>{t}</option>)}
              </select>
              <select value={filterStatus} onChange={e => setFilterStatus(e.target.value)} className="px-3 py-2 rounded-lg border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary/50">
                {['All Statuses', 'final', 'draft'].map(s => <option key={s}>{s.charAt(0).toUpperCase() + s.slice(1)}</option>)}
              </select>
            </div>

            {/* Reports table */}
            {filteredReports.length === 0 ? (
              <div className="rounded-xl border bg-card p-12 text-center text-muted-foreground">
                <FileWarning className="h-8 w-8 mx-auto mb-2 opacity-50" />
                <p className="font-medium">No reports found</p>
                <p className="text-sm mt-1">Try adjusting your filters or generate a new report</p>
              </div>
            ) : (
              <div className="rounded-xl border bg-card overflow-hidden">
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b bg-muted/50">
                        <th className="text-left text-xs font-medium text-muted-foreground p-4">Name</th>
                        <th className="text-left text-xs font-medium text-muted-foreground p-4">Artist</th>
                        <th className="text-left text-xs font-medium text-muted-foreground p-4">Type</th>
                        <th className="text-left text-xs font-medium text-muted-foreground p-4">Status</th>
                        <th className="text-left text-xs font-medium text-muted-foreground p-4">Created</th>
                        <th className="text-right text-xs font-medium text-muted-foreground p-4">Download</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y">
                      {filteredReports.map((r) => {
                        const status = statusConfig[r.status] || statusConfig.draft;
                        const StatusIcon = status.icon;
                        return (
                          <tr key={r.id} className="data-row">
                            <td className="p-4">
                              <span className="text-sm font-medium">{r.name}</span>
                              {r.description && <p className="text-[10px] text-muted-foreground mt-0.5 truncate max-w-[200px]">{r.description}</p>}
                            </td>
                            <td className="p-4 text-sm text-muted-foreground">{r.artistName}</td>
                            <td className="p-4">
                              <span className="text-xs px-2 py-1 rounded-full bg-muted font-medium">{r.type}</span>
                            </td>
                            <td className="p-4">
                              <span className={`inline-flex items-center gap-1 text-xs px-2 py-1 rounded-full font-medium ${status.class}`}>
                                <StatusIcon className="h-3 w-3" /> {r.status}
                              </span>
                            </td>
                            <td className="p-4 text-sm text-muted-foreground whitespace-nowrap tabular-nums">
                              {new Date(r.created).toLocaleDateString()}
                            </td>
                            <td className="p-4 text-right">
                              <button
                                onClick={() => handleDownloadPDF(r)}
                                disabled={downloadingId === r.id}
                                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border bg-card text-xs font-medium hover:bg-accent hover:border-primary/30 transition-all disabled:opacity-50"
                              >
                                {downloadingId === r.id ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Download className="h-3.5 w-3.5" />}
                                {downloadingId === r.id ? 'PDF...' : 'PDF'}
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
          </>
        )}

        {/* Glassmorphism Modal */}
        {showModal && data && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm" onClick={() => { if (!generating) setShowModal(false); }}>
            <div className="bg-background/95 backdrop-blur-xl rounded-xl border shadow-2xl w-full max-w-lg mx-4 max-h-[80vh] overflow-y-auto animate-fade-scale-in" onClick={e => e.stopPropagation()}>
              <div className="flex items-center justify-between p-6 border-b">
                <h2 className="text-lg font-semibold">Generate New Report</h2>
                <button onClick={() => { if (!generating) setShowModal(false); }} className="p-1 hover:bg-accent rounded-lg transition-colors">
                  <X className="h-5 w-5" />
                </button>
              </div>
              <div className="p-6 space-y-3">
                <p className="text-sm text-muted-foreground mb-4">Select a template to generate a new report:</p>
                {data.templates.map((t) => {
                  const meta = templateMeta[t.type] || { icon: FileText, color: '', gradient: '' };
                  const Icon = meta.icon;
                  return (
                    <button
                      key={t.id}
                      onClick={() => setSelectedTemplate(t.id)}
                      className={`w-full text-left p-4 rounded-xl border transition-all bg-gradient-to-br ${meta.color} ${
                        selectedTemplate === t.id
                          ? 'border-primary bg-primary/5 ring-1 ring-primary shadow-glow-primary'
                          : 'hover:border-primary/50 hover:bg-accent/50'
                      }`}
                    >
                      <div className="flex items-start gap-3">
                        <Icon className="h-5 w-5 text-primary mt-0.5" />
                        <div>
                          <p className="font-medium text-sm">{t.name}</p>
                          <p className="text-xs text-muted-foreground mt-0.5">{t.description}</p>
                        </div>
                      </div>
                    </button>
                  );
                })}
              </div>
              <div className="flex items-center justify-end gap-3 p-6 border-t">
                <button onClick={() => setShowModal(false)} disabled={generating} className="px-4 py-2 rounded-lg border text-sm hover:bg-accent transition-colors disabled:opacity-50">Cancel</button>
                <button onClick={handleGenerate} disabled={!selectedTemplate || generating} className="flex items-center gap-2 px-4 py-2 rounded-lg bg-primary text-primary-foreground text-sm font-medium hover:opacity-90 transition-opacity disabled:opacity-50">
                  {generating ? <Loader2 className="h-4 w-4 animate-spin" /> : <Plus className="h-4 w-4" />}
                  {generating ? 'Generating...' : 'Generate'}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
