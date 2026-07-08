// ───────────────────────────────────────────────
// SIGNAL Data Merger
// Combines partial data from multiple providers into
// unified, normalized schemas
// ───────────────────────────────────────────────

import type {
  NormalizedProfile,
  NormalizedMetrics,
  NormalizedImages,
  NormalizedSocials,
  NormalizedLinks,
  NormalizedAlbum,
  IntelligenceConfig,
  IntelligenceResult,
  IntelligenceError,
  UnifiedArtist,
} from '../types';

// ── Default Configuration ──

export const DEFAULT_INTELLIGENCE_CONFIG: IntelligenceConfig = {
  minProvidersForHighConfidence: 2,
  allowPartialResults: true,
  scorePriority: ['generated', 'spotify', 'average'],
};

// ── Merge Helpers ──

/**
 * Merge multiple partial profiles into one.
 * Later providers override earlier ones for non-null/defined values.
 */
export function mergeProfiles(profiles: Partial<NormalizedProfile>[]): Partial<NormalizedProfile> {
  const result: Partial<NormalizedProfile> = {
    externalId: '',
    name: '',
    bio: null,
    genres: [],
    country: null,
    city: null,
    profileUrl: null,
    provider: 'merged',
  };

  for (const profile of profiles) {
    if (profile.externalId) result.externalId = profile.externalId;
    if (profile.name) result.name = profile.name;
    if (profile.bio) result.bio = profile.bio;
    if (profile.genres && profile.genres.length > 0) {
      // Merge genres, deduplicating
      const existing = new Set(result.genres);
      for (const g of profile.genres) {
        if (!existing.has(g)) {
          result.genres.push(g);
          existing.add(g);
        }
      }
    }
    if (profile.country) result.country = profile.country;
    if (profile.city) result.city = profile.city;
    if (profile.profileUrl) result.profileUrl = profile.profileUrl;
    // Keep the provider name of the last non-empty contributor
    if (profile.provider) result.provider = profile.provider;
  }

  return result;
}

/**
 * Merge metrics from multiple sources, preferring non-null values.
 */
export function mergeMetrics(metrics: Partial<NormalizedMetrics>[]): Partial<NormalizedMetrics> {
  const result: Partial<NormalizedMetrics> = {
    externalId: '',
    monthlyListeners: null,
    followers: null,
    engagement: null,
    growth: null,
    momentum: null,
    provider: 'merged',
  };

  for (const m of metrics) {
    if (m.externalId) result.externalId = m.externalId;
    if (m.monthlyListeners !== null && m.monthlyListeners !== undefined) result.monthlyListeners = m.monthlyListeners;
    if (m.followers !== null && m.followers !== undefined) result.followers = m.followers;
    if (m.engagement !== null && m.engagement !== undefined) result.engagement = m.engagement;
    if (m.growth !== null && m.growth !== undefined) result.growth = m.growth;
    if (m.momentum !== null && m.momentum !== undefined) result.momentum = m.momentum;
    if (m.provider) result.provider = m.provider;
  }

  return result;
}

/**
 * Merge images from multiple sources.
 * Preference: largest image available.
 */
export function mergeImages(images: Partial<NormalizedImages>[]): Partial<NormalizedImages> {
  const result: Partial<NormalizedImages> = {
    externalId: '',
    small: null,
    medium: null,
    large: null,
    provider: 'merged',
  };

  for (const img of images) {
    if (img.externalId) result.externalId = img.externalId;
    if (img.small && !result.small) result.small = img.small;
    if (img.medium && !result.medium) result.medium = img.medium;
    if (img.large && !result.large) result.large = img.large;

    // If we already have a large image, prefer it over smaller ones
    if (img.large) {
      result.large = img.large;
      if (!result.medium) result.medium = img.medium ?? img.large;
      if (!result.small) result.small = img.small ?? img.medium ?? img.large;
    }

    if (img.provider) result.provider = `${result.provider},${img.provider}`;
  }

  return result;
}

/**
 * Merge album lists from multiple sources, deduplicating by title.
 */
export function mergeAlbums(albumLists: NormalizedAlbum[][]): NormalizedAlbum[] {
  const seen = new Set<string>();
  const result: NormalizedAlbum[] = [];

  for (const albums of albumLists) {
    for (const album of albums) {
      const key = album.title.toLowerCase().trim();
      if (!seen.has(key)) {
        seen.add(key);
        result.push(album);
      }
    }
  }

  return result;
}

// ── Confidence Calculation ──

export function calculateConfidence(
  providersUsed: number,
  errors: IntelligenceError[],
  config: IntelligenceConfig
): 'high' | 'medium' | 'low' {
  if (providersUsed >= config.minProvidersForHighConfidence && errors.length === 0) {
    return 'high';
  }

  if (providersUsed >= 1 && errors.filter(e => !e.recoverable).length === 0) {
    return 'medium';
  }

  return 'low';
}
