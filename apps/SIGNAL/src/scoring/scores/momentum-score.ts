// ───────────────────────────────────────────────
// SIGNAL — Artist Momentum Score
// Measures the trajectory and velocity of an artist's
// growth across all platforms.
// ───────────────────────────────────────────────

import { BaseScore, clamp, normalizeToRange, weightedAverage, sigmoid } from '../base-score';
import type { ArtistFeatures, ScoreInputSpec, ScoreIdentity, WeightConfig, ContributingFactor } from '../types';

export class MomentumScore extends BaseScore {
  readonly identity: ScoreIdentity = {
    id: 'artist-momentum',
    version: '1.0.0',
    name: 'Artist Momentum',
    description: 'Measures growth trajectory and velocity across all platforms',
    category: 'growth',
  };

  readonly spec: ScoreInputSpec = {
    required: ['followers', 'followerGrowth', 'engagementRate', 'crossPlatformPresence'],
    optional: ['monthlyListenerGrowth', 'avgViewGrowth', 'recentReleaseCount', 'genreTrendAlignment'],
    minimumConfidence: 30,
    defaultWeights: {
      followerGrowth: 1.0,
      engagementRate: 0.8,
      crossPlatformPresence: 0.7,
      monthlyListenerGrowth: 0.9,
      avgViewGrowth: 0.7,
      recentReleaseCount: 0.5,
      genreTrendAlignment: 0.4,
      followers: 0.3,
    },
  };

  protected computeFactors(features: ArtistFeatures, weights: WeightConfig): ContributingFactor[] {
    const factors: ContributingFactor[] = [];

    // 1. Follower growth rate (highest impact)
    const growthScore = normalizeToRange(features.followerGrowth, -5, 50);
    const growthWeight = weights.global.followerGrowth ?? 1.0;
    factors.push({
      name: 'Follower Growth Rate',
      value: features.followerGrowth,
      impact: growthScore * 100 * growthWeight,
      weight: growthWeight,
      direction: growthScore >= 0.5 ? 'positive' : 'negative',
      reasoning: features.followerGrowth > 0
        ? `Growing at ${features.followerGrowth.toFixed(1)}% — strong upward trajectory`
        : `Declining at ${Math.abs(features.followerGrowth).toFixed(1)}% — needs attention`,
    });

    // 2. Engagement rate (quality of growth)
    const engagementScore = normalizeToRange(features.engagementRate, 0, 15);
    const engagementWeight = weights.global.engagementRate ?? 0.8;
    factors.push({
      name: 'Engagement Rate',
      value: features.engagementRate,
      impact: engagementScore * 100 * engagementWeight,
      weight: engagementWeight,
      direction: engagementScore >= 0.5 ? 'positive' : 'negative',
      reasoning: features.engagementRate > 5
        ? `Strong engagement at ${features.engagementRate.toFixed(1)}% — audience is actively connecting`
        : `Engagement at ${features.engagementRate.toFixed(1)}% — room for improvement`,
    });

    // 3. Cross-platform presence (breadth of momentum)
    const presenceScore = normalizeToRange(features.crossPlatformPresence, 0, 5);
    const presenceWeight = weights.global.crossPlatformPresence ?? 0.7;
    factors.push({
      name: 'Cross-Platform Presence',
      value: features.crossPlatformPresence,
      impact: presenceScore * 100 * presenceWeight,
      weight: presenceWeight,
      direction: presenceScore >= 0.5 ? 'positive' : 'negative',
      reasoning: features.crossPlatformPresence >= 3
        ? `Active on ${features.crossPlatformPresence} platforms — diversified reach`
        : `Present on ${features.crossPlatformPresence} platform(s) — expand to more channels`,
    });

    // 4. Optional: Monthly listener growth
    if (features.monthlyListenerGrowth !== 0) {
      const listenerGrowthScore = normalizeToRange(features.monthlyListenerGrowth, -5, 50);
      const listenerWeight = weights.global.monthlyListenerGrowth ?? 0.9;
      factors.push({
        name: 'Monthly Listener Growth',
        value: features.monthlyListenerGrowth,
        impact: listenerGrowthScore * 100 * listenerWeight,
        weight: listenerWeight,
        direction: listenerGrowthScore >= 0.5 ? 'positive' : 'negative',
        reasoning: `Monthly listeners ${features.monthlyListenerGrowth > 0 ? 'growing' : 'declining'} at ${Math.abs(features.monthlyListenerGrowth).toFixed(1)}%`,
      });
    }

    // 5. Optional: Recent releases (creative momentum)
    if (features.recentReleaseCount > 0) {
      const releaseScore = normalizeToRange(features.recentReleaseCount, 0, 10);
      const releaseWeight = weights.global.recentReleaseCount ?? 0.5;
      factors.push({
        name: 'Recent Releases',
        value: features.recentReleaseCount,
        impact: releaseScore * 100 * releaseWeight,
        weight: releaseWeight,
        direction: releaseScore >= 0.5 ? 'positive' : 'negative',
        reasoning: features.recentReleaseCount >= 3
          ? `${features.recentReleaseCount} releases in 12 months — consistent creative output`
          : `${features.recentReleaseCount} release(s) in 12 months — increase cadence`,
      });
    }

    // 6. Optional: Genre trend alignment
    if (features.genreTrendAlignment > 0) {
      const trendScore = normalizeToRange(features.genreTrendAlignment, 0, 100);
      const trendWeight = weights.global.genreTrendAlignment ?? 0.4;
      factors.push({
        name: 'Genre Trend Alignment',
        value: features.genreTrendAlignment,
        impact: trendScore * 100 * trendWeight,
        weight: trendWeight,
        direction: trendScore >= 0.5 ? 'positive' : 'negative',
        reasoning: features.genreTrendAlignment >= 60
          ? `Genre aligned with current trends (${features.genreTrendAlignment}%) — tailwind`
          : `Genre trending below market (${features.genreTrendAlignment}%)`,
      });
    }

    return factors;
  }

  protected aggregateScore(factors: ContributingFactor[], _weights: WeightConfig): number {
    return clamp(weightedAverage(factors), 0, 100);
  }

  protected generateRecommendations(score: number, factors: ContributingFactor[], features: ArtistFeatures): string[] {
    const recommendations: string[] = [];

    const lowEngagement = features.engagementRate < 3;
    const lowPresence = features.crossPlatformPresence < 2;
    const negativeGrowth = features.followerGrowth < 0;
    const lowReleases = features.recentReleaseCount < 2;

    if (negativeGrowth) {
      recommendations.push('Reverse follower decline — run targeted engagement campaigns');
    }
    if (lowEngagement) {
      recommendations.push('Boost engagement rate — interactive content, polls, Q&As');
    }
    if (lowPresence) {
      const platforms = ['TikTok', 'Instagram', 'YouTube', 'Spotify'];
      const missing = platforms.filter((p) => !features.platforms.some((fp) => fp.toLowerCase().includes(p.toLowerCase())));
      if (missing.length > 0) {
        recommendations.push(`Expand to ${missing.slice(0, 2).join(' and ')} to capture new audiences`);
      }
    }
    if (lowReleases && features.albumCount > 0) {
      recommendations.push('Increase release cadence — aim for 3+ releases per year');
    }
    if (score < 40) {
      recommendations.push('Develop a 90-day growth plan with specific platform targets');
    }
    if (score >= 80) {
      recommendations.push('Capitalize on momentum — plan a major release or tour announcement');
    }

    return recommendations;
  }
}
