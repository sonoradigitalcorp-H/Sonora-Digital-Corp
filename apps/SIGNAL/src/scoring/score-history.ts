// ───────────────────────────────────────────────
// SIGNAL Score Engine — Score History
// Tracks daily, weekly, and monthly score snapshots
// ───────────────────────────────────────────────

import type {
  ScoreResult,
  ScoreHistory as ScoreHistoryType,
  ScoreHistoryEntry,
  TrendDirection,
  ContributingFactor,
} from './types';
import { determineTrend, calculateVolatility } from './reasoning';

// ── In-memory history store ──
// Key: `${scoreId}:${artistName}`
// Future: persist to database or KV store

interface HistoryRecord {
  entries: ScoreHistoryEntry[];
  createdAt: string;
}

class ScoreHistoryManager {
  private store = new Map<string, HistoryRecord>();
  private static instance: ScoreHistoryManager | null = null;

  static getInstance(): ScoreHistoryManager {
    if (!ScoreHistoryManager.instance) {
      ScoreHistoryManager.instance = new ScoreHistoryManager();
    }
    return ScoreHistoryManager.instance;
  }

  /**
   * Record a new score result in history.
   */
  async record(
    scoreId: string,
    artistName: string,
    result: ScoreResult
  ): Promise<void> {
    const key = `${scoreId}:${artistName}`;
    const existing = this.store.get(key);
    const entries = existing?.entries ?? [];

    const lastEntry = entries.length > 0 ? entries[entries.length - 1] : null;
    const change = lastEntry ? result.score - lastEntry.score : 0;

    let trend: TrendDirection = 'stable';
    if (change > 3) trend = 'up';
    else if (change < -3) trend = 'down';

    const entry: ScoreHistoryEntry = {
      score: result.score,
      confidence: result.confidence,
      timestamp: result.timestamp,
      trend,
      change,
      reason: this.inferReason(change, result.factors),
      factors: result.factors,
    };

    entries.push(entry);

    // Keep max 90 daily entries, 52 weekly, 36 monthly
    // For simplicity, we keep last 90 entries and aggregate
    if (entries.length > 90) {
      entries.splice(0, entries.length - 90);
    }

    this.store.set(key, {
      entries,
      createdAt: existing?.createdAt ?? result.timestamp,
    });
  }

  /**
   * Get aggregated history for a score + artist.
   */
  async getHistory(
    scoreId: string,
    artistName: string
  ): Promise<ScoreHistoryType> {
    const key = `${scoreId}:${artistName}`;
    const record = this.store.get(key);
    const entries = record?.entries ?? [];

    if (entries.length === 0) {
      return {
        daily: [],
        weekly: [],
        monthly: [],
        trend: 'stable',
        volatility: 0,
      };
    }

    // Daily: entries from last 30 days
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
    const daily = entries.filter((e) => new Date(e.timestamp) >= thirtyDaysAgo);

    // Weekly: aggregate last 12 weeks (take latest entry per week)
    const weekly = this.aggregateByPeriod(entries, 7, 12);

    // Monthly: aggregate last 12 months (take latest entry per 30 days)
    const monthly = this.aggregateByPeriod(entries, 30, 12);

    return {
      daily,
      weekly,
      monthly,
      trend: determineTrend(entries),
      volatility: calculateVolatility(entries),
    };
  }

  /**
   * Aggregate entries by period (days).
   */
  private aggregateByPeriod(
    entries: ScoreHistoryEntry[],
    periodDays: number,
    maxPeriods: number
  ): ScoreHistoryEntry[] {
    if (entries.length === 0) return [];

    const now = new Date();
    const periods: ScoreHistoryEntry[] = [];

    for (let i = 0; i < maxPeriods; i++) {
      const periodEnd = new Date(now.getTime() - i * periodDays * 86400000);
      const periodStart = new Date(periodEnd.getTime() - periodDays * 86400000);

      const periodEntries = entries.filter((e) => {
        const date = new Date(e.timestamp);
        return date >= periodStart && date < periodEnd;
      });

      if (periodEntries.length > 0) {
        // Take the latest entry in the period
        periods.push(periodEntries[periodEntries.length - 1]);
      }
    }

    return periods;
  }

  /**
   * Infer a human-readable reason for the change.
   */
  private inferReason(change: number, factors: ContributingFactor[]): string {
    if (Math.abs(change) < 1) return 'Stable — no significant change';

    const topFactor = factors
      .sort((a, b) => Math.abs(b.impact) - Math.abs(a.impact))
      [0];

    if (!topFactor) return `Changed by ${change.toFixed(1)} points`;

    const direction = change > 0 ? 'Increased' : 'Decreased';
    return `${direction} by ${Math.abs(change).toFixed(1)} — driven by ${topFactor.name}`;
  }

  /**
   * Clear all history (for testing).
   */
  clear(): void {
    this.store.clear();
  }

  /** Reset the internal singleton (for testing) */
  static resetInstance(): void {
    ScoreHistoryManager.instance = null;
  }

  /**
   * Get storage stats.
   */
  stats(): { entries: number; keys: number } {
    let entries = 0;
    for (const record of this.store.values()) {
      entries += record.entries.length;
    }
    return { entries, keys: this.store.size };
  }
}

export function getHistoryManager(): ScoreHistoryManager {
  return ScoreHistoryManager.getInstance();
}

export function resetHistoryManager(): void {
  const hm = ScoreHistoryManager.getInstance();
  hm.clear();
  ScoreHistoryManager.resetInstance();
}
