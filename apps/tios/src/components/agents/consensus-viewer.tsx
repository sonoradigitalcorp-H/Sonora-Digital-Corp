'use client';

import { useState, useCallback } from 'react';
import {
  ChevronDown, ChevronRight, CheckCircle, XCircle, AlertTriangle,
  Users, Download, Loader2, FileText,
} from 'lucide-react';
import { downloadConsensusDecisionAsPDF } from '@/lib/report-pdf';

function confidenceColor(c: number): string {
  if (c >= 80) return 'text-green-500';
  if (c >= 60) return 'text-yellow-500';
  return 'text-red-500';
}

function confidenceBarColor(c: number): string {
  if (c >= 80) return 'bg-green-500';
  if (c >= 60) return 'bg-yellow-500';
  return 'bg-red-500';
}

function decisionIcon(decision: string) {
  const d = decision.toUpperCase();
  if (d === 'APPROVED') return <CheckCircle className="h-4 w-4 text-green-500" />;
  if (d === 'FLAGGED' || d === 'REJECTED') return <XCircle className="h-4 w-4 text-red-500" />;
  return <AlertTriangle className="h-4 w-4 text-amber-500" />;
}

function voteBadge(vote: string) {
  const colors: Record<string, string> = {
    APPROVED: 'bg-green-500/10 text-green-600 border-green-500/20',
    CONDITIONAL: 'bg-amber-500/10 text-amber-600 border-amber-500/20',
    PENDING: 'bg-gray-500/10 text-gray-600 border-gray-500/20',
    FLAGGED: 'bg-red-500/10 text-red-600 border-red-500/20',
  };
  const c = colors[vote] || colors.PENDING;
  return (
    <span className={`inline-block text-[9px] px-1.5 py-0.5 rounded font-semibold border ${c}`}>
      {vote}
    </span>
  );
}

