// ───────────────────────────────────────────────
// SIGNAL Intelligence Engine
// Receives data from providers, merges into one
// unified Artist object with confidence scoring
// ───────────────────────────────────────────────

import { getProviderRegistry, ProviderRegistry } from '../registry';
import { getCacheManager } from '../cache/cache-manager';
import {
  mergeProfiles,
  mergeMetrics,
  mergeImages,
  mergeAlbums,
  calculateConfidence,
  DEFAULT_INTELLIGENCE_CONFIG,
} from './merger';
import type {
  DataProvider,
  IntelligenceConfig,
  IntelligenceResult,
  IntelligenceError,
  UnifiedArtist,
  NormalizedSearchResult,
  NormalizedImages,
  NormalizedAlbum,
} from '../types';

export class IntelligenceEngine {
  private readonly registry: ProviderRegistry;
  private readonly config: IntelligenceConfig;

  constructor(registry?: ProviderRegistry, config?: Partial<IntelligenceConfig>) {
    this.registry = registry ?? getProviderRegistry();
    this.config = { ...DEFAULT_INTELLIGENCE_CONFIG, ...config };
  }

  /**
   * Search for an artist across all registered providers.
   * Returns a merged list of search results sorted by match score.
   */
  async search(query: string): Promise<NormalizedSearchResult[]> {
    const providers = this.registry.getAll();
    const cache = getCacheManager();

    // Check cache first
    const cacheKey = `search:${query.toLowerCase().trim()}`;
    const cached = cache.get<NormalizedSearchResult[]>('intelligence', 'search', cacheKey);
    if (cached && cache.isFresh(cached)) {
      return cached.data;
    }

    // Query all providers concurrently
    const results = await Promise.allSettled(
      providers.map(async (provider) => {
        try {
          const results = await provider.searchArtist(query);
          return results;
        } catch (error) {
          this.log('warn', `Provider search failed: ${provider.name}`, {
            query,
            error: error instanceof Error ? error.message : String(error),
          });
          return [] as NormalizedSearchResult[];
        }
      })
    );

    // Merge and sort
    const allResults: NormalizedSearchResult[] = [];
    for (const result of results) {
      if (result.status === 'fulfilled') {
        allResults.push(...result.value);
      }
    }

    // Sort by match score descending
    allResults.sort((a, b) => b.matchScore - a.matchScore);

    // Deduplicate by name (keep best match)
    const seen = new Set<string>();
    const deduplicated: NormalizedSearchResult[] = [];
    for (const result of allResults) {
      const key = result.name.toLowerCase().trim();
      if (!seen.has(key)) {
        seen.add(key);
        deduplicated.push(result);
      }
    }

    // Cache for 1 hour
    cache.set('intelligence', 'search', cacheKey, deduplicated, 60 * 60 * 1000);
    return deduplicated;
  }

