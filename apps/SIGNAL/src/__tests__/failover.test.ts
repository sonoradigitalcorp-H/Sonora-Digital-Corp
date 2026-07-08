import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { ProviderRegistry, getProviderRegistry } from '../providers/registry';
import { IntelligenceEngine } from '../providers/intelligence/engine';
import { getCacheManager } from '../providers/cache/cache-manager';
import type {
  DataProvider,
  ProviderHealth,
  NormalizedSearchResult,
  NormalizedProfile,
  NormalizedMetrics,
  NormalizedImages,
  NormalizedAlbum,
} from '../providers/types';

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

function degradedHealth(name: string, msg: string): ProviderHealth {
  return {
    name,
    status: 'degraded',
    message: msg,
    latencyMs: 200,
    lastChecked: new Date().toISOString(),
    configured: true,
    configurationError: null,
  };
}

function makeSearchResult(provider: string, id: string, name: string, score: number): NormalizedSearchResult {
  return { externalId: id, name, genres: [], imageUrl: null, matchScore: score, provider };
}

function makeProfile(provider: string, overrides: Partial<NormalizedProfile> = {}): Partial<NormalizedProfile> {
  return {
    externalId: `${provider}-id`,
    name: 'Test Artist',
    bio: `Bio from ${provider}`,
    genres: ['rock'],
    country: 'US',
    city: 'Los Angeles',
    profileUrl: `https://${provider}.com/artist`,
    provider,
    ...overrides,
  };
}

