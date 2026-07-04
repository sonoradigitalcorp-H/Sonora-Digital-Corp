// ───────────────────────────────────────────────
// Provider Dashboard — Status, Latency, Cache, Health
// Shows all registered providers with real-time status
// ───────────────────────────────────────────────

'use client';

import { useEffect, useState } from 'react';

// ── Types ──

interface ProviderStatus {
  name: string;
  status: 'healthy' | 'degraded' | 'unhealthy';
  message: string;
  configured: boolean;
  configurationError: string | null;
  latencyMs: number;
  lastChecked: string;
  cache: {
    entries: number;
    hits: number;
    misses: number;
    total: number;
  };
  capabilities: string[];
}

interface DashboardSummary {
  total: number;
  healthy: number;
  degraded: number;
  unhealthy: number;
  totalCacheEntries: number;
  totalCacheHits: number;
  lastCacheClear: number | null;
}

interface DashboardData {
  providers: ProviderStatus[];
  summary: DashboardSummary;
  registry: {
    size: number;
    initialized: boolean;
    providerNames: string[];
  };
  timestamp: string;
}

// ── Helpers ──

const STATUS_COLORS: Record<string, string> = {
  healthy: 'bg-emerald-500',
  degraded: 'bg-amber-500',
  unhealthy: 'bg-red-500',
};

const STATUS_TEXT: Record<string, string> = {
  healthy: 'Operational',
  degraded: 'Degraded',
  unhealthy: 'Unavailable',
};

const PROVIDER_ICONS: Record<string, string> = {
  spotify: '🎵',
  deezer: '🎧',
  youtube: '▶️',
  instagram: '📷',
  tiktok: '🎬',
};

function formatLatency(ms: number): string {
  if (ms < 1) return '<1ms';
  if (ms < 1000) return `${Math.round(ms)}ms`;
  return `${(ms / 1000).toFixed(1)}s`;
}

function formatTime(iso: string): string {
  try {
    const d = new Date(iso);
    return d.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  } catch {
    return '—';
  }
}

// ── Component ──

