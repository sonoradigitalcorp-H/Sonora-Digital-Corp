// ───────────────────────────────────────────────
// GET /api/v1/providers
// Provider Dashboard — status, latency, rate limits,
// errors, cache age, health for all providers
// ───────────────────────────────────────────────

import { NextResponse } from 'next/server';
import { getProviderRegistry, registerDefaultProviders } from '@/providers/registry';
import { getCacheManager } from '@/providers/cache/cache-manager';

let initialized = false;

async function ensureProviders() {
  if (!initialized) {
    try {
      await registerDefaultProviders();
      initialized = true;
    } catch (error) {
      console.error('[Providers API] Init failed:', error);
    }
  }
}

export async function GET() {
  await ensureProviders();

  const registry = getProviderRegistry();
  const cache = getCacheManager();

  // Get provider health for all
  const healthResults = await registry.healthAll();

  // Get cache stats
  const cacheStats = cache.getStats();

  // Get per-provider cache stats
  const perProviderCache = await registry.cacheStatsAll();

  // Build dashboard response
  const providers = healthResults.map(health => {
    const providerInstance = registry.get(health.name);
    const providerCache = perProviderCache[health.name] ?? { hits: 0, misses: 0, size: 0 };

    return {
      name: health.name,
      status: health.status,
      message: health.message,
      configured: health.configured,
      configurationError: health.configurationError,
      latencyMs: health.latencyMs,
      lastChecked: health.lastChecked,
      cache: {
        entries: providerCache.size,
        hits: providerCache.hits,
        misses: providerCache.misses,
        total: cacheStats.byProvider[health.name]?.entries ?? 0,
        totalHits: cacheStats.byProvider[health.name]?.hits ?? 0,
        totalMisses: cacheStats.byProvider[health.name]?.misses ?? 0,
      },
      // Provider-specific metadata
      capabilities: getProviderCapabilities(health.name, providerInstance),
    };
  });

  // Sort: healthy first, then degraded, then unhealthy
  providers.sort((a, b) => {
    const order = { healthy: 0, degraded: 1, unhealthy: 2 };
    return (order[a.status] ?? 3) - (order[b.status] ?? 3);
  });

  return NextResponse.json({
    providers,
    summary: {
      total: providers.length,
      healthy: providers.filter(p => p.status === 'healthy').length,
      degraded: providers.filter(p => p.status === 'degraded').length,
      unhealthy: providers.filter(p => p.status === 'unhealthy').length,
      totalCacheEntries: cacheStats.total,
      totalCacheHits: cacheStats.totalHits,
      lastCacheClear: cacheStats.lastClearedAt,
    },
    registry: {
      size: registry.size,
      initialized: registry.isInitialized,
      providerNames: registry.getAll().map(p => p.name),
    },
    timestamp: new Date().toISOString(),
  });
}

function getProviderCapabilities(name: string, instance: unknown): string[] {
  const caps: string[] = [];

  switch (name) {
    case 'spotify':
      caps.push('genres', 'images', 'albums', 'profile', 'search');
      break;
    case 'deezer':
      caps.push('images (small, medium, large)', 'search');
      break;
    case 'youtube':
      caps.push('subscribers', 'total views', 'video count', 'upload frequency',
        'average views', 'channel age', 'latest videos', 'top videos', 'engagement estimates');
      break;
    case 'instagram':
      caps.push('profile', 'bio', 'profile image', 'verified', 'public metrics',
        'posting frequency', 'recent media');
      break;
    case 'tiktok':
      caps.push('followers', 'video count', 'likes', 'engagement',
        'recent videos');
      break;
  }

  return caps;
}