  /**
   * Build a unified Artist from all available providers.
   * This is the core intelligence operation.
   */
  async buildArtist(
    artistId: string,
    artistName: string,
    options?: {
      /** Override provider name to use as primary */
      primaryProvider?: string;
      /** External IDs per provider (e.g., { spotify: '123', deezer: '456' }) */
      externalIds?: Record<string, string>;
    }
  ): Promise<IntelligenceResult> {
    const errors: IntelligenceError[] = [];
    const providers = this.registry.getAll();
    const sources: string[] = [];
    const startTime = Date.now();

    // Find external IDs by searching if not provided
    const externalIds = options?.externalIds ?? {};
    if (Object.keys(externalIds).length === 0) {
      // Search all providers for this artist name
      const searchResults = await this.search(artistName);

      for (const result of searchResults) {
        if (!externalIds[result.provider]) {
          externalIds[result.provider] = result.externalId;
        }
      }
    }

    // Collect data from all providers concurrently
    const profilePromises = providers.map(async (provider) => {
      const extId = externalIds[provider.name];
      if (!extId) return null;

      try {
        const profile = await provider.fetchProfile(extId);
        if (profile) sources.push(provider.name);
        return profile;
      } catch (error) {
        errors.push({
          provider: provider.name,
          error: error instanceof Error ? error.message : String(error),
          recoverable: true,
        });
        return null;
      }
    });

    const metricsPromises = providers.map(async (provider) => {
      const extId = externalIds[provider.name];
      if (!extId) return null;

      try {
        return await provider.fetchMetrics(extId);
      } catch (error) {
        errors.push({
          provider: provider.name,
          error: `Metrics: ${error instanceof Error ? error.message : String(error)}`,
          recoverable: true,
        });
        return null;
      }
    });

    const imagesPromises = providers.map(async (provider) => {
      const extId = externalIds[provider.name];
      if (!extId) return { externalId: '', small: null, medium: null, large: null, provider: provider.name } as Partial<NormalizedImages>;

      try {
        return await provider.fetchImages(extId);
      } catch (error) {
        errors.push({
          provider: provider.name,
          error: `Images: ${error instanceof Error ? error.message : String(error)}`,
          recoverable: true,
        });
        return { externalId: '', small: null, medium: null, large: null, provider: provider.name } as Partial<NormalizedImages>;
      }
    });

    const albumsPromises = providers.map(async (provider) => {
      if (typeof provider.fetchAlbums !== 'function') return [] as NormalizedAlbum[];
      const extId = externalIds[provider.name];
      if (!extId) return [] as NormalizedAlbum[];

      try {
        return await provider.fetchAlbums(extId);
      } catch (error) {
        errors.push({
          provider: provider.name,
          error: `Albums: ${error instanceof Error ? error.message : String(error)}`,
          recoverable: true,
        });
        return [] as NormalizedAlbum[];
      }
    });

    // Wait for all provider data
    const [profiles, metricss, imagess, albumss] = await Promise.all([
      Promise.all(profilePromises),
      Promise.all(metricsPromises),
      Promise.all(imagesPromises),
      Promise.all(albumsPromises),
    ]);

    // Merge data from all providers
    const mergedProfile = mergeProfiles(profiles.filter(Boolean) as Partial<import('../types').NormalizedProfile>[]);
    const mergedMetrics = mergeMetrics(metricss.filter(Boolean) as Partial<import('../types').NormalizedMetrics>[]);
    const mergedImages = mergeImages(imagess.filter(Boolean));
    const mergedAlbums = mergeAlbums(albumss.filter(a => a.length > 0));

    // Determine primary provider
    const primaryProvider = options?.primaryProvider
      ?? (profiles.find(p => p?.provider)?.provider ?? 'generated');

    // Build socials and links from provider profile data
    const socials = buildSocialsFromProfiles(profiles.filter(Boolean) as Partial<import('../types').NormalizedProfile>[]);
    const links = buildLinksFromProfiles(profiles.filter(Boolean) as Partial<import('../types').NormalizedProfile>[]);

    // Build the unified artist
    const artist: UnifiedArtist = {
      id: artistId,
      name: artistName,
      profile: mergedProfile as import('../types').NormalizedProfile,
      metrics: mergedMetrics as import('../types').NormalizedMetrics,
      images: mergedImages as import('../types').NormalizedImages,
      socials,
      links,
      albums: mergedAlbums,
      primaryProvider,
    };

    const confidence = calculateConfidence(
      sources.length,
      errors,
      this.config
    );

    this.log('info', 'Artist built', {
      artistId,
      artistName,
      sources: sources.length,
      errors: errors.length,
      confidence,
      durationMs: Date.now() - startTime,
    });

    return {
      artist,
      sources,
      confidence,
      errors,
      mergedAt: new Date().toISOString(),
    };
  }

  /**
   * Refresh all provider caches for a given artist.
   */
  async refreshArtist(artistId: string, artistName: string): Promise<void> {
    const cache = getCacheManager();

    // Remove all cache entries for this artist
    // (type-specific entries will be re-fetched on next buildArtist call)
    const providers = this.registry.getAll();
    for (const provider of providers) {
      cache.removeByProvider(provider.name);
    }

    this.log('info', 'Artist cache refreshed', { artistId, artistName });
  }

