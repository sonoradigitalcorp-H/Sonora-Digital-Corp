// ───────────────────────────────────────────────
// SIGNAL — Virality Index
// Measures viral potential and likelihood of content
// spreading rapidly across platforms.
// ───────────────────────────────────────────────

import { BaseScore, clamp, normalizeToRange, weightedAverage, sigmoid } from '../base-score';
import type { ArtistFeatures, ScoreInputSpec, ScoreIdentity, WeightConfig, ContributingFactor } from '../types';

export class ViralityIndex extends BaseScore {
  readonly identity: ScoreIdentity = {
    id: 'virality-index',
    version: '1.0.0',
    name: 'Virality Index',
    description: 'Measures viral potential and content amplification likelihood',
    category: 'performance',
  };

  readonly spec: ScoreInputSpec = {
    required: ['followerGrowth', 'engagementRate', 'crossPlatformPresence'],
    optional: ['postingFrequency', 'videoUploadFrequency', 'avgViews', 'avgViewGrowth', 'followers', 'genreTrendAlignment'],
    minimumConfidence: 25,
    defaultWeights: {
      followerGrowth: 0.9,
      engagementRate: 1.0,
      crossPlatformPresence: 0.7,
      postingFrequency: 0.6,
      videoUploadFrequency: 0.5,
      avgViews: 0.6,
      avgViewGrowth: 0.8,
      followers: 0.3,
      genreTrendAlignment: 0.5,
    },
  };

  protected computeFactors(features: ArtistFeatures, weights: WeightConfig): ContributingFactor[] {
    const factors: ContributingFactor[] = [];

    // 1. Engagement rate (sharing propensity)
    const engagementScore = normalizeToRange(features.engagementRate, 0, 20);
    const engagementWeight = weights.global.engagementRate ?? 1.0;
    const viralEngagement = sigmoid(features.engagementRate, 8, 0.4);
    factors.push({
      name: 'Share Propensity',
      value: features.engagementRate,
      impact: viralEngagement * 100 * engagementWeight,
      weight: engagementWeight,
      direction: viralEngagement >= 0.5 ? 'positive' : 'negative',
      reasoning: features.engagementRate >= 8
        ? `High share propensity at ${features.engagementRate.toFixed(1)}% engagement — content is sticky`
        : `Moderate share propensity at ${features.engagementRate.toFixed(1)}% — improve shareability`,
    });

    // 2. Growth acceleration
    const accelScore = normalizeToRange(features.followerGrowth, 0, 100);
    const growthWeight = weights.global.followerGrowth ?? 0.9;
    const viralGrowth = sigmoid(features.followerGrowth, 20, 0.08);
    factors.push({
      name: 'Growth Acceleration',
      value: features.followerGrowth,
      impact: viralGrowth * 100 * growthWeight,
      weight: growthWeight,
      direction: features.followerGrowth >= 0 ? 'positive' : 'negative',
      reasoning: features.followerGrowth > 20
        ? `Explosive growth at ${features.followerGrowth.toFixed(1)}% — viral trajectory`
        : features.followerGrowth > 5
          ? `Accelerating at ${features.followerGrowth.toFixed(1)}% — approaching viral threshold`
          : `Moderate growth ${features.followerGrowth.toFixed(1)}% — not yet viral`,
    });

    // 3. Multi-platform amplification
    const ampScore = normalizeToRange(features.crossPlatformPresence, 0, 5);
    const ampWeight = weights.global.crossPlatformPresence ?? 0.7;
    factors.push({
      name: 'Multi-Platform Amplification',
      value: features.crossPlatformPresence,
      impact: ampScore * 100 * ampWeight,
      weight: ampWeight,
      direction: ampScore >= 0.5 ? 'positive' : 'negative',
      reasoning: features.crossPlatformPresence >= 3
        ? `${features.crossPlatformPresence} platforms — content can cross-pollinate`
        : `${features.crossPlatformPresence} platform(s) — limited amplification channels`,
    });

    // 4. Optional: View growth momentum (viral video indicator)
    if (features.avgViewGrowth !== 0) {
      const viewViralScore = sigmoid(features.avgViewGrowth, 50, 0.05);
      const viewWeight = weights.global.avgViewGrowth ?? 0.8;
      factors.push({
        name: 'View Momentum',
        value: features.avgViewGrowth,
        impact: viewViralScore * 100 * viewWeight,
        weight: viewWeight,
        direction: viewViralScore >= 0.5 ? 'positive' : 'negative',
        reasoning: features.avgViewGrowth > 50
          ? `Views surging ${features.avgViewGrowth.toFixed(1)}% — potential viral breakout`
          : features.avgViewGrowth > 10
            ? `Views growing ${features.avgViewGrowth.toFixed(1)}% — building momentum`
            : `Views growing slowly — optimize for shareability`,
      });
    }

    // 5. Optional: Genre virality potential
    if (features.genreTrendAlignment > 0) {
      const trendScore = normalizeToRange(features.genreTrendAlignment, 0, 100);
      const trendWeight = weights.global.genreTrendAlignment ?? 0.5;
      factors.push({
        name: 'Genre Virality Potential',
        value: features.genreTrendAlignment,
        impact: trendScore * 100 * trendWeight,
        weight: trendWeight,
        direction: trendScore >= 0.5 ? 'positive' : 'negative',
        reasoning: features.genreTrendAlignment >= 70
          ? `Genre is trending at ${features.genreTrendAlignment}% — viral tailwind`
          : `Genre trending at ${features.genreTrendAlignment}% — niche audience`,
      });
    }

    return factors;
  }

  protected aggregateScore(factors: ContributingFactor[], _weights: WeightConfig): number {
    return clamp(weightedAverage(factors), 0, 100);
  }

  protected generateRecommendations(score: number, _factors: ContributingFactor[], features: ArtistFeatures): string[] {
    const recommendations: string[] = [];

    if (features.crossPlatformPresence < 2) {
      recommendations.push('Create short-form content for TikTok and Reels — primary viral channels');
    }
    if (features.postingFrequency > 0 && features.engagementRate > 5) {
      recommendations.push('High engagement + content — test a viral challenge or trend');
    }
    if (score < 40) {
      recommendations.push('Study viral moments in your genre — identify patterns to replicate');
    }
    if (score >= 70) {
      recommendations.push('Prepare infrastructure — ensure website/merch/links handle viral traffic');
    }
    if (features.engagementRate > 10 && features.followerGrowth < 10) {
      recommendations.push('Highly engaged but not sharing — add social share triggers to content');
    }

    return recommendations;
  }
}