export function ConsensusViewer({ decisions }: { decisions: any[] }) {
  const [expandedRow, setExpandedRow] = useState<string | null>(null);
  const [downloadingId, setDownloadingId] = useState<string | null>(null);

  const handleDownload = useCallback(async (d: any) => {
    setDownloadingId(d.id);
    try {
      downloadConsensusDecisionAsPDF(d);
    } catch (err) {
      console.error('Failed to download consensus PDF:', err);
    } finally {
      setDownloadingId(null);
    }
  }, []);

  return (
    <div className="rounded-xl border bg-card p-5">
      <div className="flex items-center justify-between mb-5">
        <div>
          <h2 className="font-semibold">Consensus Decisions</h2>
          <p className="text-xs text-muted-foreground mt-0.5">Recent agent voting outcomes</p>
        </div>
        <span className="text-xs text-muted-foreground">{decisions?.length || 0} decisions</span>
      </div>

      <div className="space-y-2">
        {(decisions || []).map((d: any) => {
          const isOpen = expandedRow === d.id;
          return (
            <div key={d.id} className="rounded-lg border bg-accent/20 overflow-hidden">
              {/* Header row */}
              <button
                onClick={() => setExpandedRow(isOpen ? null : d.id)}
                className="w-full flex items-center justify-between p-3 hover:bg-accent/50 transition-colors text-left"
              >
                <div className="flex items-center gap-2 min-w-0">
                  {isOpen ? <ChevronDown className="h-4 w-4 shrink-0 text-muted-foreground" /> : <ChevronRight className="h-4 w-4 shrink-0 text-muted-foreground" />}
                  <div className="min-w-0">
                    <p className="text-sm font-medium truncate">{d.type}</p>
                    <p className="text-xs text-muted-foreground truncate">{d.artistName}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3 shrink-0 ml-2">
                  {decisionIcon(d.decision)}
                  <span className="text-xs font-mono font-bold">{d.confidence}%</span>
                </div>
              </button>

              {/* Expanded content */}
              {isOpen && (
                <div className="border-t px-3 py-3 space-y-3">
                  {/* Summary cards */}
                  <div className="grid grid-cols-3 gap-2">
                    <div className="p-2 rounded-lg bg-primary/5 border border-primary/10 text-center">
                      <p className="text-xs text-muted-foreground">Decision</p>
                      <p className="text-sm font-semibold">{d.decision}</p>
                    </div>
                    <div className="p-2 rounded-lg bg-primary/5 border border-primary/10 text-center">
                      <p className="text-xs text-muted-foreground">Confidence</p>
                      <p className={`text-sm font-semibold ${confidenceColor(d.confidence)}`}>{d.confidence}%</p>
                    </div>
                    <div className="p-2 rounded-lg bg-primary/5 border border-primary/10 text-center">
                      <p className="text-xs text-muted-foreground">Date</p>
                      <p className="text-sm font-semibold">{d.date || 'Today'}</p>
                    </div>
                  </div>

                  {/* Confidence bar */}
                  <div className="h-1.5 rounded-full bg-muted overflow-hidden">
                    <div className={`h-full rounded-full ${confidenceBarColor(d.confidence)}`} style={{ width: `${d.confidence}%` }} />
                  </div>

                  {/* Participating agents */}
                  <div>
                    <div className="flex items-center gap-1.5 text-xs font-medium text-muted-foreground mb-2">
                      <Users className="h-3 w-3" /> Participating Agents ({d.agents?.length || 0})
                    </div>
                    <div className="flex flex-wrap gap-1.5">
                      {(d.agents || []).map((a: string, i: number) => (
                        <span key={i} className="text-xs px-2 py-1 rounded-md bg-accent font-medium">{a}</span>
                      ))}
                    </div>
                  </div>

                  {/* Agent Voting Details */}
                  {d.agentVotes && d.agentVotes.length > 0 && (
                    <div>
                      <div className="flex items-center gap-1.5 text-xs font-medium text-muted-foreground mb-2">
                        <FileText className="h-3 w-3" /> Agent Votes
                      </div>
                      <div className="space-y-1.5">
                        {d.agentVotes.map((av: any, i: number) => (
                          <div key={i} className="flex items-start gap-2 p-2 rounded-lg bg-accent/30">
                            <div className="flex-shrink-0 mt-0.5">
                              {av.vote === 'APPROVED' ? <CheckCircle className="h-3.5 w-3.5 text-green-500" /> :
                               av.vote === 'FLAGGED' ? <XCircle className="h-3.5 w-3.5 text-red-500" /> :
                               <AlertTriangle className="h-3.5 w-3.5 text-amber-500" />}
                            </div>
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-2 flex-wrap">
                                <span className="text-xs font-medium">{av.agent}</span>
                                {voteBadge(av.vote)}
                                <span className="text-[10px] text-muted-foreground">{av.confidence}%</span>
                              </div>
                              <p className="text-[10px] text-muted-foreground mt-0.5 leading-relaxed">{av.reason}</p>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Process Steps (collapsed) */}
                  {d.processSteps && d.processSteps.length > 0 && (
                    <details className="group">
                      <summary className="text-xs font-medium text-muted-foreground cursor-pointer hover:text-foreground transition-colors flex items-center gap-1">
                        <ChevronRight className="h-3 w-3 group-open:rotate-90 transition-transform" />
                        Decision Process ({d.processSteps.length} steps)
                      </summary>
                      <div className="mt-2 space-y-1.5 pl-4 border-l-2 border-primary/20">
                        {d.processSteps.map((step: any, i: number) => (
                          <div key={i} className="text-xs text-muted-foreground">
                            <span className="font-medium text-foreground">{step.agent}:</span>{' '}
                            {step.action}
                          </div>
                        ))}
                      </div>
                    </details>
                  )}

                  {/* Justification */}
                  {d.justification && (
                    <p className="text-xs text-muted-foreground leading-relaxed bg-accent/30 p-2 rounded-lg italic">
                      &ldquo;{d.justification}&rdquo;
                    </p>
                  )}

                  {/* Human handoff alert */}
                  <div className="flex items-start gap-2 p-3 rounded-lg border border-amber-500/20 bg-amber-500/5 mt-3">
                    <AlertTriangle className="h-4 w-4 text-amber-500 flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="text-xs font-semibold text-amber-500 uppercase tracking-wide">
                        HUMAN DECISION REQUIRED
                      </p>
                      <p className="text-[11px] text-muted-foreground mt-1 leading-relaxed">
                        SIGNAL agents have analyzed and recommended. Agents cannot make final decisions.
                        This recommendation requires <strong>human review and approval</strong> before
                        any action is taken. Please review agent votes, process steps, and justification above.
                      </p>
                    </div>
                  </div>

                  {/* Download PDF button */}
                  <div className="flex justify-end pt-2">
                    <button
                      onClick={() => handleDownload(d)}
                      disabled={downloadingId === d.id}
                      className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-primary text-primary-foreground text-xs font-medium hover:opacity-90 transition-opacity disabled:opacity-50"
                    >
                      {downloadingId === d.id ? (
                        <Loader2 className="h-3.5 w-3.5 animate-spin" />
                      ) : (
                        <Download className="h-3.5 w-3.5" />
                      )}
                      {downloadingId === d.id ? 'Generating PDF...' : 'Download Report'}
                    </button>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {(!decisions || decisions.length === 0) && (
        <div className="flex items-center justify-center py-8 text-sm text-muted-foreground">
          No consensus data available
        </div>
      )}
    </div>
  );
}