function makeMetrics(provider: string, overrides: Partial<NormalizedMetrics> = {}): Partial<NormalizedMetrics> {
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

function makeImages(provider: string, overrides: Partial<NormalizedImages> = {}): Partial<NormalizedImages> {
  return {
    externalId: `${provider}-id`,
    small: `https://${provider}.com/small.jpg`,
    medium: `https://${provider}.com/medium.jpg`,
    large: `https://${provider}.com/large.jpg`,
    provider,
    ...overrides,
  };
}

function makeAlbum(provider: string, title: string, overrides: Partial<NormalizedAlbum> = {}): NormalizedAlbum {
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

interface ProviderControl {
  failSearch: boolean;
  failProfile: boolean;
  failMetrics: boolean;
  failImages: boolean;
  failAlbums: boolean;
  failInit: boolean;
  failHealth: boolean;
  healthResult: ProviderHealth;
  searchResults: NormalizedSearchResult[];
  profileData: Partial<NormalizedProfile> | null;
  metricsData: Partial<NormalizedMetrics> | null;
  imagesData: Partial<NormalizedImages>;
  albumsData: NormalizedAlbum[];
}

function createControllableProvider(
  name: string,
  overrides?: Partial<ProviderControl>
): { provider: DataProvider; control: ProviderControl } {
  const control: ProviderControl = {
    failSearch: false,
    failProfile: false,
    failMetrics: false,
    failImages: false,
    failAlbums: false,
    failInit: false,
    failHealth: false,
    healthResult: healthyHealth(name),
    searchResults: [makeSearchResult(name, `${name}-id`, 'Test Artist', 90)],
    profileData: makeProfile(name),
    metricsData: makeMetrics(name),
    imagesData: makeImages(name),
    albumsData: [makeAlbum(name, 'Album One'), makeAlbum(name, 'Album Two')],
    ...overrides,
  };

  const provider: DataProvider = {
    name,
    initialize: vi.fn().mockImplementation(async () => {
      if (control.failInit) throw new Error(`${name} init failed`);
    }),
    health: vi.fn().mockImplementation(async () => {
      if (control.failHealth) throw new Error(`${name} health check failed`);
      return control.healthResult;
    }),
    searchArtist: vi.fn().mockImplementation(async (_query: string) => {
      if (control.failSearch) throw new Error(`${name} search failed`);
      return control.searchResults;
    }),
    fetchProfile: vi.fn().mockImplementation(async (_externalId: string) => {
      if (control.failProfile) throw new Error(`${name} profile fetch failed`);
      return control.profileData;
    }),
    fetchMetrics: vi.fn().mockImplementation(async (_externalId: string) => {
      if (control.failMetrics) throw new Error(`${name} metrics fetch failed`);
      return control.metricsData;
    }),
    fetchImages: vi.fn().mockImplementation(async (_externalId: string) => {
      if (control.failImages) throw new Error(`${name} images fetch failed`);
      return control.imagesData;
    }),
    fetchGenres: vi.fn().mockImplementation(async (_externalId: string) => {
      return control.profileData?.genres ?? [];
    }),
    fetchAlbums: vi.fn().mockImplementation(async (_externalId: string) => {
      if (control.failAlbums) throw new Error(`${name} albums fetch failed`);
      return control.albumsData;
    }),
  };

  return { provider, control };
}

beforeEach(() => {
  const cm = getCacheManager();
  cm.clear();
});

describe('Failover — All providers disabled', () => {
  let registry: ProviderRegistry;
  let engine: IntelligenceEngine;

  beforeEach(() => {
    registry = new ProviderRegistry();
  });

  it('search returns empty array when all providers have no results', async () => {
    const { provider: spotify, control: sc } = createControllableProvider('spotify');
    const { provider: youtube, control: yc } = createControllableProvider('youtube');
    const { provider: deezer, control: dc } = createControllableProvider('deezer');

    sc.searchResults = [];
    yc.searchResults = [];
    dc.searchResults = [];

    registry.registerAll([spotify, youtube, deezer]);
    engine = new IntelligenceEngine(registry);

    const results = await engine.search('test artist');
    expect(results).toEqual([]);
  });

  it('buildArtist returns low confidence when all providers return no data', async () => {
    const { provider: spotify, control: sc } = createControllableProvider('spotify');
    const { provider: youtube, control: yc } = createControllableProvider('youtube');

    sc.searchResults = [];
    sc.profileData = null;
    sc.metricsData = null;
    yc.searchResults = [];
    yc.profileData = null;
    yc.metricsData = null;

    registry.registerAll([spotify, youtube]);
    engine = new IntelligenceEngine(registry);

    const result = await engine.buildArtist('artist-1', 'Test Artist', {
      externalIds: { spotify: 's1', youtube: 'y1' },
    });

    expect(result.confidence).toBe('low');
    expect(result.sources).toHaveLength(0);
    expect(result.errors.length).toBeGreaterThanOrEqual(0);
  });
});

describe('Failover — Spotify disabled, remaining work', () => {
  let registry: ProviderRegistry;
  let engine: IntelligenceEngine;

  beforeEach(() => {
    registry = new ProviderRegistry();
  });

  it('builds a valid artist from YouTube only when Spotify returns nothing', async () => {
    const { provider: spotify, control: sc } = createControllableProvider('spotify');
    const { provider: youtube, control: yc } = createControllableProvider('youtube');

    sc.searchResults = [];
    sc.profileData = null;
    sc.metricsData = null;

    registry.registerAll([spotify, youtube]);
    engine = new IntelligenceEngine(registry);

    const result = await engine.buildArtist('artist-1', 'Test Artist', {
      externalIds: { youtube: 'yt-id' },
    });

    expect(result.artist.id).toBe('artist-1');
    expect(result.artist.name).toBe('Test Artist');
    expect(result.sources).toContain('youtube');
    expect(result.sources).not.toContain('spotify');
    expect(result.artist.profile.provider).toBe('youtube');
    expect(result.confidence).toBe('medium');
  });

  it('search returns only YouTube results when Spotify disabled', async () => {
    const { provider: spotify, control: sc } = createControllableProvider('spotify');
    const { provider: youtube, control: yc } = createControllableProvider('youtube');
    const ytResult = makeSearchResult('youtube', 'yt-1', 'Test Artist', 95);

    sc.searchResults = [];
    yc.searchResults = [ytResult];

    registry.registerAll([spotify, youtube]);
    engine = new IntelligenceEngine(registry);

    const results = await engine.search('test artist');

    expect(results).toHaveLength(1);
    expect(results[0].provider).toBe('youtube');
    expect(results[0].matchScore).toBe(95);
  });
});

describe('Failover — All providers fail during search', () => {
  let registry: ProviderRegistry;
  let engine: IntelligenceEngine;

  beforeEach(() => {
    registry = new ProviderRegistry();
  });

  it('returns empty array without crashing when all providers throw in searchArtist', async () => {
    const { provider: a, control: ac } = createControllableProvider('provider-a');
    const { provider: b, control: bc } = createControllableProvider('provider-b');

    ac.failSearch = true;
    bc.failSearch = true;

    registry.registerAll([a, b]);
    engine = new IntelligenceEngine(registry);

    const results = await engine.search('test');

    expect(results).toEqual([]);
  });

  it('does not throw an exception when every searchArtist rejects', async () => {
    const { provider: a, control: ac } = createControllableProvider('provider-a');
    const { provider: b, control: bc } = createControllableProvider('provider-b');
    const { provider: c, control: cc } = createControllableProvider('provider-c');

    ac.failSearch = true;
    bc.failSearch = true;
    cc.failSearch = true;

    registry.registerAll([a, b, c]);
    engine = new IntelligenceEngine(registry);

    await expect(engine.search('test')).resolves.toEqual([]);
  });
});

describe('Failover — All providers fail during buildArtist', () => {
  let registry: ProviderRegistry;
  let engine: IntelligenceEngine;

  beforeEach(() => {
    registry = new ProviderRegistry();
  });

  it('returns low confidence with errors when all fetchProfile calls throw', async () => {
    const { provider: a, control: ac } = createControllableProvider('provider-a');
    const { provider: b, control: bc } = createControllableProvider('provider-b');

    ac.failProfile = true;
    ac.failMetrics = true;
    ac.failImages = true;
    bc.failProfile = true;
    bc.failMetrics = true;
    bc.failImages = true;

    registry.registerAll([a, b]);
    engine = new IntelligenceEngine(registry);

    const result = await engine.buildArtist('artist-1', 'Test Artist', {
      externalIds: { 'provider-a': 'a1', 'provider-b': 'b1' },
    });

    expect(result.confidence).toBe('low');
    expect(result.sources).toHaveLength(0);
    expect(result.errors.length).toBeGreaterThanOrEqual(1);
  });

  it('accumulates errors from every failed provider in buildArtist', async () => {
    const { provider: a, control: ac } = createControllableProvider('provider-a');
    const { provider: b, control: bc } = createControllableProvider('provider-b');

    ac.failProfile = true;
    bc.failProfile = true;

    registry.registerAll([a, b]);
    engine = new IntelligenceEngine(registry);

    const result = await engine.buildArtist('artist-1', 'Test Artist', {
      externalIds: { 'provider-a': 'a1', 'provider-b': 'b1' },
    });

    const providerNames = result.errors.map(e => e.provider);
    expect(providerNames).toContain('provider-a');
    expect(providerNames).toContain('provider-b');
    expect(result.errors.every(e => e.recoverable === true)).toBe(true);
  });
});

describe('Failover — Mixed failures', () => {
  let registry: ProviderRegistry;
  let engine: IntelligenceEngine;

  beforeEach(() => {
    registry = new ProviderRegistry();
  });

  it('produces a merged valid result when one provider fails and another succeeds', async () => {
    const { provider: failing, control: fc } = createControllableProvider('failing');
    const { provider: working, control: wc } = createControllableProvider('working');

    fc.failProfile = true;
    fc.failMetrics = true;

    wc.profileData = makeProfile('working', { name: 'Test Artist', bio: 'Working bio' });
    wc.metricsData = makeMetrics('working', { monthlyListeners: 500_000 });

    registry.registerAll([failing, working]);
    engine = new IntelligenceEngine(registry);

    const result = await engine.buildArtist('artist-1', 'Test Artist', {
      externalIds: { failing: 'f1', working: 'w1' },
    });

    expect(result.artist.id).toBe('artist-1');
    expect(result.artist.name).toBe('Test Artist');
    expect(result.artist.profile.bio).toBe('Working bio');
    expect(result.artist.metrics.monthlyListeners).toBe(500_000);
    expect(result.sources).toContain('working');
    expect(result.sources).not.toContain('failing');
    expect(result.confidence).toBe('medium');
  });

  it('search still returns partial results when some providers fail', async () => {
    const { provider: failing, control: fc } = createControllableProvider('failing');
    const { provider: working, control: wc } = createControllableProvider('working');

    fc.failSearch = true;
    wc.searchResults = [makeSearchResult('working', 'w1', 'Found Artist', 85)];

    registry.registerAll([failing, working]);
    engine = new IntelligenceEngine(registry);

    const results = await engine.search('test');

    expect(results).toHaveLength(1);
    expect(results[0].provider).toBe('working');
    expect(results[0].matchScore).toBe(85);
  });

  it('merges data from the working provider while recording errors from the failed one', async () => {
    const { provider: failing, control: fc } = createControllableProvider('failing');
    const { provider: youtube, control: yc } = createControllableProvider('youtube');

    fc.failProfile = true;
    fc.failMetrics = true;

    yc.profileData = makeProfile('youtube', { bio: 'YouTube bio', genres: ['pop'] });
    yc.metricsData = makeMetrics('youtube', { followers: 1_200_000 });

    registry.registerAll([failing, youtube]);
    engine = new IntelligenceEngine(registry);

    const result = await engine.buildArtist('artist-1', 'Test Artist', {
      externalIds: { failing: 'f1', youtube: 'yt1' },
    });

    expect(result.artist.profile.bio).toBe('YouTube bio');
    expect(result.artist.profile.genres).toContain('pop');
    expect(result.artist.metrics.followers).toBe(1_200_000);
    expect(result.errors.some(e => e.provider === 'failing')).toBe(true);
    expect(result.errors.some(e => e.provider === 'youtube')).toBe(false);
  });
});

describe('Failover — Registry handles unregister gracefully', () => {
  let registry: ProviderRegistry;
  let engine: IntelligenceEngine;

  beforeEach(() => {
    registry = new ProviderRegistry();
  });

  it('search works after unregistering a provider', async () => {
    const { provider: spotify } = createControllableProvider('spotify');
    const { provider: youtube } = createControllableProvider('youtube');

    registry.registerAll([spotify, youtube]);
    registry.unregister('spotify');
    engine = new IntelligenceEngine(registry);

    const results = await engine.search('test');

    expect(Array.isArray(results)).toBe(true);
    expect(results.length).toBeGreaterThanOrEqual(0);
  });

  it('buildArtist works after unregistering a provider', async () => {
    const { provider: spotify, control: sc } = createControllableProvider('spotify');
    const { provider: youtube, control: yc } = createControllableProvider('youtube');

    registry.registerAll([spotify, youtube]);
    registry.unregister('youtube');
    engine = new IntelligenceEngine(registry);

    const result = await engine.buildArtist('artist-1', 'Test Artist', {
      externalIds: { spotify: 's1' },
    });

    expect(result.artist.id).toBe('artist-1');
    expect(result.artist.name).toBe('Test Artist');
    expect(result.sources).toContain('spotify');
  });

  it('healthAll works after unregistering all providers', async () => {
    const { provider: spotify } = createControllableProvider('spotify');
    registry.register(spotify);
    registry.unregister('spotify');

    engine = new IntelligenceEngine(registry);
    const health = await engine.health();

    expect(health.status).toBe('unhealthy');
    expect(health.providers).toBe(0);
  });

  it('unregister returns false for non-existent provider and does not crash', () => {
    const result = registry.unregister('nonexistent');
    expect(result).toBe(false);
  });
});

describe('Failover — No providers registered', () => {
  let registry: ProviderRegistry;
  let engine: IntelligenceEngine;

  beforeEach(() => {
    registry = new ProviderRegistry();
    engine = new IntelligenceEngine(registry);
  });

  it('search returns empty array', async () => {
    const results = await engine.search('test artist');
    expect(results).toEqual([]);
  });

  it('buildArtist returns low confidence with empty sources', async () => {
    const result = await engine.buildArtist('artist-1', 'Test Artist');

    expect(result.artist.id).toBe('artist-1');
    expect(result.artist.name).toBe('Test Artist');
    expect(result.sources).toHaveLength(0);
    expect(result.confidence).toBe('low');
  });

  it('health returns unhealthy status', async () => {
    const health = await engine.health();
    expect(health.status).toBe('unhealthy');
    expect(health.providers).toBe(0);
    expect(health.healthyProviders).toBe(0);
  });
});

describe('Failover — healthAll returns degraded/unhealthy gracefully', () => {
  let registry: ProviderRegistry;

  beforeEach(() => {
    registry = new ProviderRegistry();
  });

  it('returns all healthy statuses for fully healthy providers', async () => {
    const { provider: a } = createControllableProvider('provider-a');
    const { provider: b } = createControllableProvider('provider-b');

    registry.registerAll([a, b]);
    const health = await registry.healthAll();

    expect(health).toHaveLength(2);
    expect(health.every(h => h.status === 'healthy')).toBe(true);
    expect(health.every(h => h.configured === true)).toBe(true);
  });

  it('returns degraded when some but not all providers are unhealthy', async () => {
    const { provider: a, control: ac } = createControllableProvider('provider-a');
    const { provider: b, control: bc } = createControllableProvider('provider-b');

    ac.healthResult = degradedHealth('provider-a', 'rate limited');
    registry.registerAll([a, b]);

    const health = await registry.healthAll();

    const aHealth = health.find(h => h.name === 'provider-a')!;
    const bHealth = health.find(h => h.name === 'provider-b')!;
    expect(aHealth.status).toBe('degraded');
    expect(bHealth.status).toBe('healthy');
  });

  it('returns unhealthy status for providers that throw during health check', async () => {
    const { provider: a, control: ac } = createControllableProvider('provider-a');

    ac.failHealth = true;
    registry.register(a);

    const health = await registry.healthAll();

    expect(health).toHaveLength(1);
    expect(health[0].status).toBe('unhealthy');
    expect(health[0].message).toBe('provider-a health check failed');
  });

  it('returns unhealthy status for all providers when all health checks fail', async () => {
    const { provider: a, control: ac } = createControllableProvider('provider-a');
    const { provider: b, control: bc } = createControllableProvider('provider-b');

    ac.failHealth = true;
    bc.failHealth = true;
    registry.registerAll([a, b]);

    const health = await registry.healthAll();

    expect(health).toHaveLength(2);
    expect(health.every(h => h.status === 'unhealthy')).toBe(true);
  });

  it('gracefully handles a mix of degraded, unhealthy, and healthy providers', async () => {
    const { provider: a, control: ac } = createControllableProvider('provider-a');
    const { provider: b, control: bc } = createControllableProvider('provider-b');
    const { provider: c, control: cc } = createControllableProvider('provider-c');

    ac.healthResult = healthyHealth('provider-a');
    bc.healthResult = degradedHealth('provider-b', 'high latency');
    cc.failHealth = true;
    registry.registerAll([a, b, c]);

    const health = await registry.healthAll();

    expect(health).toHaveLength(3);
    expect(health.find(h => h.name === 'provider-a')!.status).toBe('healthy');
    expect(health.find(h => h.name === 'provider-b')!.status).toBe('degraded');
    expect(health.find(h => h.name === 'provider-c')!.status).toBe('unhealthy');
  });

  it('IntelligenceEngine.health reflects overall system health after provider failures', async () => {
    const { provider: ok } = createControllableProvider('healthy-provider');
    const { provider: bad } = createControllableProvider('failing-provider');
    bad.health = vi.fn().mockResolvedValue(unhealthyHealth('failing-provider', 'API down'));

    const r = new ProviderRegistry();
    r.registerAll([ok, bad]);

    const engine = new IntelligenceEngine(r);
    const health = await engine.health();

    expect(health.status).toBe('degraded');
    expect(health.healthyProviders).toBe(1);
    expect(health.errors).toContain('failing-provider: API down');
    expect(health.providers).toBe(r.size);
  });
});

describe('Failover — Provider error isolation', () => {
  let registry: ProviderRegistry;
  let engine: IntelligenceEngine;

  beforeEach(() => {
    registry = new ProviderRegistry();
  });

  it('one provider throwing in search does not prevent others from returning data', async () => {
    const { provider: a, control: ac } = createControllableProvider('provider-a');
    const { provider: b, control: bc } = createControllableProvider('provider-b');

    ac.failSearch = true;
    bc.searchResults = [makeSearchResult('provider-b', 'b1', 'Artist B', 80)];

    registry.registerAll([a, b]);
    engine = new IntelligenceEngine(registry);

    const results = await engine.search('test');

    expect(results).toHaveLength(1);
    expect(results[0].provider).toBe('provider-b');
  });

  it('one provider throwing in fetchProfile does not prevent others from contributing', async () => {
    const { provider: a, control: ac } = createControllableProvider('provider-a');
    const { provider: b, control: bc } = createControllableProvider('provider-b');

    ac.failProfile = true;

    registry.registerAll([a, b]);
    engine = new IntelligenceEngine(registry);

    const result = await engine.buildArtist('artist-1', 'Test Artist', {
      externalIds: { 'provider-a': 'a1', 'provider-b': 'b1' },
    });

    expect(result.artist.profile.name).toBe('Test Artist');
    expect(result.artist.profile.provider).toBe('provider-b');
    expect(result.sources).toContain('provider-b');
  });

  it('one provider throwing in fetchMetrics does not prevent metrics from being populated', async () => {
    const { provider: a, control: ac } = createControllableProvider('provider-a');
    const { provider: b, control: bc } = createControllableProvider('provider-b');

    ac.failMetrics = true;

    registry.registerAll([a, b]);
    engine = new IntelligenceEngine(registry);

    const result = await engine.buildArtist('artist-1', 'Test Artist', {
      externalIds: { 'provider-a': 'a1', 'provider-b': 'b1' },
    });

    expect(result.artist.metrics.monthlyListeners).toBe(1_000_000);
    expect(result.artist.metrics.provider).toBe('provider-b');
  });

  it('one provider throwing in fetchImages does not prevent images from being populated', async () => {
    const { provider: a, control: ac } = createControllableProvider('provider-a');
    const { provider: b, control: bc } = createControllableProvider('provider-b');

    ac.failImages = true;

    registry.registerAll([a, b]);
    engine = new IntelligenceEngine(registry);

    const result = await engine.buildArtist('artist-1', 'Test Artist', {
      externalIds: { 'provider-a': 'a1', 'provider-b': 'b1' },
    });

    expect(result.artist.images.large).toBe('https://provider-b.com/large.jpg');
  });
});

describe('Failover — Partial provider initialization', () => {
  let registry: ProviderRegistry;

  beforeEach(() => {
    registry = new ProviderRegistry();
  });

  it('returns failed list when some providers fail init and others succeed', async () => {
    const { provider: ok, control: oc } = createControllableProvider('good-provider');
    const { provider: bad, control: bc } = createControllableProvider('bad-provider');

    bc.failInit = true;

    registry.registerAll([ok, bad]);
    const result = await registry.initializeAll();

    expect(result.success).toEqual(['good-provider']);
    expect(result.failed).toEqual(['bad-provider']);
  });

  it('successfully initialized providers are usable via the registry', async () => {
    const { provider: ok, control: oc } = createControllableProvider('good-provider');
    const { provider: bad, control: bc } = createControllableProvider('bad-provider');

    bc.failInit = true;

    registry.registerAll([ok, bad]);
    const initResult = await registry.initializeAll();

    expect(initResult.success).toContain('good-provider');
    expect(initResult.failed).toContain('bad-provider');

    const good = registry.get('good-provider');
    expect(good).toBeDefined();
    const health = await good!.health();
    expect(health.status).toBe('healthy');
  });

  it('failed init providers are still registered but marked in failed list', async () => {
    const { provider: ok, control: oc } = createControllableProvider('good-provider');
    const { provider: bad, control: bc } = createControllableProvider('bad-provider');

    bc.failInit = true;

    registry.registerAll([ok, bad]);
    const initResult = await registry.initializeAll();

    const retrieved = registry.get('bad-provider');
    expect(retrieved).toBeDefined();
    expect(initResult.failed).toContain('bad-provider');
  });

  it('engine built with partially initialized registry still works with healthy providers', async () => {
    const { provider: ok, control: oc } = createControllableProvider('good-provider');
    const { provider: bad, control: bc } = createControllableProvider('bad-provider');

    bc.failInit = true;

    registry.registerAll([ok, bad]);
    await registry.initializeAll();

    const engine = new IntelligenceEngine(registry);
    const result = await engine.buildArtist('artist-1', 'Test Artist', {
      externalIds: { 'good-provider': 'g1' },
    });

    expect(result.artist.id).toBe('artist-1');
    expect(result.artist.name).toBe('Test Artist');
    expect(result.sources).toContain('good-provider');
    expect(result.confidence).toBe('medium');
  });
});

describe('Failover — Cache survives provider failures', () => {
  let registry: ProviderRegistry;
  let engine: IntelligenceEngine;

  beforeEach(() => {
    registry = new ProviderRegistry();
    getCacheManager().clear();
  });

  it('returns cached search results when provider becomes unavailable', async () => {
    const { provider: spotify, control: sc } = createControllableProvider('spotify');

    registry.register(spotify);
    engine = new IntelligenceEngine(registry);

    const firstResults = await engine.search('cached-artist');

    expect(firstResults).toHaveLength(1);
    expect(firstResults[0].provider).toBe('spotify');

    sc.failSearch = true;

    const secondResults = await engine.search('cached-artist');

    expect(secondResults).toEqual(firstResults);
  });

  it('returns cached data from search even when all providers fail', async () => {
    const { provider: a, control: ac } = createControllableProvider('provider-a');
    const { provider: b, control: bc } = createControllableProvider('provider-b');

    registry.registerAll([a, b]);
    engine = new IntelligenceEngine(registry);

    const first = await engine.search('unique-query');

    expect(first).toHaveLength(1);

    ac.failSearch = true;
    bc.failSearch = true;

    const cached = await engine.search('unique-query');

    expect(cached).toEqual(first);
  });

  it('cache miss on first query calls providers, cache hit on second skips them', async () => {
    const { provider: spotify, control: sc } = createControllableProvider('spotify');

    registry.register(spotify);
    engine = new IntelligenceEngine(registry);

    const miss = await engine.search('miss-hit-test');
    expect(miss).toHaveLength(1);

    // Second call should return cached result even when provider fails
    sc.failSearch = true;

    const hit = await engine.search('miss-hit-test');
    expect(hit).toEqual(miss);
  });

  it('different cache keys result in separate cache entries', async () => {
    const { provider: spotify, control: sc } = createControllableProvider('spotify');

    sc.searchResults = [makeSearchResult('spotify', 's1', 'Artist One', 90)];
    registry.register(spotify);
    engine = new IntelligenceEngine(registry);

    const res1 = await engine.search('alpha-cache');
    const baseline1 = (spotify.searchArtist as ReturnType<typeof vi.fn>).mock.calls.length;

    sc.searchResults = [makeSearchResult('spotify', 's2', 'Artist Two', 85)];
    const res2 = await engine.search('beta-cache');
    expect((spotify.searchArtist as ReturnType<typeof vi.fn>).mock.calls.length).toBeGreaterThan(baseline1);

    sc.failSearch = true;

    const cached1 = await engine.search('alpha-cache');
    expect(cached1).toEqual(res1);

    const cached2 = await engine.search('beta-cache');
    expect(cached2).toEqual(res2);

    expect(cached1).not.toEqual(cached2);
  });
});

describe('Failover — Registry handles double registration', () => {
  let registry: ProviderRegistry;

  beforeEach(() => {
    registry = new ProviderRegistry();
  });

  it('replaces an existing provider when registering the same name', () => {
    const { provider: first } = createControllableProvider('spotify');
    const { provider: second } = createControllableProvider('spotify');

    registry.register(first);
    registry.register(second);

    const retrieved = registry.get('spotify');
    expect(retrieved).toBe(second);
    expect(retrieved).not.toBe(first);
    expect(registry.size).toBe(1);
  });

  it('the new provider responds to calls instead of the old one', async () => {
    const firstSearch = vi.fn().mockResolvedValue([makeSearchResult('spotify', 'old', 'Old Artist', 50)]);
    const secondSearch = vi.fn().mockResolvedValue([makeSearchResult('spotify', 'new', 'New Artist', 100)]);

    const first = createControllableProvider('spotify');
    first.provider.searchArtist = firstSearch;
    registry.register(first.provider);

    const second = createControllableProvider('spotify');
    second.provider.searchArtist = secondSearch;
    registry.register(second.provider);

    const engine = new IntelligenceEngine(registry);
    const results = await engine.search('test');

    expect(results).toHaveLength(1);
    expect(results[0].externalId).toBe('new');
    expect(firstSearch).not.toHaveBeenCalled();
    expect(secondSearch).toHaveBeenCalledTimes(1);
  });

  it('double registration does not increase registry size', () => {
    const r = new ProviderRegistry();
    expect(r.size).toBe(0);

    const { provider: a } = createControllableProvider('double-reg-test');
    const { provider: b } = createControllableProvider('double-reg-test');

    r.register(a);
    expect(r.size).toBe(1);

    r.register(b);
    expect(r.size).toBe(1);

    r.register(a);
    expect(r.size).toBe(1);
  });

  it('the getProviderRegistry singleton handles replacement without increasing internal map size', () => {
    const singleton = getProviderRegistry();
    const sizeBefore = singleton.size;

    const { provider: a } = createControllableProvider('singleton-test');
    const { provider: b } = createControllableProvider('singleton-test');

    singleton.register(a);
    singleton.register(b);

    expect(singleton.size).toBe(sizeBefore + 1);
    expect(singleton.get('singleton-test')).toBe(b);
  });
});
