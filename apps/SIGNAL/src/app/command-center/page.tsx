'use client';

import { useEffect, useState, useMemo, useCallback } from 'react';
import useSWR from 'swr';
import { DashboardLayout } from '@/components/dashboard/layout';
import {
  RefreshCw, Activity, Zap, Users, Cpu, Target, AlertTriangle, Clock,
  CheckCircle2, Loader2, Radio, BrainCircuit, FileBarChart, TrendingUp,
  Quote, Layers, ArrowUp, ArrowDown,
} from 'lucide-react';
import { generateQuote } from '@/lib/data-generator';

const API = process.env.NEXT_PUBLIC_API_URL || '';
const fetcher = (url: string) => fetch(url).then(r => { if (!r.ok) throw new Error('Failed to fetch'); return r.json(); });

/* ─── Types ─── */
interface Priority { rank: number; artistName: string; action: string; reason: string; deadline: string; }
interface Recommendation { agent: string; text: string; priority: string; }
interface ServiceHealth { name: string; role: string; status: string; uptime: string; tasksCompleted: number; tasksPending: number; lastActive: string; currentTask: string; }
interface BriefingData { date: string; summary: string; priorities: Priority[]; recommendations: Recommendation[]; }
interface HealthData { services: ServiceHealth[]; summary: { total: number; healthy: number; degraded: number; down: number }; agentPilot: { status: string; workflowsRunning: number; totalArtistsAnalyzed: number }; updatedAt: string; }

