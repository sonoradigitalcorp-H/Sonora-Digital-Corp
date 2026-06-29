'use client';

import { DashboardLayout } from '@/components/dashboard/layout';
import {
  Star, Loader2, AlertCircle, Search, RefreshCw, X, ChevronDown, ChevronUp,
  DollarSign, TrendingUp, Users, Music2, Phone, Mail, Activity
} from 'lucide-react';
import useSWR from 'swr';
import { useState, useMemo, useCallback, useEffect, useRef } from 'react';

const fetcher = (url: string) => fetch(url).then(r => r.json());

const STAGE_META: Record<string, { label: string; labelEs: string; color: string }> = {
  discovery: { label: 'Discovery', labelEs: 'Descubrimiento', color: 'bg-blue-500' },
  initial_contact: { label: 'Initial Contact', labelEs: 'Contacto Inicial', color: 'bg-purple-500' },
  due_diligence: { label: 'Due Diligence', labelEs: 'Debida Diligencia', color: 'bg-amber-500' },
  negotiation: { label: 'Negotiation', labelEs: 'Negociación', color: 'bg-orange-500' },
  closed: { label: 'Closed', labelEs: 'Cerrado', color: 'bg-green-500' },
};

const COST_BREAKDOWN = [
  { label: 'Advance', labelEs: 'Anticipo', pct: 45, color: '#3B82F6' },
  { label: 'Marketing', labelEs: 'Marketing', pct: 25, color: '#8B5CF6' },
  { label: 'Production', labelEs: 'Producción', pct: 18, color: '#F59E0B' },
  { label: 'Legal', labelEs: 'Legal', pct: 7, color: '#10B981' },
  { label: 'Operations', labelEs: 'Operaciones', pct: 5, color: '#EF4444' },
];

const WORKFLOW_AGENTS = [
  { name: 'Analyst Agent', role: 'Data & Scoring', roleEs: 'Datos & Scoring', status: 'completed' },
  { name: 'Writer Agent', role: 'Content & Briefs', roleEs: 'Contenido & Briefs', status: 'completed' },
  { name: 'Legal Agent', role: 'Compliance & Contracts', roleEs: 'Compliance & Contratos', status: 'in_progress' },
  { name: 'GBrain', role: 'Orchestrator', roleEs: 'Orquestador', status: 'pending' },
  { name: 'Hermes', role: 'Auto-improvement', roleEs: 'Auto-mejora', status: 'pending' },
];

const PRIORITY_STYLES: Record<string, string> = {
  critical: 'text-red-500 bg-red-500/10 border-red-500/20',
  high: 'text-amber-500 bg-amber-500/10 border-amber-500/20',
  medium: 'text-blue-500 bg-blue-500/10 border-blue-500/20',
  low: 'text-muted-foreground bg-muted border-border',
};

const SCORE_COLORS = [
  { min: 90, color: 'text-emerald-500', bar: 'bg-emerald-500' },
  { min: 80, color: 'text-green-500', bar: 'bg-green-500' },
  { min: 70, color: 'text-amber-500', bar: 'bg-amber-500' },
  { min: 0, color: 'text-red-500', bar: 'bg-red-500' },
];

function getScoreColor(score: number) {
  return SCORE_COLORS.find(s => score >= s.min) || SCORE_COLORS[SCORE_COLORS.length - 1];
}

function formatCurrency(n: number) {
  if (n >= 1_000_000) return `$${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `$${(n / 1_000).toFixed(0)}K`;
  return `$${n.toLocaleString()}`;
}

function formatNumber(n: number) {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(0)}K`;
  return n.toLocaleString();
}

function useDebounce(value: string, delay: number) {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const t = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(t);
  }, [value, delay]);
  return debounced;
}

function Skeleton({ className }: { className?: string }) {
  return <div className={`animate-pulse rounded bg-muted ${className || ''}`} />;
}

