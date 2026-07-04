// ───────────────────────────────────────────────
// SIGNAL Abstract Base Provider
// Retry logic, rate limiting, health check, logging
// ───────────────────────────────────────────────

import type {
  DataProvider,
  ProviderConfig,
  ProviderHealth,
  NormalizedSearchResult,
  NormalizedProfile,
  NormalizedMetrics,
  NormalizedImages,
} from './types';

// ── Logger ──

export function logProvider(
  provider: string,
  level: 'info' | 'warn' | 'error' | 'debug',
  message: string,
  context?: Record<string, unknown>
): void {
  const timestamp = new Date().toISOString();
  const prefix = `[${provider}] ${timestamp}`;
  const ctx = context ? ` ${JSON.stringify(context)}` : '';

  switch (level) {
    case 'debug':
      if (process.env.NODE_ENV === 'development') {
        console.debug(`${prefix}  ${message}${ctx}`);
      }
      break;
    case 'info':
      console.log(`${prefix} ${message}${ctx}`);
      break;
    case 'warn':
      console.warn(`${prefix} ⚠️ ${message}${ctx}`);
      break;
    case 'error':
      console.error(`${prefix} ❌ ${message}${ctx}`);
      break;
  }
}

// ── AbortController Helper ──

export function createTimeoutSignal(ms: number): { signal: AbortSignal; clear: () => void } {
  const controller = new AbortController();
  const timeoutId = setTimeout(
    () => controller.abort(new DOMException('Request timed out', 'TimeoutError')),
    ms
  );
  return {
    signal: controller.signal,
    clear: () => clearTimeout(timeoutId),
  };
}

// ── Rate Limiter ──

export class RateLimiter {
  private lastRequestTime = 0;
  private readonly intervalMs: number;

  constructor(intervalMs: number) {
    this.intervalMs = intervalMs;
  }

  async throttle(): Promise<void> {
    const now = Date.now();
    const elapsed = now - this.lastRequestTime;
    const waitTime = Math.max(0, this.intervalMs - elapsed);

    if (waitTime > 0) {
      await new Promise(resolve => setTimeout(resolve, waitTime));
    }

    this.lastRequestTime = Date.now();
  }

  reset(): void {
    this.lastRequestTime = 0;
  }
}

// ── Retry Handler ──

export async function withRetry<T>(
  provider: string,
  fn: () => Promise<T>,
  options: {
    maxRetries: number;
    baseDelayMs: number;
    onRetry?: (attempt: number, error: Error) => void;
  }
): Promise<T> {
  let lastError: Error | null = null;

  for (let attempt = 0; attempt <= options.maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error instanceof Error ? error : new Error(String(error));

      if (attempt < options.maxRetries) {
        // Exponential backoff with jitter
        const delay = Math.min(
          30000, // Cap at 30s
          options.baseDelayMs * Math.pow(2, attempt) + Math.random() * 1000
        );

        logProvider(provider, 'warn', `Retry ${attempt + 1}/${options.maxRetries}`, {
          error: lastError.message,
          delayMs: Math.round(delay),
        });

        options.onRetry?.(attempt + 1, lastError);
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
  }

  throw lastError ?? new Error(`${provider}: max retries exceeded`);
}

// ── Default Provider Config ──

export function createDefaultConfig(overrides: Partial<ProviderConfig> & { name: string }): ProviderConfig {
  return {
    name: overrides.name,
    enabled: true,
    timeoutMs: 10000,
    rateLimitIntervalMs: 200,
    maxRetries: 3,
    retryBaseDelayMs: 1000,
    healthCheckIntervalMs: 60000,
    cacheTTLMs: 24 * 60 * 60 * 1000, // 24 hours
    ...overrides,
  };
}

// ── Abstract Base Provider ──

export abstract class BaseProvider implements DataProvider {
  abstract readonly name: string;
  protected readonly config: ProviderConfig;
  protected readonly rateLimiter: RateLimiter;
  protected initialized = false;

  constructor(config: Partial<ProviderConfig> & { name: string }) {
    this.config = createDefaultConfig(config);
    this.rateLimiter = new RateLimiter(this.config.rateLimitIntervalMs);
  }

  // ── Lifecycle ──

  abstract initialize(): Promise<void>;

  // ── Abstract Provider Methods ──

  abstract searchArtist(query: string): Promise<NormalizedSearchResult[]>;
  abstract fetchProfile(externalId: string): Promise<Partial<NormalizedProfile> | null>;
  abstract fetchMetrics(externalId: string): Promise<Partial<NormalizedMetrics> | null>;
  abstract fetchImages(externalId: string): Promise<Partial<NormalizedImages>>;
  abstract fetchGenres(externalId: string): Promise<string[]>;

  // ── Health Check ──

  abstract health(): Promise<ProviderHealth>;

  protected buildHealthResult(
    status: ProviderHealth['status'],
    message: string,
    latencyMs: number,
    configured: boolean,
    configurationError: string | null
  ): ProviderHealth {
    return {
      name: this.name,
      status,
      message,
      latencyMs,
      lastChecked: new Date().toISOString(),
      configured,
      configurationError,
    };
  }

  // ── Protected Helpers ──

  /**
   * Make a rate-limited, retry-enabled HTTP request.
   * Handles 429 rate limiting with exponential backoff.
   */
  protected async request<T>(
    url: string,
    options: RequestInit & { retryCount?: number } = {}
  ): Promise<{ ok: boolean; status: number; data: T | null; error: string | null }> {
    return withRetry(
      this.name,
      async () => {
        await this.rateLimiter.throttle();

        const { signal, clear } = createTimeoutSignal(this.config.timeoutMs);
        let retryCount = options.retryCount ?? 0;

        try {
          const response = await fetch(url, {
            ...options,
            signal,
            headers: {
              ...options.headers,
            },
          });

          // Handle 429 Too Many Requests
          if (response.status === 429) {
            const retryAfter = parseInt(response.headers.get('Retry-After') || '1', 10);
            if (retryCount >= this.config.maxRetries) {
              return {
                ok: false,
                status: 429,
                data: null,
                error: `Rate limited after ${this.config.maxRetries} retries`,
              };
            }

            const delay = retryAfter * 1000 + Math.random() * 1000;
            logProvider(this.name, 'warn', 'Rate limited', {
              retryAfter,
              retryCount: retryCount + 1,
              delayMs: Math.round(delay),
            });

            await new Promise(resolve => setTimeout(resolve, delay));
            return this.request(url, { ...options, retryCount: retryCount + 1 });
          }

          if (!response.ok) {
            const body = await response.text().catch(() => '(empty)');
            return {
              ok: false,
              status: response.status,
              data: null,
              error: `${response.status} ${response.statusText}: ${body.slice(0, 200)}`,
            };
          }

          const data = await response.json() as T;
          return { ok: true, status: response.status, data, error: null };
        } finally {
          clear();
        }
      },
      {
        maxRetries: this.config.maxRetries,
        baseDelayMs: this.config.retryBaseDelayMs,
      }
    );
  }

  /**
   * Log a message with this provider's prefix.
   */
  protected log(level: 'info' | 'warn' | 'error' | 'debug', message: string, context?: Record<string, unknown>): void {
    logProvider(this.name, level, message, context);
  }
}
