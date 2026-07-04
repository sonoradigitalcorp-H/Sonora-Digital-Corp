// ───────────────────────────────────────────────
// SIGNAL — Tour Readiness Score
// Evaluates whether an artist has the audience and
// infrastructure to support a live tour.
// ───────────────────────────────────────────────

import { BaseScore, clamp, normalizeToRange, weightedAverage } from '../base-score';
import type { ArtistFeatures, ScoreInputSpec, ScoreIdentity, WeightConfig, ContributingFactor } from '../types';

export class TourReadinessScore extends BaseScore {
  readonly identity: ScoreIdentity = {
    id: 'tour-readiness',
    version: '1.0.0',
    name: 'Tour Readiness',
    description: 'Evaluates audience size, engagement, and infrastructure for live touring',
    category: 'commercial',
  };

  readonly spec: ScoreInputSpec = {
    required: ['followers', 'engagementRate', 'albumCount', 'monthlyListeners'],
    optional: ['crossPlatformPresence', 'hasTouringHistory', 'hasWebsite', 'hasMerch', 'channelAge', 'genreTrendAlignment', 'followerGrowth'],
    minimumConfidence: 30,
    defaultWeights: {
      followers: 0.9,
      engagementRate: 0.7,
      albumCount: 0.6,
      monthlyListeners: 0.8,
      crossPlatformPresence: 0.5,
      hasTouringHistory: 0.7,
      hasWebsite: 0.4,
      hasMerch: 0.3,
      channelAge: 0.3,
      genreTrendAlignment: 0.4,
      followerGrowth: 0.5,
    },
  };

  protected computeFactors(features: ArtistFeatures, weights: WeightConfig): ContributingFactor[] {
    const factors: ContributingFactor[] = [];

    // 1. Local audience density (followers in market area)
    const audienceScore = normalizeToRange(Math.log10(features.followers + 1), 2, 6);
    const audienceWeight = weights.global.followers ?? 0.9;
    factors.push({
      name: 'Ticket-Buying Audience',
      value: features.followers,
      impact: audienceScore * 100 * audienceWeight,
      weight: audienceWeight,
      direction: audienceScore >= 0.5 ? 'positive' : 'negative',
      reasoning: features.followers >= 50000
        ? `${features.followers.toLocaleString()} followers — viable live event audience`
        : features.followers >= 5000
          ? `${features.followers.toLocaleString()} followers — supports small venue tours`
          : `${features.followers.toLocaleString()} followers — build before touring`,
    });

    // 2. Streaming presence (album catalog to perform)
    const catalogScore = normalizeToRange(features.albumCount, 0, 15);
    const catalogWeight = weights.global.albumCount ?? 0.6;
    factors.push({
      name: 'Performance Catalog',
      value: features.albumCount,
      impact: catalogScore * 100 * catalogWeight,
      weight: catalogWeight,
      direction: catalogScore >= 0.5 ? 'positive' : 'negative',
      reasoning: features.albumCount >= 5
        ? `${features.albumCount} releases — ample material for a setlist`
        : `${features.albumCount} release(s) — need more content for a full show`,
    });

    // 3. Monthly listeners (demand indicator)
    if (features.monthlyListeners > 0) {
      const demandScore = normalizeToRange(Math.log10(features.monthlyListeners + 1), 2, 6);
      const demandWeight = weights.global.monthlyListeners ?? 0.8;
      factors.push({
        name: 'Live Demand Signal',
        value: features.monthlyListeners,
        impact: demandScore * 100 * demandWeight,
        weight: demandWeight,
        direction: demandScore >= 0.5 ? 'positive' : 'negative',
        reasoning: features.monthlyListeners >= 100000
          ? `${features.monthlyListeners.toLocaleString()} monthly listeners — proven demand`
          : features.monthlyListeners >= 10000
            ? `${features.monthlyListeners.toLocaleString()} monthly listeners — growing demand`
            : `Limited streaming demand at ${features.monthlyListeners.toLocaleString()} listeners`,
      });
    }

    // 4. Fan engagement (ticket conversion potential)
    const engagementScore = normalizeToRange(features.engagementRate, 0, 10);
    const engagementWeight = weights.global.engagementRate ?? 0.7;
    factors.push({
      name: 'Ticket Conversion Potential',
      value: features.engagementRate,
      impact: engagementScore * 100 * engagementWeight,
      weight: engagementWeight,
      direction: engagementScore >= 0.5 ? 'positive' : 'negative',
      reasoning: features.engagementRate >= 5
        ? `${features.engagementRate.toFixed(1)}% engagement — fans likely to buy tickets`
        : `${features.engagementRate.toFixed(1)}% engagement — improve to drive ticket sales`,
    });

    // 5. Optional: Touring track record
    if (features.hasTouringHistory) {
      factors.push({
        name: 'Tour Track Record',
        value: 1,
        impact: 15,
        weight: 0.7,
        direction: 'positive',
        reasoning: 'Previous touring experience — operational readiness confirmed',
      });
    }

    // 6. Optional: Market timing
    if (features.genreTrendAlignment > 0) {
      const marketScore = normalizeToRange(features.genreTrendAlignment, 0, 100);
      const marketWeight = weights.global.genreTrendAlignment ?? 0.4;
      factors.push({
        name: 'Market Timing',
        value: features.genreTrendAlignment,
        impact: marketScore * 100 * marketWeight,
        weight: marketWeight,
        direction: marketScore >= 0.5 ? 'positive' : 'negative',
        reasoning: features.genreTrendAlignment >= 60
          ? `Genre trending at ${features.genreTrendAlignment}% — favorable tour timing`
          : `Genre at ${features.genreTrendAlignment}% — niche tour might be better`,
      });
    }

    return factors;
  }

  protected aggregateScore(factors: ContributingFactor[], _weights: WeightConfig): number {
    return clamp(weightedAverage(factors), 0, 100);
  }

  protected generateRecommendations(score: number, _factors: ContributingFactor[], features: ArtistFeatures): string[] {
    const recommendations: string[] = [];

    if (features.followers < 5000) {
      recommendations.push('Build local following to 5K+ before planning a tour');
    }
    if (features.albumCount < 3) {
      recommendations.push('Release more music — need 30-45 min of material for a live show');
    }
    if (features.engagementRate < 4) {
      recommendations.push('Build fan excitement with live-content teasers before booking venues');
    }
    if (features.monthlyListeners > 0 && features.monthlyListeners < 10000) {
      recommendations.push('Grow streaming presence — use playlist pitching to build tour demand');
    }
    if (!features.hasWebsite) {
      recommendations.push('Create a tour-ready website with ticketing integration');
    }
    if (score >= 70) {
      recommendations.push('Tour-ready — start with small venues in top listener cities');
    }
    if (score >= 50 && score < 70 && features.crossPlatformPresence >= 3) {
      recommendations.push('Near tour-ready — consider a regional mini-tour to test live demand');
    }

    return recommendations;
  }
}
