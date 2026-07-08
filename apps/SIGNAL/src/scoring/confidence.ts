// ───────────────────────────────────────────────
// SIGNAL Score Engine — Confidence Calculation
// Every score must justify its confidence level
// ───────────────────────────────────────────────

import type { ArtistFeatures, ScoreInputSpec, ContributingFactor } from './types';

export interface ConfidenceInput {
  /** Features available vs required */
  featuresAvailable: number;
  featuresRequired: number;
  featuresOptional: number;
  featuresOptionalPresent: number;
  /** Data freshness (0-1, 1 = fresh) */
  dataFreshness: number;
  /** Number of platforms contributing data */
  platformCount: number;
  /** Total providers that contributed */
  providerCount: number;
  /** Factor agreement (0-1, 1 = all factors agree) */
  factorAgreement: number;
}

/**
 * Calculate confidence level for a score result.
 *
 * Factors:
 * - Feature coverage (required + optional features present)
 * - Data freshness (recency of source data)
 * - Platform diversity (more platforms = higher confidence)
 * - Factor agreement (do multiple signals point same direction?)
 */
export function calculateConfidence(input: ConfidenceInput): number {
  if (input.featuresRequired === 0) return 0;

  // Weight 1: Feature coverage (40% of confidence)
  const requiredRatio = Math.min(1, input.featuresAvailable / input.featuresRequired);
  const optionalRatio = input.featuresOptional > 0
    ? Math.min(1, input.featuresOptionalPresent / input.featuresOptional)
    : 1;
  const featureScore = requiredRatio * 0.7 + optionalRatio * 0.3;

  // Weight 2: Data freshness (25% of confidence)
  const freshnessScore = input.dataFreshness;

  // Weight 3: Platform/provider diversity (20% of confidence)
  const platformScore = Math.min(1, input.platformCount / 3);

  // Weight 4: Factor agreement (15% of confidence)
  const agreementScore = input.factorAgreement;

  // Composite
  const confidence =
    featureScore * 0.40 +
    freshnessScore * 0.25 +
    platformScore * 0.20 +
    agreementScore * 0.15;

  // Clamp to 0-100
  return Math.max(0, Math.min(100, Math.round(confidence * 100)));
}

/**
 * Compute factor agreement.
 * Measures how much the contributing factors point in the same direction.
 * 1.0 = perfect agreement, 0.0 = completely contradictory
 */
export function computeFactorAgreement(factors: ContributingFactor[]): number {
  if (factors.length === 0) return 0.5;

  const positiveCount = factors.filter((f) => f.direction === 'positive').length;
  const negativeCount = factors.filter((f) => f.direction === 'negative').length;
  const total = factors.length;

  // Agreement = how one-sided the factors are
  const ratio = Math.max(positiveCount, negativeCount) / total;

  // Penalize if there are very few factors
  const sizeBonus = Math.min(1, total / 5);

  return ratio * 0.7 + sizeBonus * 0.3;
}

/**
 * Estimate data freshness from feature timestamps.
 * Currently returns 1.0 since normalized data doesn't carry timestamps.
 * Future: use actual staleness from cache layer.
 */
export function estimateDataFreshness(features: ArtistFeatures): number {
  // Placeholder — returns 0.9 for any data
  // Future: check last-updated timestamps from cache/providers
  if (!features || Object.keys(features).length === 0) return 0;
  return 0.9;
}

/**
 * Build confidence input from features, spec, and factors.
 */
export function buildConfidenceInput(
  features: ArtistFeatures,
  spec: ScoreInputSpec,
  factors: ContributingFactor[]
): ConfidenceInput {
  const featuresAvailable = spec.required.filter((f) => {
    const val = (features as unknown as Record<string, unknown>)[f];
    return val !== undefined && val !== null && val !== 0 && val !== '';
  }).length;

  const featuresOptionalPresent = spec.optional.filter((f) => {
    const val = (features as unknown as Record<string, unknown>)[f];
    return val !== undefined && val !== null && val !== 0 && val !== '';
  }).length;

  return {
    featuresAvailable,
    featuresRequired: spec.required.length,
    featuresOptional: spec.optional.length,
    featuresOptionalPresent,
    dataFreshness: estimateDataFreshness(features),
    platformCount: features.platforms.length,
    providerCount: features.platforms.length,
    factorAgreement: computeFactorAgreement(factors),
  };
}
