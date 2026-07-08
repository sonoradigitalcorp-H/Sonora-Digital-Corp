// ───────────────────────────────────────────────
// SIGNAL Score Engine — Abstract Base Score
// Every score module extends this class.
// Strategy Pattern + Template Method.
// ───────────────────────────────────────────────

import type {
  ArtistFeatures,
  ScoreResult,
  ScoreReasoning,
  ScoreInputSpec,
  ScoreHistory,
  ValidationResult,
  WeightConfig,
  WeightOverrides,
  ScoreIdentity,
  ContributingFactor,
} from './types';
import { resolveWeights, getEffectiveWeight } from './weights';
import { calculateConfidence, buildConfidenceInput, computeFactorAgreement } from './confidence';
import { buildReasoning } from './reasoning';
import { getHistoryManager } from './score-history';

export abstract class BaseScore {
  public abstract readonly identity: ScoreIdentity;
  public abstract readonly spec: ScoreInputSpec;

  protected initialized = false;

  /**
   * Initialize the score module.
   * Called once during registration.
   */
  async initialize(): Promise<void> {
    this.initialized = true;
  }

  /**
   * Calculate the score from normalized features.
   * This is the main entry point for all score modules.
   */
  async calculate(
    features: ArtistFeatures,
    weights?: WeightOverrides
  ): Promise<ScoreResult> {
    if (!this.initialized) {
      throw new Error(`Score ${this.identity.id} not initialized. Call initialize() first.`);
    }

    const validation = this.validate(features);
    if (!validation.valid && validation.missingRequired.length > 0) {
      throw new Error(
        `Score ${this.identity.id}: missing required features: ${validation.missingRequired.join(', ')}`
      );
    }

    const resolvedWeights = resolveWeights(this.spec, {
      providers: features.platforms,
      markets: features.markets,
      genres: features.genres,
    });

    // Merge global overrides
    if (weights?.global) {
      resolvedWeights.global = { ...resolvedWeights.global, ...weights.global };
    }

    // Template method — subclasses implement this
    const factors = this.computeFactors(features, resolvedWeights);

    // Calculate raw score from factors
    const score = this.aggregateScore(factors, resolvedWeights);

    // Calculate confidence
    const confidenceInput = buildConfidenceInput(features, this.spec, factors);
    const confidence = calculateConfidence(confidenceInput);

    // Generate recommendations
    const recommendations = this.generateRecommendations(score, factors, features);

    const result: ScoreResult = {
      score,
      confidence,
      timestamp: new Date().toISOString(),
      factors,
      recommendations,
      metadata: {
        scoreId: this.identity.id,
        version: this.identity.version,
        featuresUsed: this.spec.required.filter((f) => {
          const val = (features as unknown as Record<string, unknown>)[f];
          return val !== undefined && val !== null && val !== 0 && val !== '';
        }).length,
        featuresTotal: this.spec.required.length,
      },
    };

    // Record history
    const historyManager = getHistoryManager();
    await historyManager.record(this.identity.id, features.name, result);

    return result;
  }

  /**
   * Validate that features meet minimum requirements for this score.
   */
  validate(features: ArtistFeatures): ValidationResult {
    const missingRequired: string[] = [];
    const missingOptional: string[] = [];

    for (const req of this.spec.required) {
      const val = (features as unknown as Record<string, unknown>)[req];
      if (val === undefined || val === null) {
        missingRequired.push(req);
      }
    }

    for (const opt of this.spec.optional) {
      const val = (features as unknown as Record<string, unknown>)[opt];
      if (val === undefined || val === null) {
        missingOptional.push(opt);
      }
    }

    const featuresAvailable = this.spec.required.length - missingRequired.length;
    const featureRatio = featuresAvailable / Math.max(1, this.spec.required.length);
    const confidenceWarning = featureRatio < (this.spec.minimumConfidence / 100);

    const valid = missingRequired.length === 0;

    let message: string;
    if (valid) {
      message = `All required features present for ${this.identity.name}`;
    } else {
      message = `Missing ${missingRequired.length} required feature(s): ${missingRequired.join(', ')}`;
    }

    return {
      valid,
      missingRequired,
      missingOptional,
      confidenceWarning,
      message,
    };
  }

  /**
   * Get reasoning for a result.
   */
  reasoning(result: ScoreResult, features: ArtistFeatures): ScoreReasoning {
    return buildReasoning(this.identity.name, result, features);
  }

  /**
   * Get score history for an artist.
   */
  async history(artistId: string): Promise<ScoreHistory> {
    const historyManager = getHistoryManager();
    return historyManager.getHistory(this.identity.id, artistId);
  }

  /**
   * Get effective weights for this score.
   */
  weights(options?: {
    providers?: string[];
    markets?: string[];
    genres?: string[];
  }): WeightConfig {
    return resolveWeights(this.spec, options);
  }

  // ── Abstract Methods (implemented by each score) ──

  /**
   * Compute all contributing factors from features.
   * Each factor becomes a row in the explainability output.
   */
  protected abstract computeFactors(
    features: ArtistFeatures,
    weights: WeightConfig
  ): ContributingFactor[];

  /**
   * Aggregate individual factors into a final 0-100 score.
   */
  protected abstract aggregateScore(
    factors: ContributingFactor[],
    weights: WeightConfig
  ): number;

  /**
   * Generate actionable recommendations based on the score.
   */
  protected abstract generateRecommendations(
    score: number,
    factors: ContributingFactor[],
    features: ArtistFeatures
  ): string[];
}

// ── Utility for score normalization ──

/**
 * Clamp a value between min and max.
 */
export function clamp(value: number, min: number, max: number): number {
  return Math.max(min, Math.min(max, value));
}

/**
 * Normalize a value to a 0-1 range using min-max scaling.
 */
export function normalizeToRange(
  value: number,
  min: number,
  max: number
): number {
  if (max <= min) return 0.5;
  return clamp((value - min) / (max - min), 0, 1);
}

/**
 * Apply a weight to a raw value and return the weighted impact.
 */
export function weightedImpact(
  rawValue: number,
  weight: number,
  direction: 'positive' | 'negative' = 'positive'
): { value: number; impact: number; weight: number } {
  const value = clamp(rawValue, 0, 100);
  const impact = clamp(value * weight, -100, 100);
  return {
    value,
    impact: direction === 'negative' ? -impact : impact,
    weight,
  };
}

/**
 * Calculate weighted average of factor impacts.
 */
export function weightedAverage(
  factors: ContributingFactor[]
): number {
  if (factors.length === 0) return 50;
  const totalWeight = factors.reduce((a, f) => a + f.weight, 0);
  if (totalWeight === 0) return 50;
  const weightedSum = factors.reduce((a, f) => a + f.impact * f.weight, 0);
  return clamp(50 + weightedSum / totalWeight, 0, 100);
}

/**
 * Sigmoid function to map any real number to a 0-1 range.
 * Useful for non-linear score transformations.
 */
export function sigmoid(x: number, midpoint = 0, steepness = 1): number {
  return 1 / (1 + Math.exp(-steepness * (x - midpoint)));
}
