import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { IntelligenceEngine } from '../../providers/intelligence/engine';
import { ProviderRegistry } from '../../providers/registry';
import type {
  DataProvider,
  ProviderHealth,
  NormalizedSearchResult,
  NormalizedProfile,
  NormalizedMetrics,
  NormalizedImages,
  NormalizedAlbum,
} from '../../providers/types';

// ── Helpers ──

function healthyHealth(name: string): ProviderHealth {
  return {
    name,
    status: 'healthy',
    message: 'OK',
    latencyMs: 5,
    lastChecked: new Date().toISOString(),
    configured: true,
    configurationError: null,
  };
}

function unhealthyHealth(name: string, msg: string): ProviderHealth {
  return {
    name,
    status: 'unhealthy',
    message: msg,
    latencyMs: 0,
    lastChecked: new Date().toISOString(),
    configured: false,
    configurationError: msg,
  };
}

function createMockProvider(
  name: string,
  data?: {
    searchResults?: NormalizedSearchResult[];
    profile?: Partial<NormalizedProfile> | null;
    metrics?: Partial<NormalizedMetrics> | null;
    images?: Partial<NormalizedImages>;
    albums?: NormalizedAlbum[];
    healthResult?: ProviderHealth;
  }
): DataProvider {
  return {
    name,
    initialize: vi.fn().mockResolvedValue(undefined),
    health: vi.fn().mockResolvedValue(
      data?.healthResult ?? healthyHealth(name)
    ),
    searchArtist: vi.fn().mockResolvedValue(data?.searchResults ?? []),
    fetchProfile: vi.fn().mockResolvedValue(data?.profile ?? null),
    fetchMetrics: vi.fn().mockResolvedValue(data?.metrics ?? null),
    fetchImages: vi.fn().mockResolvedValue(
      data?.images ?? {
        externalId: '',
        small: null,
        medium: null,
        large: null,
        provider: name,
      }
    ),
    fetchGenres: vi.fn().mockResolvedValue([]),
    fetchAlbums: vi.fn().mockResolvedValue(data?.albums ?? []),
  };
}

function makeSearchResult(
  provider: string,
  id: string,
  name: string,
  score: number
): NormalizedSearchResult {
  return {
    externalId: id,
    name,
    genres: [],
    imageUrl: null,
    matchScore: score,
    provider,
  };
}

function makeProfile(
  provider: string,
  overrides: Partial<NormalizedProfile> = {}
): Partial<NormalizedProfile> {
  return {
    externalId: `${provider}-id`,
    name: 'Test Artist',
    bio: `Bio from ${provider}`,
    genres: ['rock', 'pop'],
    country: 'US',
    city: null,
    profileUrl: `https://${provider}.com/artist`,
    provider,
    ...overrides,
  };
}

function makeMetrics(
  provider: string,
  overrides: Partial<NormalizedMetrics> = {}
): Partial<NormalizedMetrics> {
  return {
    externalId: `${provider}-id`,
    monthlyListeners: 1_000_000,
    followers: 500_000,
    engagement: 75,
    growth: 12,
    momentum: 80,
    provider,
    ...overrides,
  };
}

function makeImages(
  provider: string,
  overrides: Partial<NormalizedImages> = {}
): Partial<NormalizedImages> {
  return {
    externalId: `${provider}-id`,
    small: `https://${provider}.com/small.jpg`,
    medium: `https://${provider}.com/medium.jpg`,
    large: `https://${provider}.com/large.jpg`,
    provider,
    ...overrides,
  };
}

function makeAlbum(
  provider: string,
  title: string,
  overrides: Partial<NormalizedAlbum> = {}
): NormalizedAlbum {
  return {
    externalId: `${provider}-${title}`,
    title,
    releaseDate: '2024-01-01',
    imageUrl: null,
    trackCount: 10,
    albumType: 'album',
    provider,
    ...overrides,
  };
}

// ── Tests ──

