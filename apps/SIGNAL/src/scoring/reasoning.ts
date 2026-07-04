// ───────────────────────────────────────────────
// SIGNAL Score Engine — Explainability Engine
// Every score must explain itself in human terms.
// Never show only numbers.
// ───────────────────────────────────────────────

import type {
  ArtistFeatures,
  ScoreResult,
  ScoreReasoning,
  ContributingFactor,
  ScoreHistory,
  ScoreHistoryEntry,
  TrendDirection,
} from './types';

/**
 * Build full reasoning for a score result.
 * This is the explainability layer — every number gets a human-readable story.
 */
export function buildReasoning(
  scoreName: string,
  result: ScoreResult,
  features: ArtistFeatures
): ScoreReasoning {
  const topPositive = result.factors
    .filter((f) => f.direction === 'positive')
    .sort((a, b) => Math.abs(b.impact) - Math.abs(a.impact))
    .slice(0, 5);

  const topNegative = result.factors
    .filter((f) => f.direction === 'negative')
    .sort((a, b) => Math.abs(b.impact) - Math.abs(a.impact))
    .slice(0, 5);

  const summary = buildSummary(scoreName, result, topPositive, topNegative);
  const dataQuality = assessDataQuality(features);

  return {
    summary,
    factors: result.factors,
    recommendations: result.recommendations,
    dataQuality,
  };
}

function buildSummary(
  scoreName: string,
  result: ScoreResult,
  topPositive: ContributingFactor[],
  topNegative: ContributingFactor[]
): string {
  const score = result.score;
  const confidence = result.confidence;

  let level: string;
  if (score >= 80) level = 'Exceptional';
  else if (score >= 65) level = 'Strong';
  else if (score >= 50) level = 'Moderate';
  else if (score >= 35) level = 'Developing';
  else level = 'Emerging';

  let confidenceNote: string;
  if (confidence >= 80) confidenceNote = 'high confidence';
  else if (confidence >= 50) confidenceNote = 'moderate confidence';
  else confidenceNote = 'low confidence — more data needed';

  const positiveFactors = topPositive.map((f) => `+${Math.round(Math.abs(f.impact))} ${f.name}`).join(', ');
  const negativeFactors = topNegative.map((f) => `-${Math.round(Math.abs(f.impact))} ${f.name}`).join(', ');

  const positiveSection = positiveFactors ? ` Driven by ${positiveFactors}.` : '';
  const negativeSection = negativeFactors ? ` Offset by ${negativeFactors}.` : '';

  return `${scoreName}: ${score}/100 — ${level} (${confidenceNote}).${positiveSection}${negativeSection}`;
}

function assessDataQuality(features: ArtistFeatures): string {
  const platformCount = features.platforms.length;
  const hasFollowers = features.followers > 0;
  const hasEngagement = features.engagementRate > 0;
  const hasGrowth = features.followerGrowth !== 0;
  const hasAlbums = features.albumCount > 0;

  const dataPoints = [hasFollowers, hasEngagement, hasGrowth, hasAlbums, platformCount >= 2];
  const presentCount = dataPoints.filter(Boolean).length;
  const totalCount = dataPoints.length;

  if (presentCount === totalCount) return 'Excellent — full data across multiple platforms';
  if (presentCount >= totalCount - 1) return 'Good — most data dimensions available';
  if (presentCount >= totalCount / 2) return 'Adequate — core metrics present, some gaps';
  return 'Limited — few data points available, score may be unreliable';
}

/**
 * Format contributing factors for display.
 */
export function formatFactors(factors: ContributingFactor[]): string[] {
  return factors
    .sort((a, b) => Math.abs(b.impact) - Math.abs(a.impact))
    .map((f) => {
      const sign = f.direction === 'positive' ? '+' : '-';
      return `${sign}${Math.round(Math.abs(f.impact))} ${f.name} (weight: ${Math.round(f.weight * 100)}%)`;
    });
}

/**
 * Determine trend direction from history.
 */
export function determineTrend(history: ScoreHistoryEntry[]): TrendDirection {
  if (history.length < 2) return 'stable';

  const recent = history.slice(-5);
  if (recent.length < 2) return 'stable';

  const changes = recent.map((e) => e.change);
  const avgChange = changes.reduce((a, b) => a + b, 0) / changes.length;

  if (avgChange > 3) return 'up';
  if (avgChange < -3) return 'down';
  return 'stable';
}

/**
 * Calculate volatility from history.
 * 0 = perfectly stable, 100 = wildly fluctuating
 */
export function calculateVolatility(history: ScoreHistoryEntry[]): number {
  if (history.length < 3) return 0;

  const scores = history.map((e) => e.score);
  const mean = scores.reduce((a, b) => a + b, 0) / scores.length;
  const variance = scores.reduce((a, b) => a + (b - mean) ** 2, 0) / scores.length;
  const stdDev = Math.sqrt(variance);

  // Normalize to 0-100 (max reasonable std dev is ~30 for 0-100 scale)
  return Math.min(100, Math.round((stdDev / 30) * 100));
}

/**
 * Format a full score result for display/API.
 */
export function formatScoreForDisplay(
  scoreName: string,
  result: ScoreResult,
  features: ArtistFeatures,
  history?: ScoreHistory
): Record<string, unknown> {
  return {
    score: result.score,
    confidence: result.confidence,
    trend: history?.trend ?? 'stable',
    volatility: history?.volatility ?? 0,
    summary: buildReasoning(scoreName, result, features).summary,
    contributingFactors: formatFactors(result.factors),
    recommendations: result.recommendations,
    dataQuality: assessDataQuality(features),
    history: history
      ? {
          daily: history.daily.slice(-7),
          weekly: history.weekly.slice(-4),
          monthly: history.monthly.slice(-3),
        }
      : null,
  };
}
