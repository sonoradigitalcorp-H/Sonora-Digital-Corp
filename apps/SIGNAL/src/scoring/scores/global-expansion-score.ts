// ───────────────────────────────────────────────
// SIGNAL — Global Expansion Score
// Evaluates potential for international market growth
// and cross-border audience development.
// ───────────────────────────────────────────────

import { BaseScore, clamp, normalizeToRange, weightedAverage } from '../base-score';
import type { ArtistFeatures, ScoreInputSpec, ScoreIdentity, WeightConfig, ContributingFactor } from '../types';

export class GlobalExpansionScore extends BaseScore {
  readonly identity: ScoreIdentity = {
    id: 'global-expansion',
    version: '1.0.0',
    name: 'Global Expansion',
    description: 'Evaluates potential for international market growth and cross-border audience development',
    category: 'growth',
  };

  readonly spec: ScoreInputSpec = {
    required: ['followerGrowth', 'crossPlatformPresence', 'followers'],
    optional: ['monthlyListeners', 'genreTrendAlignment', 'engagementRate', 'channelAge', 'markets', 'albumCount', 'primaryLanguage'],
    minimumConfidence: 25,
    defaultWeights: {
      followerGrowth: 0.8,
      crossPlatformPresence: 0.8,
      followers: 0.6,
      monthlyListeners: 0.6,
      genreTrendAlignment: 0.7,
      engagementRate: 0.5,
      channelAge: 0.3,
      albumCount: 0.4,
      primaryLanguage: 0.5,
    },
  };

  protected computeFactors(features: ArtistFeatures, weights: WeightConfig): ContributingFactor[] {
    const factors: ContributingFactor[] = [];

    // 1. Genre global appeal
    const globalGenres = ['pop', 'electronic', 'latin', 'afrobeats', 'kpop', 'rnb', 'hipHop', 'rap', 'edm', 'reggaeton', 'dance'];
    const isGlobalGenre = features.genres.some((g) =>
      globalGenres.some((gg) => g.toLowerCase().includes(gg.toLowerCase()))
    );
    const genreAppealScore = isGlobalGenre ? 0.8 : normalizeToRange(features.genreTrendAlignment, 0, 100);
    const genreWeight = weights.global.genreTrendAlignment ?? 0.7;
    factors.push({
      name: 'Genre Global Appeal',
      value: isGlobalGenre ? 1 : features.genreTrendAlignment,
      impact: genreAppealScore * 100 * genreWeight,
      weight: genreWeight,
      direction: genreAppealScore >= 0.5 ? 'positive' : 'negative',
      reasoning: isGlobalGenre
        ? 'Genre has proven global appeal — strong international potential'
        : `${features.genre} genre — may find niche international audiences`,
    });

    // 2. Platform global distribution
    const distributionScore = normalizeToRange(features.crossPlatformPresence, 0, 5);
    const distributionWeight = weights.global.crossPlatformPresence ?? 0.8;
    factors.push({
      name: 'Global Distribution Network',
      value: features.crossPlatformPresence,
      impact: distributionScore * 100 * distributionWeight,
      weight: distributionWeight,
      direction: distributionScore >= 0.5 ? 'positive' : 'negative',
      reasoning: features.crossPlatformPresence >= 3
        ? `${features.crossPlatformPresence} platforms — multiple channels for international reach`
        : `${features.crossPlatformPresence} platform(s) — limited international distribution`,
    });

    // 3. Growth momentum (global scalability)
    const momentumScore = normalizeToRange(features.followerGrowth, 0, 30);
    const momentumWeight = weights.global.followerGrowth ?? 0.8;
    factors.push({
      name: 'Scalable Momentum',
      value: features.followerGrowth,
      impact: momentumScore * 100 * momentumWeight,
      weight: momentumWeight,
      direction: momentumScore >= 0.5 ? 'positive' : 'negative',
      reasoning: features.followerGrowth > 10
        ? `${features.followerGrowth.toFixed(1)}% growth — momentum can scale internationally`
        : `${features.followerGrowth.toFixed(1)}% growth — build domestic momentum first`,
    });

    // 4. Audience base (foundation for expansion)
    const baseScore = normalizeToRange(Math.log10(features.followers + 1), 2, 6);
    const baseWeight = weights.global.followers ?? 0.6;
    factors.push({
      name: 'International Foundation',
      value: features.followers,
      impact: baseScore * 100 * baseWeight,
      weight: baseWeight,
      direction: baseScore >= 0.5 ? 'positive' : 'negative',
      reasoning: features.followers >= 100000
        ? `${features.followers.toLocaleString()} followers — strong base for international push`
        : `${features.followers.toLocaleString()} followers — build audience before international expansion`,
    });

    // 5. Optional: Language versatility
    if (features.primaryLanguage === 'en' || features.primaryLanguage === 'es') {
      factors.push({
        name: 'Language Accessibility',
        value: 1,
        impact: 12,
        weight: 0.5,
        direction: 'positive',
        reasoning: `${features.primaryLanguage === 'en' ? 'English' : 'Spanish'} content — wide global accessibility`,
      });
    }

    // 6. Optional: Existing international markets
    if (features.markets.length > 1) {
      const marketScore = normalizeToRange(features.markets.length, 1, 10);
      const marketWeight = 0.4;
      factors.push({
        name: 'Existing International Markets',
        value: features.markets.length,
        impact: marketScore * 100 * marketWeight,
        weight: marketWeight,
        direction: 'positive',
        reasoning: `Already present in ${features.markets.length} market(s) — proven international reach`,
      });
    }

    // 7. Optional: Catalog size for international release cycles
    if (features.albumCount > 0) {
      const catalogScore = normalizeToRange(features.albumCount, 0, 15);
      const catalogWeight = weights.global.albumCount ?? 0.4;
      factors.push({
        name: 'International Catalog',
        value: features.albumCount,
        impact: catalogScore * 100 * catalogWeight,
        weight: catalogWeight,
        direction: catalogScore >= 0.5 ? 'positive' : 'negative',
        reasoning: features.albumCount >= 5
          ? `${features.albumCount} releases — adequate catalog for international release campaigns`
          : `${features.albumCount} release(s) — limited catalog for sustained international push`,
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
      recommendations.push('Expand to globally-relevant platforms (YouTube, Spotify, TikTok) first');
    }
    if (features.followers < 50000) {
      recommendations.push('Build domestic audience to 50K+ before investing in international markets');
    }
    if (features.albumCount < 3) {
      recommendations.push('Release more music — international expansion requires catalog depth');
    }
    if (features.markets.length < 2) {
      recommendations.push('Identify top 3 international markets by streaming data and target them');
    }
    if (score >= 70) {
      recommendations.push('Global-ready — plan market-specific campaigns for top 3 international cities');
    }
    if (score >= 50 && score < 70) {
      recommendations.push('International potential — start with English-language content and global playlists');
    }

    return recommendations;
  }
}
