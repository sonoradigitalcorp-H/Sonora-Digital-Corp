// ───────────────────────────────────────────────
// SIGNAL Insight Generation Layer
// Deterministic insights from features + scores
// No ML — pure rule-based intelligence
// ───────────────────────────────────────────────

import type { ArtistFeatures } from './types';
import type { ScoreOutput, EngineResult } from './score-engine';

export interface Insight {
  type: 'growth' | 'risk' | 'opportunity' | 'achievement' | 'warning';
  message: string;
  severity: 'high' | 'medium' | 'low';
  category: string;
  source: string; // Which feature or score generated this
}

// ── Main Generator ──

export function generateInsights(
  features: ArtistFeatures,
  engineResult: EngineResult
): Insight[] {
  const insights: Insight[] = [];

  // Growth signals
  insights.push(...detectGrowthSignals(features, engineResult));

  // Risk signals
  insights.push(...detectRiskSignals(features, engineResult));

  // Opportunity signals
  insights.push(...detectOpportunitySignals(features, engineResult));

  // Score-based achievements
  insights.push(...detectScoreAchievements(engineResult));

  // Sort by severity: high first, then medium, then low
  const severityOrder = { high: 0, medium: 1, low: 2 };
  insights.sort((a, b) => severityOrder[a.severity] - severityOrder[b.severity]);

  return insights;
}

// ── Growth Signals ──

function detectGrowthSignals(
  features: ArtistFeatures,
  result: EngineResult
): Insight[] {
  const signals: Insight[] = [];

  // Strong follower growth
  if (features.followerGrowth > 15) {
    signals.push({
      type: 'growth',
      message: `Strong follower growth at ${features.followerGrowth.toFixed(1)}% — audience is accelerating`,
      severity: features.followerGrowth > 30 ? 'high' : 'medium',
      category: 'audience growth',
      source: 'followerGrowth',
    });
  }

  // High engagement
  if (features.engagementRate > 8) {
    signals.push({
      type: 'growth',
      message: `Elite engagement rate at ${features.engagementRate.toFixed(1)}% — audience is highly active`,
      severity: 'high',
      category: 'engagement',
      source: 'engagementRate',
    });
  } else if (features.engagementRate > 5) {
    signals.push({
      type: 'growth',
      message: `Healthy engagement at ${features.engagementRate.toFixed(1)}% — above industry average`,
      severity: 'medium',
      category: 'engagement',
      source: 'engagementRate',
    });
  }

  // Cross-platform presence
  if (features.crossPlatformPresence >= 4) {
    signals.push({
      type: 'growth',
      message: `Strong cross-platform presence across ${features.crossPlatformPresence} major platforms`,
      severity: 'medium',
      category: 'platform diversification',
      source: 'crossPlatformPresence',
    });
  }

  // Multi-market reach
  if (features.markets.length > 1) {
    signals.push({
      type: 'growth',
      message: `Already reaching ${features.markets.length} geographic markets — international potential`,
      severity: 'medium',
      category: 'market reach',
      source: 'markets',
    });
  }

  // Consistent releases
  if (features.recentReleaseCount >= 3) {
    signals.push({
      type: 'growth',
      message: `${features.recentReleaseCount} releases in 12 months — consistent creative output driving momentum`,
      severity: 'medium',
      category: 'content velocity',
      source: 'recentReleaseCount',
    });
  }

  // Aggregate momentum
  const momentumScore = result.scores.find(s => s.id === 'artist-momentum');
  if (momentumScore && momentumScore.score >= 70) {
    signals.push({
      type: 'growth',
      message: `Artist Momentum at ${momentumScore.score}/100 — strong upward trajectory across all signals`,
      severity: 'high',
      category: 'momentum',
      source: 'artist-momentum',
    });
  }

  return signals;
}

// ── Risk Signals ──

function detectRiskSignals(
  features: ArtistFeatures,
  result: EngineResult
): Insight[] {
  const signals: Insight[] = [];

  // Negative growth
  if (features.followerGrowth < 0) {
    signals.push({
      type: 'risk',
      message: `Audience declining at ${Math.abs(features.followerGrowth).toFixed(1)}% — investigate content strategy`,
      severity: 'high',
      category: 'audience decline',
      source: 'followerGrowth',
    });
  }

  // Low engagement
  if (features.engagementRate < 2) {
    signals.push({
      type: 'risk',
      message: `Very low engagement at ${features.engagementRate.toFixed(1)}% — audience may be passive or purchased`,
      severity: 'high',
      category: 'engagement risk',
      source: 'engagementRate',
    });
  } else if (features.engagementRate < 4) {
    signals.push({
      type: 'warning',
      message: `Below-average engagement at ${features.engagementRate.toFixed(1)}% — needs improvement`,
      severity: 'medium',
      category: 'engagement risk',
      source: 'engagementRate',
    });
  }

  // Low cross-platform presence
  if (features.crossPlatformPresence < 2) {
    signals.push({
      type: 'risk',
      message: 'Limited to 1 platform — high dependency risk, diversify presence',
      severity: 'high',
      category: 'platform concentration',
      source: 'crossPlatformPresence',
    });
  }

  // No recent releases
  if (features.recentReleaseCount === 0 && features.albumCount > 0) {
    signals.push({
      type: 'warning',
      message: 'No releases in the last 12 months — fading audience attention',
      severity: 'medium',
      category: 'content stall',
      source: 'recentReleaseCount',
    });
  }

  // Low catalog depth for commercial scores
  const labelScore = result.scores.find(s => s.id === 'label-readiness');
  if (labelScore && labelScore.valid && features.albumCount < 3) {
    signals.push({
      type: 'warning',
      message: `Only ${features.albumCount} release(s) — limited catalog depth for label interest`,
      severity: 'medium',
      category: 'catalog depth',
      source: 'albumCount',
    });
  }

  // Score volatility
  for (const score of result.scores) {
    if (score.valid && score.volatility > 50) {
      signals.push({
        type: 'warning',
        message: `High volatility in ${score.name} (${score.volatility}%) — score fluctuates significantly`,
        severity: 'medium',
        category: 'volatility',
        source: score.id,
      });
      break; // One volatility warning is enough
    }
  }

  return signals;
}

