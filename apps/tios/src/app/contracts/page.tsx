'use client';

import { useState, useMemo, useCallback } from 'react';
import useSWR from 'swr';
import { DashboardLayout } from '@/components/dashboard/layout';
import {
  FileText, Loader2, AlertCircle, Download, ShieldCheck,
  Clock, CheckCircle2, XCircle, FileWarning, User, DollarSign,
  AlertTriangle, Globe, Scale, Calendar, Gavel, Shield,
  BookOpen, Music, Radio, Handshake,
} from 'lucide-react';
import { downloadContractAsPDF } from '@/lib/report-pdf';

const fetcher = (url: string) => fetch(url).then(res => {
  if (!res.ok) throw new Error('Failed to fetch');
  return res.json();
});

interface Contract {
  id: string;
  artistName: string;
  artistGenre: string;
  artistScore: number;
  type: 'Recording' | 'Distribution' | '360' | 'Joint Venture' | 'Licensing';
  subType: string;
  status: 'pending_review' | 'draft' | 'negotiation' | 'signed' | 'terminated';
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

interface ContractsResponse {
  contracts: Contract[];
  total: number;
  stats: Record<string, number>;
}

const statusConfig: Record<string, { icon: any; class: string; label: string }> = {
  pending_review: { icon: AlertTriangle, class: 'bg-red-500/10 text-red-500 border-red-500/20', label: 'Pending Review' },
  draft: { icon: FileWarning, class: 'bg-amber-500/10 text-amber-500 border-amber-500/20', label: 'Draft' },
  negotiation: { icon: Clock, class: 'bg-blue-500/10 text-blue-500 border-blue-500/20', label: 'Negotiation' },
  signed: { icon: CheckCircle2, class: 'bg-green-500/10 text-green-500 border-green-500/20', label: 'Signed' },
  terminated: { icon: XCircle, class: 'bg-gray-500/10 text-gray-500 border-gray-500/20', label: 'Terminated' },
};

const riskConfig: Record<string, { class: string; dot: string }> = {
  low: { class: 'text-green-600 bg-green-50', dot: 'bg-green-500' },
  medium: { class: 'text-amber-600 bg-amber-50', dot: 'bg-amber-500' },
  high: { class: 'text-red-600 bg-red-50', dot: 'bg-red-500' },
};

const contractTypes = ['All', 'Recording', 'Distribution', '360', 'Joint Venture', 'Licensing'];
const contractStatuses = ['All', 'pending_review', 'draft', 'negotiation', 'signed', 'terminated'];

const typeIcons: Record<string, any> = {
  'Recording': Music,
  'Distribution': Radio,
  '360': Globe,
  'Joint Venture': Handshake,
  'Licensing': BookOpen,
};

function formatCurrency(n: number) {
  return '$' + n.toLocaleString('en-US');
}

export default function ContractsPage() {
  const { data, error, isLoading, mutate } = useSWR<ContractsResponse>('/api/v1/contracts', fetcher);
  const [filterType, setFilterType] = useState('All');
  const [filterStatus, setFilterStatus] = useState('All');
  const [downloadingId, setDownloadingId] = useState<string | null>(null);

  const filteredContracts = useMemo(() => {
    if (!data?.contracts) return [];
    return data.contracts.filter(c => {
      if (filterType !== 'All' && c.type !== filterType) return false;
      if (filterStatus !== 'All' && c.status !== filterStatus) return false;
      return true;
    });
  }, [data?.contracts, filterType, filterStatus]);

  const handleDownload = useCallback(async (contract: Contract) => {
    setDownloadingId(contract.id);
    try {
      await downloadContractAsPDF(contract);
    } catch (err) {
      console.error('Failed to download contract PDF:', err);
    } finally {
      setDownloadingId(null);
    }
  }, []);

  const pendingCount = data?.stats?.pending_review ?? 0;

  return (
    <DashboardLayout>
      <div className="p-6 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight flex items-center gap-3">
              <Scale className="h-7 w-7 text-primary" />
              Contracts
            </h1>
            <p className="text-muted-foreground mt-1">
              Contract lifecycle management &mdash; {data?.total ?? 0} total contracts
              {pendingCount > 0 && (
                <span className="text-red-500 font-medium ml-2">
                  &middot; {pendingCount} pending review
                </span>
              )}
            </p>
          </div>
          <button
            onClick={() => mutate()}
            className="flex items-center gap-2 px-4 py-2.5 rounded-lg border bg-card text-sm font-medium hover:bg-accent transition-colors"
          >
            <Loader2 className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>

        {/* Error */}
        {error && (
          <div className="flex items-center gap-2 p-4 rounded-xl border border-red-500/20 bg-red-500/5 text-red-500">
            <AlertCircle className="h-4 w-4" />
            <span className="text-sm">Failed to load contracts</span>
          </div>
        )}

        {/* Loading */}
        {isLoading && (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
          </div>
        )}

        {data && (
          <>
            {/* ⚠️ AGENT HANDOFF ALERT — Fixed banner on every page load */}
            <div className="flex items-start gap-4 p-4 md:p-5 rounded-xl border border-amber-500/30 bg-gradient-to-r from-amber-500/10 to-red-500/5">
              <Shield className="h-6 w-6 text-amber-500 flex-shrink-0 mt-0.5" />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-bold text-amber-500 uppercase tracking-wide flex items-center gap-2">
                  <AlertTriangle className="h-4 w-4" />
                  AGENT REVIEW COMPLETE — HUMAN SIGNATURE REQUIRED
                </p>
                <p className="text-xs text-muted-foreground mt-2 leading-relaxed">
                  SIGNAL agents have drafted and reviewed these contracts for your evaluation.{' '}
                  <strong className="text-amber-400">Agents cannot sign or execute contracts.</strong>{' '}
                  These documents are draft recommendations only. Forward to{' '}
                  <strong>legal counsel</strong> for final review, negotiation, and execution.{' '}
                  No binding agreement exists until signed by authorized representatives of both parties.
                </p>
              </div>
            </div>

            {/* Stats Cards */}
            <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
              {[
                { key: 'pending_review', label: 'Pending Review', icon: AlertTriangle, color: 'text-red-500', bg: 'bg-red-500/10' },
                { key: 'draft', label: 'Draft', icon: FileWarning, color: 'text-amber-500', bg: 'bg-amber-500/10' },
                { key: 'negotiation', label: 'Negotiation', icon: Clock, color: 'text-blue-500', bg: 'bg-blue-500/10' },
                { key: 'signed', label: 'Signed', icon: CheckCircle2, color: 'text-green-500', bg: 'bg-green-500/10' },
                { key: 'terminated', label: 'Terminated', icon: XCircle, color: 'text-gray-500', bg: 'bg-gray-500/10' },
              ].map(s => {
                const Icon = s.icon;
                const count = data.stats[s.key] ?? 0;
                return (
                  <div key={s.key} className="rounded-xl border bg-card p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs text-muted-foreground">{s.label}</span>
                      <Icon className={`h-4 w-4 ${s.color}`} />
                    </div>
                    <p className={`text-2xl font-bold ${count > 0 && s.key === 'pending_review' ? 'text-red-500' : ''}`}>
                      {count}
                    </p>
                  </div>
                );
              })}
            </div>

            {/* Filters */}
            <div className="flex items-center gap-3 flex-wrap">
              <select
                value={filterType}
                onChange={e => setFilterType(e.target.value)}
                className="px-3 py-2 rounded-lg border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
              >
                {contractTypes.map(t => <option key={t} value={t}>{t}</option>)}
              </select>
              <select
                value={filterStatus}
                onChange={e => setFilterStatus(e.target.value)}
                className="px-3 py-2 rounded-lg border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
              >
                {contractStatuses.map(s => (
                  <option key={s} value={s}>
                    {s === 'All' ? 'All Statuses' : s.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}
                  </option>
                ))}
              </select>
            </div>

            {/* Contracts Table */}
            {filteredContracts.length === 0 ? (
              <div className="rounded-xl border bg-card p-12 text-center text-muted-foreground">
                <FileText className="h-8 w-8 mx-auto mb-2 opacity-50" />
                <p className="font-medium">No contracts found</p>
                <p className="text-sm mt-1">Try adjusting your filters</p>
              </div>
            ) : (
              <div className="rounded-xl border bg-card overflow-hidden">
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b bg-muted/50">
                        <th className="text-left text-xs font-medium text-muted-foreground p-3">Artist</th>
                        <th className="text-left text-xs font-medium text-muted-foreground p-3">Type</th>
                        <th className="text-left text-xs font-medium text-muted-foreground p-3">Status</th>
                        <th className="text-right text-xs font-medium text-muted-foreground p-3">Advance</th>
                        <th className="text-left text-xs font-medium text-muted-foreground p-3">Masters</th>
                        <th className="text-left text-xs font-medium text-muted-foreground p-3">Term</th>
                        <th className="text-left text-xs font-medium text-muted-foreground p-3">Risk</th>
                        <th className="text-left text-xs font-medium text-muted-foreground p-3">Created</th>
                        <th className="text-right text-xs font-medium text-muted-foreground p-3">PDF</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y">
                      {filteredContracts.map((c) => {
                          const status = statusConfig[c.status] || statusConfig.draft;
                          const StatusIcon = status.icon;
                          const risk = riskConfig[c.riskLevel] || riskConfig.low;
                          const TypeIcon = typeIcons[c.type] || FileText;

                          return (
                            <tr
                              key={c.id}
                              className={`hover:bg-accent/50 transition-colors ${
                                c.status === 'pending_review' ? 'bg-red-500/5' : ''
                              }`}
                            >
                              <td className="p-3">
                                <div>
                                  <span className="text-sm font-medium">{c.artistName}</span>
                                  <p className="text-[10px] text-muted-foreground mt-0.5">{c.artistGenre} · Score {c.artistScore}</p>
                                </div>
                              </td>
                              <td className="p-3">
                                <div className="flex items-center gap-1.5">
                                  <TypeIcon className="h-3.5 w-3.5 text-muted-foreground" />
                                  <span className="text-xs font-medium">{c.type}</span>
                                </div>
                                <p className="text-[10px] text-muted-foreground mt-0.5 truncate max-w-[120px]">{c.subType}</p>
                              </td>
                              <td className="p-3">
                                <span className={`inline-flex items-center gap-1 text-xs px-2 py-1 rounded-full border font-medium ${status.class}`}>
                                  <StatusIcon className="h-3 w-3" />
                                  {status.label}
                                </span>
                              </td>
                              <td className="p-3 text-right">
                                <span className="text-sm font-semibold">{formatCurrency(c.advance)}</span>
                                <p className="text-[10px] text-muted-foreground">{c.revenueShare}</p>
                              </td>
                              <td className="p-3">
                                <p className="text-xs font-medium">{c.mastersOwnership.includes('Artist') ? 'Artist Owns' : 'Label Owns'}</p>
                                <p className="text-[10px] text-muted-foreground mt-0.5">{c.albumCommitment} album(s)</p>
                              </td>
                              <td className="p-3">
                                <div className="flex items-center gap-1 text-sm text-muted-foreground">
                                  <Calendar className="h-3 w-3 shrink-0" />
                                  <span className="text-xs truncate max-w-[100px]">{c.term}</span>
                                </div>
                              </td>
                              <td className="p-3">
                                <span className={`inline-flex items-center gap-1.5 text-xs px-2 py-1 rounded-full font-medium ${risk.class}`}>
                                  <span className={`w-1.5 h-1.5 rounded-full ${risk.dot}`} />
                                  {c.riskLevel}
                                </span>
                              </td>
                              <td className="p-3 text-xs text-muted-foreground whitespace-nowrap">
                                {new Date(c.createdAt).toLocaleDateString()}
                              </td>
                              <td className="p-3 text-right">
                                <button
                                  onClick={() => handleDownload(c)}
                                  disabled={downloadingId === c.id}
                                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border bg-card text-xs font-medium hover:bg-accent hover:border-primary/30 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                                  title="Download contract as PDF"
                                >
                                  {downloadingId === c.id ? (
                                    <Loader2 className="h-3.5 w-3.5 animate-spin" />
                                  ) : (
                                    <Download className="h-3.5 w-3.5" />
                                  )}
                                  {downloadingId === c.id ? 'PDF...' : 'PDF'}
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

            {/* Pending Review Alert */}
            {pendingCount > 0 && (
              <div className="flex items-start gap-3 p-4 rounded-xl border border-red-500/20 bg-red-500/5">
                <AlertTriangle className="h-5 w-5 text-red-500 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-red-500">
                    {pendingCount} contract{pendingCount !== 1 ? 's' : ''} pending human review
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">
                    SIGNAL agents have completed their analysis. <strong>Human legal review is required</strong>{' '}
                    before these contracts can proceed. Forward to legal counsel for final review,
                    negotiation, and execution. Agents cannot sign contracts.
                  </p>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </DashboardLayout>
  );
}
