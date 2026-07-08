// ───────────────────────────────────────────────
// SIGNAL Provider Registry
// Dependency injection container for all data providers
// ───────────────────────────────────────────────

import type { DataProvider, ProviderHealth } from './types';
import { logProvider } from './base-provider';
import { getCacheManager } from './cache/cache-manager';

// ── Registry ──

export class ProviderRegistry {
  private providers: Map<string, DataProvider> = new Map();
  private healthCache: Map<string, ProviderHealth> = new Map();
  private healthCheckTimers: Map<string, NodeJS.Timeout> = new Map();
  private initialized = false;
  private initPromise: Promise<{ success: string[]; failed: string[] }> | null = null;

  /**
   * Register a provider with the registry.
   * If a provider with the same name already exists, it will be replaced.
   */
  register(provider: DataProvider): void {
    if (this.providers.has(provider.name)) {
      logProvider('registry', 'warn', `Replacing existing provider: ${provider.name}`);
    }

    this.providers.set(provider.name, provider);
    logProvider('registry', 'info', `Provider registered: ${provider.name}`);

    // Start periodic health checks if configured
    this.startHealthChecks(provider);
  }

  /**
   * Register multiple providers at once.
   */
  registerAll(providers: DataProvider[]): void {
    for (const provider of providers) {
      this.register(provider);
    }
  }

  /**
   * Get a provider by name.
   */
  get<T extends DataProvider>(name: string): T | undefined {
    return this.providers.get(name) as T | undefined;
  }

  /**
   * Get all registered providers.
   */
  getAll(): DataProvider[] {
    return Array.from(this.providers.values());
  }

  /**
   * Get providers that support a specific capability.
   * Checks if the method exists on the provider.
   */
  getByCapability(capability: keyof DataProvider): DataProvider[] {
    return this.getAll().filter(p => typeof p[capability] === 'function');
  }

  /**
   * Check if a provider is registered.
   */
  has(name: string): boolean {
    return this.providers.has(name);
  }

  /**
   * Remove a provider from the registry.
   */
  unregister(name: string): boolean {
    this.stopHealthChecks(name);
    this.healthCache.delete(name);
    return this.providers.delete(name);
  }

  /**
   * Initialize all registered providers.
   * Call this once during app startup.
   */
  async initializeAll(): Promise<{ success: string[]; failed: string[] }> {
    // Mutex: prevent concurrent initialization (race condition guard)
    if (this.initPromise) {
      return this.initPromise;
    }

    this.initPromise = this._initializeAll();
    return this.initPromise;
  }

  private async _initializeAll(): Promise<{ success: string[]; failed: string[] }> {
    const success: string[] = [];
    const failed: string[] = [];

    const initPromises = Array.from(this.providers.entries()).map(async ([name, provider]) => {
      try {
        await provider.initialize();
        success.push(name);
      } catch (error) {
        logProvider('registry', 'error', `Provider initialization failed: ${name}`, {
          error: error instanceof Error ? error.message : String(error),
        });
        failed.push(name);
      }
    });

    await Promise.allSettled(initPromises);
    this.initialized = true;

    logProvider('registry', 'info', 'Provider initialization complete', {
      total: this.providers.size,
      success: success.length,
      failed: failed.length,
    });

    return { success, failed };
  }

  /**
   * Get health status for all providers.
   */
  async healthAll(): Promise<ProviderHealth[]> {
    const results = await Promise.allSettled(
      Array.from(this.providers.entries()).map(async ([name, provider]) => {
        try {
          const health = await provider.health();
          this.healthCache.set(name, health);
          return health;
        } catch (error) {
          const failed: ProviderHealth = {
            name,
            status: 'unhealthy',
            message: error instanceof Error ? error.message : String(error),
            latencyMs: 0,
            lastChecked: new Date().toISOString(),
            configured: false,
            configurationError: null,
          };
          this.healthCache.set(name, failed);
          return failed;
        }
      })
    );

    return results.map(r => r.status === 'fulfilled' ? r.value : r.reason as ProviderHealth);
  }

