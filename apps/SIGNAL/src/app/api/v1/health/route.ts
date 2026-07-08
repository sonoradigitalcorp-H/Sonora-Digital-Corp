// ───────────────────────────────────────────────
// GET /api/v1/health
// System health check — providers, cache, memory
// ───────────────────────────────────────────────

import { NextResponse } from 'next/server';
import { getProviderRegistry } from '@/providers/registry';
import { getCacheManager } from '@/providers/cache/cache-manager';
import { getIntelligenceEngine } from '@/providers/intelligence/engine';
import { buildHealthResponse, getProviderLatencyStats } from '@/lib/observability';

export async function GET() {
  const registry = getProviderRegistry();
  const cache = getCacheManager();
  const engine = getIntelligenceEngine();

  let status: 'healthy' | 'degraded' | 'unhealthy' = 'healthy';
  const checks: Record<string, { status: string; message: string }> = {};

  // 1. Provider health
  try {
    const providerHealth = await engine.health();
    checks.providers = {
      status: providerHealth.status,
      message: `${providerHealth.healthyProviders}/${providerHealth.providers} providers healthy`,
    };

    if (providerHealth.status === 'unhealthy') {
      status = 'unhealthy';
    } else if (providerHealth.status === 'degraded' && status === 'healthy') {
      status = 'degraded';
    }
  } catch (error) {
    checks.providers = {
      status: 'unhealthy',
      message: error instanceof Error ? error.message : 'Provider health check failed',
    };
    status = 'unhealthy';
  }

  // 2. Cache health
  try {
    const cacheStats = cache.getStats();
    const cacheHealthy = cacheStats.total < 10000; // Arbitrary upper limit
    checks.cache = {
      status: cacheHealthy ? 'healthy' : 'degraded',
      message: `${cacheStats.total} entries, ${cacheStats.totalHits} hits, ${cacheStats.totalMisses} misses`,
    };
  } catch (error) {
    checks.cache = {
      status: 'unhealthy',
      message: error instanceof Error ? error.message : 'Cache check failed',
    };
  }

  // 3. Provider latency stats
  let latencyStats: Record<string, unknown> = {};
  try {
    latencyStats = getProviderLatencyStats();
  } catch {
    latencyStats = { error: 'Latency stats unavailable' };
  }

  const response = buildHealthResponse(status, {
    checks,
    cache: {
      entries: cache.getStats().total,
      hits: cache.getStats().totalHits,
      misses: cache.getStats().totalMisses,
    },
    registry: {
      size: registry.size,
      initialized: registry.isInitialized,
      providerNames: registry.getAll().map(p => p.name),
    },
    latency: latencyStats,
  });

  // Return appropriate status code
  const statusCode = status === 'healthy' ? 200 : status === 'degraded' ? 200 : 503;

  return NextResponse.json(response, { status: statusCode });
}
