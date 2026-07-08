// ───────────────────────────────────────────────
// SIGNAL Background Job Manager
// Handles provider refresh, cache invalidation, health checks
// ───────────────────────────────────────────────

import { getProviderRegistry, ProviderRegistry } from '../registry';
import { getCacheManager } from '../cache/cache-manager';
import { logProvider } from '../base-provider';
import type { Job, JobStatus, JobType, JobDefinition } from '../types';

// ── Job Manager ──

export class JobManager {
  private jobs: Map<string, Job> = new Map();
  private running = false;
  private intervalTimer: NodeJS.Timeout | null = null;
  private readonly registry: ProviderRegistry;
  private jobCounter = 0;

  constructor(registry?: ProviderRegistry) {
    this.registry = registry ?? getProviderRegistry();
  }

  // ── Job Lifecycle ──

  /**
   * Submit a new background job.
   */
  submit(definition: JobDefinition): string {
    const id = `job-${++this.jobCounter}-${Date.now()}`;
    const job: Job = {
      id,
      type: definition.type,
      status: 'pending',
      progress: 0,
      createdAt: new Date().toISOString(),
      startedAt: null,
      completedAt: null,
      error: null,
      result: definition.payload ?? null,
    };

    this.jobs.set(id, job);
    logProvider('jobs', 'info', `Job submitted`, { id, type: definition.type });

    // Execute immediately (non-blocking)
    this.executeJob(job, definition).catch(error => {
      logProvider('jobs', 'error', `Job execution failed`, {
        id,
        error: error instanceof Error ? error.message : String(error),
      });
    });

    return id;
  }

  /**
   * Get a job by ID.
   */
  get(id: string): Job | undefined {
    return this.jobs.get(id);
  }

  /**
   * Get all jobs, optionally filtered by status.
   */
  list(status?: JobStatus): Job[] {
    const all = Array.from(this.jobs.values());
    return status ? all.filter(j => j.status === status) : all;
  }

  /**
   * Get recent jobs (last N).
   */
  recent(count = 10): Job[] {
    return Array.from(this.jobs.values())
      .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
      .slice(0, count);
  }

  /**
   * Cancel a pending/running job.
   */
  cancel(id: string): boolean {
    const job = this.jobs.get(id);
    if (!job || job.status === 'completed') return false;

    job.status = 'cancelled';
    job.completedAt = new Date().toISOString();
    return true;
  }

  /**
   * Remove old jobs (keep only the last N).
   */
  cleanup(maxJobs = 100): number {
    const all = Array.from(this.jobs.values())
      .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());

    let removedCount = 0;
    for (let i = maxJobs; i < all.length; i++) {
      this.jobs.delete(all[i].id);
      removedCount++;
    }