/* ─── Helpers ─── */
const formatTime = (iso?: string) => {
  if (!iso) return '-';
  try { return new Date(iso).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', timeZoneName: 'short' }); }
  catch { return iso; }
};

const timeAgo = (iso?: string) => {
  if (!iso) return '-';
  try {
    const diff = Date.now() - new Date(iso).getTime();
    const mins = Math.floor(diff / 60000);
    if (mins < 1) return 'just now';
    if (mins < 60) return `${mins}m ago`;
    return `${Math.floor(mins / 60)}h ${mins % 60}m ago`;
  } catch { return iso; }
};

const statusDot = (status: string) => ({
  bg: status?.toLowerCase() === 'healthy' || status?.toLowerCase() === 'online' ? 'bg-emerald-500 shadow-[0_0_6px_rgba(16,185,129,0.5)]'
    : status?.toLowerCase() === 'degraded' || status?.toLowerCase() === 'warning' ? 'bg-amber-500 shadow-[0_0_6px_rgba(245,158,11,0.5)]'
    : status?.toLowerCase() === 'down' || status?.toLowerCase() === 'offline' || status?.toLowerCase() === 'error' ? 'bg-red-500 shadow-[0_0_6px_rgba(239,68,68,0.5)]'
    : 'bg-muted-foreground',
  label: status || 'unknown',
});

/* ─── Priority Card ─── */
function PriorityCard({ priority }: { priority: Priority }) {
  const severity = priority.rank <= 2 ? 'critical' : priority.rank <= 4 ? 'high' : 'medium';
  const borderColor = severity === 'critical' ? 'border-l-red-500'
    : severity === 'high' ? 'border-l-amber-500'
    : 'border-l-primary';

  return (
    <div className={`flex items-center gap-3 p-3 rounded-lg border border-l-4 ${borderColor} bg-card/80 card-hover`}>
      <span className="text-lg font-bold text-muted-foreground w-6 text-center shrink-0">#{priority.rank}</span>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-semibold truncate">{priority.artistName}</p>
        <p className="text-xs text-muted-foreground truncate">{priority.action}</p>
      </div>
      <div className="hidden sm:block text-xs text-muted-foreground/70 max-w-[180px] truncate">
        {priority.reason}
      </div>
      <span className="text-[10px] font-mono text-amber-500/80 shrink-0">{priority.deadline}</span>
    </div>
  );
}

/* ─── Agent Card ─── */
function AgentCard({ service }: { service: ServiceHealth }) {
  const dot = statusDot(service.status);
  const tasksTotal = service.tasksCompleted + service.tasksPending;
  const completionPct = tasksTotal > 0 ? Math.round((service.tasksCompleted / tasksTotal) * 100) : 0;

  return (
    <div className="rounded-xl border bg-card/80 p-4 card-hover group relative overflow-hidden">
      {service.status === 'healthy' && (
        <div className="absolute top-0 left-4 right-4 h-px bg-gradient-to-r from-transparent via-emerald-500/50 to-transparent" />
      )}
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2.5">
          <span className={`h-2.5 w-2.5 rounded-full ${dot.bg}`} />
          <div>
            <p className="font-semibold text-sm group-hover:text-primary transition-colors">{service.name}</p>
            <p className="text-xs text-muted-foreground">{service.role}</p>
          </div>
        </div>
        <span className="text-[10px] font-mono text-muted-foreground">{service.uptime}</span>
      </div>
      <div className="flex items-center gap-3 text-xs text-muted-foreground mb-2">
        <div className="flex items-center gap-1">
          <CheckCircle2 className="h-3 w-3 text-emerald-500" />
          {service.tasksCompleted}
        </div>
        <div className="flex items-center gap-1">
          <Clock className="h-3 w-3 text-amber-500" />
          {service.tasksPending}
        </div>
      </div>
      {/* Task completion bar */}
      <div className="w-full h-1 rounded-full bg-muted overflow-hidden mb-2">
        <div className="h-full rounded-full bg-emerald-500 transition-all" style={{ width: `${completionPct}%` }} />
      </div>
      {service.currentTask && (
        <div className="flex items-start gap-1.5">
          <Activity className="h-3 w-3 text-primary mt-0.5 shrink-0" />
          <p className="text-[11px] text-muted-foreground leading-relaxed line-clamp-1">{service.currentTask}</p>
        </div>
      )}
    </div>
  );
}

/* ─── Skeleton ─── */
function Skeleton() {
  return (
    <div className="space-y-6 animate-pulse">
      <div className="h-24 rounded-xl bg-card border" />
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-4">
          <div className="h-48 rounded-xl bg-card border" />
          <div className="h-36 rounded-xl bg-card border" />
        </div>
        <div className="space-y-4">
          <div className="h-36 rounded-xl bg-card border" />
          <div className="h-36 rounded-xl bg-card border" />
        </div>
      </div>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════
   PAGE
   ═══════════════════════════════════════════════════════════ */
export default function CommandCenterPage() {
  const [now, setNow] = useState(new Date());
  useEffect(() => { const id = setInterval(() => setNow(new Date()), 1000); return () => clearInterval(id); }, []);

  const { data: briefing, error: briefingErr, isLoading: briefingLoading, mutate: briefingMutate } = useSWR<BriefingData>(`${API}/api/v1/command-center/briefing`, fetcher, { refreshInterval: 30000 });
  const { data: health, error: healthErr, isLoading: healthLoading, mutate: healthMutate } = useSWR<HealthData>(`${API}/api/v1/command-center/health`, fetcher, { refreshInterval: 15000 });

  const handleRefresh = useCallback(() => { briefingMutate(); healthMutate(); }, [briefingMutate, healthMutate]);
  const isLoading = briefingLoading || healthLoading;
  const hasError = briefingErr || healthErr;
  const quote = useMemo(() => generateQuote(), []);
  const healthSummary = health?.summary;
  const agentsPilot = health?.agentPilot;

  return (
    <DashboardLayout>
      <div className="p-6 space-y-6 max-w-[1600px] mx-auto">
        {/* ── Header ── */}
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-3">
              <Radio className="h-5 w-5 text-primary" />
              <h1 className="text-2xl font-bold tracking-tight">Command Center</h1>
            </div>
            <p className="text-muted-foreground mt-0.5 text-sm">
              {now.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit', timeZoneName: 'short' })}
            </p>
          </div>
          <div className="flex items-center gap-3">
            {healthSummary && (
              <div className="flex items-center gap-2 text-xs font-mono bg-card border rounded-lg px-3 py-2">
                <span className="flex items-center gap-1"><span className="h-2 w-2 rounded-full bg-emerald-500" />{healthSummary.healthy}</span>
                <span className="text-muted-foreground">/</span>
                <span className="flex items-center gap-1"><span className="h-2 w-2 rounded-full bg-amber-500" />{healthSummary.degraded}</span>
                <span className="text-muted-foreground">/</span>
                <span className="flex items-center gap-1"><span className="h-2 w-2 rounded-full bg-red-500" />{healthSummary.down}</span>
              </div>
            )}
            <button onClick={handleRefresh} disabled={isLoading} className="flex items-center gap-2 px-3 py-2 rounded-lg border bg-card text-sm hover:bg-accent transition-colors disabled:opacity-50">
              <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
              Refresh
            </button>
          </div>
        </div>

        {/* ── Quote Banner (compact) ── */}
        <div className="relative overflow-hidden rounded-xl border bg-gradient-to-r from-primary/5 via-primary/10 to-primary/5 p-4">
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,rgba(59,130,246,0.06),transparent_60%)]" />
          <div className="relative flex items-start gap-2.5">
            <Quote className="h-4 w-4 text-primary/40 mt-0.5 shrink-0" />
            <p className="text-xs text-muted-foreground italic leading-relaxed">&ldquo;{quote}&rdquo;</p>
          </div>
        </div>

        {/* ── Error Banner ── */}
        {hasError && (
          <div className="flex items-center gap-2 p-4 rounded-xl border border-red-500/20 bg-red-500/5 text-red-500 text-sm">
            <AlertTriangle className="h-4 w-4 shrink-0" />
            <span>Failed to load data. Retrying automatically&hellip;</span>
          </div>
        )}

        {/* ── Loading ── */}
        {isLoading && !briefing && !health && <Skeleton />}

        {/* ── Content ── */}
        {(briefing || health) && (
          <>
            {/* ── Quick Actions ── */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <a href="/market" className="flex items-center gap-3 p-4 rounded-xl border bg-gradient-to-r from-emerald-500/5 to-transparent hover:from-emerald-500/10 hover:border-emerald-500/30 transition-all group">
                <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-emerald-500/10 group-hover:bg-emerald-500/20 transition-colors">
                  <TrendingUp className="h-5 w-5 text-emerald-500" />
                </div>
                <div>
                  <p className="text-sm font-semibold">Full Market Report</p>
                  <p className="text-xs text-muted-foreground">Trends, stats &amp; analysis</p>
                </div>
              </a>
              <a href="/artists" className="flex items-center gap-3 p-4 rounded-xl border bg-gradient-to-r from-blue-500/5 to-transparent hover:from-blue-500/10 hover:border-blue-500/30 transition-all group">
                <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-blue-500/10 group-hover:bg-blue-500/20 transition-colors">
                  <Users className="h-5 w-5 text-blue-500" />
                </div>
                <div>
                  <p className="text-sm font-semibold">View All Artists</p>
                  <p className="text-xs text-muted-foreground">110 indie Latin artists</p>
                </div>
              </a>
              <a href="/alerts" className="flex items-center gap-3 p-4 rounded-xl border bg-gradient-to-r from-amber-500/5 to-transparent hover:from-amber-500/10 hover:border-amber-500/30 transition-all group">
                <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-amber-500/10 group-hover:bg-amber-500/20 transition-colors">
                  <AlertTriangle className="h-5 w-5 text-amber-500" />
                </div>
                <div>
                  <p className="text-sm font-semibold">View All Alerts</p>
                  <p className="text-xs text-muted-foreground">Pending reviews &amp; flags</p>
                </div>
              </a>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* ── Left Column (2/3) ── */}
              <div className="lg:col-span-2 space-y-6">
                {/* Executive Briefing */}
                <div className="rounded-xl border bg-card/80 overflow-hidden">
                  <div className="flex items-center gap-2 p-4 border-b border-border/50 bg-gradient-to-r from-primary/5 to-transparent">
                    <FileBarChart className="h-4 w-4 text-primary" />
                    <h2 className="font-semibold text-sm">Executive Briefing</h2>
                    {briefing?.summary && <span className="text-xs text-muted-foreground ml-auto">{briefing.date}</span>}
                  </div>
                  <div className="p-4 space-y-4">
                    {briefing?.summary && <p className="text-xs text-muted-foreground leading-relaxed">{briefing.summary}</p>}
                    {briefing?.priorities && briefing.priorities.length > 0 && (
                      <div className="space-y-3">
                        <div className="flex items-center gap-2 text-xs text-muted-foreground font-medium uppercase tracking-wider">
                          <Target className="h-3 w-3" /> Top Priorities
                        </div>
                        <div className="space-y-2">
                          {briefing.priorities.slice(0, 6).map(p => <PriorityCard key={p.rank} priority={p} />)}
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                {/* Recommendations */}
                {briefing?.recommendations && briefing.recommendations.length > 0 && (
                  <div className="rounded-xl border bg-card/80 overflow-hidden">
                    <div className="flex items-center gap-2 p-4 border-b border-border/50 bg-gradient-to-r from-purple-500/5 to-transparent">
                      <BrainCircuit className="h-4 w-4 text-purple-500" />
                      <h2 className="font-semibold text-sm">Agent Recommendations</h2>
                    </div>
                    <div className="divide-y divide-border/30">
                      {briefing.recommendations.map((rec, i) => (
                        <div key={i} className="flex items-center gap-3 p-3 hover:bg-muted/30 transition-colors">
                          <span className={`shrink-0 text-[10px] font-semibold uppercase px-2 py-0.5 rounded ${
                            rec.priority === 'critical' ? 'bg-red-500/10 text-red-500'
                            : rec.priority === 'high' ? 'bg-amber-500/10 text-amber-500'
                            : 'bg-blue-500/10 text-blue-500'
                          }`}>{rec.priority}</span>
                          <div className="min-w-0 flex-1">
                            <p className="text-xs font-semibold text-foreground">{rec.agent}</p>
                            <p className="text-xs text-muted-foreground mt-0.5">{rec.text}</p>
                          </div>
                          <ArrowUp className="h-3.5 w-3.5 text-muted-foreground/40" />
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Agent Health Grid */}
                {health?.services && health.services.length > 0 && (
                  <div className="rounded-xl border bg-card/80 overflow-hidden">
                    <div className="flex items-center gap-2 p-4 border-b border-border/50 bg-gradient-to-r from-emerald-500/5 to-transparent">
                      <Cpu className="h-4 w-4 text-emerald-500" />
                      <h2 className="font-semibold text-sm">Agent Health</h2>
                      <span className="text-[10px] font-mono text-muted-foreground ml-auto">Updated {formatTime(health.updatedAt)}</span>
                    </div>
                    <div className="p-4">
                      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-3">
                        {health.services.map(s => <AgentCard key={s.name} service={s} />)}
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* ── Right Column (1/3) ── */}
              <div className="space-y-6">
                {/* Agent Pilot */}
                {agentsPilot && (
                  <div className="rounded-xl border bg-card/80 overflow-hidden">
                    <div className="flex items-center gap-2 p-4 border-b border-border/50 bg-gradient-to-r from-blue-500/5 to-transparent">
                      <Zap className="h-4 w-4 text-blue-500" />
                      <h2 className="font-semibold text-sm">Agent Pilot</h2>
                    </div>
                    <div className="p-4 space-y-4">
                      <div className="flex items-center justify-between">
                        <span className="text-xs text-muted-foreground">Status</span>
                        <span className="flex items-center gap-1.5 text-xs font-medium">
                          <span className={`h-2 w-2 rounded-full ${statusDot(agentsPilot.status).bg}`} />
                          {agentsPilot.status}
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-xs text-muted-foreground">Workflows Running</span>
                        <span className="text-xl font-bold font-mono text-primary">{agentsPilot.workflowsRunning}</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-xs text-muted-foreground">Artists Analyzed</span>
                        <span className="text-xl font-bold font-mono text-emerald-500">{agentsPilot.totalArtistsAnalyzed.toLocaleString()}</span>
                      </div>
                    </div>
                  </div>
                )}

                {/* Health Summary */}
                {healthSummary && (
                  <div className="rounded-xl border bg-card/80 overflow-hidden">
                    <div className="flex items-center gap-2 p-4 border-b border-border/50 bg-gradient-to-r from-cyan-500/5 to-transparent">
                      <Layers className="h-4 w-4 text-cyan-500" />
                      <h2 className="font-semibold text-sm">Service Summary</h2>
                    </div>
                    <div className="p-4 space-y-3">
                      <div className="rounded-lg bg-emerald-500/5 border border-emerald-500/10 p-3">
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-xs text-muted-foreground">Healthy</span>
                          <span className="text-xl font-bold font-mono text-emerald-500">{healthSummary.healthy}</span>
                        </div>
                        <div className="w-full h-1.5 rounded-full bg-muted overflow-hidden">
                          <div className="h-full rounded-full bg-emerald-500 transition-all" style={{ width: `${(healthSummary.healthy / Math.max(healthSummary.total, 1)) * 100}%` }} />
                        </div>
                      </div>
                      <div className="space-y-2">
                        <div className="flex justify-between text-xs text-muted-foreground">
                          <span>Degraded</span>
                          <span className="font-mono text-amber-500">{healthSummary.degraded}</span>
                        </div>
                        <div className="flex justify-between text-xs text-muted-foreground">
                          <span>Down</span>
                          <span className="font-mono text-red-500">{healthSummary.down}</span>
                        </div>
                        <div className="divider" />
                        <div className="flex justify-between text-xs text-muted-foreground">
                          <span>Total services</span>
                          <span className="font-mono">{healthSummary.total}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Live Feed */}
                {health?.services && health.services.length > 0 && (
                  <div className="rounded-xl border bg-card/80 overflow-hidden">
                    <div className="flex items-center gap-2 p-4 border-b border-border/50 bg-gradient-to-r from-amber-500/5 to-transparent">
                      <Activity className="h-4 w-4 text-amber-500" />
                      <h2 className="font-semibold text-sm">Live Feed</h2>
                      <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse ml-auto" />
                    </div>
                    <div className="p-3 max-h-[300px] overflow-y-auto">
                      {health.services
                        .sort((a, b) => new Date(b.lastActive).getTime() - new Date(a.lastActive).getTime())
                        .slice(0, 10)
                        .map(s => {
                          const dot = statusDot(s.status);
                          return (
                            <div key={s.name + s.lastActive} className="flex items-start gap-3 py-2 border-b border-border/30 last:border-0">
                              <span className={`mt-1.5 h-2 w-2 rounded-full shrink-0 ${dot.bg}`} />
                              <div className="min-w-0 flex-1">
                                <div className="flex items-center gap-2">
                                  <span className="text-xs font-semibold text-foreground">{s.name}</span>
                                  <span className="text-[10px] text-muted-foreground/50">{formatTime(s.lastActive)}</span>
                                </div>
                                <div className="flex items-center gap-2 mt-0.5">
                                  <p className="text-xs text-muted-foreground truncate flex-1">{s.currentTask || 'Idle'}</p>
                                  <span className="text-[10px] text-muted-foreground/60">{timeAgo(s.lastActive)}</span>
                                </div>
                              </div>
                            </div>
                          );
                        })}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </>
        )}
      </div>
    </DashboardLayout>
  );
}
