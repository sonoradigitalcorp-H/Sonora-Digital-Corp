// ───────────────────────────────────────────────
// SIGNAL — Fan Conversion Score
// Measures ability to convert casual listeners into
// dedicated fans who follow, engage, and purchase.
// ───────────────────────────────────────────────

import { BaseScore, clamp, normalizeToRange, weightedAverage } from '../base-score';
import type { ArtistFeatures, ScoreInputSpec, ScoreIdentity, WeightConfig, ContributingFactor } from '../types';

export class FanConversionScore extends BaseScore {
  readonly identity: ScoreIdentity = {
    id: 'fan-conversion',
    version: '1.0.0',
    name: 'Fan Conversion',
    description: 'Measures ability to convert passive listeners into active, engaged fans',
    category: 'audience',
  };

  readonly spec: ScoreInputSpec = {
    required: ['engagementRate', 'followers', 'monthlyListeners'],
    optional: ['crossPlatformPresence', 'postingFrequency', 'albumCount', 'recentReleaseCount', 'hasMerch', 'hasWebsite', 'verificationStatus'],
    minimumConfidence: 30,
    defaultWeights: {
      engagementRate: 1.0,
      followers: 0.5,
      monthlyListeners: 0.7,
      crossPlatformPresence: 0.5,
      postingFrequency: 0.6,
      albumCount: 0.4,
      recentReleaseCount: 0.5,
      hasMerch: 0.5,
      hasWebsite: 0.4,
      verificationStatus: 0.2,
    },
  };

  protected computeFactors(features: ArtistFeatures, weights: WeightConfig): ContributingFactor[] {
    const factors: ContributingFactor[] = [];

    // 1. Listener-to-follower funnel efficiency
    if (features.monthlyListeners > 0 && features.followers > 0) {
      const funnelRate = features.followers / Math.max(1, features.monthlyListeners);
      const funnelScore = normalizeToRange(funnelRate, 0, 1);
      const listenerWeight = weights.global.monthlyListeners ?? 0.7;
      factors.push({
        name: 'Listener-to-Follower Funnel',
        value: funnelRate,
        impact: funnelScore * 100 * listenerWeight,
        weight: listenerWeight,
        direction: funnelScore >= 0.5 ? 'positive' : 'negative',
        reasoning: funnelRate > 0.5
          ? `${(funnelRate * 100).toFixed(1)}% listener conversion — strong funnel`
          : `${(funnelRate * 100).toFixed(1)}% listener conversion — optimize follow prompts`,
      });
    }

    // 2. Engagement depth (fan commitment indicator)
    const engagementScore = normalizeToRange(features.engagementRate, 0, 15);
    const engagementWeight = weights.global.engagementRate ?? 1.0;
    factors.push({
      name: 'Fan Commitment Depth',
      value: features.engagementRate,
      impact: engagementScore * 100 * engagementWeight,
      weight: engagementWeight,
      direction: engagementScore >= 0.5 ? 'positive' : 'negative',
      reasoning: features.engagementRate >= 6
        ? `${features.engagementRate.toFixed(1)}% engagement — fans are highly committed`
        : features.engagementRate >= 3
          ? `${features.engagementRate.toFixed(1)}% engagement — moderate fan commitment`
          : `${features.engagementRate.toFixed(1)}% engagement — improve to convert listeners to fans`,
    });

    // 3. Content cadence (conversion touchpoints)
    if (features.postingFrequency > 0) {
      const cadenceScore = normalizeToRange(features.postingFrequency, 0, 7);
      const cadenceWeight = weights.global.postingFrequency ?? 0.6;
      factors.push({
        name: 'Conversion Touchpoints',
        value: features.postingFrequency,
        impact: cadenceScore * 100 * cadenceWeight,
        weight: cadenceWeight,
        direction: cadenceScore >= 0.5 ? 'positive' : 'negative',
        reasoning: features.postingFrequency >= 3
          ? `${features.postingFrequency.toFixed(1)}x/week — consistent touchpoints convert listeners to fans`
          : `${features.postingFrequency.toFixed(1)}x/week — increase frequency for more conversion opportunities`,
      });
    }

    // 4. Recent releases (re-engagement triggers)
    if (features.recentReleaseCount > 0) {
      const releaseScore = normalizeToRange(features.recentReleaseCount, 0, 8);
      const releaseWeight = weights.global.recentReleaseCount ?? 0.5;
      factors.push({
        name: 'Re-Engagement Triggers',
        value: features.recentReleaseCount,
        impact: releaseScore * 100 * releaseWeight,
        weight: releaseWeight,
        direction: releaseScore >= 0.5 ? 'positive' : 'negative',
        reasoning: `${features.recentReleaseCount} recent releases — each release re-converts lapsed listeners`,
      });
    }

    // 5. Optional: Monetization readiness
    if (features.hasMerch) {
      factors.push({
        name: 'Fan Monetization',
        value: 1,
        impact: 10,
        weight: 0.5,
        direction: 'positive',
        reasoning: 'Merch available — fans have a purchase path',
      });
    }
    if (features.hasWebsite) {
      factors.push({
        name: 'Fan Destination',
        value: 1,
        impact: 6,
        weight: 0.4,
        direction: 'positive',
        reasoning: 'Official website — central hub for fan conversion',
      });
    }

    // 6. Cross-platform re-targeting
    const retargetScore = normalizeToRange(features.crossPlatformPresence, 0, 5);
    const retargetWeight = weights.global.crossPlatformPresence ?? 0.5;
    factors.push({
      name: 'Cross-Platform Re-Targeting',
      value: features.crossPlatformPresence,
      impact: retargetScore * 100 * retargetWeight,
      weight: retargetWeight,
      direction: retargetScore >= 0.5 ? 'positive' : 'negative',
      reasoning: features.crossPlatformPresence >= 3
        ? `${features.crossPlatformPresence} platforms — multiple re-targeting channels`
        : `${features.crossPlatformPresence} platform(s) — limited re-targeting ability`,
    });

    return factors;
  }

  protected aggregateScore(factors: ContributingFactor[], _weights: WeightConfig): number {
    return clamp(weightedAverage(factors), 0, 100);
  }

  protected generateRecommendations(score: number, _factors: ContributingFactor[], features: ArtistFeatures): string[] {
    const recommendations: string[] = [];

    if (features.monthlyListeners > 0 && features.followers > 0) {
      const funnelRate = features.followers / Math.max(1, features.monthlyListeners);
      if (funnelRate < 0.3) {
        recommendations.push('Add follow-to-playlist and follow-to-community prompts');
      }
    }
    if (features.engagementRate < 4) {
      recommendations.push('Create fan-exclusive content (behind-the-scenes, early access) to boost engagement');
    }
    if (!features.hasMerch && score > 50) {
      recommendations.push('Launch limited merchandise — converts committed fans into customers');
    }
    if (!features.hasWebsite) {
      recommendations.push('Build a fan hub website — centralize conversion paths');
    }
    if (features.postingFrequency < 3) {
      recommendations.push('Increase content frequency — more touchpoints = more conversion');
    }
    if (score >= 70) {
      recommendations.push('Strong conversion engine — introduce a fan membership tier');
    }

    return recommendations;
  }
}
