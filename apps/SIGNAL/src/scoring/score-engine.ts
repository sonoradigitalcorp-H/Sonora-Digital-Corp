// ───────────────────────────────────────────────
// SIGNAL Score Engine — Orchestrator
// Runs all scores against an artist and aggregates results
// ───────────────────────────────────────────────

import type {
  ArtistFeatures,
  ScoreResult,
  ScoreReasoning,
  ScoreHistory as ScoreHistoryType,
  WeightOverrides,
  ValidationResult,
} from './types';
import { extractFeatures, normalizeFeatures } from './feature-extractor';
import { getRegistry } from './score-registry';
import type { UnifiedArtist } from '@/providers/types';

// ── Public Types ──

export interface ScoreOutput {
  /** Score identity */
  id: string;
  name: string;
  version: string;
  category: string;
  /** Core result */
  score: number;
  confidence: number;
  /** Explainability */
  summary: string;
  factors: Array<{
    name: string;
    impact: number;
    direction: string;
    reasoning: string;
  }>;
  recommendations: string[];
  dataQuality: string;
  /** History */
  trend: string;
  volatility: number;
  history: {
    daily: number;
    weekly: number;
    monthly: number;
  };
  /** Validation */
  valid: boolean;
  validationMessage: string;
}

export interface EngineResult {
  /** Artist name */
  artist: string;
  /** Timestamp */
  timestamp: string;
  /** All scores computed */
  scores: ScoreOutput[];
  /** Aggregate intelligence score (average of all scores) */
  aggregateScore: number;
  /** Aggregate confidence */
  aggregateConfidence: number;
  /** Number of scores that ran successfully */
  scoresComputed: number;
  /** Number of scores that failed validation */
  scoresSkipped: number;
  /** Feature summary */
  features: {
    platforms: string[];
    followers: number;
    monthlyListeners: number;
    engagementRate: number;
    albumCount: number;
    crossPlatformPresence: number;
  };
}

// ── Score Engine ──

class ScoreEngine {
  private static instance: ScoreEngine | null = null;

  static getInstance(): ScoreEngine {
    if (!ScoreEngine.instance) {
      ScoreEngine.instance = new ScoreEngine();
    }
    return ScoreEngine.instance;
  }

  static resetInstance(): void {
    ScoreEngine.instance = null;
  }

  /**
   * Run all enabled scores against a UnifiedArtist.
   * This is the main entry point for scoring.
   */
  async evaluate(
    artist: UnifiedArtist,
    weights?: WeightOverrides
  ): Promise<EngineResult> {
    const registry = getRegistry();
    const scores = registry.getEnabled();
    const features = normalizeFeatures(extractFeatures(artist));

    const outputs: ScoreOutput[] = [];
    let computed = 0;
    let skipped = 0;

    for (const score of scores) {
      const validation = score.validate(features);

      if (!validation.valid) {
        skipped++;
        outputs.push(this.buildSkippedOutput(score, validation));
        continue;
      }

      try {
        const result = await score.calculate(features, weights);
        const reasoning = score.reasoning(result, features);
        const history = await score.history(artist.name);

        outputs.push(this.buildOutput(score, result, reasoning, history, validation));
        computed++;
      } catch (error) {
        skipped++;
        outputs.push(this.buildErrorOutput(
          score,
          validation,
          error instanceof Error ? error.message : 'Unknown error'
        ));
      }
    }

    const validScores = outputs.filter((o) => o.valid);

    return {
      artist: artist.name,
      timestamp: new Date().toISOString(),
      scores: outputs,
      aggregateScore: this.calculateAggregate(validScores),
      aggregateConfidence: this.calculateAggregateConfidence(validScores),
      scoresComputed: computed,
      scoresSkipped: skipped,
      features: {
        platforms: features.platforms,
        followers: features.followers,
        monthlyListeners: features.monthlyListeners,
        engagementRate: features.engagementRate,
        albumCount: features.albumCount,
        crossPlatformPresence: features.crossPlatformPresence,
      },
    };
  }

  /**
   * Run a single score against an artist.
   */
  async evaluateScore(
    artist: UnifiedArtist,
    scoreId: string,
    weights?: WeightOverrides
  ): Promise<ScoreOutput | null> {
    const registry = getRegistry();
    const score = registry.get(scoreId);
    if (!score) return null;

    const features = normalizeFeatures(extractFeatures(artist));
    const validation = score.validate(features);

    if (!validation.valid) {
      return this.buildSkippedOutput(score, validation);
    }

    const result = await score.calculate(features, weights);
    const reasoning = score.reasoning(result, features);
    const history = await score.history(artist.name);

    return this.buildOutput(score, result, reasoning, history, validation);
  }

  // ── Private ──

  private buildOutput(
    score: { identity: { id: string; name: string; version: string; category: string } },
    result: ScoreResult,
    reasoning: ScoreReasoning,
    history: ScoreHistoryType,
    validation: ValidationResult
  ): ScoreOutput {
    return {
      id: score.identity.id,
      name: score.identity.name,
      version: score.identity.version,
      category: score.identity.category,
      score: result.score,
      confidence: result.confidence,
      summary: reasoning.summary,
      factors: result.factors.map((f) => ({
        name: f.name,
        impact: f.impact,
        direction: f.direction,
        reasoning: f.reasoning,
      })),
      recommendations: result.recommendations,
      dataQuality: reasoning.dataQuality,
      trend: history.trend,
      volatility: history.volatility,
      history: {
        daily: history.daily.length,
        weekly: history.weekly.length,
        monthly: history.monthly.length,
      },
      valid: true,
      validationMessage: validation.message,
    };
  }

  private buildSkippedOutput(
    score: { identity: { id: string; name: string; version: string; category: string } },
    validation: ValidationResult
  ): ScoreOutput {
    return {
      id: score.identity.id,
      name: score.identity.name,
      version: score.identity.version,
      category: score.identity.category,
      score: 0,
      confidence: 0,
      summary: `Cannot compute ${score.identity.name}: ${validation.message}`,
      factors: [],
      recommendations: [`Provide data for: ${validation.missingRequired.join(', ')}`],
      dataQuality: 'Insufficient data',
      trend: 'stable',
      volatility: 0,
      history: { daily: 0, weekly: 0, monthly: 0 },
      valid: false,
      validationMessage: validation.message,
    };
  }

  private buildErrorOutput(
    score: { identity: { id: string; name: string; version: string; category: string } },
    validation: ValidationResult,
    error: string
  ): ScoreOutput {
    return {
      id: score.identity.id,
      name: score.identity.name,
      version: score.identity.version,
      category: score.identity.category,
      score: 0,
      confidence: 0,
      summary: `Error computing ${score.identity.name}: ${error}`,
      factors: [],
      recommendations: ['Check provider data availability'],
      dataQuality: 'Error',
      trend: 'stable',
      volatility: 0,
      history: { daily: 0, weekly: 0, monthly: 0 },
      valid: false,
      validationMessage: `Error: ${error}`,
    };
  }

  private calculateAggregate(scores: ScoreOutput[]): number {
    if (scores.length === 0) return 0;
    const sum = scores.reduce((a, s) => a + s.score, 0);
    return Math.round(sum / scores.length);
  }

  private calculateAggregateConfidence(scores: ScoreOutput[]): number {
    if (scores.length === 0) return 0;
    const sum = scores.reduce((a, s) => a + s.confidence, 0);
    return Math.round(sum / scores.length);
  }
}

export function getEngine(): ScoreEngine {
  return ScoreEngine.getInstance();
}

export function resetEngine(): void {
  ScoreEngine.resetInstance();
}