export function ProviderDashboard() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedProvider, setExpandedProvider] = useState<string | null>(null);

  useEffect(() => {
    fetchData();
    // Auto-refresh every 30s
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  async function fetchData() {
    try {
      const res = await fetch('/api/v1/providers');
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const json = await res.json();
      setData(json);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch provider status');
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="rounded-xl border border-zinc-800 bg-[#111] p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-white">Provider Ecosystem</h2>
          <div className="animate-pulse h-4 w-24 bg-zinc-700 rounded" />
        </div>
        <div className="space-y-3">
          {[1, 2, 3, 4, 5].map(i => (
            <div key={i} className="animate-pulse h-16 bg-zinc-800 rounded-lg" />
          ))}
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="rounded-xl border border-red-900/50 bg-[#111] p-6">
        <h2 className="text-lg font-semibold text-red-400 mb-2">Provider Dashboard</h2>
        <p className="text-zinc-400 text-sm">{error || 'No data available'}</p>
        <button
          onClick={fetchData}
          className="mt-3 px-4 py-2 text-sm bg-zinc-800 hover:bg-zinc-700 text-white rounded-lg transition-colors"
        >
          Retry
        </button>
      </div>
    );
  }

  const { providers, summary, registry, timestamp } = data;

  return (
    <div className="rounded-xl border border-zinc-800 bg-[#111] p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-lg font-semibold text-white">Provider Ecosystem</h2>
          <p className="text-xs text-zinc-500 mt-1">
            {registry.providerNames.length} providers registered · Last updated {formatTime(timestamp)}
          </p>
        </div>

        {/* Summary Badges */}
        <div className="flex gap-2">
          <span className="px-2.5 py-1 text-xs rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            {summary.healthy} Healthy
          </span>
          {summary.degraded > 0 && (
            <span className="px-2.5 py-1 text-xs rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20">
              {summary.degraded} Degraded
            </span>
          )}
          {summary.unhealthy > 0 && (
            <span className="px-2.5 py-1 text-xs rounded-full bg-red-500/10 text-red-400 border border-red-500/20">
              {summary.unhealthy} Unhealthy
            </span>
          )}
        </div>
      </div>

      {/* Provider Cards */}
      <div className="space-y-2">
        {providers.map(provider => (
          <div
            key={provider.name}
            className={`rounded-lg border transition-all cursor-pointer ${
              provider.status === 'healthy'
                ? 'border-zinc-800 hover:border-zinc-700'
                : provider.status === 'degraded'
                ? 'border-amber-900/30 hover:border-amber-700/50'
                : 'border-red-900/30 hover:border-red-700/50'
            } bg-[#171717]`}
            onClick={() => setExpandedProvider(expandedProvider === provider.name ? null : provider.name)}
          >
            {/* Main Row */}
            <div className="flex items-center justify-between p-4">
              <div className="flex items-center gap-3">
                {/* Status Dot */}
                <div className={`w-2.5 h-2.5 rounded-full ${STATUS_COLORS[provider.status]}`} />

                {/* Icon + Name */}
                <span className="text-lg">{PROVIDER_ICONS[provider.name] ?? '🔌'}</span>
                <div>
                  <span className="text-sm font-medium text-white capitalize">{provider.name}</span>
                  <span className={`ml-2 text-xs ${
                    provider.status === 'healthy' ? 'text-emerald-400' :
                    provider.status === 'degraded' ? 'text-amber-400' : 'text-red-400'
                  }`}>
                    {STATUS_TEXT[provider.status]}
                  </span>
                </div>
              </div>

              {/* Stats */}
              <div className="flex items-center gap-4 text-xs text-zinc-400">
                <span title="Latency">{formatLatency(provider.latencyMs)}</span>
                <span title="Cache entries">{provider.cache.total} cached</span>
                <span title="Capabilities">{provider.capabilities.length} caps</span>
                <svg
                  className={`w-4 h-4 transition-transform ${
                    expandedProvider === provider.name ? 'rotate-180' : ''
                  }`}
                  fill="none" stroke="currentColor" viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </div>
            </div>

            {/* Expanded Details */}
            {expandedProvider === provider.name && (
              <div className="px-4 pb-4 pt-0 border-t border-zinc-800 mt-0">
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mt-3">
                  {/* Status */}
                  <div>
                    <p className="text-xs text-zinc-500 mb-1">Status</p>
                    <p className="text-sm text-zinc-300">{provider.message}</p>
                  </div>

                  {/* Configuration */}
                  <div>
                    <p className="text-xs text-zinc-500 mb-1">Configuration</p>
                    <p className={`text-sm ${provider.configured ? 'text-emerald-400' : 'text-red-400'}`}>
                      {provider.configured ? 'Configured' : 'Not Configured'}
                    </p>
                    {provider.configurationError && (
                      <p className="text-xs text-red-400 mt-0.5">{provider.configurationError}</p>
                    )}
                  </div>

                  {/* Latency */}
                  <div>
                    <p className="text-xs text-zinc-500 mb-1">Latency</p>
                    <p className="text-sm text-zinc-300">{formatLatency(provider.latencyMs)}</p>
                  </div>

                  {/* Last Checked */}
                  <div>
                    <p className="text-xs text-zinc-500 mb-1">Last Checked</p>
                    <p className="text-sm text-zinc-300">{formatTime(provider.lastChecked)}</p>
                  </div>

                  {/* Cache */}
                  <div>
                    <p className="text-xs text-zinc-500 mb-1">Cache</p>
                    <p className="text-sm text-zinc-300">
                      {provider.cache.total} entries · {provider.cache.hits} hits
                    </p>
                  </div>

                  {/* Capabilities */}
                  <div>
                    <p className="text-xs text-zinc-500 mb-1">Capabilities</p>
                    <div className="flex flex-wrap gap-1">
                      {provider.capabilities.map(cap => (
                        <span
                          key={cap}
                          className="px-1.5 py-0.5 text-xs rounded bg-zinc-800 text-zinc-300"
                        >
                          {cap}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Footer Stats */}
      <div className="mt-4 pt-4 border-t border-zinc-800">
        <div className="flex items-center justify-between text-xs text-zinc-500">
          <span>
            Cache: {summary.totalCacheEntries} total entries · {summary.totalCacheHits} total hits
          </span>
          <button
            onClick={fetchData}
            className="px-3 py-1 rounded bg-zinc-800 hover:bg-zinc-700 text-zinc-300 transition-colors"
          >
            Refresh
          </button>
        </div>
      </div>
    </div>
  );
}