  /**
   * Get cached health for a provider (fast, no API call).
   */
  getCachedHealth(name: string): ProviderHealth | undefined {
    return this.healthCache.get(name);
  }

  /**
   * Get names of all healthy providers.
   */
  getHealthyProviders(): string[] {
    const healthy: string[] = [];
    for (const [name, health] of this.healthCache) {
      if (health.status === 'healthy') {
        healthy.push(name);
      }
    }
    return healthy;
  }

  /**
   * Refresh all providers that support the refresh method.
   */
  async refreshAll(): Promise<{ refreshed: string[]; failed: string[] }> {
    const refreshed: string[] = [];
    const failed: string[] = [];

    const refreshPromises = Array.from(this.providers.entries()).map(async ([name, provider]) => {
      if (typeof provider.refresh !== 'function') return;

      try {
        await provider.refresh();
        refreshed.push(name);
      } catch (error) {
        logProvider('registry', 'error', `Provider refresh failed: ${name}`, {
          error: error instanceof Error ? error.message : String(error),
        });
        failed.push(name);
      }
    });

    await Promise.allSettled(refreshPromises);
    return { refreshed, failed };
  }

  /**
   * Get cache stats aggregated across all providers.
   */
  async cacheStatsAll(): Promise<Record<string, { hits: number; misses: number; size: number }>> {
    const stats: Record<string, { hits: number; misses: number; size: number }> = {};

    await Promise.allSettled(
      Array.from(this.providers.entries()).map(async ([name, provider]) => {
        if (typeof provider.cache === 'function') {
          try {
            stats[name] = await provider.cache();
          } catch {
            stats[name] = { hits: 0, misses: 0, size: 0 };
          }
        } else {
          stats[name] = { hits: 0, misses: 0, size: 0 };
        }
      })
    );

    return stats;
  }

  /**
   * Number of registered providers.
   */
  get size(): number {
    return this.providers.size;
  }

  /**
   * Whether the registry has been initialized.
   */
  get isInitialized(): boolean {
    return this.initialized;
  }

  // ── Private: Periodic Health Checks ──

  private startHealthChecks(provider: DataProvider): void {
    const intervalMs = 5 * 60 * 1000; // Every 5 minutes

    // Don't start if already running
    if (this.healthCheckTimers.has(provider.name)) return;

    const timer = setInterval(async () => {
      try {
        const health = await provider.health();
        this.healthCache.set(provider.name, health);

        if (health.status !== 'healthy') {
          logProvider('registry', 'warn', `Health check degraded: ${provider.name}`, {
            status: health.status,
            message: health.message,
          });
        }
      } catch (error) {
        logProvider('registry', 'error', `Health check failed: ${provider.name}`, {
          error: error instanceof Error ? error.message : String(error),
        });
      }
    }, intervalMs);

    this.healthCheckTimers.set(provider.name, timer);
  }

  private stopHealthChecks(name: string): void {
    const timer = this.healthCheckTimers.get(name);
    if (timer) {
      clearInterval(timer);
      this.healthCheckTimers.delete(name);
    }
  }
}

// ── Singleton ──

let instance: ProviderRegistry | null = null;

export function getProviderRegistry(): ProviderRegistry {
  if (!instance) {
    instance = new ProviderRegistry();
  }
  return instance;
}

/**
 * Convenience: register all built-in providers.
 */
export async function registerDefaultProviders(): Promise<ProviderRegistry> {
  const registry = getProviderRegistry();

  const { getSpotifyProvider } = await import('./spotify/spotify-provider');
  const { getDeezerProvider } = await import('./deezer/deezer-provider');
  const { getYouTubeProvider } = await import('./youtube/youtube-provider');
  const { getInstagramProvider } = await import('./instagram/instagram-provider');
  const { getTikTokProvider } = await import('./tiktok/tiktok-provider');

  registry.registerAll([
    getSpotifyProvider(),
    getDeezerProvider(),
    getYouTubeProvider(),
    getInstagramProvider(),
    getTikTokProvider(),
  ]);

  await registry.initializeAll();
  return registry;
}