    return removedCount;
  }

  /**
   * Start periodic job execution.
   * Runs cleanup and health checks on an interval.
   */
  startPeriodic(intervalMs = 5 * 60 * 1000): void {
    if (this.intervalTimer) return;

    this.intervalTimer = setInterval(async () => {
      // Run periodic refresh
      await this.runPeriodicRefresh();
      // Cleanup old jobs
      this.cleanup(200);
    }, intervalMs);

    logProvider('jobs', 'info', 'Periodic job execution started', { intervalMs });
  }

  /**
   * Stop periodic job execution.
   */
  stopPeriodic(): void {
    if (this.intervalTimer) {
      clearInterval(this.intervalTimer);
      this.intervalTimer = null;
    }
  }

  // ── Job Execution ──

  private async executeJob(job: Job, definition: JobDefinition): Promise<void> {
    job.status = 'running';
    job.startedAt = new Date().toISOString();

    try {
      switch (definition.type) {
        case 'refresh-provider':
          await this.handleRefreshProvider(job, definition);
          break;
        case 'refresh-cache':
          await this.handleRefreshCache(job);
          break;
        case 'invalidate-cache':
          await this.handleInvalidateCache(job);
          break;
        case 'health-check':
          await this.handleHealthCheck(job);
          break;
        default:
          throw new Error(`Unknown job type: ${definition.type}`);
      }

      job.status = 'completed';
      job.progress = 100;
    } catch (error) {
      job.status = 'failed';
      job.error = error instanceof Error ? error.message : String(error);
      logProvider('jobs', 'error', `Job failed`, {
        id: job.id,
        type: definition.type,
        error: job.error,
      });
    }

    job.completedAt = new Date().toISOString();
  }

  private async handleRefreshProvider(job: Job, definition: JobDefinition): Promise<void> {
    const providerName = definition.providerName;
    if (!providerName) {
      throw new Error('refresh-provider job requires providerName');
    }

    logProvider('jobs', 'info', `Refreshing provider: ${providerName}`);
    job.progress = 10;

    const providers = this.registry.getAll();
    const provider = providers.find(p => p.name === providerName);
    if (!provider) {
      throw new Error(`Provider not found: ${providerName}`);
    }

    if (typeof provider.refresh !== 'function') {
      throw new Error(`Provider ${providerName} does not support refresh`);
    }

    job.progress = 30;
    await provider.refresh();
    job.progress = 100;

    job.result = { provider: providerName, refreshed: true };
    logProvider('jobs', 'info', `Provider refreshed: ${providerName}`);
  }

  private async handleRefreshCache(job: Job): Promise<void> {
    logProvider('jobs', 'info', 'Refreshing all provider caches');
    job.progress = 10;

    const cache = getCacheManager();
    cache.clear();
    job.progress = 50;

    // Re-initialize providers to warm caches
    await this.registry.initializeAll();
    job.progress = 100;

    job.result = { cacheCleared: true };
  }

  private async handleInvalidateCache(job: Job): Promise<void> {
    logProvider('jobs', 'info', 'Invalidating stale cache entries');

    const cache = getCacheManager();
    const stats = cache.getStats();

    // Log current stats before clearing
    job.result = {
      statsBefore: stats,
      cleared: true,
    };

    cache.clear();
    job.progress = 100;
  }

  private async handleHealthCheck(job: Job): Promise<void> {
    job.progress = 20;
    const healthResults = await this.registry.healthAll();
    job.progress = 80;

    job.result = {
      providers: healthResults,
      healthyCount: healthResults.filter(h => h.status === 'healthy').length,
      unhealthyCount: healthResults.filter(h => h.status !== 'healthy').length,
    };
  }

  private async runPeriodicRefresh(): Promise<void> {
    try {
      // Check provider health
      const healthResults = await this.registry.healthAll();
      const unhealthy = healthResults.filter(h => h.status !== 'healthy');

      if (unhealthy.length > 0) {
        logProvider('jobs', 'warn', 'Unhealthy providers detected during periodic check', {
          providers: unhealthy.map(h => `${h.name}: ${h.message}`),
        });

        // Auto-refresh unhealthy providers
        for (const provider of unhealthy) {
          this.submit({
            type: 'refresh-provider',
            providerName: provider.name,
          });
        }
      }

      // Periodic cache cleanup (remove truly expired entries)
      const cache = getCacheManager();
      const stats = cache.getStats();

      if (stats.expired > stats.total * 0.5) {
        // More than 50% expired — trigger refresh
        logProvider('jobs', 'info', 'High cache expiration detected, triggering refresh', {
          expired: stats.expired,
          total: stats.total,
        });
      }
    } catch (error) {
      logProvider('jobs', 'error', 'Periodic refresh failed', {
        error: error instanceof Error ? error.message : String(error),
      });
    }
  }
}

// ── Singleton ──

let instance: JobManager | null = null;

export function getJobManager(registry?: ProviderRegistry): JobManager {
  if (!instance) {
    instance = new JobManager(registry);
  }
  return instance;
}

// ── Convenience Functions ──

/**
 * Submit a provider refresh job.
 */
export function refreshProvider(providerName: string): string {
  return getJobManager().submit({
    type: 'refresh-provider',
    providerName,
  });
}

/**
 * Submit a full cache refresh job.
 */
export function refreshCache(): string {
  return getJobManager().submit({ type: 'refresh-cache' });
}

/**
 * Submit a cache invalidation job.
 */
export function invalidateCache(): string {
  return getJobManager().submit({ type: 'invalidate-cache' });
}

/**
 * Submit a health check job.
 */
export function runHealthCheck(): string {
  return getJobManager().submit({ type: 'health-check' });
}