describe.sequential('IntelligenceEngine', () => {
  let registry: ProviderRegistry;
  let engine: IntelligenceEngine;

  beforeEach(() => {
    registry = new ProviderRegistry();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  // ── Constructor ──

  describe('constructor', () => {
    it('creates an engine with default config when no arguments provided', () => {
      const e = new IntelligenceEngine();
      expect(e).toBeInstanceOf(IntelligenceEngine);
      expect(e['config'].minProvidersForHighConfidence).toBe(2);
      expect(e['config'].allowPartialResults).toBe(true);
    });

    it('uses the provided registry', () => {
      const e = new IntelligenceEngine(registry);
      expect(e['registry']).toBe(registry);
    });

    it('merges provided config over defaults', () => {
      const e = new IntelligenceEngine(registry, {
        minProvidersForHighConfidence: 3,
        allowPartialResults: false,
      });
      expect(e['config'].minProvidersForHighConfidence).toBe(3);
      expect(e['config'].allowPartialResults).toBe(false);
      expect(e['config'].scorePriority).toEqual(['generated', 'spotify', 'average']);
    });
  });

  // ── Search ──

  describe('search', () => {
    it('returns merged search results from all providers sorted by matchScore', async () => {
      const spotify = createMockProvider('spotify', {
        searchResults: [
          makeSearchResult('spotify', 's1', 'Artist One', 90),
          makeSearchResult('spotify', 's2', 'Artist Two', 70),
        ],
      });
      const deezer = createMockProvider('deezer', {
        searchResults: [
          makeSearchResult('deezer', 'd1', 'Artist One', 85),
          makeSearchResult('deezer', 'd3', 'Artist Three', 60),
        ],
      });
      registry.registerAll([spotify, deezer]);
      engine = new IntelligenceEngine(registry);

      const results = await engine.search('artist');

      // Dedup by name keeps highest matchScore: Artist One stays at 90 (spotify)
      // Sorted descending: Artist One (90), Artist Two (70), Artist Three (60)
      expect(results).toHaveLength(3);
      expect(results[0].matchScore).toBe(90);
      expect(results[1].matchScore).toBe(70);
      expect(results[2].matchScore).toBe(60);
    });

    it('deduplicates by name keeping the highest matchScore', async () => {
      const spotify = createMockProvider('spotify', {
        searchResults: [
          makeSearchResult('spotify', 's1', 'Artist One', 90),
        ],
      });
      const deezer = createMockProvider('deezer', {
        searchResults: [
          makeSearchResult('deezer', 'd1', 'Artist One', 80),
          makeSearchResult('deezer', 'd2', 'Artist Two', 70),
        ],
      });
      registry.registerAll([spotify, deezer]);
      engine = new IntelligenceEngine(registry);

      const results = await engine.search('artist');

      expect(results).toHaveLength(2);
      const artistOne = results.find(r => r.name === 'Artist One');
      expect(artistOne!.matchScore).toBe(90);
      expect(artistOne!.provider).toBe('spotify');
    });

    it('handles partial failures gracefully', async () => {
      const ok = createMockProvider('ok', {
        searchResults: [
          makeSearchResult('ok', 'o1', 'Artist Ok', 80),
        ],
      });
      const failing = createMockProvider('failing', {
        searchArtist: vi.fn().mockRejectedValue(new Error('API error')),
      });
      registry.registerAll([ok, failing]);
      engine = new IntelligenceEngine(registry);

      const results = await engine.search('artist');
      expect(results).toHaveLength(1);
      expect(results[0].provider).toBe('ok');
    });

    it('returns empty array when all providers fail', async () => {
      const a = createMockProvider('a', {
        searchArtist: vi.fn().mockRejectedValue(new Error('fail')),
      });
      const b = createMockProvider('b', {
        searchArtist: vi.fn().mockRejectedValue(new Error('fail')),
      });
      registry.registerAll([a, b]);
      engine = new IntelligenceEngine(registry);

      const results = await engine.search('artist');
      expect(results).toEqual([]);
    });

    it('returns empty array when no providers are registered', async () => {
      engine = new IntelligenceEngine(registry);
      const results = await engine.search('artist');
      expect(results).toEqual([]);
    });
  });

  // ── Build Artist ──

  describe('buildArtist', () => {
    it('builds a unified artist from multiple providers with externalIds', async () => {
      const spotify = createMockProvider('spotify', {
        profile: makeProfile('spotify', { name: 'Test Artist', bio: 'Spotify bio' }),
        metrics: makeMetrics('spotify', { monthlyListeners: 2_000_000 }),
        images: makeImages('spotify', { large: 'https://spotify.com/large.jpg' }),
        albums: [
          makeAlbum('spotify', 'Album 1'),
          makeAlbum('spotify', 'Album 2'),
        ],
      });
      const deezer = createMockProvider('deezer', {
        profile: makeProfile('deezer', { name: 'Test Artist', bio: 'Deezer bio', country: 'GB' }),
        metrics: makeMetrics('deezer', { followers: 300_000 }),
        images: makeImages('deezer', { medium: 'https://deezer.com/med.jpg' }),
        albums: [
          makeAlbum('deezer', 'Album 1'),
          makeAlbum('deezer', 'Album 3'),
        ],
      });
      registry.registerAll([spotify, deezer]);
      engine = new IntelligenceEngine(registry);

      const result = await engine.buildArtist('artist-1', 'Test Artist', {
        externalIds: { spotify: 's1', deezer: 'd1' },
      });

      expect(result.artist.id).toBe('artist-1');
      expect(result.artist.name).toBe('Test Artist');
      expect(result.sources).toContain('spotify');
      expect(result.sources).toContain('deezer');
      expect(result.errors).toHaveLength(0);
    });

    it('uses externalIds from options when provided', async () => {
      const spotify = createMockProvider('spotify', {
        profile: makeProfile('spotify'),
      });
      registry.register(spotify);
      engine = new IntelligenceEngine(registry);

      await engine.buildArtist('a1', 'Test Artist', {
        externalIds: { spotify: 'ext-spotify-123' },
      });

      expect(spotify.fetchProfile).toHaveBeenCalledWith('ext-spotify-123');
    });

    it('auto-discovers externalIds by searching when not provided', async () => {
      const spotify = createMockProvider('spotify', {
        searchResults: [
          makeSearchResult('spotify', 'auto-s1', 'Test Artist', 95),
        ],
        profile: makeProfile('spotify', { name: 'Test Artist' }),
      });
      registry.register(spotify);
      engine = new IntelligenceEngine(registry);

      await engine.buildArtist('a1', 'Test Artist');

      expect(spotify.searchArtist).toHaveBeenCalledWith('Test Artist');
      expect(spotify.fetchProfile).toHaveBeenCalledWith('auto-s1');
    });

    it('merges profile data correctly from multiple providers', async () => {
      const spotify = createMockProvider('spotify', {
        profile: makeProfile('spotify', {
          name: 'Test Artist',
          bio: 'Spotify bio',
          genres: ['rock'],
          country: 'US',
        }),
      });
      const deezer = createMockProvider('deezer', {
        profile: makeProfile('deezer', {
          name: 'Test Artist',
          bio: 'Deezer bio',
          genres: ['pop', 'jazz'],
          city: 'London',
        }),
      });
      registry.registerAll([spotify, deezer]);
      engine = new IntelligenceEngine(registry);

      const result = await engine.buildArtist('a1', 'Test Artist', {
        externalIds: { spotify: 's1', deezer: 'd1' },
      });

      expect(result.artist.profile.name).toBe('Test Artist');
      expect(result.artist.profile.genres).toContain('rock');
      expect(result.artist.profile.genres).toContain('pop');
      expect(result.artist.profile.genres).toContain('jazz');
    });

    it('merges metrics preferring later non-null values', async () => {
      const spotify = createMockProvider('spotify', {
        metrics: makeMetrics('spotify', { monthlyListeners: 2_000_000, engagement: 80 }),
      });
      const deezer = createMockProvider('deezer', {
        metrics: makeMetrics('deezer', { followers: 500_000, growth: 15 }),
      });
      registry.registerAll([spotify, deezer]);
      engine = new IntelligenceEngine(registry);

      const result = await engine.buildArtist('a1', 'Test Artist', {
        externalIds: { spotify: 's1', deezer: 'd1' },
      });

      // spotify values: monthlyListeners=2M, engagement=80, followers=500K (default)
      // deezer values: followers=500K, growth=15, engagement=75 (default), monthlyListeners=1M (default)
      // mergeMetrics: later non-null overrides → deezer's 1M overrides spotify's 2M, deezer's 75 overrides 80
      expect(result.artist.metrics.monthlyListeners).toBe(1_000_000);
      expect(result.artist.metrics.followers).toBe(500_000);
      expect(result.artist.metrics.engagement).toBe(75);
      expect(result.artist.metrics.growth).toBe(15);
    });

    it('merges images preferring larger sizes', async () => {
      const spotify = createMockProvider('spotify', {
        images: makeImages('spotify', {
          large: 'https://spotify.com/large.jpg',
          medium: 'https://spotify.com/medium.jpg',
          small: 'https://spotify.com/small.jpg',
        }),
      });
      const deezer = createMockProvider('deezer', {
        images: makeImages('deezer', {
          large: 'https://deezer.com/large.jpg',
        }),
      });
      registry.registerAll([spotify, deezer]);
      engine = new IntelligenceEngine(registry);

      const result = await engine.buildArtist('a1', 'Test Artist', {
        externalIds: { spotify: 's1', deezer: 'd1' },
      });

      // mergeImages: later provider's large overrides earlier
      expect(result.artist.images.large).toBe('https://deezer.com/large.jpg');
      expect(result.artist.images.provider).toContain('spotify');
      expect(result.artist.images.provider).toContain('deezer');
    });

    it('merges albums deduplicating by title', async () => {
      const spotify = createMockProvider('spotify', {
        albums: [
          makeAlbum('spotify', 'Album One'),
          makeAlbum('spotify', 'Album Two'),
        ],
      });
      const deezer = createMockProvider('deezer', {
        albums: [
          makeAlbum('deezer', 'Album One'),
          makeAlbum('deezer', 'Album Three'),
        ],
      });
      registry.registerAll([spotify, deezer]);
      engine = new IntelligenceEngine(registry);

      const result = await engine.buildArtist('a1', 'Test Artist', {
        externalIds: { spotify: 's1', deezer: 'd1' },
      });

      expect(result.artist.albums).toHaveLength(3);
      const titles = result.artist.albums.map(a => a.title);
      expect(titles).toContain('Album One');
      expect(titles).toContain('Album Two');
      expect(titles).toContain('Album Three');
    });

    it('returns socials with all-null fields by default', async () => {
      const spotify = createMockProvider('spotify', {
        profile: makeProfile('spotify'),
      });
      registry.register(spotify);
      engine = new IntelligenceEngine(registry);

      const result = await engine.buildArtist('a1', 'Test Artist', {
        externalIds: { spotify: 's1' },
      });

      expect(result.artist.socials).toEqual({
        externalId: 'spotify-id',
        instagram: null,
        tiktok: null,
        twitter: null,
        youtube: null,
        spotify: 'https://spotify.com/artist',
        appleMusic: null,
        provider: 'merged',
      });
    });

    it('returns links with all-null fields by default', async () => {
      const spotify = createMockProvider('spotify', {
        profile: makeProfile('spotify'),
      });
      registry.register(spotify);
      engine = new IntelligenceEngine(registry);

      const result = await engine.buildArtist('a1', 'Test Artist', {
        externalIds: { spotify: 's1' },
      });

      expect(result.artist.links).toEqual({
        externalId: 'spotify-id',
        deezer: null,
        soundcloud: null,
        bandcamp: null,
        website: null,
        provider: 'merged',
      });
    });
  });

  // ── Build Artist: error accumulation ──

  describe('buildArtist error accumulation', () => {
    it('collects errors from providers that fail', async () => {
      const ok = createMockProvider('ok', {
        profile: makeProfile('ok'),
      });
      const failing = createMockProvider('failing', {
        profile: makeProfile('failing'),
        metrics: makeMetrics('failing'),
        images: makeImages('failing'),
      });
      failing.fetchProfile = vi.fn().mockRejectedValue(new Error('profile error'));
      registry.registerAll([ok, failing]);
      engine = new IntelligenceEngine(registry);

      const result = await engine.buildArtist('a1', 'Test Artist', {
        externalIds: { ok: 'o1', failing: 'f1' },
      });

      expect(result.errors.length).toBeGreaterThanOrEqual(1);
      const failingError = result.errors.find(e => e.provider === 'failing');
      expect(failingError).toBeDefined();
      expect(failingError!.error).toContain('profile error');
      expect(failingError!.recoverable).toBe(true);
    });

    it('collects errors from metrics failures', async () => {
      const failing = createMockProvider('failing', {
        profile: makeProfile('failing'),
        metrics: null,
        images: makeImages('failing'),
      });
      failing.fetchMetrics = vi.fn().mockRejectedValue(new Error('metrics error'));
      registry.register(failing);
      engine = new IntelligenceEngine(registry);

      const result = await engine.buildArtist('a1', 'Test Artist', {
        externalIds: { failing: 'f1' },
      });

      const metricsError = result.errors.find(e => e.error.includes('Metrics'));
      expect(metricsError).toBeDefined();
    });

    it('collects errors from image fetch failures', async () => {
      const failing = createMockProvider('failing', {
        profile: makeProfile('failing'),
        metrics: makeMetrics('failing'),
      });
      failing.fetchImages = vi.fn().mockRejectedValue(new Error('image error'));
      registry.register(failing);
      engine = new IntelligenceEngine(registry);

      const result = await engine.buildArtist('a1', 'Test Artist', {
        externalIds: { failing: 'f1' },
      });

      const imageError = result.errors.find(e => e.error.includes('Images'));
      expect(imageError).toBeDefined();
    });

    it('does not call fetchAlbums on providers without that method', async () => {
      const noAlbums: DataProvider = {
        name: 'basic',
        initialize: vi.fn().mockResolvedValue(undefined),
        health: vi.fn().mockResolvedValue(healthyHealth('basic')),
        searchArtist: vi.fn().mockResolvedValue([]),
        fetchProfile: vi.fn().mockResolvedValue(makeProfile('basic')),
        fetchMetrics: vi.fn().mockResolvedValue(makeMetrics('basic')),
        fetchImages: vi.fn().mockResolvedValue(makeImages('basic')),
        fetchGenres: vi.fn().mockResolvedValue([]),
      };
      registry.register(noAlbums);
      engine = new IntelligenceEngine(registry);

      const result = await engine.buildArtist('a1', 'Test Artist', {
        externalIds: { basic: 'b1' },
      });

      expect(result.artist.albums).toEqual([]);
    });
  });

  // ── Build Artist: confidence scoring ──

  describe('buildArtist confidence scoring', () => {
    it('returns high confidence when multiple providers succeed with no errors', async () => {
      const spotify = createMockProvider('spotify', {
        profile: makeProfile('spotify'),
        metrics: makeMetrics('spotify'),
      });
      const deezer = createMockProvider('deezer', {
        profile: makeProfile('deezer'),
        metrics: makeMetrics('deezer'),
      });
      registry.registerAll([spotify, deezer]);
      engine = new IntelligenceEngine(registry);

      const result = await engine.buildArtist('a1', 'Test Artist', {
        externalIds: { spotify: 's1', deezer: 'd1' },
      });

      expect(result.confidence).toBe('high');
    });

    it('returns medium confidence when only one provider contributes sources', async () => {
      const spotify = createMockProvider('spotify', {
        profile: makeProfile('spotify'),
      });
      registry.register(spotify);
      engine = new IntelligenceEngine(registry);

      const result = await engine.buildArtist('a1', 'Test Artist', {
        externalIds: { spotify: 's1' },
      });

      expect(result.confidence).toBe('medium');
    });

    it('returns medium confidence when there are only recoverable errors', async () => {
      const spotify = createMockProvider('spotify', {
        profile: makeProfile('spotify'),
        fetchMetrics: vi.fn().mockRejectedValue(new Error('metrics down')),
        images: makeImages('spotify'),
      });
      registry.register(spotify);
      engine = new IntelligenceEngine(registry);

      const result = await engine.buildArtist('a1', 'Test Artist', {
        externalIds: { spotify: 's1' },
      });

      expect(result.confidence).toBe('medium');
    });

    it('returns low confidence when no provider contributes sources', async () => {
      const failing = createMockProvider('failing', {
        fetchProfile: vi.fn().mockRejectedValue(new Error('total failure')),
        searchArtist: vi.fn().mockResolvedValue([]),
      });
      registry.register(failing);
      engine = new IntelligenceEngine(registry);

      const result = await engine.buildArtist('a1', 'Test Artist', {
        externalIds: { failing: 'f1' },
      });

      expect(result.confidence).toBe('low');
    });

    it('uses custom minProvidersForHighConfidence from config', async () => {
      const spotify = createMockProvider('spotify', {
        profile: makeProfile('spotify'),
      });
      const deezer = createMockProvider('deezer', {
        profile: makeProfile('deezer'),
      });
      registry.registerAll([spotify, deezer]);
      engine = new IntelligenceEngine(registry, { minProvidersForHighConfidence: 3 });

      const result = await engine.buildArtist('a1', 'Test Artist', {
        externalIds: { spotify: 's1', deezer: 'd1' },
      });

      expect(result.confidence).toBe('medium');
    });
  });

  // ── Refresh Artist ──

  describe('refreshArtist', () => {
    it('calls removeByProvider for all registered providers', async () => {
      const spotify = createMockProvider('spotify');
      const deezer = createMockProvider('deezer');
      registry.registerAll([spotify, deezer]);
      engine = new IntelligenceEngine(registry);

      const cacheManager = (await import('../../providers/cache/cache-manager')).getCacheManager();
      const removeByProviderSpy = vi.spyOn(cacheManager, 'removeByProvider');

      await engine.refreshArtist('a1', 'Test Artist');

      expect(removeByProviderSpy).toHaveBeenCalledWith('spotify');
      expect(removeByProviderSpy).toHaveBeenCalledWith('deezer');
    });

    it('removes cached data stored under provider namespaces', async () => {
      const spotify = createMockProvider('spotify', {
        profile: makeProfile('spotify'),
      });
      registry.register(spotify);
      engine = new IntelligenceEngine(registry);

      const cacheManager = (await import('../../providers/cache/cache-manager')).getCacheManager();
      cacheManager.set('spotify', 'artist', 's1', { name: 'Test Artist' });
      cacheManager.set('deezer', 'artist', 'd1', { name: 'Other Artist' });

      await engine.refreshArtist('a1', 'Test Artist');

      expect(cacheManager.get('spotify', 'artist', 's1')).toBeUndefined();
      expect(cacheManager.get('deezer', 'artist', 'd1')).toBeDefined();
    });
  });

  // ── Health ──

  describe('health', () => {
    it('returns healthy when all providers are healthy', async () => {
      const a = createMockProvider('a', {
        healthResult: healthyHealth('a'),
      });
      const b = createMockProvider('b', {
        healthResult: healthyHealth('b'),
      });
      registry.registerAll([a, b]);
      engine = new IntelligenceEngine(registry);

      const health = await engine.health();
      expect(health.status).toBe('healthy');
      expect(health.providers).toBe(2);
      expect(health.healthyProviders).toBe(2);
      expect(health.errors).toEqual([]);
    });

    it('returns degraded when some providers are unhealthy', async () => {
      const a = createMockProvider('a', {
        healthResult: healthyHealth('a'),
      });
      const b = createMockProvider('b', {
        healthResult: unhealthyHealth('b', 'rate limited'),
      });
      registry.registerAll([a, b]);
      engine = new IntelligenceEngine(registry);

      const health = await engine.health();
      expect(health.status).toBe('degraded');
      expect(health.providers).toBe(2);
      expect(health.healthyProviders).toBe(1);
      expect(health.errors).toContain('b: rate limited');
    });

    it('returns unhealthy when all providers are unhealthy', async () => {
      const a = createMockProvider('a', {
        healthResult: unhealthyHealth('a', 'down'),
      });
      const b = createMockProvider('b', {
        healthResult: unhealthyHealth('b', 'down'),
      });
      registry.registerAll([a, b]);
      engine = new IntelligenceEngine(registry);

      const health = await engine.health();
      expect(health.status).toBe('unhealthy');
      expect(health.healthyProviders).toBe(0);
    });

    it('returns unhealthy when no providers are registered', async () => {
      engine = new IntelligenceEngine(registry);
      const health = await engine.health();
      expect(health.status).toBe('unhealthy');
      expect(health.providers).toBe(0);
      expect(health.healthyProviders).toBe(0);
    });
  });

  // ── Error Absorption ──

  describe('error absorption', () => {
    it('a provider failure does not crash the engine during buildArtist', async () => {
      const spotify = createMockProvider('spotify', {
        profile: makeProfile('spotify'),
        metrics: null,
        images: makeImages('spotify'),
      });
      spotify.fetchMetrics = vi.fn().mockRejectedValue(new Error('metrics crash'));
      const deezer = createMockProvider('deezer', {
        profile: makeProfile('deezer'),
      });
      registry.registerAll([spotify, deezer]);
      engine = new IntelligenceEngine(registry);

      const result = await engine.buildArtist('a1', 'Test Artist', {
        externalIds: { spotify: 's1', deezer: 'd1' },
      });

      expect(result.artist).toBeDefined();
      expect(result.artist.id).toBe('a1');
      expect(result.errors.length).toBeGreaterThanOrEqual(1);
    });

    it('a provider failure does not crash the engine during search', async () => {
      const ok = createMockProvider('ok', {
        searchResults: [makeSearchResult('ok', 'o1', 'Found', 90)],
      });
      const failing = createMockProvider('failing', {
        searchArtist: vi.fn().mockRejectedValue(new Error('search crash')),
      });
      registry.registerAll([ok, failing]);
      engine = new IntelligenceEngine(registry);

      const results = await engine.search('test');
      expect(results).toHaveLength(1);
      expect(results[0].name).toBe('Found');
    });

    it('all providers can fail without crashing', async () => {
      const a = createMockProvider('a', {
        fetchProfile: vi.fn().mockRejectedValue(new Error('fail')),
        searchArtist: vi.fn().mockResolvedValue([]),
      });
      registry.register(a);
      engine = new IntelligenceEngine(registry);

      const result = await engine.buildArtist('a1', 'Test Artist', {
        externalIds: { a: 'a1' },
      });

      expect(result.artist).toBeDefined();
      expect(result.artist.id).toBe('a1');
      expect(result.sources).toHaveLength(0);
    });
  });

  // ── Partial Data ──

  describe('partial data acceptance', () => {
    it('produces valid output even when profile is mostly nulls', async () => {
      const spotify = createMockProvider('spotify', {
        profile: { externalId: 's1', name: 'Test Artist', bio: null, genres: [], country: null, city: null, profileUrl: null, provider: 'spotify' },
      });
      registry.register(spotify);
      engine = new IntelligenceEngine(registry);

      const result = await engine.buildArtist('a1', 'Test Artist', {
        externalIds: { spotify: 's1' },
      });

      expect(result.artist.profile.name).toBe('Test Artist');
      expect(result.artist.profile.bio).toBeNull();
      expect(result.artist.profile.country).toBeNull();
    });

    it('produces valid output when metrics are null', async () => {
      const spotify = createMockProvider('spotify', {
        profile: makeProfile('spotify'),
        metrics: { externalId: 's1', monthlyListeners: null, followers: null, engagement: null, growth: null, momentum: null, provider: 'spotify' },
      });
      registry.register(spotify);
      engine = new IntelligenceEngine(registry);

      const result = await engine.buildArtist('a1', 'Test Artist', {
        externalIds: { spotify: 's1' },
      });

      expect(result.artist.metrics.monthlyListeners).toBeNull();
      expect(result.artist.metrics.followers).toBeNull();
    });

    it('produces valid output when images are all null', async () => {
      const spotify = createMockProvider('spotify', {
        profile: makeProfile('spotify'),
        images: { externalId: 's1', small: null, medium: null, large: null, provider: 'spotify' },
      });
      registry.register(spotify);
      engine = new IntelligenceEngine(registry);

      const result = await engine.buildArtist('a1', 'Test Artist', {
        externalIds: { spotify: 's1' },
      });

      expect(result.artist.images.small).toBeNull();
      expect(result.artist.images.medium).toBeNull();
      expect(result.artist.images.large).toBeNull();
    });

    it('produces valid output with empty albums array', async () => {
      const spotify = createMockProvider('spotify', {
        profile: makeProfile('spotify'),
        albums: [],
      });
      registry.register(spotify);
      engine = new IntelligenceEngine(registry);

      const result = await engine.buildArtist('a1', 'Test Artist', {
        externalIds: { spotify: 's1' },
      });

      expect(result.artist.albums).toEqual([]);
    });

    it('handles providers that return null for every data type', async () => {
      const spotify = createMockProvider('spotify', {
        profile: null,
        metrics: null,
        images: { externalId: '', small: null, medium: null, large: null, provider: 'spotify' },
        albums: [],
      });
      registry.register(spotify);
      engine = new IntelligenceEngine(registry);

      const result = await engine.buildArtist('a1', 'Test Artist', {
        externalIds: { spotify: 's1' },
      });

      expect(result.artist).toBeDefined();
      expect(result.artist.id).toBe('a1');
      expect(result.confidence).toBe('low');
    });
  });
});
