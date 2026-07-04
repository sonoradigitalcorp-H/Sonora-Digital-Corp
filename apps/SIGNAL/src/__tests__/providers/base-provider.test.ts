// ───────────────────────────────────────────────
// BaseProvider Tests — Rate Limiting, Retries, Timeouts
// ───────────────────────────────────────────────

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { BaseProvider, RateLimiter, withRetry, createTimeoutSignal, createDefaultConfig } from '../../providers/base-provider';
import type { ProviderHealth, NormalizedSearchResult, NormalizedProfile, NormalizedMetrics, NormalizedImages } from '../../providers/types';

afterEach(() => {
  vi.useRealTimers();
});

// ── Mock Provider Implementation ──

class MockProvider extends BaseProvider {
  readonly name = 'mock-test';

  constructor() {
    super({
      name: 'mock-test',
      timeoutMs: 100,
      rateLimitIntervalMs: 50,
      maxRetries: 2,
      retryBaseDelayMs: 10,
    });
  }

  async initialize(): Promise<void> {
    this.initialized = true;
  }

  async health(): Promise<ProviderHealth> {
    return this.buildHealthResult('healthy', 'Mock operational', 5, true, null);
  }

  async searchArtist(_query: string): Promise<NormalizedSearchResult[]> {
    return [];
  }

  async fetchProfile(_externalId: string): Promise<Partial<NormalizedProfile> | null> {
    return null;
  }

  async fetchMetrics(_externalId: string): Promise<Partial<NormalizedMetrics> | null> {
    return null;
  }

  async fetchImages(_externalId: string): Promise<Partial<NormalizedImages>> {
    return { externalId: '', small: null, medium: null, large: null, provider: 'mock-test' };
  }

  async fetchGenres(_externalId: string): Promise<string[]> {
    return [];
  }
}

// ── Tests ──

describe('createDefaultConfig', () => {
  it('creates config with default values', () => {
    const config = createDefaultConfig({ name: 'test' });
    expect(config.name).toBe('test');
    expect(config.enabled).toBe(true);
    expect(config.timeoutMs).toBe(10000);
    expect(config.maxRetries).toBe(3);
    expect(config.retryBaseDelayMs).toBe(1000);
    expect(config.cacheTTLMs).toBe(24 * 60 * 60 * 1000);
  });

  it('overrides specific values', () => {
    const config = createDefaultConfig({ name: 'test', timeoutMs: 5000, maxRetries: 1 });
    expect(config.timeoutMs).toBe(5000);
    expect(config.maxRetries).toBe(1);
    // Other values still default
    expect(config.retryBaseDelayMs).toBe(1000);
  });
});

describe('createTimeoutSignal', () => {
  it('creates a signal that aborts after timeout', async () => {
    vi.useFakeTimers();
    const { signal, clear } = createTimeoutSignal(50);
    expect(signal.aborted).toBe(false);

    vi.advanceTimersByTime(60);
    expect(signal.aborted).toBe(true);
    expect(signal.reason).toBeInstanceOf(DOMException);
    expect((signal.reason as DOMException).name).toBe('TimeoutError');

    clear();
    vi.useRealTimers();
  });

  it('clear prevents abort', async () => {
    vi.useFakeTimers();
    const { signal, clear } = createTimeoutSignal(50);
    clear();
    vi.advanceTimersByTime(100);
    expect(signal.aborted).toBe(false);
    vi.useRealTimers();
  });
});

describe('RateLimiter', () => {
  it('throttles requests to minimum interval', async () => {
    const limiter = new RateLimiter(30);
    const t1 = Date.now();
    await limiter.throttle();
    const t2 = Date.now();
    expect(t2 - t1).toBeLessThan(20);

    await limiter.throttle();
    const t3 = Date.now();
    expect(t3 - t2).toBeGreaterThanOrEqual(25);
  });

  it('can be reset', async () => {
    const limiter = new RateLimiter(100);
    await limiter.throttle();
    limiter.reset();

    const start = Date.now();
    await limiter.throttle();
    expect(Date.now() - start).toBeLessThan(50);
  });
});

