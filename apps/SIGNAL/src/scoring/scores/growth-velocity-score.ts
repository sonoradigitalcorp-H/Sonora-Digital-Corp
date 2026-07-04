// ───────────────────────────────────────────────
// SIGNAL — Growth Velocity Score
// Measures how fast an artist is growing relative to
// their baseline and industry benchmarks.
// ───────────────────────────────────────────────

import { BaseScore, clamp, normalizeToRange, weightedAverage, sigmoid } from '../base-score';
import type { ArtistFeatures, ScoreInputSpec, ScoreIdentity, WeightConfig, ContributingFactor } from '../types';

export class GrowthVelocityScore extends BaseScore {
  readonly identity: ScoreIdentity = {
    id: 'growth-velocity',
    version: '1.0.0',
    name: 'Growth Velocity',
    description: 'Measures growth speed relative to baseline and benchmarks',
    category: 'growth',
  };

  readonly spec: ScoreInputSpec = {
    required: ['followerGrowth', 'followers', 'monthlyListeners'],
    optional: ['engagementRate', 'crossPlatformPresence', 'channelAge', 'avgViewGrowth', 'videoUploadFrequency'],
    minimumConfidence: 30,
    defaultWeights: {
      followerGrowth: 1.0,
      followers: 0.4,
      monthlyListeners: 0.5,
      engagementRate: 0.6,
      crossPlatformPresence: 0.5,
      channelAge: 0.3,
      avgViewGrowth: 0.7,
      videoUploadFrequency: 0.4,
    },
  };

  protected computeFactors(features: ArtistFeatures, weights: WeightConfig): ContributingFactor[] {
    const factors: ContributingFactor[] = [];

    // 1. Growth-to-audience ratio (growth velocity normalized by size)
    // Small artists growing fast score higher than large artists growing slowly
    const growthToAudience = features.followers > 0
      ? Math.abs(features.followerGrowth) / Math.log10(features.followers + 1)
      : 0;
    const velocityScore = normalizeToRange(growthToAudience, 0, 20);
    const velocityWeight = weights.global.followerGrowth ?? 1.0;
    factors.push({
      name: 'Growth-to-Audience Velocity',
      value: growthToAudience,
      impact: velocityScore * 100 * velocityWeight,
      weight: velocityWeight,
      direction: features.followerGrowth >= 0 ? 'positive' : 'negative',
      reasoning: features.followerGrowth > 0
        ? `Growing ${Math.abs(features.followerGrowth).toFixed(1)}% relative to ${features.followers.toLocaleString()} followers — strong velocity`
        : `Declining at ${Math.abs(features.followerGrowth).toFixed(1)}% — velocity needs recovery`,
    });

    // 2. Listener-to-follower ratio (conversion efficiency)
    if (features.monthlyListeners > 0 && features.followers > 0) {
      const conversionRatio = features.monthlyListeners / Math.max(1, features.followers);
      const conversionScore = normalizeToRange(conversionRatio, 0, 3);
      const listenerWeight = weights.global.monthlyListeners ?? 0.5;
      factors.push({
        name: 'Listener-to-Follower Ratio',
        value: conversionRatio,
        impact: conversionScore * 100 * listenerWeight,
        weight: listenerWeight,
        direction: conversionScore >= 0.5 ? 'positive' : 'negative',
        reasoning: conversionRatio > 1
          ? `${conversionRatio.toFixed(1)}x listeners per follower — strong passive reach`
          : `${conversionRatio.toFixed(1)}x listeners per follower — room to grow active audience`,
      });
    }

    // 3. Platform growth breadth
    const breadthScore = normalizeToRange(features.crossPlatformPresence, 0, 5);
    const breadthWeight = weights.global.crossPlatformPresence ?? 0.5;
    factors.push({
      name: 'Platform Breadth',
      value: features.crossPlatformPresence,
      impact: breadthScore * 100 * breadthWeight,
      weight: breadthWeight,
      direction: breadthScore >= 0.5 ? 'positive' : 'negative',
      reasoning: features.crossPlatformPresence >= 3
        ? `Growing across ${features.crossPlatformPresence} platforms — diversified velocity`
        : `Active on ${features.crossPlatformPresence} platform(s) — add channels`,
    });

    // 4. Optional: Channel age adjustment
    if (features.channelAge > 0) {
      const ageScore = normalizeToRange(features.channelAge, 0, 10);
      const ageWeight = weights.global.channelAge ?? 0.3;
      // Younger channels with high growth = higher velocity
      const ageAdjustedScore = ageScore < 0.3 ? 0.8 : ageScore > 0.7 ? 0.3 : 0.5;
      factors.push({
        name: 'Channel Age',
        value: features.channelAge,
        impact: ageAdjustedScore * 100 * ageWeight,
        weight: ageWeight,
        direction: ageAdjustedScore >= 0.5 ? 'positive' : 'negative',
        reasoning: features.channelAge < 2
          ? `Channel is ${features.channelAge.toFixed(1)} years old — rapid early growth phase`
          : `Established channel at ${features.channelAge.toFixed(1)} years — sustained growth expected`,
      });
    }

    // 5. Optional: View growth velocity (YouTube)
    if (features.avgViewGrowth !== 0) {
      const viewGrowthScore = normalizeToRange(features.avgViewGrowth, -5, 50);
      const viewWeight = weights.global.avgViewGrowth ?? 0.7;
      factors.push({
        name: 'View Growth Velocity',
        value: features.avgViewGrowth,
        impact: viewGrowthScore * 100 * viewWeight,
        weight: viewWeight,
        direction: viewGrowthScore >= 0.5 ? 'positive' : 'negative',
        reasoning: `Average views ${features.avgViewGrowth > 0 ? 'growing' : 'declining'} at ${Math.abs(features.avgViewGrowth).toFixed(1)}%`,
      });
    }

    return factors;
  }

  protected aggregateScore(factors: ContributingFactor[], _weights: WeightConfig): number {
    return clamp(weightedAverage(factors), 0, 100);
  }

  protected generateRecommendations(score: number, _factors: ContributingFactor[], features: ArtistFeatures): string[] {
    const recommendations: string[] = [];

    if (features.followerGrowth < 2 && features.followers > 0) {
      recommendations.push('Accelerate growth — cross-promote with similar artists in your genre');
    }
    if (features.crossPlatformPresence < 3) {
      recommendations.push('Increase platform presence to amplify growth velocity');
    }
    if (features.monthlyListeners > 0 && features.followers > 0) {
      const ratio = features.monthlyListeners / Math.max(1, features.followers);
      if (ratio < 0.5) {
        recommendations.push('Convert listeners to followers — add follow prompts in content');
      }
    }
    if (score < 40) {
      recommendations.push('Audit content strategy — identify what drove past growth spikes');
    }
    if (score >= 75) {
      recommendations.push('Maintain velocity — consistency is the #1 growth driver');
    }
    if (recommendations.length === 0 && score >= 40 && score < 75) {
      recommendations.push('Steady growth velocity — identify acceleration opportunities in top-performing content');
    }

    return recommendations;
  }
}