  /**
   * Get health status of the intelligence system itself.
   */
  async health(): Promise<{
    status: 'healthy' | 'degraded' | 'unhealthy';
    providers: number;
    healthyProviders: number;
    errors: string[];
  }> {
    const providerHealth = await this.registry.healthAll();
    const healthyProviders = providerHealth.filter(h => h.status === 'healthy').length;
    const errors = providerHealth
      .filter(h => h.status !== 'healthy' && h.message)
      .map(h => `${h.name}: ${h.message}`);

    let status: 'healthy' | 'degraded' | 'unhealthy';
    if (healthyProviders === providerHealth.length && providerHealth.length > 0) {
      status = 'healthy';
    } else if (healthyProviders > 0) {
      status = 'degraded';
    } else {
      status = 'unhealthy';
    }

    return {
      status,
      providers: providerHealth.length,
      healthyProviders,
      errors,
    };
  }

  private log(level: 'info' | 'warn' | 'error', message: string, context?: Record<string, unknown>): void {
    const timestamp = new Date().toISOString();
    const ctx = context ? ` ${JSON.stringify(context)}` : '';
    switch (level) {
      case 'info':
        console.log(`[Intelligence] ${timestamp} ${message}${ctx}`);
        break;
      case 'warn':
        console.warn(`[Intelligence] ${timestamp} ⚠️ ${message}${ctx}`);
        break;
      case 'error':
        console.error(`[Intelligence] ${timestamp} ❌ ${message}${ctx}`);
        break;
    }
  }
}

// ── Socials & Links Builders ──

/**
 * Build social media links from provider profiles.
 * Extracts social platform URLs from profileUrl fields.
 */
function buildSocialsFromProfiles(
  profiles: Partial<import('../types').NormalizedProfile>[]
): import('../types').NormalizedSocials {
  const socials: import('../types').NormalizedSocials = {
    externalId: '',
    instagram: null,
    tiktok: null,
    twitter: null,
    youtube: null,
    spotify: null,
    appleMusic: null,
    provider: 'merged',
  };

  for (const profile of profiles) {
    if (!profile.profileUrl) continue;

    if (profile.externalId) socials.externalId = profile.externalId;

    // Extract platform from profile URL
    const url = profile.profileUrl.toLowerCase();
    if (url.includes('instagram.com') || profile.provider === 'instagram') {
      socials.instagram = profile.profileUrl;
    }
    if (url.includes('tiktok.com') || profile.provider === 'tiktok') {
      socials.tiktok = profile.profileUrl;
    }
    if (url.includes('youtube.com') || profile.provider === 'youtube') {
      socials.youtube = profile.profileUrl;
    }
    if (url.includes('spotify.com') || profile.provider === 'spotify') {
      socials.spotify = profile.profileUrl;
    }
    if (url.includes('twitter.com') || url.includes('x.com')) {
      socials.twitter = profile.profileUrl;
    }
    if (url.includes('apple.com/music') || url.includes('music.apple.com')) {
      socials.appleMusic = profile.profileUrl;
    }
  }

  return socials;
}

/**
 * Build external links from provider profiles.
 */
function buildLinksFromProfiles(
  profiles: Partial<import('../types').NormalizedProfile>[]
): import('../types').NormalizedLinks {
  const links: import('../types').NormalizedLinks = {
    externalId: '',
    deezer: null,
    soundcloud: null,
    bandcamp: null,
    website: null,
    provider: 'merged',
  };

  for (const profile of profiles) {
    if (!profile.profileUrl) continue;

    if (profile.externalId) links.externalId = profile.externalId;

    const url = profile.profileUrl.toLowerCase();
    if (url.includes('deezer.com') || profile.provider === 'deezer') {
      links.deezer = profile.profileUrl;
    }
    if (url.includes('soundcloud.com')) {
      links.soundcloud = profile.profileUrl;
    }
    if (url.includes('bandcamp.com')) {
      links.bandcamp = profile.profileUrl;
    }
    // Non-platform URLs are treated as websites
    if (!url.includes('.com/') && !url.includes('.org/') && !url.includes('.io/')) {
      links.website = profile.profileUrl;
    }
  }

  return links;
}

// ── Singleton ──

let instance: IntelligenceEngine | null = null;

export function getIntelligenceEngine(registry?: ProviderRegistry): IntelligenceEngine {
  if (!instance) {
    instance = new IntelligenceEngine(registry);
  }
  return instance;
}
