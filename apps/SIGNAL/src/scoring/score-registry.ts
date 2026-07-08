// ───────────────────────────────────────────────
// SIGNAL Score Engine — Score Registry
// Register, enable/disable, and version scores
// ───────────────────────────────────────────────

import type { ScoreIdentity, ScoreRegistration, ScoreRegistryState } from './types';
import type { BaseScore } from './base-score';

class ScoreRegistry {
  private scores = new Map<string, BaseScore>();
  private registrations = new Map<string, ScoreRegistration>();
  private version = '1.0.0';
  private static instance: ScoreRegistry | null = null;

  static getInstance(): ScoreRegistry {
    if (!ScoreRegistry.instance) {
      ScoreRegistry.instance = new ScoreRegistry();
    }
    return ScoreRegistry.instance;
  }

  /**
   * Register a new score module.
   * Scores are enabled by default.
   */
  async register(score: BaseScore): Promise<void> {
    const id = score.identity.id;

    // Check if we need to replace an existing registration
    if (this.scores.has(id)) {
      const existing = this.registrations.get(id);
      if (existing && existing.identity.version >= score.identity.version) {
        // Allow re-registration — replaces the existing score silently
        this.scores.delete(id);
        this.registrations.delete(id);
      }
    }

    // Initialize the score
    await score.initialize();

    // Register in both maps
    this.scores.set(id, score);
    this.registrations.set(id, {
      identity: score.identity,
      enabled: true,
      createdAt: this.registrations.get(id)?.createdAt ?? new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    });
  }

  /**
   * Unregister a score.
   */
  unregister(scoreId: string): void {
    this.scores.delete(scoreId);
    this.registrations.delete(scoreId);
  }

  /**
   * Get a registered score by ID.
   */
  get(scoreId: string): BaseScore | undefined {
    return this.scores.get(scoreId);
  }

  /**
   * Get all registered scores.
   */
  getAll(): BaseScore[] {
    return Array.from(this.scores.values());
  }

  /**
   * Get all enabled scores.
   */
  getEnabled(): BaseScore[] {
    return this.getAll().filter((s) => {
      const reg = this.registrations.get(s.identity.id);
      return reg?.enabled ?? true;
    });
  }

  /**
   * Enable a score.
   */
  enable(scoreId: string): void {
    const reg = this.registrations.get(scoreId);
    if (reg) {
      reg.enabled = true;
      reg.updatedAt = new Date().toISOString();
    }
  }

  /**
   * Disable a score.
   */
  disable(scoreId: string): void {
    const reg = this.registrations.get(scoreId);
    if (reg) {
      reg.enabled = false;
      reg.updatedAt = new Date().toISOString();
    }
  }

  /**
   * Check if a score is enabled.
   */
  isEnabled(scoreId: string): boolean {
    return this.registrations.get(scoreId)?.enabled ?? false;
  }

  /**
   * Get registration details for a score.
   */
  getRegistration(scoreId: string): ScoreRegistration | undefined {
    return this.registrations.get(scoreId);
  }

  /**
   * Get all registrations.
   */
  getAllRegistrations(): ScoreRegistration[] {
    return Array.from(this.registrations.values());
  }

  /**
   * Get registry state (for dashboard display).
   */
  getState(): ScoreRegistryState {
    return {
      scores: this.registrations,
      version: this.version,
    };
  }

  /**
   * Get count of registered scores.
   */
  get size(): number {
    return this.scores.size;
  }

  /**
   * Reset registry (for testing).
   */
  reset(): void {
    this.scores.clear();
    this.registrations.clear();
  }

  /** Reset the internal singleton (for testing) */
  static resetInstance(): void {
    ScoreRegistry.instance = null;
  }
}

export function getRegistry(): ScoreRegistry {
  return ScoreRegistry.getInstance();
}

export function resetRegistry(): void {
  const reg = ScoreRegistry.getInstance();
  reg.reset();
  ScoreRegistry.resetInstance();
}

// Export the class for direct testing (tests create their own instances)
export { ScoreRegistry };
