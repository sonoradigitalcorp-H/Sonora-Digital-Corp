// ───────────────────────────────────────────────
// SIGNAL Observability — Structured Logging,
// Request Correlation, Latency Tracking
// ───────────────────────────────────────────────

let requestCounter = 0;

// ── Correlation IDs ──

/**
 * Generate a unique request correlation ID.
 */
export function generateCorrelationId(): string {
  requestCounter++;
  const timestamp = Date.now().toString(36);
  const random = Math.random().toString(36).substring(2, 8);
  const counter = requestCounter.toString(36);
  return `sig-${timestamp}-${random}-${counter}`;
}

/**
 * Generate a simple unique ID (for jobs, events, etc.)
 */
export function generateId(prefix = 'evt'): string {
  return `${prefix}-${Date.now().toString(36)}-${Math.random().toString(36).substring(2, 8)}`;
}

// ── Structured Log Levels ──

export type LogLevel = 'debug' | 'info' | 'warn' | 'error';

export interface LogEntry {
  timestamp: string;
  level: LogLevel;
  service: string;
  message: string;
  correlationId?: string;
  durationMs?: number;
  error?: string;
  [key: string]: unknown;
}

// ── Structured Logger ──

export class StructuredLogger {
  private readonly service: string;

  constructor(service: string) {
    this.service = service;
  }

  debug(message: string, context?: Record<string, unknown>): void {
    this.log('debug', message, context);
  }

  info(message: string, context?: Record<string, unknown>): void {
    this.log('info', message, context);
  }

  warn(message: string, context?: Record<string, unknown>): void {
    this.log('warn', message, context);
  }

  error(message: string, context?: Record<string, unknown>): void {
    this.log('error', message, context);
  }

  private log(level: LogLevel, message: string, context?: Record<string, unknown>): void {
    const entry: LogEntry = {
      timestamp: new Date().toISOString(),
      level,
      service: this.service,
      message,
      ...context,
    };

    const formatted = JSON.stringify(entry);

    switch (level) {
      case 'error':
        console.error(formatted);
        break;
      case 'warn':
        console.warn(formatted);
        break;
      case 'debug':
        if (process.env.NODE_ENV === 'development') {
          console.debug(formatted);
        }
        break;
      default:
        console.log(formatted);
    }
  }

  /**
   * Measure and log the duration of an operation.
   */
  async timed<T>(operation: string, fn: () => Promise<T>, context?: Record<string, unknown>): Promise<T> {
    const start = Date.now();
    try {
      const result = await fn();
      this.info(`${operation} completed`, {
        ...context,
        durationMs: Date.now() - start,
      });
      return result;
    } catch (error) {
      this.error(`${operation} failed`, {
        ...context,
        durationMs: Date.now() - start,
        error: error instanceof Error ? error.message : String(error),
      });
      throw error;
    }
  }

  /**
   * Measure sync duration without promise handling.
   */
  timedSync<T>(operation: string, fn: () => T, context?: Record<string, unknown>): T {
    const start = Date.now();
    try {
      const result = fn();
      this.info(`${operation} completed`, {
        ...context,
        durationMs: Date.now() - start,
      });
      return result;
    } catch (error) {
      this.error(`${operation} failed`, {
        ...context,
        durationMs: Date.now() - start,
        error: error instanceof Error ? error.message : String(error),
      });
      throw error;
    }
  }
}

// ── Provider Latency Tracker ──

export interface ProviderLatency {
  provider: string;
  operation: string;
  durationMs: number;
  success: boolean;
  timestamp: string;
}

const providerLatencies: ProviderLatency[] = [];

const MAX_LATENCY_HISTORY = 1000;

/**
 * Record a provider operation latency for monitoring.
 */
export function recordProviderLatency(
  provider: string,
  operation: string,
  durationMs: number,
  success: boolean
): void {
  providerLatencies.push({
    provider,
    operation,
    durationMs,
    success,
    timestamp: new Date().toISOString(),
  });

  // Trim history to prevent memory leak
  if (providerLatencies.length > MAX_LATENCY_HISTORY) {
    providerLatencies.splice(0, providerLatencies.length - MAX_LATENCY_HISTORY);
  }
}

/**
 * Get provider latency statistics.
 */
export function getProviderLatencyStats(): Record<string, {
  totalCalls: number;
  successCalls: number;
  failedCalls: number;
  avgLatencyMs: number;
  p50Ms: number;
  p95Ms: number;
  p99Ms: number;
}> {
  const byProvider: Record<string, number[]> = {};
  const stats: Record<string, {
    totalCalls: number;
    successCalls: number;
    failedCalls: number;
    avgLatencyMs: number;
    p50Ms: number;
    p95Ms: number;
    p99Ms: number;
  }> = {};

  for (const entry of providerLatencies) {
    if (!byProvider[entry.provider]) {
      byProvider[entry.provider] = [];
      stats[entry.provider] = {
        totalCalls: 0,
        successCalls: 0,
        failedCalls: 0,
        avgLatencyMs: 0,
        p50Ms: 0,
        p95Ms: 0,
        p99Ms: 0,
      };
    }

    byProvider[entry.provider].push(entry.durationMs);
    stats[entry.provider].totalCalls++;
    if (entry.success) stats[entry.provider].successCalls++;
    else stats[entry.provider].failedCalls++;
  }

  // Compute percentiles
  for (const [provider, latencies] of Object.entries(byProvider)) {
    const sorted = [...latencies].sort((a, b) => a - b);
    stats[provider].avgLatencyMs = Math.round(
      sorted.reduce((a, b) => a + b, 0) / sorted.length
    );
    stats[provider].p50Ms = sorted[Math.floor(sorted.length * 0.5)] ?? 0;
    stats[provider].p95Ms = sorted[Math.floor(sorted.length * 0.95)] ?? 0;
    stats[provider].p99Ms = sorted[Math.floor(sorted.length * 0.99)] ?? 0;
  }

  return stats;
}

/**
 * Clear latency history (for testing).
 */
export function clearLatencyHistory(): void {
  providerLatencies.length = 0;
}

// ── Health Response Builder ──

export interface HealthResponse {
  status: 'healthy' | 'degraded' | 'unhealthy';
  version: string;
  timestamp: string;
  uptime: number;
  providers?: unknown;
  cache?: unknown;
}

/**
 * Build a standardized health check response.
 */
export function buildHealthResponse(
  status: HealthResponse['status'],
  extra?: Record<string, unknown>
): HealthResponse {
  return {
    status,
    version: process.env.NEXT_PUBLIC_APP_VERSION || '1.0.0',
    timestamp: new Date().toISOString(),
    uptime: process.uptime ? Math.floor(process.uptime()) : 0,
    ...extra,
  };
}

// ── Singleton loggers ──

export const providerLogger = new StructuredLogger('provider');
export const apiLogger = new StructuredLogger('api');
export const cacheLogger = new StructuredLogger('cache');
export const systemLogger = new StructuredLogger('system');
