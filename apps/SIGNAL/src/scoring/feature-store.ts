// ───────────────────────────────────────────────
// SIGNAL Feature Store — Internal Core
// Tracks feature provenance, quality, and freshness
// INTERNAL ONLY — never exposed to frontend directly
// ───────────────────────────────────────────────

import type { ArtistFeatures } from './types';
import type { UnifiedArtist } from '@/providers/types';
import { extractFeatures, normalizeFeatures } from './feature-extractor';

// ── Types ──

export interface FeatureMetadata {
  name: string;
  value: number;
  confidence: number;
  provider: string;
  source: 'provider' | 'extracted' | 'default';
  lastUpdated: string;
  quality: number; // 0-1
}

export interface FeaturedArtist {
  id: string;
  name: string;
  features: FeatureMetadata[];
  raw: ArtistFeatures;
  updatedAt: string;
}

// ── Feature Store ──

class FeatureStore {
  private static instance: FeatureStore | null = null;
  private cache = new Map<string, FeaturedArtist>();

  static getInstance(): FeatureStore {
    if (!FeatureStore.instance) {
      FeatureStore.instance = new FeatureStore();
    }
    return FeatureStore.instance;
  }

  static resetInstance(): void {
    FeatureStore.instance = null;
  }

  /**
   * Extract features from a UnifiedArtist and enrich with metadata.
   * This is the ONLY way features enter the system.
   */
  async ingest(artist: UnifiedArtist): Promise<FeaturedArtist> {
    const features = normalizeFeatures(extractFeatures(artist));
    const now = new Date().toISOString();

    const metadata: FeatureMetadata[] = [
      this.buildMetadata('followers', features.followers, artist, features.followers > 0 ? features.followers : 0),
      this.buildMetadata('followerGrowth', features.followerGrowth, artist, features.followerGrowth),
      this.buildMetadata('monthlyListeners', features.monthlyListeners, artist, features.monthlyListeners),
      this.buildMetadata('engagementRate', features.engagementRate, artist, features.engagementRate),
      this.buildMetadata('albumCount', features.albumCount, artist, features.albumCount),
      this.buildMetadata('crossPlatformPresence', features.crossPlatformPresence, artist, features.crossPlatformPresence),
      this.buildMetadata('genreTrendAlignment', features.genreTrendAlignment, artist, features.genreTrendAlignment),
    ];

    // Add optional features only if they have values
    if (features.monthlyListenerGrowth !== 0) {
      metadata.push(this.buildMetadata('monthlyListenerGrowth', features.monthlyListenerGrowth, artist, features.monthlyListenerGrowth));
    }
    if (features.postingFrequency > 0) {
      metadata.push(this.buildMetadata('postingFrequency', features.postingFrequency, artist, features.postingFrequency));
    }
    if (features.avgViews > 0) {
      metadata.push(this.buildMetadata('avgViews', features.avgViews, artist, features.avgViews));
    }
    if (features.avgViewGrowth !== 0) {
      metadata.push(this.buildMetadata('avgViewGrowth', features.avgViewGrowth, artist, features.avgViewGrowth));
    }
    if (features.subscriberCount > 0) {
      metadata.push(this.buildMetadata('subscriberCount', features.subscriberCount, artist, features.subscriberCount));
    }
    if (features.recentReleaseCount > 0) {
      metadata.push(this.buildMetadata('recentReleaseCount', features.recentReleaseCount, artist, features.recentReleaseCount));
    }

    const featured: FeaturedArtist = {
      id: artist.id,
      name: artist.name,
      features: metadata,
      raw: features,
      updatedAt: now,
    };

    this.cache.set(artist.id, featured);
    return featured;
  }

  /**
   * Get ingested features for an artist.
   */
  get(artistId: string): FeaturedArtist | undefined {
    return this.cache.get(artistId);
  }

  /**
   * Get raw ArtistFeatures for an artist (consumed by Score Engine).
   */
  getRaw(artistId: string): ArtistFeatures | undefined {
    return this.cache.get(artistId)?.raw;
  }

  /**
   * Clear cache.
   */
  clear(): void {
    this.cache.clear();
  }

  // ── Private ──

  private buildMetadata(
    name: string,
    value: number,
    artist: UnifiedArtist,
    rawValue: number
  ): FeatureMetadata {
    const quality = this.computeFeatureQuality(name, rawValue, artist);
    const provider = this.detectProvider(name, artist);
    const source: 'provider' | 'extracted' | 'default' = rawValue !== 0 ? 'provider' : 'default';

    return {
      name,
      value,
      confidence: Math.round(quality * 100),
      provider,
      source,
      lastUpdated: new Date().toISOString(),
      quality: Math.round(quality * 100) / 100,
    };
  }

  private computeFeatureQuality(name: string, value: number, artist: UnifiedArtist): number {
    // Base quality: 0.5 if default/zero, up to 1.0 if real provider data
    if (value === 0) return 0.3;
    if (value < 10 && name !== 'crossPlatformPresence' && name !== 'albumCount') return 0.5;

    // Check if we have provider data
    const hasSpotify = !!artist.socials?.spotify;
    const hasYoutube = !!artist.socials?.youtube;
    const hasInstagram = !!artist.socials?.instagram;

    let quality = 0.6;
    if (hasSpotify) quality += 0.15;
    if (hasYoutube) quality += 0.1;
    if (hasInstagram) quality += 0.1;
    if (artist.metrics?.followers && artist.metrics.followers > 0) quality += 0.05;

    return Math.min(1.0, quality);
  }

  private detectProvider(name: string, artist: UnifiedArtist): string {
    // Map feature names to most likely provider source
    const providerMap: Record<string, string> = {
      followers: artist.socials?.spotify ? 'spotify' : 'generated',
      followerGrowth: artist.socials?.spotify ? 'spotify' : 'generated',
      monthlyListeners: artist.socials?.spotify ? 'spotify' : 'generated',
      monthlyListenerGrowth: artist.socials?.spotify ? 'spotify' : 'generated',
      engagementRate: artist.socials?.instagram ? 'instagram' : artist.socials?.spotify ? 'spotify' : 'generated',
      albumCount: 'spotify',
      recentReleaseCount: 'spotify',
      postingFrequency: artist.socials?.instagram ? 'instagram' : 'generated',
      avgViews: artist.socials?.youtube ? 'youtube' : 'generated',
      avgViewGrowth: artist.socials?.youtube ? 'youtube' : 'generated',
      subscriberCount: artist.socials?.youtube ? 'youtube' : 'generated',
      crossPlatformPresence: 'extracted',
      genreTrendAlignment: 'extracted',
    };

    return providerMap[name] ?? 'unknown';
  }
}

export function getFeatureStore(): FeatureStore {
  return FeatureStore.getInstance();
}

export function resetFeatureStore(): void {
  FeatureStore.resetInstance();
}

export type { FeatureStore };
