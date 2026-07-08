import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { ProviderRegistry } from '../../providers/registry';
import type { DataProvider, ProviderHealth } from '../../providers/types';

function createMockProvider(name: string, overrides: Partial<DataProvider> = {}): DataProvider {
  return {
    name,
    initialize: vi.fn().mockResolvedValue(undefined),
    health: vi.fn().mockResolvedValue({
      name,
      status: 'healthy' as const,
      message: 'OK',
      latencyMs: 10,
      lastChecked: new Date().toISOString(),
      configured: true,
      configurationError: null,
    }),
    searchArtist: vi.fn().mockResolvedValue([]),
    fetchProfile: vi.fn().mockResolvedValue(null),
    fetchMetrics: vi.fn().mockResolvedValue(null),
    fetchImages: vi.fn().mockResolvedValue({
      externalId: '',
      small: null,
      medium: null,
      large: null,
      provider: name,
    }),
    fetchGenres: vi.fn().mockResolvedValue([]),
    ...overrides,
  };
}

describe.sequential('ProviderRegistry', () => {
  let registry: ProviderRegistry;

  beforeEach(() => {
    registry = new ProviderRegistry();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  // ── Register / Get ──

  describe('register / get', () => {
    it('registers a provider and retrieves it by name', () => {
      const provider = createMockProvider('spotify');
      registry.register(provider);
      const retrieved = registry.get('spotify');
      expect(retrieved).toBeDefined();
      expect(retrieved!.name).toBe('spotify');
    });

    it('returns undefined for an unregistered provider', () => {
      const retrieved = registry.get('nonexistent');
      expect(retrieved).toBeUndefined();
    });

    it('preserves full provider interface on retrieval', async () => {
      const provider = createMockProvider('spotify');
      registry.register(provider);
      const retrieved = registry.get<DataProvider>('spotify')!;
      const initResult = retrieved.initialize();
      const healthResult = retrieved.health();
      const searchResult = retrieved.searchArtist('test');
      await expect(initResult).resolves.toBeUndefined();
      await expect(healthResult).resolves.toMatchObject({ status: 'healthy' });
      await expect(searchResult).resolves.toEqual([]);
    });
  });

  // ── Register All ──

  describe('registerAll', () => {
    it('registers multiple providers at once', () => {
      const providers = [
        createMockProvider('spotify'),
        createMockProvider('deezer'),
        createMockProvider('youtube'),
      ];
      registry.registerAll(providers);
      expect(registry.size).toBe(3);
      expect(registry.has('spotify')).toBe(true);
      expect(registry.has('deezer')).toBe(true);
      expect(registry.has('youtube')).toBe(true);
    });

    it('registers an empty array without errors', () => {
      registry.registerAll([]);
      expect(registry.size).toBe(0);
    });
  });

  // ── Replace ──

  describe('replace (register same name)', () => {
    it('replaces an existing provider when registering with the same name', () => {
      const first = createMockProvider('spotify');
      const second = createMockProvider('spotify');
      registry.register(first);
      registry.register(second);

      expect(registry.size).toBe(1);
      const retrieved = registry.get('spotify');
      expect(retrieved).toBe(second);
      expect(retrieved).not.toBe(first);
    });

    it('the new provider is used for subsequent calls', async () => {
      const first = createMockProvider('spotify', {
        health: vi.fn().mockResolvedValue({
          name: 'spotify',
          status: 'degraded',
          message: 'old',
          latencyMs: 100,
          lastChecked: new Date().toISOString(),
          configured: true,
          configurationError: null,
        }),
      });
      const second = createMockProvider('spotify', {
        health: vi.fn().mockResolvedValue({
          name: 'spotify',
          status: 'healthy',
          message: 'new',
          latencyMs: 5,
          lastChecked: new Date().toISOString(),
          configured: true,
          configurationError: null,
        }),
      });

      registry.register(first);
      registry.register(second);

      const health = await registry.get<DataProvider>('spotify')!.health();
      expect(health.status).toBe('healthy');
      expect(health.message).toBe('new');
    });
  });

  // ── Has ──

  describe('has', () => {
    it('returns true for a registered provider', () => {
      registry.register(createMockProvider('spotify'));
      expect(registry.has('spotify')).toBe(true);
    });

    it('returns false for an unregistered provider', () => {
      expect(registry.has('nonexistent')).toBe(false);
    });

    it('returns false after unregistering', () => {
      registry.register(createMockProvider('spotify'));
      registry.unregister('spotify');
      expect(registry.has('spotify')).toBe(false);
    });
  });

  // ── Get All ──

  describe('getAll', () => {
    it('returns all registered providers', () => {
      const p1 = createMockProvider('spotify');
      const p2 = createMockProvider('deezer');
      registry.registerAll([p1, p2]);
      const all = registry.getAll();
      expect(all).toHaveLength(2);
      expect(all).toContain(p1);
      expect(all).toContain(p2);
    });

    it('returns an empty array when nothing is registered', () => {
      expect(registry.getAll()).toEqual([]);
    });
  });

  // ── Get By Capability ──

  describe('getByCapability', () => {
    it('returns providers that have the specified method', () => {
      const withRefresh = createMockProvider('with-refresh', {
        refresh: vi.fn().mockResolvedValue(undefined),
      });
      const withoutRefresh = createMockProvider('without-refresh');
      registry.registerAll([withRefresh, withoutRefresh]);
      const capable = registry.getByCapability('refresh');
      expect(capable).toHaveLength(1);
      expect(capable[0].name).toBe('with-refresh');
    });

    it('returns providers that have the cache method', () => {
      const withCache = createMockProvider('with-cache', {
        cache: vi.fn().mockResolvedValue({ hits: 1, misses: 0, size: 10 }),
      });
      const withoutCache = createMockProvider('without-cache');
      registry.registerAll([withCache, withoutCache]);
      const capable = registry.getByCapability('cache');
      expect(capable).toHaveLength(1);
      expect(capable[0].name).toBe('with-cache');
    });

    it('returns providers that have fetchAlbums', () => {
      const withAlbums = createMockProvider('with-albums', {
        fetchAlbums: vi.fn().mockResolvedValue([]),
      });
      const withoutAlbums = createMockProvider('without-albums');
      registry.registerAll([withAlbums, withoutAlbums]);
      const capable = registry.getByCapability('fetchAlbums');
      expect(capable).toHaveLength(1);
      expect(capable[0].name).toBe('with-albums');
    });

    it('returns empty array when no provider has the capability', () => {
      registry.register(createMockProvider('basic'));
      const capable = registry.getByCapability('refresh');
      expect(capable).toHaveLength(0);
    });

    it('returns all providers when checking initialize which is always present', () => {
      const p1 = createMockProvider('a');
      const p2 = createMockProvider('b');
      registry.registerAll([p1, p2]);
      const capable = registry.getByCapability('initialize');
      expect(capable).toHaveLength(2);
    });
  });

  // ── Unregister ──

  describe('unregister', () => {
    it('removes the provider and returns true', () => {
      registry.register(createMockProvider('spotify'));
      const result = registry.unregister('spotify');
      expect(result).toBe(true);
      expect(registry.has('spotify')).toBe(false);
      expect(registry.get('spotify')).toBeUndefined();
    });

    it('returns false when provider does not exist', () => {
      const result = registry.unregister('nonexistent');
      expect(result).toBe(false);
    });

    it('decrements size', () => {
      registry.register(createMockProvider('spotify'));
      registry.register(createMockProvider('deezer'));
      expect(registry.size).toBe(2);
      registry.unregister('spotify');
      expect(registry.size).toBe(1);
    });

    it('clears the cached health entry', async () => {
      const provider = createMockProvider('spotify');
      registry.register(provider);
      await registry.healthAll();
      const before = registry.getCachedHealth('spotify');
      expect(before).toBeDefined();
      registry.unregister('spotify');
      const after = registry.getCachedHealth('spotify');
      expect(after).toBeUndefined();
    });

    it('stops health check timers', () => {
      vi.useFakeTimers();
      const healthMock = vi.fn().mockResolvedValue({
        name: 'spotify',
        status: 'healthy',
        message: 'OK',
        latencyMs: 10,
        lastChecked: new Date().toISOString(),
        configured: true,
        configurationError: null,
      });
      const provider = createMockProvider('spotify', { health: healthMock });
      registry.register(provider);
      const initialCalls = healthMock.mock.calls.length;
      registry.unregister('spotify');
      vi.advanceTimersByTime(5 * 60 * 1000 + 100);
      expect(healthMock.mock.calls.length).toBe(initialCalls);
    });
  });

  // ── Initialize All ──

  describe('initializeAll', () => {
    it('calls initialize on all providers and returns success', async () => {
      const p1 = createMockProvider('spotify');
      const p2 = createMockProvider('deezer');
      registry.registerAll([p1, p2]);
      const result = await registry.initializeAll();
      expect(result.success).toEqual(['spotify', 'deezer']);
      expect(result.failed).toEqual([]);
    });

    it('returns failed providers when initialize throws', async () => {
      const failing = createMockProvider('failing', {
        initialize: vi.fn().mockRejectedValue(new Error('init failed')),
      });
      const ok = createMockProvider('ok');
      registry.registerAll([failing, ok]);
      const result = await registry.initializeAll();
      expect(result.success).toEqual(['ok']);
      expect(result.failed).toEqual(['failing']);
    });

    it('sets isInitialized to true after completion', async () => {
      expect(registry.isInitialized).toBe(false);
      registry.register(createMockProvider('spotify'));
      await registry.initializeAll();
      expect(registry.isInitialized).toBe(true);
    });

    it('handles all providers failing', async () => {
      const a = createMockProvider('a', {
        initialize: vi.fn().mockRejectedValue(new Error('fail')),
      });
      const b = createMockProvider('b', {
        initialize: vi.fn().mockRejectedValue(new Error('fail')),
      });
      registry.registerAll([a, b]);
      const result = await registry.initializeAll();
      expect(result.success).toEqual([]);
      expect(result.failed).toEqual(['a', 'b']);
    });

    it('succeeds with no providers registered', async () => {
      const result = await registry.initializeAll();
      expect(result.success).toEqual([]);
      expect(result.failed).toEqual([]);
      expect(registry.isInitialized).toBe(true);
    });
  });

  // ── Health All ──

  describe('healthAll', () => {
    it('returns health for all providers', async () => {
      const p1 = createMockProvider('spotify');
      const p2 = createMockProvider('deezer');
      registry.registerAll([p1, p2]);
      const health = await registry.healthAll();
      expect(health).toHaveLength(2);
      expect(health.every(h => h.status === 'healthy')).toBe(true);
    });

    it('handles provider failures gracefully with unhealthy status', async () => {
      const failing = createMockProvider('failing', {
        health: vi.fn().mockRejectedValue(new Error('API down')),
      });
      const ok = createMockProvider('ok');
      registry.registerAll([failing, ok]);
      const health = await registry.healthAll();
      expect(health).toHaveLength(2);
      const failedHealth = health.find(h => h.name === 'failing');
      expect(failedHealth!.status).toBe('unhealthy');
      expect(failedHealth!.message).toBe('API down');
      const okHealth = health.find(h => h.name === 'ok');
      expect(okHealth!.status).toBe('healthy');
    });

    it('updates the health cache for each provider', async () => {
      const p1 = createMockProvider('spotify');
      const p2 = createMockProvider('deezer');
      registry.registerAll([p1, p2]);
      await registry.healthAll();
      expect(registry.getCachedHealth('spotify')).toBeDefined();
      expect(registry.getCachedHealth('deezer')).toBeDefined();
    });
  });

  // ── Get Cached Health ──

  describe('getCachedHealth', () => {
    it('returns cached health after healthAll', async () => {
      registry.register(createMockProvider('spotify'));
      await registry.healthAll();
      const cached = registry.getCachedHealth('spotify');
      expect(cached).toBeDefined();
      expect(cached!.status).toBe('healthy');
    });

    it('returns undefined if no health check has been run', () => {
      registry.register(createMockProvider('spotify'));
      expect(registry.getCachedHealth('spotify')).toBeUndefined();
    });

    it('returns undefined for a provider that was never registered', () => {
      expect(registry.getCachedHealth('nonexistent')).toBeUndefined();
    });

    it('returns stale cached health even if provider later fails', async () => {
      const provider = createMockProvider('spotify');
      registry.register(provider);
      await registry.healthAll();
      const cached = registry.getCachedHealth('spotify');
      expect(cached).toBeDefined();
      expect(cached!.status).toBe('healthy');
      provider.health = vi.fn().mockRejectedValue(new Error('now down'));
      const stillCached = registry.getCachedHealth('spotify');
      expect(stillCached).toBeDefined();
      expect(stillCached!.status).toBe('healthy');
    });
  });

  // ── Get Healthy Providers ──

  describe('getHealthyProviders', () => {
    it('returns names of healthy providers', async () => {
      const ok = createMockProvider('ok');
      const alsoOk = createMockProvider('also-ok');
      registry.registerAll([ok, alsoOk]);
      await registry.healthAll();
      const healthy = registry.getHealthyProviders();
      expect(healthy).toContain('ok');
      expect(healthy).toContain('also-ok');
    });

    it('excludes unhealthy providers', async () => {
      const ok = createMockProvider('ok');
      const failing = createMockProvider('failing', {
        health: vi.fn().mockRejectedValue(new Error('down')),
      });
      registry.registerAll([ok, failing]);
      await registry.healthAll();
      const healthy = registry.getHealthyProviders();
      expect(healthy).toEqual(['ok']);
    });

    it('returns empty array when no health checks have been run', () => {
      registry.register(createMockProvider('spotify'));
      expect(registry.getHealthyProviders()).toEqual([]);
    });

    it('returns empty array when all providers are unhealthy', async () => {
      const a = createMockProvider('a', {
        health: vi.fn().mockRejectedValue(new Error('fail')),
      });
      const b = createMockProvider('b', {
        health: vi.fn().mockRejectedValue(new Error('fail')),
      });
      registry.registerAll([a, b]);
      await registry.healthAll();
      expect(registry.getHealthyProviders()).toEqual([]);
    });
  });

  // ── Refresh All ──

  describe('refreshAll', () => {
    it('calls refresh on providers that have it', async () => {
      const refreshMock = vi.fn().mockResolvedValue(undefined);
      const withRefresh = createMockProvider('with-refresh', {
        refresh: refreshMock,
      });
      const withoutRefresh = createMockProvider('without-refresh');
      registry.registerAll([withRefresh, withoutRefresh]);
      const result = await registry.refreshAll();
      expect(result.refreshed).toEqual(['with-refresh']);
      expect(result.failed).toEqual([]);
      expect(refreshMock).toHaveBeenCalledTimes(1);
    });

    it('collects failed refreshes', async () => {
      const failing = createMockProvider('failing', {
        refresh: vi.fn().mockRejectedValue(new Error('refresh failed')),
      });
      const ok = createMockProvider('ok', {
        refresh: vi.fn().mockResolvedValue(undefined),
      });
      registry.registerAll([failing, ok]);
      const result = await registry.refreshAll();
      expect(result.refreshed).toEqual(['ok']);
      expect(result.failed).toEqual(['failing']);
    });

    it('returns empty arrays when no providers have refresh', async () => {
      registry.register(createMockProvider('basic'));
      const result = await registry.refreshAll();
      expect(result.refreshed).toEqual([]);
      expect(result.failed).toEqual([]);
    });

    it('handles empty registry', async () => {
      const result = await registry.refreshAll();
      expect(result.refreshed).toEqual([]);
      expect(result.failed).toEqual([]);
    });
  });

  // ── Cache Stats All ──

  describe('cacheStatsAll', () => {
    it('returns cache stats for providers with cache method', async () => {
      const withCache = createMockProvider('with-cache', {
        cache: vi.fn().mockResolvedValue({ hits: 5, misses: 2, size: 100 }),
      });
      const withoutCache = createMockProvider('without-cache');
      registry.registerAll([withCache, withoutCache]);
      const stats = await registry.cacheStatsAll();
      expect(stats['with-cache']).toEqual({ hits: 5, misses: 2, size: 100 });
      expect(stats['without-cache']).toEqual({ hits: 0, misses: 0, size: 0 });
    });

    it('returns zeros for providers without cache method', async () => {
      registry.register(createMockProvider('nocache'));
      const stats = await registry.cacheStatsAll();
      expect(stats['nocache']).toEqual({ hits: 0, misses: 0, size: 0 });
    });

    it('handles cache method failures gracefully', async () => {
      const failing = createMockProvider('failing', {
        cache: vi.fn().mockRejectedValue(new Error('cache error')),
      });
      registry.register(failing);
      const stats = await registry.cacheStatsAll();
      expect(stats['failing']).toEqual({ hits: 0, misses: 0, size: 0 });
    });

    it('returns empty object when nothing is registered', async () => {
      const stats = await registry.cacheStatsAll();
      expect(stats).toEqual({});
    });
  });

  // ── Size ──

  describe('size', () => {
    it('returns 0 for empty registry', () => {
      expect(registry.size).toBe(0);
    });

    it('returns the correct count after registering providers', () => {
      registry.register(createMockProvider('a'));
      expect(registry.size).toBe(1);
      registry.register(createMockProvider('b'));
      expect(registry.size).toBe(2);
    });

    it('decrements after unregister', () => {
      registry.register(createMockProvider('a'));
      registry.register(createMockProvider('b'));
      registry.unregister('a');
      expect(registry.size).toBe(1);
    });

    it('does not increase when replacing an existing provider', () => {
      registry.register(createMockProvider('a'));
      registry.register(createMockProvider('a'));
      expect(registry.size).toBe(1);
    });
  });

  // ── Is Initialized ──

  describe('isInitialized', () => {
    it('starts as false', () => {
      expect(registry.isInitialized).toBe(false);
    });

    it('becomes true after initializeAll', async () => {
      registry.register(createMockProvider('a'));
      await registry.initializeAll();
      expect(registry.isInitialized).toBe(true);
    });

    it('remains false if initializeAll is never called', () => {
      registry.register(createMockProvider('a'));
      expect(registry.isInitialized).toBe(false);
    });

    it('stays true even if initializeAll throws on some providers', async () => {
      const failing = createMockProvider('fail', {
        initialize: vi.fn().mockRejectedValue(new Error('boom')),
      });
      registry.register(failing);
      await registry.initializeAll();
      expect(registry.isInitialized).toBe(true);
    });
  });

  // ── Error Isolation ──

  describe('error isolation', () => {
    it('one provider failing initialize does not affect others', async () => {
      const failing = createMockProvider('failing', {
        initialize: vi.fn().mockRejectedValue(new Error('init error')),
      });
      const ok = createMockProvider('ok');
      registry.registerAll([failing, ok]);
      const result = await registry.initializeAll();
      expect(result.success).toEqual(['ok']);
      expect(result.failed).toEqual(['failing']);
      expect(ok.initialize).toHaveBeenCalledTimes(1);
    });

    it('one provider failing health does not affect others', async () => {
      const failing = createMockProvider('failing', {
        health: vi.fn().mockRejectedValue(new Error('health error')),
      });
      const ok = createMockProvider('ok');
      registry.registerAll([failing, ok]);
      const health = await registry.healthAll();
      expect(health.find(h => h.name === 'failing')!.status).toBe('unhealthy');
      expect(health.find(h => h.name === 'ok')!.status).toBe('healthy');
    });

    it('one provider failing refresh does not affect others', async () => {
      const failing = createMockProvider('failing', {
        refresh: vi.fn().mockRejectedValue(new Error('refresh error')),
      });
      const ok = createMockProvider('ok', {
        refresh: vi.fn().mockResolvedValue(undefined),
      });
      registry.registerAll([failing, ok]);
      const result = await registry.refreshAll();
      expect(result.failed).toEqual(['failing']);
      expect(result.refreshed).toEqual(['ok']);
    });

    it('unregistering one provider does not affect others', () => {
      const a = createMockProvider('a');
      const b = createMockProvider('b');
      registry.registerAll([a, b]);
      registry.unregister('a');
      expect(registry.has('a')).toBe(false);
      expect(registry.has('b')).toBe(true);
      expect(registry.get('b')).toBe(b);
    });

    it('providers can be registered and used independently', async () => {
      const spotifySearch = vi.fn().mockResolvedValue([
        { externalId: 's1', name: 'Artist', genres: [], imageUrl: null, matchScore: 90, provider: 'spotify' },
      ]);
      const deezerSearch = vi.fn().mockResolvedValue([
        { externalId: 'd1', name: 'Artist', genres: [], imageUrl: null, matchScore: 80, provider: 'deezer' },
      ]);
      const spotify = createMockProvider('spotify', { searchArtist: spotifySearch });
      const deezer = createMockProvider('deezer', { searchArtist: deezerSearch });
      registry.registerAll([spotify, deezer]);
      const r1 = await spotify.searchArtist('test');
      const r2 = await deezer.searchArtist('test');
      expect(r1).toHaveLength(1);
      expect(r2).toHaveLength(1);
      expect(spotifySearch).toHaveBeenCalledTimes(1);
      expect(deezerSearch).toHaveBeenCalledTimes(1);
    });
  });
});
