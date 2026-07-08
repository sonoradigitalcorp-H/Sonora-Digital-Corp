// ───────────────────────────────────────────────
// SIGNAL — Discovery Score
// Measures how discoverable and emerging an artist is.
// High = new audiences finding them rapidly.
// ───────────────────────────────────────────────

import { BaseScore, clamp, normalizeToRange, weightedAverage } from '../base-score';
import type { ArtistFeatures, ScoreInputSpec, ScoreIdentity, WeightConfig, ContributingFactor } from '../types';

export class DiscoveryScore extends BaseScore {
  readonly identity: ScoreIdentity = {
    id: 'discovery-score',
    version: '1.0.0',
    name: 'Discovery Score',
    description: 'Measures how discoverable and rapidly emerging an artist is',
    category: 'discovery',
  };

  readonly spec: ScoreInputSpec = {
    required: ['followerGrowth', 'crossPlatformPresence', 'engagementRate'],
    optional: ['postingFrequency', 'albumCount', 'recentReleaseCount', 'videoUploadFrequency', 'followers'],
    minimumConfidence: 30,
    defaultWeights: {
      followerGrowth: 1.0,
      crossPlatformPresence: 0.8,
      engagementRate: 0.6,
      postingFrequency: 0.7,
      albumCount: 0.4,
      recentReleaseCount: 0.6,
      videoUploadFrequency: 0.5,
      followers: 0.3,
    },
  };

  protected computeFactors(features: ArtistFeatures, weights: WeightConfig): ContributingFactor[] {
    const factors: ContributingFactor[] = [];

    // 1. Growth rate (discovery velocity)
    const growthScore = normalizeToRange(features.followerGrowth, 0, 50);
    const growthWeight = weights.global.followerGrowth ?? 1.0;
    factors.push({
      name: 'Discovery Velocity',
      value: features.followerGrowth,
      impact: growthScore * 100 * growthWeight,
      weight: growthWeight,
      direction: features.followerGrowth >= 0 ? 'positive' : 'negative',
      reasoning: features.followerGrowth > 10
        ? `Rapid discovery phase — growing at ${features.followerGrowth.toFixed(1)}%`
        : features.followerGrowth > 0
          ? `Steady discovery at ${features.followerGrowth.toFixed(1)}% growth`
          : `Not gaining new audiences — declining ${Math.abs(features.followerGrowth).toFixed(1)}%`,
    });

    // 2. Platform breadth (discovery surface area)
    const breadthScore = normalizeToRange(features.crossPlatformPresence, 0, 5);
    const breadthWeight = weights.global.crossPlatformPresence ?? 0.8;
    factors.push({
      name: 'Discovery Surface Area',
      value: features.crossPlatformPresence,
      impact: breadthScore * 100 * breadthWeight,
      weight: breadthWeight,
      direction: breadthScore >= 0.5 ? 'positive' : 'negative',
      reasoning: features.crossPlatformPresence >= 3
        ? `${features.crossPlatformPresence} platforms — multiple discovery entry points`
        : `${features.crossPlatformPresence} platform(s) — limited discovery surface`,
    });

    // 3. Engagement on new content (stickiness)
    const engagementScore = normalizeToRange(features.engagementRate, 0, 15);
    const engagementWeight = weights.global.engagementRate ?? 0.6;
    factors.push({
      name: 'New Audience Stickiness',
      value: features.engagementRate,
      impact: engagementScore * 100 * engagementWeight,
      weight: engagementWeight,
      direction: engagementScore >= 0.5 ? 'positive' : 'negative',
      reasoning: features.engagementRate > 5
        ? `New audiences are engaging at ${features.engagementRate.toFixed(1)}% — high retention`
        : `Low engagement at ${features.engagementRate.toFixed(1)}% — audiences discover but don't stay`,
    });

    // 4. Optional: Posting frequency (algorithmic visibility)
    if (features.postingFrequency > 0) {
      const freqScore = normalizeToRange(features.postingFrequency, 0, 10);
      const freqWeight = weights.global.postingFrequency ?? 0.7;
      factors.push({
        name: 'Content Cadence',
        value: features.postingFrequency,
        impact: freqScore * 100 * freqWeight,
        weight: freqWeight,
        direction: freqScore >= 0.5 ? 'positive' : 'negative',
        reasoning: features.postingFrequency >= 3
          ? `Posting ${features.postingFrequency.toFixed(1)}x/week — strong algorithmic visibility`
          : `Posting ${features.postingFrequency.toFixed(1)}x/week — increase for more discovery`,
      });
    }

    // 5. Optional: Recent releases (discovery triggers)
    if (features.recentReleaseCount > 0) {
      const releaseScore = normalizeToRange(features.recentReleaseCount, 0, 10);
      const releaseWeight = weights.global.recentReleaseCount ?? 0.6;
      factors.push({
        name: 'Discovery Triggers',
        value: features.recentReleaseCount,
        impact: releaseScore * 100 * releaseWeight,
        weight: releaseWeight,
        direction: releaseScore >= 0.5 ? 'positive' : 'negative',
        reasoning: `${features.recentReleaseCount} recent releases — each release is a discovery event`,
      });
    }

    // 6. Optional: Video upload frequency (YouTube discovery)
    if (features.videoUploadFrequency > 0) {
      const videoScore = normalizeToRange(features.videoUploadFrequency, 0, 52);
      const videoWeight = weights.global.videoUploadFrequency ?? 0.5;
      factors.push({
        name: 'Video Discovery Engine',
        value: features.videoUploadFrequency,
        impact: videoScore * 100 * videoWeight,
        weight: videoWeight,
        direction: videoScore >= 0.5 ? 'positive' : 'negative',
        reasoning: `${features.videoUploadFrequency} videos/year — YouTube is a discovery engine`,
      });
    }

    return factors;
  }

  protected aggregateScore(factors: ContributingFactor[], _weights: WeightConfig): number {
    return clamp(weightedAverage(factors), 0, 100);
  }

  protected generateRecommendations(score: number, _factors: ContributingFactor[], features: ArtistFeatures): string[] {
    const recommendations: string[] = [];

    if (features.crossPlatformPresence < 3) {
      const missing = ['TikTok', 'Instagram', 'YouTube', 'Spotify']
        .filter((p) => !features.platforms.some((fp) => fp.toLowerCase().includes(p.toLowerCase())));
      if (missing.length > 0) {
        recommendations.push(`Join ${missing[0]} to tap into new discovery networks`);
      }
    }
    if (features.postingFrequency < 3 && features.platforms.length > 0) {
      recommendations.push('Increase posting frequency to 3-5x/week for algorithmic boost');
    }
    if (features.recentReleaseCount < 2) {
      recommendations.push('Release more frequently — each release triggers discovery algorithms');
    }
    if (score >= 70) {
      recommendations.push('Capitalize on discovery wave — prepare for influx of new audience');
    }
    if (features.engagementRate < 3 && features.followerGrowth > 5) {
      recommendations.push('Growing but not engaging — add interactive elements to capture attention');
    }

    return recommendations;
  }
}