// ── Opportunity Signals ──

function detectOpportunitySignals(
  features: ArtistFeatures,
  result: EngineResult
): Insight[] {
  const signals: Insight[] = [];

  // High growth + low engagement = untapped potential
  if (features.followerGrowth > 10 && features.engagementRate < 4) {
    signals.push({
      type: 'opportunity',
      message: 'Growing fast but not engaging — adding interactive content could amplify retention',
      severity: 'high',
      category: 'engagement optimization',
      source: 'followerGrowth',
    });
  }

  // High engagement + low platform count = expand
  if (features.engagementRate > 6 && features.crossPlatformPresence < 3) {
    const missing = 3 - features.crossPlatformPresence;
    signals.push({
      type: 'opportunity',
      message: `High engagement but only ${features.crossPlatformPresence} platform(s) — adding ${missing} more could multiply reach`,
      severity: 'high',
      category: 'platform expansion',
      source: 'crossPlatformPresence',
    });
  }

  // Moderate audience + good growth = approaching breakthrough
  if (features.followers >= 10000 && features.followers < 100000 && features.followerGrowth > 10) {
    signals.push({
      type: 'opportunity',
      message: `${features.followers.toLocaleString()} followers with strong growth — approaching breakthrough threshold`,
      severity: 'high',
      category: 'breakthrough potential',
      source: 'followers',
    });
  }

  // Brand partnership potential
  const brandScore = result.scores.find(s => s.id === 'brand-partnership');
  if (brandScore && brandScore.valid && brandScore.score >= 60 && !features.hasWebsite) {
    signals.push({
      type: 'opportunity',
      message: 'Brand-ready but missing professional website — adding one unlocks brand partnerships',
      severity: 'medium',
      category: 'monetization',
      source: 'brand-partnership',
    });
  }

  // Virality potential
  const viralScore = result.scores.find(s => s.id === 'virality-index');
  if (viralScore && viralScore.valid && viralScore.score >= 65) {
    signals.push({
      type: 'opportunity',
      message: `Virality Index at ${viralScore.score}/100 — content has strong amplification potential`,
      severity: 'medium',
      category: 'virality',
      source: 'virality-index',
    });
  }

  // Tour readiness opportunity
  const tourScore = result.scores.find(s => s.id === 'tour-readiness');
  if (tourScore && tourScore.valid && tourScore.score >= 60 && !features.hasTouringHistory) {
    signals.push({
      type: 'opportunity',
      message: 'Tour-ready audience without touring history — first tour could be highly successful',
      severity: 'medium',
      category: 'live events',
      source: 'tour-readiness',
    });
  }

  return signals;
}

// ── Score Achievements ──

function detectScoreAchievements(result: EngineResult): Insight[] {
  const signals: Insight[] = [];

  for (const score of result.scores) {
    if (!score.valid) continue;

    if (score.score >= 85) {
      signals.push({
        type: 'achievement',
        message: `Exceptional ${score.name}: ${score.score}/100 — top-tier performance`,
        severity: 'high',
        category: 'score achievement',
        source: score.id,
      });
    } else if (score.score >= 75) {
      signals.push({
        type: 'achievement',
        message: `Strong ${score.name}: ${score.score}/100 — well above average`,
        severity: 'medium',
        category: 'score achievement',
        source: score.id,
      });
    }
  }

  // Aggregate achievement
  if (result.aggregateScore >= 75 && result.scoresComputed >= 5) {
    signals.push({
      type: 'achievement',
      message: `Overall intelligence score ${result.aggregateScore}/100 across ${result.scoresComputed} dimensions — exceptional artist profile`,
      severity: 'high',
      category: 'overall intelligence',
      source: 'aggregate',
    });
  }

  return signals;
}

// ── Summary Generator ──

export function generateSummary(insights: Insight[]): string[] {
  const highSeverity = insights.filter(i => i.severity === 'high');
  const mediumSeverity = insights.filter(i => i.severity === 'medium');

  const summaries: string[] = [];

  if (highSeverity.length > 0) {
    summaries.push(highSeverity[0].message);
    if (highSeverity.length > 1) {
      summaries.push(highSeverity[1].message);
    }
  }

  if (mediumSeverity.length > 0 && summaries.length < 3) {
    summaries.push(mediumSeverity[0].message);
  }

  return summaries;
}
