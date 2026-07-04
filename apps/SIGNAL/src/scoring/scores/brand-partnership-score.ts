// ───────────────────────────────────────────────
// SIGNAL — Brand Partnership Score
// Evaluates an artist's suitability for brand
// partnerships and sponsorships.
// ───────────────────────────────────────────────

import { BaseScore, clamp, normalizeToRange, weightedAverage } from '../base-score';
import type { ArtistFeatures, ScoreInputSpec, ScoreIdentity, WeightConfig, ContributingFactor } from '../types';

export class BrandPartnershipScore extends BaseScore {
  readonly identity: ScoreIdentity = {
    id: 'brand-partnership',
    version: '1.0.0',
    name: 'Brand Partnership',
    description: 'Evaluates suitability for brand sponsorships and commercial partnerships',
    category: 'commercial',
  };

  readonly spec: ScoreInputSpec = {
    required: ['engagementRate', 'followers', 'crossPlatformPresence'],
    optional: ['monthlyListeners', 'hasWebsite', 'verificationStatus', 'genreTrendAlignment', 'followerGrowth', 'postingFrequency', 'avgViews'],
    minimumConfidence: 30,
    defaultWeights: {
      engagementRate: 1.0,
      followers: 0.7,
      crossPlatformPresence: 0.8,
      monthlyListeners: 0.5,
      hasWebsite: 0.5,
      verificationStatus: 0.5,
      genreTrendAlignment: 0.5,
      followerGrowth: 0.6,
      postingFrequency: 0.6,
      avgViews: 0.5,
    },
  };

  protected computeFactors(features: ArtistFeatures, weights: WeightConfig): ContributingFactor[] {
    const factors: ContributingFactor[] = [];

    // 1. Engagement rate (brands pay for attention, not followers)
    const engagementScore = normalizeToRange(features.engagementRate, 0, 15);
    const engagementWeight = weights.global.engagementRate ?? 1.0;
    const brandEngagement = features.engagementRate >= 4 ? engagementScore : engagementScore * 0.5;
    factors.push({
      name: 'Brand Engagement Premium',
      value: features.engagementRate,
      impact: brandEngagement * 100 * engagementWeight,
      weight: engagementWeight,
      direction: brandEngagement >= 0.5 ? 'positive' : 'negative',
      reasoning: features.engagementRate >= 6
        ? `Premium engagement at ${features.engagementRate.toFixed(1)}% — brands pay premium for this`
        : features.engagementRate >= 3
          ? `Adequate engagement at ${features.engagementRate.toFixed(1)}% — meets brand minimums`
          : `Low engagement at ${features.engagementRate.toFixed(1)}% — below brand partnership threshold`,
    });

    // 2. Audience reach (brand impressions)
    const reachScore = normalizeToRange(Math.log10(features.followers + 1), 2, 6);
    const reachWeight = weights.global.followers ?? 0.7;
    factors.push({
      name: 'Brand Impression Reach',
      value: features.followers,
      impact: reachScore * 100 * reachWeight,
      weight: reachWeight,
      direction: reachScore >= 0.5 ? 'positive' : 'negative',
      reasoning: features.followers >= 50000
        ? `${features.followers.toLocaleString()} followers — substantial brand impressions`
        : features.followers >= 10000
          ? `${features.followers.toLocaleString()} followers — micro-influencer range, attractive to niche brands`
          : `${features.followers.toLocaleString()} followers — build for brand-level impressions`,
    });

    // 3. Multi-platform brand surface area
    const surfaceScore = normalizeToRange(features.crossPlatformPresence, 0, 5);
    const surfaceWeight = weights.global.crossPlatformPresence ?? 0.8;
    factors.push({
      name: 'Brand Surface Area',
      value: features.crossPlatformPresence,
      impact: surfaceScore * 100 * surfaceWeight,
      weight: surfaceWeight,
      direction: surfaceScore >= 0.5 ? 'positive' : 'negative',
      reasoning: features.crossPlatformPresence >= 3
        ? `${features.crossPlatformPresence} platforms — brands can run integrated campaigns`
        : `${features.crossPlatformPresence} platform(s) — limited campaign surface area`,
    });

    // 4. Optional: Sponsored content readiness
    if (features.hasWebsite) {
      factors.push({
        name: 'Brand Integration Ready',
        value: 1,
        impact: 10,
        weight: 0.5,
        direction: 'positive',
        reasoning: 'Official website — brand integration and campaign landing page ready',
      });
    }

    // 5. Optional: Verification and authenticity
    if (features.verificationStatus) {
      factors.push({
        name: 'Authenticity Signal',
        value: 1,
        impact: 10,
        weight: 0.5,
        direction: 'positive',
        reasoning: 'Verified account — brands prefer verified partners',
      });
    }

    // 6. Optional: Growth trend (brands want rising artists)
    if (features.followerGrowth > 0) {
      const trendScore = normalizeToRange(features.followerGrowth, 0, 30);
      const trendWeight = weights.global.followerGrowth ?? 0.6;
      factors.push({
        name: 'Brand Momentum',
        value: features.followerGrowth,
        impact: trendScore * 100 * trendWeight,
        weight: trendWeight,
        direction: 'positive',
        reasoning: `Growing ${features.followerGrowth.toFixed(1)}% — brands invest in rising artists`,
      });
    }

    // 7. Optional: Content quality (view-based)
    if (features.avgViews > 0) {
      const viewScore = normalizeToRange(Math.log10(features.avgViews + 1), 2, 6);
      const viewWeight = weights.global.avgViews ?? 0.5;
      factors.push({
        name: 'Content Quality Signal',
        value: features.avgViews,
        impact: viewScore * 100 * viewWeight,
        weight: viewWeight,
        direction: viewScore >= 0.5 ? 'positive' : 'negative',
        reasoning: features.avgViews >= 10000
          ? `Average ${features.avgViews.toLocaleString()} views — strong content for brand integration`
          : `Average ${features.avgViews.toLocaleString()} views — build content quality`,
      });
    }

    return factors;
  }

  protected aggregateScore(factors: ContributingFactor[], _weights: WeightConfig): number {
    return clamp(weightedAverage(factors), 0, 100);
  }

  protected generateRecommendations(score: number, _factors: ContributingFactor[], features: ArtistFeatures): string[] {
    const recommendations: string[] = [];

    if (features.engagementRate < 4) {
      recommendations.push('Improve engagement rate — brands require 3-5% minimum engagement');
    }
    if (features.followers < 10000) {
      recommendations.push('Grow to 10K+ followers for micro-brand partnerships');
    }
    if (features.crossPlatformPresence < 3) {
      recommendations.push('Expand to more platforms — brands run multi-channel campaigns');
    }
    if (!features.hasWebsite) {
      recommendations.push('Create professional website with media kit download — brands need this');
    }
    if (features.postingFrequency < 3 && features.avgViews > 1000) {
      recommendations.push('Post more frequently — brands need consistent content calendars');
    }
    if (score >= 65) {
      recommendations.push('Brand-ready — create a media kit with audience demographics');
    }
    if (score >= 50 && score < 65) {
      recommendations.push('Near brand-ready — close gaps in engagement and platform presence');
    }

    return recommendations;
  }
}
