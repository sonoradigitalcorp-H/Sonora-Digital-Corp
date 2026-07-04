// ───────────────────────────────────────────────
// SIGNAL — Label Readiness Score
// Evaluates how ready an artist is for label partnership.
// Based on audience, momentum, and professional signals.
// ───────────────────────────────────────────────

import { BaseScore, clamp, normalizeToRange, weightedAverage } from '../base-score';
import type { ArtistFeatures, ScoreInputSpec, ScoreIdentity, WeightConfig, ContributingFactor } from '../types';

export class LabelReadinessScore extends BaseScore {
  readonly identity: ScoreIdentity = {
    id: 'label-readiness',
    version: '1.0.0',
    name: 'Label Readiness',
    description: 'Evaluates artist readiness for major label or independent label partnership',
    category: 'commercial',
  };

  readonly spec: ScoreInputSpec = {
    required: ['followers', 'followerGrowth', 'engagementRate', 'albumCount', 'crossPlatformPresence'],
    optional: ['monthlyListeners', 'recentReleaseCount', 'hasWebsite', 'hasMerch', 'hasTouringHistory', 'channelAge', 'verificationStatus'],
    minimumConfidence: 35,
    defaultWeights: {
      followers: 0.8,
      followerGrowth: 0.9,
      engagementRate: 0.7,
      albumCount: 0.6,
      crossPlatformPresence: 0.7,
      monthlyListeners: 0.7,
      recentReleaseCount: 0.6,
      hasWebsite: 0.5,
      hasMerch: 0.4,
      hasTouringHistory: 0.6,
      channelAge: 0.3,
      verificationStatus: 0.3,
    },
  };

  protected computeFactors(features: ArtistFeatures, weights: WeightConfig): ContributingFactor[] {
    const factors: ContributingFactor[] = [];

    // 1. Audience size (reach potential)
    const audienceScore = normalizeToRange(Math.log10(features.followers + 1), 2, 6);
    const audienceWeight = weights.global.followers ?? 0.8;
    factors.push({
      name: 'Audience Scale',
      value: features.followers,
      impact: audienceScore * 100 * audienceWeight,
      weight: audienceWeight,
      direction: audienceScore >= 0.5 ? 'positive' : 'negative',
      reasoning: features.followers >= 100000
        ? `${features.followers.toLocaleString()} followers — strong audience scale for label interest`
        : features.followers >= 10000
          ? `${features.followers.toLocaleString()} followers — developing audience, shows potential`
          : `${features.followers.toLocaleString()} followers — needs audience growth for label attention`,
    });

    // 2. Growth trajectory (label sees momentum)
    const growthScore = normalizeToRange(features.followerGrowth, 0, 30);
    const growthWeight = weights.global.followerGrowth ?? 0.9;
    factors.push({
      name: 'Growth Trajectory',
      value: features.followerGrowth,
      impact: growthScore * 100 * growthWeight,
      weight: growthWeight,
      direction: growthScore >= 0.5 ? 'positive' : 'negative',
      reasoning: features.followerGrowth > 10
        ? `Growing ${features.followerGrowth.toFixed(1)}% — labels invest in momentum`
        : features.followerGrowth > 0
          ? `Steady growth ${features.followerGrowth.toFixed(1)}% — consistent trajectory`
          : `Declining ${Math.abs(features.followerGrowth).toFixed(1)}% — labels avoid shrinking audiences`,
    });

    // 3. Commercial engagement (fan monetization potential)
    const engagementScore = normalizeToRange(features.engagementRate, 0, 10);
    const engagementWeight = weights.global.engagementRate ?? 0.7;
    factors.push({
      name: 'Commercial Engagement',
      value: features.engagementRate,
      impact: engagementScore * 100 * engagementWeight,
      weight: engagementWeight,
      direction: engagementScore >= 0.5 ? 'positive' : 'negative',
      reasoning: features.engagementRate >= 5
        ? `${features.engagementRate.toFixed(1)}% engagement — fans are responsive to calls-to-action`
        : `${features.engagementRate.toFixed(1)}% engagement — improve to show fan monetization potential`,
    });

    // 4. Content catalog depth
    const catalogScore = normalizeToRange(features.albumCount, 0, 20);
    const catalogWeight = weights.global.albumCount ?? 0.6;
    factors.push({
      name: 'Catalog Depth',
      value: features.albumCount,
      impact: catalogScore * 100 * catalogWeight,
      weight: catalogWeight,
      direction: catalogScore >= 0.5 ? 'positive' : 'negative',
      reasoning: features.albumCount >= 5
        ? `${features.albumCount} releases — substantial catalog for label exploitation`
        : `${features.albumCount} release(s) — build catalog depth for label interest`,
    });

    // 5. Platform diversification
    const platformScore = normalizeToRange(features.crossPlatformPresence, 0, 5);
    const platformWeight = weights.global.crossPlatformPresence ?? 0.7;
    factors.push({
      name: 'Platform Diversification',
      value: features.crossPlatformPresence,
      impact: platformScore * 100 * platformWeight,
      weight: platformWeight,
      direction: platformScore >= 0.5 ? 'positive' : 'negative',
      reasoning: features.crossPlatformPresence >= 3
        ? `${features.crossPlatformPresence} platforms — labels value multi-channel presence`
        : `${features.crossPlatformPresence} platform(s) — expand to improve label appeal`,
    });

    // 6. Optional: Professional infrastructure
    if (features.hasWebsite) {
      factors.push({
        name: 'Professional Website',
        value: 1,
        impact: 10,
        weight: 0.5,
        direction: 'positive',
        reasoning: 'Official website — signals professional artist operation',
      });
    }
    if (features.hasMerch) {
      factors.push({
        name: 'Merchandise Operations',
        value: 1,
        impact: 8,
        weight: 0.4,
        direction: 'positive',
        reasoning: 'Merch available — existing revenue stream for labels to scale',
      });
    }
    if (features.hasTouringHistory) {
      factors.push({
        name: 'Live Performance Track Record',
        value: 1,
        impact: 12,
        weight: 0.6,
        direction: 'positive',
        reasoning: 'Touring history — proven live draw, label-signed artists tour',
      });
    }

    return factors;
  }

  protected aggregateScore(factors: ContributingFactor[], _weights: WeightConfig): number {
    return clamp(weightedAverage(factors), 0, 100);
  }

  protected generateRecommendations(score: number, _factors: ContributingFactor[], features: ArtistFeatures): string[] {
    const recommendations: string[] = [];

    if (features.followers < 10000) {
      recommendations.push('Build audience to 10K+ before approaching labels');
    }
    if (features.albumCount < 3) {
      recommendations.push('Release more music — labels prefer artists with 3+ releases');
    }
    if (features.engagementRate < 4) {
      recommendations.push('Improve engagement — labels look at fan connection, not just follower count');
    }
    if (!features.hasWebsite) {
      recommendations.push('Create an official website — essential for professional credibility');
    }
    if (!features.hasMerch && score > 50) {
      recommendations.push('Start basic merch (t-shirts, digital) — shows commercial potential');
    }
    if (features.crossPlatformPresence < 3) {
      recommendations.push('Expand to more platforms — labels want multi-channel artists');
    }
    if (score >= 75) {
      recommendations.push('Label-ready — prepare press kit, highlight reel, and audience demographics');
    }
    if (score >= 60 && score < 75) {
      recommendations.push('Near label-readiness — focus on closing gaps in engagement and catalog');
    }

    return recommendations;
  }
}
