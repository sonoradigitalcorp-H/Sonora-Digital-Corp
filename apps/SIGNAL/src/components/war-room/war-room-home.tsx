'use client';

import { useState } from 'react';
import useSWR from 'swr';
import {
  Clock, Users, TrendingUp, AlertTriangle, Target, Shield, Star,
  Sparkles, Music2, Globe, ChevronRight, FileText,
  MessageSquare, CheckCircle, XCircle, HelpCircle, Loader2,
} from 'lucide-react';

const fetcher = (url: string) => fetch(url).then(r => {
  if (!r.ok) throw new Error('Failed to load war room data');
  return r.json();
});

interface WarRoomHomeProps {
  warRoomId: string;
}

interface WarRoomData {
  id: string;
  artist: {
    name: string;
    score: number;
    image: string;
    photoUrl?: string;
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

export function WarRoomHome({ warRoomId }: WarRoomHomeProps) {
  const [language, setLanguage] = useState<'en' | 'es'>('en');
  const t = (en: string, es: string) => language === 'en' ? en : es;

  const { data, error, isLoading } = useSWR<WarRoomData>(
    `/api/v1/war-rooms/${warRoomId}`,
    fetcher,
    { refreshInterval: 30000 }
  );

  if (isLoading) {
    return (
      <div className="p-6 space-y-6 max-w-[1600px] mx-auto">
        <div className="flex justify-end">
          <div className="h-8 w-16 rounded-lg bg-muted animate-pulse" />
        </div>
        <div className="rounded-2xl border bg-card p-8">
          <div className="flex items-center gap-6">
            <div className="w-24 h-24 rounded-2xl bg-muted animate-pulse" />
            <div className="space-y-3 flex-1">
              <div className="h-8 w-64 bg-muted animate-pulse rounded" />
              <div className="h-4 w-96 bg-muted animate-pulse rounded" />
              <div className="flex gap-6 mt-4">
                {Array.from({ length: 5 }).map((_, i) => (
                  <div key={i} className="space-y-2">
                    <div className="h-5 w-12 bg-muted animate-pulse rounded" />
                    <div className="h-3 w-16 bg-muted animate-pulse rounded" />
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
        <div className="grid grid-cols-5 gap-3">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="h-20 rounded-xl bg-muted animate-pulse" />
          ))}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 h-96 rounded-xl bg-muted animate-pulse" />
          <div className="h-96 rounded-xl bg-muted animate-pulse" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 max-w-[1600px] mx-auto">
        <div className="flex items-center gap-3 p-6 rounded-2xl border border-red-500/20 bg-red-500/5">
          <AlertTriangle className="h-6 w-6 text-red-500" />
          <div>
            <p className="font-semibold text-red-500">{t('Failed to load war room', 'Error al cargar war room')}</p>
            <p className="text-sm text-muted-foreground mt-1">{error.message}</p>
          </div>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="p-6 max-w-[1600px] mx-auto">
        <div className="flex items-center gap-3 p-6 rounded-2xl border bg-card">
          <HelpCircle className="h-6 w-6 text-muted-foreground" />
          <div>
            <p className="font-semibold">{t('No war room data', 'Sin datos del war room')}</p>
            <p className="text-sm text-muted-foreground mt-1">{t('No data available for this war room.', 'No hay datos disponibles para este war room.')}</p>
          </div>
        </div>
      </div>
    );
  }

  const { artist, growthData, dealBreakdown, teamMembers, alerts } = data;
  const maxGrowthValue = Math.max(...growthData.map(g => Math.max(g.followers, g.streams)), 1);
  const dealCategories = [
    { label: t('Advance', 'Adelanto'), value: dealBreakdown.advance, color: 'bg-blue-500' },
    { label: t('Marketing', 'Marketing'), value: dealBreakdown.marketing, color: 'bg-emerald-500' },
    { label: t('Production', 'Producción'), value: dealBreakdown.production, color: 'bg-amber-500' },
    { label: t('Legal', 'Legal'), value: dealBreakdown.legal, color: 'bg-purple-500' },
    { label: t('Operations', 'Operaciones'), value: dealBreakdown.operations, color: 'bg-rose-500' },
  ];

  return (
    <div className="p-6 space-y-6 max-w-[1600px] mx-auto">
      <div className="flex justify-end">
        <button
          onClick={() => setLanguage(language === 'en' ? 'es' : 'en')}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg border bg-card text-xs font-medium hover:bg-accent transition-colors"
        >
          <Globe className="h-3.5 w-3.5" />
          {language === 'en' ? 'ES' : 'EN'}
        </button>
      </div>

      {/* ARTIST HERO */}
      <div className="relative overflow-hidden rounded-2xl border bg-gradient-to-br from-card via-card to-primary/5">
        <div className="absolute top-0 right-0 w-96 h-96 bg-primary/5 rounded-full blur-3xl" />
        <div className="absolute bottom-0 left-0 w-64 h-64 bg-emerald-500/5 rounded-full blur-3xl" />

        <div className="relative p-8">
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-6">
              <div
                className="w-24 h-24 rounded-2xl bg-cover bg-center shadow-xl flex items-center justify-center text-4xl font-bold text-primary-foreground overflow-hidden"
                style={(artist.photoUrl || artist.image) ? { backgroundImage: `url(${artist.photoUrl || artist.image})` } : { background: 'linear-gradient(135deg, var(--primary), var(--primary)/0.6)' }}
              >
                {!(artist.photoUrl || artist.image) && artist.name.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase()}
              </div>

              <div>
                <div className="flex items-center gap-3 mb-1">
                  <h1 className="text-4xl font-bold tracking-tight">{artist.name}</h1>
                  <span className={`px-3 py-1 rounded-full border text-xs font-bold uppercase tracking-wider ${
                    artist.score >= 90 ? 'bg-red-500/10 text-red-500 border-red-500/20' :
                    artist.score >= 75 ? 'bg-amber-500/10 text-amber-500 border-amber-500/20' :
                    'bg-emerald-500/10 text-emerald-500 border-emerald-500/20'
                  }`}>
                    {artist.score >= 90 ? t('Critical Priority', 'Prioridad Crítica') :
                     artist.score >= 75 ? t('High Priority', 'Alta Prioridad') :
                     t('Standard', 'Estándar')}
                  </span>
                </div>
                <div className="flex items-center gap-4 text-sm text-muted-foreground">
                  <span>{artist.genres.join(' / ')}</span>
                  <span className="w-1 h-1 rounded-full bg-muted-foreground" />
                  <span>{artist.city}, {artist.country}</span>
                  <span className="w-1 h-1 rounded-full bg-muted-foreground" />
                  <span className="flex items-center gap-1">
                    <Users className="h-3.5 w-3.5" />
                    {t('Lead', 'Contacto')}: {artist.contact}
                  </span>
                </div>

                <div className="flex items-center gap-6 mt-4">
                  {[
                    { label: t('Score', 'Score'), value: artist.score.toString(), icon: Star, color: 'text-primary' },
                    { label: t('Growth', 'Crecimiento'), value: `${artist.growth}%`, icon: TrendingUp, color: 'text-emerald-500' },
                    { label: t('Listeners', 'Oyentes'), value: artist.listeners >= 1000000 ? `${(artist.listeners / 1000000).toFixed(1)}M` : artist.listeners >= 1000 ? `${(artist.listeners / 1000).toFixed(0)}K` : artist.listeners.toString(), icon: Music2, color: 'text-amber-500' },
                    { label: t('Momentum', 'Momentum'), value: `${artist.momentum}%`, icon: Sparkles, color: 'text-purple-500' },
                    { label: t('Engagement', 'Engagement'), value: `${artist.engagement}%`, icon: Users, color: 'text-blue-500' },
                  ].map(stat => {
                    const Icon = stat.icon;
                    return (
                      <div key={stat.label} className="text-center">
                        <p className="text-lg font-bold">{stat.value}</p>
                        <p className="text-xs text-muted-foreground flex items-center gap-1">
                          <Icon className={`h-3 w-3 ${stat.color}`} />
                          {stat.label}
                        </p>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>

            <div className="text-right">
              <div className="p-4 rounded-xl border bg-card/50">
                <p className="text-xs text-muted-foreground mb-1">{t('Deal Amount', 'Monto del Trato')}</p>
                <p className="text-2xl font-bold text-primary">${(artist.deal / 1000).toFixed(0)}K</p>
                <p className="text-xs text-muted-foreground">{t('estimated', 'estimado')}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* MISSION STATUS */}
      <div className="grid grid-cols-5 gap-3">
        {([
          { stage: 'research', label: t('Research', 'Investigación'), done: true, current: false },
          { stage: 'due_diligence', label: t('Due Diligence', 'Debida Diligencia'), done: artist.score >= 80, current: artist.score >= 80 && artist.score < 90 },
          { stage: 'negotiation', label: t('Negotiation', 'Negociación'), done: artist.score >= 90, current: artist.score >= 85 && artist.score < 90 },
          { stage: 'committee_review', label: t('Committee Review', 'Revisión del Comité'), done: false, current: artist.score >= 90 },
          { stage: 'decision', label: t('Decision', 'Decisión'), done: false, current: false },
        ] as const).map((stage, i) => (
          <div
            key={stage.stage}
            className={`relative p-4 rounded-xl border text-center transition-all ${
              stage.current
                ? 'bg-primary/10 border-primary/30 shadow-lg shadow-primary/5'
                : stage.done
                ? 'bg-card border-border/50'
                : 'bg-muted/30 border-border/30 opacity-50'
            }`}
          >
            {stage.done ? (
              <CheckCircle className="h-5 w-5 text-emerald-500 mx-auto mb-1" />
            ) : stage.current ? (
              <div className="relative mx-auto mb-1 w-5 h-5">
                <div className="absolute inset-0 rounded-full border-2 border-primary animate-ping opacity-25" />
                <div className="relative w-5 h-5 rounded-full border-2 border-primary flex items-center justify-center">
                  <div className="w-2 h-2 rounded-full bg-primary" />
                </div>
              </div>
            ) : (
              <div className="w-5 h-5 rounded-full border-2 border-muted-foreground/30 mx-auto mb-1" />
            )}
            <p className={`text-xs font-medium mt-1 ${stage.current ? 'text-primary' : stage.done ? 'text-foreground' : 'text-muted-foreground'}`}>
              {stage.label}
            </p>
            {stage.current && (
              <p className="text-[10px] text-primary/70 mt-0.5 font-medium">{t('In Progress', 'En Progreso')}</p>
            )}
            {i < 4 && (
              <div className={`absolute top-1/2 -right-2.5 w-5 h-[2px] ${stage.done ? 'bg-emerald-500/50' : 'bg-border'}`} />
            )}
          </div>
        ))}
      </div>

      {/* MAIN GRID */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          {/* Growth History */}
          <div className="rounded-xl border bg-card overflow-hidden">
            <div className="p-5 border-b bg-gradient-to-r from-primary/5 to-transparent flex items-center justify-between">
              <div>
                <div className="flex items-center gap-2">
                  <TrendingUp className="h-4 w-4 text-primary" />
                  <h2 className="font-semibold">{t('Growth History', 'Historial de Crecimiento')}</h2>
                </div>
                <p className="text-xs text-muted-foreground mt-0.5">
                  {t('Monthly follower and stream growth', 'Crecimiento mensual de seguidores y streams')}
                </p>
              </div>
            </div>
            <div className="p-5">
              <div className="flex items-center gap-6 text-xs text-muted-foreground mb-4">
                <span className="flex items-center gap-1.5">
                  <span className="w-3 h-3 rounded-sm bg-primary/60" />
                  {t('Followers', 'Seguidores')}
                </span>
                <span className="flex items-center gap-1.5">
                  <span className="w-3 h-3 rounded-sm bg-emerald-500/60" />
                  {t('Streams', 'Reproducciones')}
                </span>
              </div>
              <div className="flex items-end gap-3 h-48">
                {growthData.map((point) => (
                  <div key={point.month} className="flex-1 flex flex-col items-center gap-1 h-full justify-end">
                    <div className="w-full flex flex-col items-center gap-0.5 h-full justify-end">
                      <div
                        className="w-full rounded-t-sm bg-primary/60 transition-all"
                        style={{ height: `${(point.followers / maxGrowthValue) * 100}%` }}
                      />
                      <div
                        className="w-full rounded-t-sm bg-emerald-500/60 transition-all"
                        style={{ height: `${(point.streams / maxGrowthValue) * 100}%` }}
                      />
                    </div>
                    <span className="text-[10px] text-muted-foreground mt-2">{point.month}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Deal Breakdown */}
          <div className="rounded-xl border bg-card p-5">
            <h2 className="font-semibold mb-4 flex items-center gap-2">
              <Target className="h-4 w-4 text-amber-500" />
              {t('Deal Breakdown', 'Desglose del Trato')}
            </h2>
            <div className="space-y-3">
              {/* Stacked Bar */}
              <div className="h-6 rounded-full bg-muted overflow-hidden flex">
                {dealCategories.map(cat => (
                  <div
                    key={cat.label}
                    className={`${cat.color} transition-all`}
                    style={{ width: `${(cat.value / dealBreakdown.total) * 100}%` }}
                    title={`${cat.label}: $${cat.value.toLocaleString()}`}
                  />
                ))}
              </div>
              <div className="grid grid-cols-5 gap-3">
                {dealCategories.map(cat => (
                  <div key={cat.label} className="text-center">
                    <div className="flex items-center justify-center gap-1">
                      <span className={`w-2 h-2 rounded-full ${cat.color.replace('bg-', 'bg-').replace('500', '500')}`} />
                      <span className="text-xs text-muted-foreground">{cat.label}</span>
                    </div>
                    <p className="text-sm font-bold mt-1">${(cat.value / 1000).toFixed(0)}K</p>
                  </div>
                ))}
              </div>
              <div className="pt-2 border-t flex justify-between text-sm">
                <span className="text-muted-foreground">{t('Total', 'Total')}</span>
                <span className="font-bold">${(dealBreakdown.total / 1000).toFixed(0)}K</span>
              </div>
            </div>
          </div>
        </div>

        {/* RIGHT COLUMN */}
        <div className="space-y-6">
          {/* Team */}
          <div className="rounded-xl border bg-card p-4">
            <h3 className="font-semibold mb-3 flex items-center gap-2">
              <Users className="h-4 w-4 text-blue-500" />
              {t('Team', 'Equipo')}
            </h3>
            {teamMembers.length === 0 ? (
              <p className="text-sm text-muted-foreground text-center py-4">{t('No team members assigned', 'Sin miembros del equipo asignados')}</p>
            ) : (
              <div className="space-y-2">
                {teamMembers.map(member => (
                  <div key={member.name} className="flex items-center justify-between p-2 rounded-lg hover:bg-accent/50 transition-colors">
                    <div className="flex items-center gap-2">
                      <div className="relative">
                        <div className="w-7 h-7 rounded-full bg-primary/10 flex items-center justify-center text-xs font-bold">
                          {member.name.charAt(0)}
                        </div>
                        <span className={`absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 rounded-full border-2 border-background ${
                          member.isAgent ? 'bg-primary' : 'bg-green-500'
                        }`} />
                      </div>
                      <div>
                        <p className="text-sm font-medium">{member.name}</p>
                        <p className="text-xs text-muted-foreground">{member.role}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Alerts */}
          {alerts.length > 0 && (
            <div className="rounded-xl border bg-card p-4">
              <h3 className="font-semibold mb-3 flex items-center gap-2">
                <AlertTriangle className="h-4 w-4 text-amber-500" />
                {t('Alerts', 'Alertas')}
              </h3>
              <div className="space-y-2">
                {alerts.slice(0, 4).map((alert, i) => (
                  <div key={i} className={`p-3 rounded-lg text-sm ${
                    alert.type === 'error' ? 'bg-red-500/10 border border-red-500/20' :
                    alert.type === 'warning' ? 'bg-amber-500/10 border border-amber-500/20' :
                    'bg-blue-500/10 border border-blue-500/20'
                  }`}>
                    <div className="flex items-center gap-2">
                      {alert.type === 'error' ? <XCircle className="h-3.5 w-3.5 text-red-500" /> :
                       alert.type === 'warning' ? <AlertTriangle className="h-3.5 w-3.5 text-amber-500" /> :
                       <CheckCircle className="h-3.5 w-3.5 text-blue-500" />}
                      <span className="font-medium text-xs">{alert.title}</span>
                    </div>
                    <p className="text-xs text-muted-foreground mt-1">{alert.description}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Label Copilot */}
          <div className="rounded-xl border bg-card p-4">
            <h3 className="font-semibold mb-3 flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-primary" />
              {t('Label Copilot', 'Copilot del Sello')}
            </h3>
            <div className="relative">
              <input
                type="text"
                placeholder={t('Ask anything...', 'Pregunta lo que sea...')}
                className="w-full px-3 py-2.5 pr-10 rounded-lg border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
              />
              <button className="absolute right-2 top-1/2 -translate-y-1/2 p-1 rounded-md hover:bg-accent transition-colors">
                <MessageSquare className="h-4 w-4 text-muted-foreground" />
              </button>
            </div>
            <div className="flex flex-wrap gap-2 mt-2">
              {[t('Should we sign?', '¿Firmamos?'), t('What risks?', '¿Riesgos?'), t('ROI estimate', 'Estimar ROI')].map(q => (
                <button key={q} className="px-2 py-1 rounded-md bg-accent/50 text-xs text-muted-foreground hover:text-foreground hover:bg-accent transition-colors">
                  {q}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