describe('withRetry', () => {
  it('succeeds on first try', async () => {
    let callCount = 0;
    const fn = async () => { callCount++; return 'success'; };
    const result = await withRetry('test', fn, { maxRetries: 2, baseDelayMs: 10 });
    expect(result).toBe('success');
    expect(callCount).toBe(1);
  });

  it('retries on failure and eventually succeeds', async () => {
    let attempts = 0;
    const fn = async () => {
      attempts++;
      if (attempts < 3) throw new Error('fail');
      return 'success';
    };

    const result = await withRetry('test', fn, { maxRetries: 2, baseDelayMs: 10 });
    expect(result).toBe('success');
    expect(attempts).toBe(3);
  });

  it('throws after exhausting retries', async () => {
    const fn = async () => { throw new Error('persistent'); };
    await expect(
      withRetry('test', fn, { maxRetries: 1, baseDelayMs: 10 })
    ).rejects.toThrow('persistent');
  });

  it('calls onRetry callback', async () => {
    let attempts = 0;
    const fn = async () => {
      attempts++;
      if (attempts < 2) throw new Error('fail');
      return 'success';
    };
    let retryAttempt: number | null = null;
    let retryError: Error | null = null;
    const onRetry = (attempt: number, error: Error) => {
      retryAttempt = attempt;
      retryError = error;
    };

    await withRetry('test', fn, { maxRetries: 1, baseDelayMs: 10, onRetry });
    expect(retryAttempt).toBe(1);
    expect(retryError).toBeInstanceOf(Error);
  });
});

describe('BaseProvider', () => {
  let provider: MockProvider;
  let originalFetch: typeof globalThis.fetch;

  beforeEach(() => {
    provider = new MockProvider();
    originalFetch = globalThis.fetch;
  });

  afterEach(() => {
    globalThis.fetch = originalFetch;
  });

  it('has a name', () => {
    expect(provider.name).toBe('mock-test');
  });

  it('initializes', async () => {
    await provider.initialize();
    expect(provider['initialized']).toBe(true);
  });

  it('reports health', async () => {
    const health = await provider.health();
    expect(health.name).toBe('mock-test');
    expect(health.status).toBe('healthy');
    expect(health.configured).toBe(true);
    expect(health.latencyMs).toBeGreaterThanOrEqual(0);
    expect(health.lastChecked).toBeTruthy();
  });

  it('builds health result correctly', () => {
    const healthResult = provider['buildHealthResult'](
      'healthy', 'test', 100, true, null
    );
    expect(healthResult).toEqual({
      name: 'mock-test',
      status: 'healthy',
      message: 'test',
      latencyMs: 100,
      lastChecked: expect.any(String),
      configured: true,
      configurationError: null,
    });
  });

  it('builds degraded health result', () => {
    const healthResult = provider['buildHealthResult'](
      'degraded', 'partial', 200, true, 'missing key'
    );
    expect(healthResult.status).toBe('degraded');
    expect(healthResult.configurationError).toBe('missing key');
  });

  it('builds unhealthy health result', () => {
    const healthResult = provider['buildHealthResult'](
      'unhealthy', 'down', 0, false, 'not configured'
    );
    expect(healthResult.status).toBe('unhealthy');
    expect(healthResult.configured).toBe(false);
  });

  it('returns empty arrays for unimplemented methods', async () => {
    const search = await provider.searchArtist('test');
    expect(search).toEqual([]);

    const profile = await provider.fetchProfile('test');
    expect(profile).toBeNull();

    const metrics = await provider.fetchMetrics('test');
    expect(metrics).toBeNull();

    const genres = await provider.fetchGenres('test');
    expect(genres).toEqual([]);
  });

  it('request handles network errors', async () => {
    globalThis.fetch = vi.fn().mockRejectedValue(new Error('Network failure'));
    const origRetries = provider['config'].maxRetries;
    provider['config'].maxRetries = 0;

    await expect(provider['request']('http://example.com')).rejects.toThrow('Network failure');

    provider['config'].maxRetries = origRetries;
  });

  it('request handles HTTP errors', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 404,
      statusText: 'Not Found',
      text: () => Promise.resolve('not found'),
    });

    const result = await provider['request']('http://example.com');
    expect(result.ok).toBe(false);
    expect(result.status).toBe(404);
  });

  it('request succeeds on valid response', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: () => Promise.resolve({ data: 'test' }),
    });

    const result = await provider['request']('http://example.com');
    expect(result.ok).toBe(true);
    expect(result.data).toEqual({ data: 'test' });
  });

  it('handles 429 rate limits with retry', async () => {
    const resp429 = Promise.resolve({
      ok: false,
      status: 429,
      headers: { get: () => '0' },
      text: () => Promise.resolve('rate limited'),
    });
    const resp200 = Promise.resolve({
      ok: true,
      status: 200,
      json: () => Promise.resolve({ data: 'ok' }),
    });

    let callCount = 0;
    globalThis.fetch = vi.fn((_url: string) => {
      callCount++;
      return callCount === 1 ? resp429 : resp200;
    });

    provider['config'].maxRetries = 3;

    const result = await provider['request']('http://example.com');
    expect(result.ok).toBe(true);
    expect(callCount).toBeGreaterThanOrEqual(2);
  });
});
