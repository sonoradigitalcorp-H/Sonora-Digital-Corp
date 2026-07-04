// ───────────────────────────────────────────────
// SIGNAL — Audience Quality Score
// Measures the depth and authenticity of audience engagement.
// High = loyal, active fanbase, not passive followers.
// ───────────────────────────────────────────────

import { BaseScore, clamp, normalizeToRange, weightedAverage } from '../base-score';
import type { ArtistFeatures, ScoreInputSpec, ScoreIdentity, WeightConfig, ContributingFactor } from '../types';

export class AudienceQualityScore extends BaseScore {
  readonly identity: ScoreIdentity = {
    id: 'audience-quality',
    version: '1.0.0',
    name: 'Audience Quality',
    description: 'Measures audience depth, loyalty, and authentic engagement',
    category: 'audience',
  };

  readonly spec: ScoreInputSpec = {
    required: ['engagementRate', 'followers', 'crossPlatformPresence'],
    optional: ['monthlyListeners', 'postingFrequency', 'subscriberCount', 'avgViews', 'totalViews', 'verificationStatus'],
    minimumConfidence: 30,
    defaultWeights: {
      engagementRate: 1.0,
      followers: 0.3,
      monthlyListeners: 0.5,
      crossPlatformPresence: 0.6,
      postingFrequency: 0.4,
      subscriberCount: 0.5,
      avgViews: 0.6,
      totalViews: 0.3,
      verificationStatus: 0.2,
    },
  };

  protected computeFactors(features: ArtistFeatures, weights: WeightConfig): ContributingFactor[] {
    const factors: ContributingFactor[] = [];

    // 1. Engagement rate (primary quality signal)
    const engagementScore = normalizeToRange(features.engagementRate, 0, 15);
    const engagementWeight = weights.global.engagementRate ?? 1.0;
    factors.push({
      name: 'Audience Engagement Depth',
      value: features.engagementRate,
      impact: engagementScore * 100 * engagementWeight,
      weight: engagementWeight,
      direction: engagementScore >= 0.5 ? 'positive' : 'negative',
      reasoning: features.engagementRate >= 8
        ? `Elite engagement at ${features.engagementRate.toFixed(1)}% — top-tier audience quality`
        : features.engagementRate >= 4
          ? `Healthy engagement at ${features.engagementRate.toFixed(1)}% — solid audience connection`
          : `Low engagement at ${features.engagementRate.toFixed(1)}% — audience may be passive or purchased`,
    });

    // 2. Listener-to-follower depth
    if (features.monthlyListeners > 0 && features.followers > 0) {
      const depthRatio = features.monthlyListeners / Math.max(1, features.followers);
      const depthScore = normalizeToRange(depthRatio, 0, 5);
      const listenerWeight = weights.global.monthlyListeners ?? 0.5;
      factors.push({
        name: 'Audience Depth Ratio',
        value: depthRatio,
        impact: depthScore * 100 * listenerWeight,
        weight: listenerWeight,
        direction: depthScore >= 0.5 ? 'positive' : 'negative',
        reasoning: depthRatio > 2
          ? `${depthRatio.toFixed(1)}x listeners per follower — deep passive audience`
          : depthRatio > 1
            ? `${depthRatio.toFixed(1)}x listeners per follower — balanced audience`
            : `${depthRatio.toFixed(1)}x listeners per follower — more followers than listeners`,
      });
    }

    // 3. Cross-platform consistency
    const consistencyScore = normalizeToRange(features.crossPlatformPresence, 0, 5);
    const consistencyWeight = weights.global.crossPlatformPresence ?? 0.6;
    factors.push({
      name: 'Cross-Platform Consistency',
      value: features.crossPlatformPresence,
      impact: consistencyScore * 100 * consistencyWeight,
      weight: consistencyWeight,
      direction: consistencyScore >= 0.5 ? 'positive' : 'negative',
      reasoning: features.crossPlatformPresence >= 3
        ? `Audience quality consistent across ${features.crossPlatformPresence} platforms`
        : `Limited to ${features.crossPlatformPresence} platform(s) — quality may be platform-specific`,
    });

    // 4. Optional: Subscriber-to-view ratio (YouTube quality)
    if (features.subscriberCount > 0 && features.avgViews > 0) {
      const viewRatio = features.avgViews / Math.max(1, features.subscriberCount);
      const viewRatioScore = normalizeToRange(viewRatio, 0, 0.5);
      const subWeight = weights.global.subscriberCount ?? 0.5;
      factors.push({
        name: 'Subscriber-to-View Ratio',
        value: viewRatio,
        impact: viewRatioScore * 100 * subWeight,
        weight: subWeight,
        direction: viewRatioScore >= 0.5 ? 'positive' : 'negative',
        reasoning: viewRatio > 0.1
          ? `${(viewRatio * 100).toFixed(1)}% of subscribers watch each video — highly engaged`
          : `${(viewRatio * 100).toFixed(1)}% subscriber view rate — improve content relevance`,
      });
    }

    // 5. Optional: Verification status (authenticity signal)
    if (features.verificationStatus) {
      factors.push({
        name: 'Verified Authenticity',
        value: 1,
        impact: 8,
        weight: 0.2,
        direction: 'positive',
        reasoning: 'Verified account — authentic identity confirmed',
      });
    }

    return factors;
  }

  protected aggregateScore(factors: ContributingFactor[], _weights: WeightConfig): number {
    return clamp(weightedAverage(factors), 0, 100);
  }

  protected generateRecommendations(score: number, _factors: ContributingFactor[], features: ArtistFeatures): string[] {
    const recommendations: string[] = [];

    if (features.engagementRate < 3) {
      recommendations.push('Improve engagement quality — reply to comments, run community polls');
    }
    if (features.crossPlatformPresence < 3) {
      recommendations.push('Build consistent presence across more platforms to validate audience quality');
    }
    if (score < 40) {
      recommendations.push('Audit audience for bots and inactive followers — clean your community');
    }
    if (features.engagementRate > 2 && features.followerGrowth < 0) {
      recommendations.push('Quality audience but not growing — leverage existing fans for word-of-mouth');
    }
    if (score >= 75) {
      recommendations.push('Premium audience quality — leverage for brand partnerships and label discussions');
    }
    if (features.monthlyListeners > 0 && features.followers > 0) {
      const ratio = features.monthlyListeners / Math.max(1, features.followers);
      if (ratio < 0.5) {
        recommendations.push('Convert passive listeners to followers — add Spotify follow-to-playlist prompts');
      }
    }

    return recommendations;
  }
}
