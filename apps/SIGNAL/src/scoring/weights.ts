// ───────────────────────────────────────────────
// SIGNAL Score Engine — Weight Configuration
// Configurable, explainable, ML-replaceable weights
// ───────────────────────────────────────────────

import type { WeightConfig, WeightOverrides, ScoreInputSpec } from './types';

/**
 * Default global weight configuration.
 * Every score module provides its own defaults;
 * these are overrides applied globally across all scores.
 */
const DEFAULT_GLOBAL_WEIGHTS: Record<string, number> = {
  followers: 0.8,
  followerGrowth: 1.0,
  monthlyListeners: 0.7,
  monthlyListenerGrowth: 0.9,
  engagementRate: 1.0,
  postingFrequency: 0.6,
  videoUploadFrequency: 0.5,
  avgViews: 0.6,
  avgViewGrowth: 0.8,
  subscriberCount: 0.5,
  totalViews: 0.4,
  channelAge: 0.3,
  albumCount: 0.5,
  recentReleaseCount: 0.7,
  crossPlatformPresence: 0.8,
  genreTrendAlignment: 0.6,
  verificationStatus: 0.3,
};

/** Default provider multipliers */
const DEFAULT_PROVIDER_WEIGHTS: Record<string, number> = {
  spotify: 1.0,
  youtube: 0.9,
  instagram: 0.85,
  tiktok: 0.8,
  deezer: 0.6,
  appleMusic: 0.7,
  soundcloud: 0.5,
  bandcamp: 0.5,
};

/** Default market multipliers */
const DEFAULT_MARKET_WEIGHTS: Record<string, number> = {
  us: 1.0,
  gb: 0.9,
  jp: 0.85,
  kr: 0.8,
  de: 0.85,
  fr: 0.85,
  br: 0.8,
  mx: 0.75,
  in: 0.7,
  ng: 0.65,
};

/** Default genre multipliers */
const DEFAULT_GENRE_WEIGHTS: Record<string, number> = {
  pop: 1.0,
  hipHop: 1.0,
  rap: 1.0,
  electronic: 0.9,
  rock: 0.85,
  indie: 0.8,
  latin: 0.85,
  afrobeats: 0.9,
  kpop: 0.9,
  jazz: 0.6,
  classical: 0.5,
  country: 0.8,
  rnb: 1.0,
  reggaeton: 0.9,
  metal: 0.7,
};

let globalOverrides: WeightOverrides = {};

// ── Weight Engine API ──

/**
 * Set global weight overrides (loaded from config/env).
 * These are merged on top of per-score defaults.
 */
export function setGlobalWeights(overrides: WeightOverrides): void {
  globalOverrides = overrides;
}

/** Reset all global overrides to defaults */
export function resetGlobalWeights(): void {
  globalOverrides = {};
}

/**
 * Resolve effective weights for a given score, merging:
 * 1. Score's own default weights (from ScoreInputSpec)
 * 2. Global overrides
 * 3. Provider multipliers
 * 4. Market multipliers
 * 5. Genre multipliers
 */
export function resolveWeights(
  spec: ScoreInputSpec,
  options?: {
    providers?: string[];
    markets?: string[];
    genres?: string[];
  }
): WeightConfig {
  // Start with global defaults, overlay score defaults (score takes priority),
  // then apply global overrides (user config takes highest priority)
  const global: Record<string, number> = {
    ...DEFAULT_GLOBAL_WEIGHTS,
    ...spec.defaultWeights,
    ...(globalOverrides.global ?? {}),
  };

  const providers: Record<string, number> = {
    ...DEFAULT_PROVIDER_WEIGHTS,
    ...(globalOverrides.providers ?? {}),
  };

  const markets: Record<string, number> = {
    ...DEFAULT_MARKET_WEIGHTS,
    ...(globalOverrides.markets ?? {}),
  };

  const genres: Record<string, number> = {
    ...DEFAULT_GENRE_WEIGHTS,
    ...(globalOverrides.genres ?? {}),
  };

  // Apply provider multipliers
  if (options?.providers) {
    for (const [key, val] of Object.entries(global)) {
      let multiplier = 1.0;
      for (const provider of options.providers) {
        if (providers[provider]) {
          multiplier = Math.max(multiplier, providers[provider]);
        }
      }
      global[key] = val * multiplier;
    }
  }

  // Apply market multipliers
  if (options?.markets) {
    for (const [key, val] of Object.entries(global)) {
      let multiplier = 1.0;
      for (const market of options.markets) {
        const m = market.toLowerCase().slice(0, 2);
        if (markets[m]) {
          multiplier = Math.max(multiplier, markets[m]);
        }
      }
      global[key] = val * multiplier;
    }
  }

  // Apply genre multipliers
  if (options?.genres) {
    for (const [key, val] of Object.entries(global)) {
      let multiplier = 1.0;
      for (const genre of options.genres) {
        if (genres[genre]) {
          multiplier = Math.max(multiplier, genres[genre]);
        }
      }
      global[key] = val * multiplier;
    }
  }

  return { global, providers, markets, genres };
}

/** Get the current effective weight for a named input */
export function getEffectiveWeight(
  inputName: string,
  weights: WeightConfig
): number {
  return weights.global[inputName] ?? 1.0;
}

/** Future: Replace with ML-predicted weights */
export function enableMLWeights(modelPath?: string): void {
  // Placeholder for ML weight prediction
  // When enabled, weights are derived from a trained model
  // rather than static configuration
  console.info('[Weights] ML weight prediction not yet implemented');
}

export { DEFAULT_GLOBAL_WEIGHTS, DEFAULT_PROVIDER_WEIGHTS, DEFAULT_MARKET_WEIGHTS, DEFAULT_GENRE_WEIGHTS };