function PieChart({ breakdown }: { breakdown: { label: string; labelEs: string; pct: number; color: string }[] }) {
  const gradient = breakdown.map((b, i) => {
    const start = breakdown.slice(0, i).reduce((a, c) => a + c.pct, 0);
    return `${b.color} ${start}% ${start + b.pct}%`;
  }).join(', ');

  return (
    <div className="flex items-center gap-4">
      <div className="relative w-24 h-24 shrink-0">
        <div
          className="w-24 h-24 rounded-full"
          style={{ background: `conic-gradient(${gradient})` }}
        />
        <div className="absolute inset-3 rounded-full bg-card flex items-center justify-center">
          <span className="text-xs font-bold">100%</span>
        </div>
      </div>
      <div className="space-y-1.5 text-xs">
        {breakdown.map(b => (
          <div key={b.label} className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full shrink-0" style={{ background: b.color }} />
            <span className="text-muted-foreground w-20">{b.labelEs}</span>
            <span className="font-medium w-8">{b.pct}%</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function SigningsPage() {
  const [lang, setLang] = useState<'en' | 'es'>('en');
  const { data, error, isLoading, mutate } = useSWR('/api/v1/signings', fetcher, { revalidateOnFocus: false });
  const [search, setSearch] = useState('');
  const [stageFilter, setStageFilter] = useState('');
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const debouncedSearch = useDebounce(search, 300);
  const searchRef = useRef<HTMLInputElement>(null);

  const t = useCallback((en: string, es: string) => lang === 'en' ? en : es, [lang]);

  const filteredPipeline = useMemo(() => {
    if (!data?.pipeline) return [];
    return data.pipeline.filter((a: any) => {
      const matchSearch = !debouncedSearch ||
        a.name.toLowerCase().includes(debouncedSearch.toLowerCase()) ||
        a.genres.some((g: string) => g.toLowerCase().includes(debouncedSearch.toLowerCase())) ||
        a.contact.toLowerCase().includes(debouncedSearch.toLowerCase());
      const matchStage = !stageFilter || a.stage === stageFilter;
      return matchSearch && matchStage;
    });
  }, [data, debouncedSearch, stageFilter]);

  const handleRefresh = useCallback(() => {
    mutate();
    setExpandedId(null);
  }, [mutate]);

  return (
    <DashboardLayout>
      <div className="p-4 sm:p-6 space-y-6 max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold tracking-tight">
              {t('Signing Pipeline', 'Pipeline de Firmas')}
            </h1>
            <p className="text-muted-foreground text-sm mt-1">
              {t('Artist acquisition pipeline and deal flow', 'Pipeline de adquisición de artistas y flujo de deals')}
            </p>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setLang(lang === 'en' ? 'es' : 'en')}
              className="text-xs px-2 py-1 rounded-md border border-border hover:bg-accent transition-colors font-medium"
            >
              {lang === 'en' ? 'ES' : 'EN'}
            </button>
            <button
              onClick={handleRefresh}
              disabled={isLoading}
              className="flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 transition-colors font-medium disabled:opacity-50"
            >
              <RefreshCw className={`h-3.5 w-3.5 ${isLoading ? 'animate-spin' : ''}`} />
              {t('Refresh', 'Actualizar')}
            </button>
          </div>
        </div>

        {/* Error */}
        {error && (
          <div className="flex items-center gap-2 p-4 rounded-xl border border-red-500/20 bg-red-500/5 text-red-500">
            <AlertCircle className="h-4 w-4 shrink-0" />
            <span className="text-sm">
              {t('Failed to load signing data', 'Error al cargar datos de firmas')}
            </span>
          </div>
        )}

        {/* Loading Skeleton */}
        {isLoading && !data && (
          <div className="space-y-6">
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
              {Array.from({ length: 5 }).map((_, i) => (
                <div key={i} className="rounded-xl border bg-card p-4">
                  <Skeleton className="h-8 w-12 mb-2" />
                  <Skeleton className="h-3 w-24 mb-1" />
                  <Skeleton className="h-3 w-16" />
                </div>
              ))}
            </div>
            <div className="rounded-xl border bg-card overflow-hidden">
              <div className="p-4 border-b"><Skeleton className="h-5 w-40" /></div>
              <div className="divide-y">
                {Array.from({ length: 6 }).map((_, i) => (
                  <div key={i} className="p-4 flex items-center gap-4">
                    <Skeleton className="h-4 w-32" />
                    <Skeleton className="h-5 w-20 rounded-full" />
                    <Skeleton className="h-3 w-24" />
                    <Skeleton className="h-4 w-16 ml-auto" />
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {data && (
          <>
            {/* Summary Cards */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <div className="rounded-xl border bg-card p-3 sm:p-4">
                <p className="text-xs text-muted-foreground mb-1">{t('Total Artists', 'Artistas Totales')}</p>
                <p className="text-xl sm:text-2xl font-bold">{data.total}</p>
                <p className="text-[10px] text-muted-foreground mt-0.5">
                  {t('In pipeline', 'En pipeline')}
                </p>
              </div>
              <div className="rounded-xl border bg-card p-3 sm:p-4">
                <p className="text-xs text-muted-foreground mb-1">{t('Total Value', 'Valor Total')}</p>
                <p className="text-xl sm:text-2xl font-bold text-emerald-500">{formatCurrency(data.totalValue)}</p>
                <p className="text-[10px] text-muted-foreground mt-0.5">
                  {t('Combined deals', 'Deals combinados')}
                </p>
              </div>
              <div className="rounded-xl border bg-card p-3 sm:p-4">
                <p className="text-xs text-muted-foreground mb-1">{t('Avg Score', 'Score Promedio')}</p>
                <p className="text-xl sm:text-2xl font-bold text-primary">
                  {data.pipeline.length ? Math.round(data.pipeline.reduce((a: number, p: any) => a + p.score, 0) / data.pipeline.length) : 0}
                </p>
                <p className="text-[10px] text-muted-foreground mt-0.5">
                  {t('Pipeline average', 'Promedio del pipeline')}
                </p>
              </div>
              <div className="rounded-xl border bg-card p-3 sm:p-4">
                <p className="text-xs text-muted-foreground mb-1">{t('Avg Value', 'Valor Promedio')}</p>
                <p className="text-xl sm:text-2xl font-bold text-amber-500">
                  {data.pipeline.length ? formatCurrency(Math.round(data.totalValue / data.pipeline.length)) : '$0'}
                </p>
                <p className="text-[10px] text-muted-foreground mt-0.5">
                  {t('Per artist deal', 'Deal por artista')}
                </p>
              </div>
            </div>

            {/* Pipeline Stages */}
            <div className="rounded-xl border bg-card p-4 sm:p-5">
              <h2 className="font-semibold text-sm mb-3 flex items-center gap-2">
                <Activity className="h-4 w-4 text-primary" />
                {t('Pipeline Stages', 'Etapas del Pipeline')}
              </h2>
              <div className="grid grid-cols-1 sm:grid-cols-5 gap-3">
                {data.stages.map((s: any) => {
                  const meta = STAGE_META[s.id] || {};
                  const pct = data.total ? Math.round((s.value / data.totalValue) * 100) : 0;
                  return (
                    <div key={s.id} className="rounded-lg border bg-card p-3">
                      <div className="flex items-center justify-between mb-2">
                        <span className={`text-xs font-semibold px-1.5 py-0.5 rounded ${meta.color} text-white`}>
                          {t(meta.label || s.label, meta.labelEs || s.label)}
                        </span>
                        <span className={`text-lg font-bold ${meta.color ? meta.color.replace('bg-', 'text-') : ''}`}>
                          {s.count}
                        </span>
                      </div>
                      <div className="h-2 rounded-full bg-muted overflow-hidden mb-1.5">
                        <div
                          className={`h-full rounded-full transition-all duration-500 ${meta.color}`}
                          style={{ width: `${pct}%` }}
                        />
                      </div>
                      <p className="text-[10px] text-muted-foreground">
                        {formatCurrency(s.value)} — {pct}%
                      </p>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Search / Filter */}
            <div className="flex flex-col sm:flex-row gap-3">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <input
                  ref={searchRef}
                  type="text"
                  value={search}
                  onChange={e => setSearch(e.target.value)}
                  placeholder={t('Search by name, genre, contact...', 'Buscar por nombre, género, contacto...')}
                  className="w-full h-9 pl-9 pr-8 rounded-lg border border-border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary/30"
                />
                {search && (
                  <button onClick={() => { setSearch(''); searchRef.current?.focus(); }} className="absolute right-2 top-1/2 -translate-y-1/2">
                    <X className="h-4 w-4 text-muted-foreground hover:text-foreground" />
                  </button>
                )}
              </div>
              <select
                value={stageFilter}
                onChange={e => setStageFilter(e.target.value)}
                className="h-9 px-3 rounded-lg border border-border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary/30"
              >
                <option value="">{t('All Stages', 'Todas las etapas')}</option>
                {data.stages.map((s: any) => {
                  const meta = STAGE_META[s.id] || {};
                  return (
                    <option key={s.id} value={s.id}>
                      {t(meta.label || s.label, meta.labelEs || s.label)} ({s.count})
                    </option>
                  );
                })}
              </select>
            </div>

            {/* Pipeline Table */}
            <div className="rounded-xl border bg-card overflow-hidden">
              <div className="p-4 border-b flex items-center justify-between">
                <h2 className="font-semibold text-sm flex items-center gap-2">
                  <Star className="h-4 w-4 text-primary" />
                  {t('Artist Pipeline', 'Pipeline de Artistas')}
                  <span className="text-xs font-normal text-muted-foreground">({filteredPipeline.length})</span>
                </h2>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b bg-muted/50">
                      <th className="text-left text-xs font-medium text-muted-foreground p-3 pl-4">{t('Artist', 'Artista')}</th>
                      <th className="text-left text-xs font-medium text-muted-foreground p-3">{t('Score', 'Puntaje')}</th>
                      <th className="text-left text-xs font-medium text-muted-foreground p-3">{t('Stage', 'Etapa')}</th>
                      <th className="text-left text-xs font-medium text-muted-foreground p-3">{t('Growth', 'Crec.')}</th>
                      <th className="text-left text-xs font-medium text-muted-foreground p-3">{t('Listeners', 'Oyentes')}</th>
                      <th className="text-left text-xs font-medium text-muted-foreground p-3">{t('Deal', 'Deal')}</th>
                      <th className="text-left text-xs font-medium text-muted-foreground p-3">{t('Priority', 'Prioridad')}</th>
                      <th className="text-left text-xs font-medium text-muted-foreground p-3 pr-4">{t('Contact', 'Contacto')}</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y">
                    {filteredPipeline.length === 0 && (
                      <tr>
                        <td colSpan={8} className="p-8 text-center text-sm text-muted-foreground">
                          {t('No artists match your search', 'Ningún artista coincide con tu búsqueda')}
                        </td>
                      </tr>
                    )}
                    {filteredPipeline.map((a: any) => {
                      const sc = getScoreColor(a.score);
                      const stageMeta = STAGE_META[a.stage] || {};
                      const isExpanded = expandedId === a.id;
                      return (
                        <tr key={a.id} className="group">
                          <td colSpan={8} className="p-0">
                            <div
                              onClick={() => setExpandedId(isExpanded ? null : a.id)}
                              className="flex items-center w-full p-3 pl-4 pr-4 hover:bg-accent/50 transition-colors cursor-pointer"
                            >
                              <div className="flex-1 min-w-0 flex items-center gap-2">
                                <span className="text-base">{a.image}</span>
                                <div className="min-w-0">
                                  <p className="text-sm font-medium truncate">{a.name}</p>
                                  <p className="text-[10px] text-muted-foreground truncate">{a.genres?.join(', ')}</p>
                                </div>
                              </div>
                              <div className="w-24 flex items-center gap-1.5">
                                <div className="h-1.5 w-12 rounded-full bg-muted overflow-hidden">
                                  <div className={`h-full rounded-full ${sc.bar}`} style={{ width: `${a.score}%` }} />
                                </div>
                                <span className={`text-xs font-mono font-medium ${sc.color}`}>{a.score}</span>
                              </div>
                              <div className="w-28 px-2">
                                <span className={`text-[10px] px-1.5 py-0.5 rounded-full font-medium ${stageMeta.color ? 'text-white' : ''}`}
                                  style={stageMeta.color ? {} : {}}>
                                  {t(stageMeta.label || a.stage, stageMeta.labelEs || a.stage)}
                                </span>
                              </div>
                              <div className="w-24 flex items-center gap-1.5">
                                <div className="h-4 w-10 rounded-sm bg-muted overflow-hidden flex items-end">
                                  <div
                                    className={`w-full rounded-sm transition-all ${a.growth >= 30 ? 'bg-emerald-500' : a.growth >= 15 ? 'bg-green-500' : 'bg-amber-500'}`}
                                    style={{ height: `${Math.min(100, a.growth)}%` }}
                                  />
                                </div>
                                <span className={`text-xs font-medium ${a.growth >= 20 ? 'text-green-500' : 'text-amber-500'}`}>
                                  +{a.growth}%
                                </span>
                              </div>
                              <div className="w-24 text-sm text-muted-foreground font-mono text-xs">
                                <div className="flex items-center gap-1">
                                  <Users className="h-3 w-3" />
                                  {formatNumber(a.listeners)}
                                </div>
                              </div>
                              <div className="w-24 text-sm font-medium font-mono">
                                {formatCurrency(a.value)}
                              </div>
                              <div className="w-24">
                                <span className={`text-[10px] px-1.5 py-0.5 rounded-full font-medium border ${PRIORITY_STYLES[a.priority] || ''}`}>
                                  {a.priority}
                                </span>
                              </div>
                              <div className="w-32 text-xs text-muted-foreground truncate flex items-center gap-1">
                                <Mail className="h-3 w-3 shrink-0" />
                                <span className="truncate">{a.contact}</span>
                              </div>
                              <div className="w-6 flex justify-end">
                                {isExpanded ? <ChevronUp className="h-4 w-4 text-muted-foreground" /> : <ChevronDown className="h-4 w-4 text-muted-foreground" />}
                              </div>
                            </div>
                            {/* Expandable Row */}
                            {isExpanded && (
                              <div className="bg-muted/30 border-t px-4 sm:px-6 py-4 space-y-4">
                                {/* Cost Breakdown */}
                                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                                  <div>
                                    <h3 className="text-sm font-semibold mb-3 flex items-center gap-2">
                                      <DollarSign className="h-4 w-4 text-primary" />
                                      {t('Deal Breakdown', 'Desglose del Deal')}
                                      <span className="text-xs font-mono text-muted-foreground">{formatCurrency(a.value)}</span>
                                    </h3>
                                    <div className="flex flex-col sm:flex-row items-start gap-4">
                                      <PieChart breakdown={COST_BREAKDOWN} />
                                      <div className="flex-1 w-full space-y-1.5 text-xs">
                                        {COST_BREAKDOWN.map(b => {
                                          const amount = Math.round(a.value * b.pct / 100);
                                          return (
                                            <div key={b.label} className="flex items-center gap-2">
                                              <span className="w-2 h-2 rounded-full shrink-0" style={{ background: b.color }} />
                                              <span className="text-muted-foreground w-24">{b.labelEs}</span>
                                              <div className="flex-1 h-1.5 rounded-full bg-muted overflow-hidden">
                                                <div className="h-full rounded-full" style={{ width: `${b.pct}%`, background: b.color }} />
                                              </div>
                                              <span className="font-mono font-medium w-20 text-right">{formatCurrency(amount)}</span>
                                              <span className="text-muted-foreground w-8 text-right">{b.pct}%</span>
                                            </div>
                                          );
                                        })}
                                      </div>
                                    </div>
                                  </div>
                                  {/* Workflow Agents */}
                                  <div>
                                    <h3 className="text-sm font-semibold mb-3 flex items-center gap-2">
                                      <Activity className="h-4 w-4 text-primary" />
                                      {t('Agent Workflow', 'Workflow de Agentes')}
                                    </h3>
                                    <div className="space-y-2">
                                      {WORKFLOW_AGENTS.map(agent => {
                                        const statusStyles: Record<string, string> = {
                                          completed: 'text-green-500 border-green-500/30 bg-green-500/5',
                                          in_progress: 'text-amber-500 border-amber-500/30 bg-amber-500/5',
                                          pending: 'text-muted-foreground border-border bg-muted/30',
                                        };
                                        return (
                                          <div key={agent.name} className="flex items-center gap-3 p-2 rounded-lg border text-xs"
                                            style={{ borderColor: 'inherit' }}>
                                            <div className={`w-2 h-2 rounded-full ${agent.status === 'completed' ? 'bg-green-500' : agent.status === 'in_progress' ? 'bg-amber-500 animate-pulse' : 'bg-muted-foreground'}`} />
                                            <div className="flex-1">
                                              <p className="font-medium">{agent.name}</p>
                                              <p className="text-muted-foreground">{lang === 'en' ? agent.role : agent.roleEs}</p>
                                            </div>
                                            <span className={`text-[10px] px-1.5 py-0.5 rounded-full border font-medium ${statusStyles[agent.status]}`}>
                                              {agent.status === 'completed' ? t('Done', 'Listo') : agent.status === 'in_progress' ? t('Working', 'Trabajando') : t('Pending', 'Pendiente')}
                                            </span>
                                          </div>
                                        );
                                      })}
                                    </div>
                                  </div>
                                </div>
                                {/* Genres & Contact Details */}
                                <div className="flex flex-wrap items-center gap-3 text-xs text-muted-foreground border-t border-border pt-3">
                                  <div className="flex items-center gap-1.5">
                                    <Music2 className="h-3 w-3" />
                                    <span className="font-medium text-foreground">
                                      {t('Genres', 'Géneros')}:
                                    </span>
                                    {a.genres?.join(', ')}
                                  </div>
                                  <div className="flex items-center gap-1.5">
                                    <Phone className="h-3 w-3" />
                                    <span className="font-medium text-foreground">
                                      {t('Contact', 'Contacto')}:
                                    </span>
                                    {a.contact}
                                  </div>
                                </div>
                              </div>
                            )}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        )}
      </div>
    </DashboardLayout>
  );
}
