// ───────────────────────────────────────────────
// TikTok Data Provider
// Official APIs only — no scraping
// Uses TikTok Research API (preferred) or Business API
// Gracefully degrades to placeholder if unavailable
// ───────────────────────────────────────────────

import { BaseProvider } from '../base-provider';
import { getCacheManager } from '../cache/cache-manager';
import { createTikTokClient, TikTokPlaceholderClient } from './tiktok-types';
import type { TikTokAPIClient } from './tiktok-types';
import type {
  ProviderHealth,
  NormalizedSearchResult,
  NormalizedProfile,
  NormalizedMetrics,
  NormalizedImages,
} from '../types';

// ── Provider ──

export class TikTokProvider extends BaseProvider {
  readonly name = 'tiktok';
  private apiClient: TikTokAPIClient;

  constructor() {
    super({
      name: 'tiktok',
      rateLimitIntervalMs: parseInt(process.env.TIKTOK_RATE_LIMIT_INTERVAL || '500', 10),
      maxRetries: parseInt(process.env.TIKTOK_MAX_RETRIES || '2', 10),
      timeoutMs: parseInt(process.env.TIKTOK_REQUEST_TIMEOUT || '10000', 10),
      cacheTTLMs:
        parseInt(process.env.TIKTOK_CACHE_TTL_HOURS || '6', 10) * 60 * 60 * 1000,
    });

    this.apiClient = createTikTokClient();

    if (process.env.TIKTOK_PROVIDER_ENABLED === 'false') {
      this.config.enabled = false;
    }
  }

  private isDisabled(): boolean {
    return !this.config.enabled || process.env.TIKTOK_PROVIDER_ENABLED === 'false';
  }

  get apiAvailable(): boolean {
    return !(this.apiClient instanceof TikTokPlaceholderClient);
  }

  async initialize(): Promise<void> {
    if (this.isDisabled()) {
      this.log('info', 'TikTok provider disabled via TIKTOK_PROVIDER_ENABLED=false');
      this.initialized = false;
      return;
    }

    // Re-create client (env vars may have been updated)
    this.apiClient = createTikTokClient();

    if (this.apiClient.available) {
      const health = await this.apiClient.health();
      if (health.ok) {
        this.initialized = true;
        this.log('info', `TikTok provider initialized (${this.apiClient.name} API)`);
        return;
      }
      this.log('warn', `TikTok ${this.apiClient.name} API health check failed: ${health.message}`);
    } else {
      this.log('info', 'TikTok provider initialized in placeholder mode — no API access configured');
    }

    // Gracefully degrade — provider is "initialized" but will return empty data
    // This allows the system to work without TikTok API access
    this.initialized = true;
  }

  async health(): Promise<ProviderHealth> {
    const start = Date.now();

    if (this.isDisabled()) {
      return this.buildHealthResult(
        'unhealthy', 'Provider disabled via config', Date.now() - start,
        false, 'TIKTOK_PROVIDER_ENABLED=false'
      );
    }

    if (!this.apiClient.available) {
      return this.buildHealthResult(
        'degraded', 'No API credentials — set TIKTOK_ACCESS_TOKEN for Research API', Date.now() - start,
        false, 'TikTok API not configured'
      );
    }

    try {
      const health = await this.apiClient.health();
      if (health.ok) {
        return this.buildHealthResult(
          'healthy', `TikTok ${this.apiClient.name} API operational`, Date.now() - start, true, null
        );
      }
      return this.buildHealthResult(
        'degraded', health.message, Date.now() - start, true, 'API health check failed'
      );
    } catch (error) {
      return this.buildHealthResult(
        'unhealthy', error instanceof Error ? error.message : String(error), Date.now() - start, true, null
      );
    }
  }

  async searchArtist(query: string): Promise<NormalizedSearchResult[]> {
    if (this.isDisabled() || !this.apiClient.available) return [];

    const cache = getCacheManager();
    const cacheKey = `search:${query.toLowerCase().trim()}`;
    const cached = cache.get<NormalizedSearchResult[]>('tiktok', 'search', cacheKey);
    if (cached && cache.isFresh(cached)) return cached.data;

    const users = await this.apiClient.searchUsers(query);
    if (!users || users.length === 0) return [];

    const results: NormalizedSearchResult[] = users
      .filter(u => u.display_name || u.username)
      .map((user, index) => ({
        externalId: user.user_id,
        name: user.display_name ?? user.username ?? query,
        genres: [],
        imageUrl: user.avatar_url ?? null,
        matchScore: Math.max(0, 100 - index * 20),
        provider: 'tiktok',
      }));

    cache.set('tiktok', 'search', cacheKey, results, 60 * 60 * 1000);
    return results;
  }

  async fetchProfile(externalId: string): Promise<Partial<NormalizedProfile> | null> {
    if (this.isDisabled() || !this.apiClient.available) return null;

    const cache = getCacheManager();
    const cached = cache.get<Partial<NormalizedProfile>>('tiktok', 'profile', externalId);
    if (cached && cache.isFresh(cached)) return cached.data;

    const user = await this.apiClient.getUser(externalId);
    if (!user) return null;

    const profile: Partial<NormalizedProfile> = {
      externalId,
      name: user.display_name ?? user.username ?? 'Unknown',
      bio: user.bio_description ?? null,
      genres: [],
      country: null,
      city: null,
      profileUrl: user.profile_deep_link
        ?? (user.username ? `https://www.tiktok.com/@${user.username}` : null),
      provider: 'tiktok',
    };

    cache.set('tiktok', 'profile', externalId, profile, this.config.cacheTTLMs);
    return profile;
  }

  async fetchMetrics(externalId: string): Promise<Partial<NormalizedMetrics> | null> {
    if (this.isDisabled() || !this.apiClient.available) return null;

    const cache = getCacheManager();
    const cacheKey = `metrics:${externalId}`;
    const cached = cache.get<Partial<NormalizedMetrics>>('tiktok', 'metrics', cacheKey);
    if (cached && cache.isFresh(cached)) return cached.data;

    const user = await this.apiClient.getUser(externalId);
    if (!user) return null;

    // Fetch recent videos for engagement calculation
    const videos = await this.apiClient.getUserVideos(externalId, 10);
    let totalViews = 0;
    let totalLikes = 0;
    let totalComments = 0;
    let totalShares = 0;
    let videoCount = 0;

    for (const video of videos || []) {
      totalViews += video.view_count ?? 0;
      totalLikes += video.like_count ?? 0;
      totalComments += video.comment_count ?? 0;
      totalShares += video.share_count ?? 0;
      videoCount++;
    }

    const avgViews = videoCount > 0 ? Math.round(totalViews / videoCount) : 0;
    const avgLikes = videoCount > 0 ? Math.round(totalLikes / videoCount) : 0;

    // TikTok engagement: (likes + comments + shares) / views per video
    const engagement = avgViews > 0
      ? Math.min(100, Math.round(((avgLikes + (totalComments / videoCount) + (totalShares / videoCount)) / avgViews) * 150))
      : 0;

    const metrics: Partial<NormalizedMetrics> = {
      externalId,
      monthlyListeners: null,
      followers: user.follower_count ?? null,
      engagement,
      growth: null,
      momentum: null,
      provider: 'tiktok',
    };

    cache.set('tiktok', 'metrics', cacheKey, {
      ...metrics,
      _extra: {
        following: user.following_count ?? 0,
        totalLikes: user.likes_count ?? 0,
        videoCount: user.video_count ?? 0,
        avgViews,
        avgLikes,
        recentVideoCount: videoCount,
      },
    }, this.config.cacheTTLMs);

    return metrics;
  }

  async fetchImages(externalId: string): Promise<Partial<NormalizedImages>> {
    if (this.isDisabled() || !this.apiClient.available) {
      return { externalId, small: null, medium: null, large: null, provider: 'tiktok' };
    }

    const cache = getCacheManager();
    const cacheKey = `images:${externalId}`;
    const cached = cache.get<Partial<NormalizedImages>>('tiktok', 'images', cacheKey);
    if (cached && cache.isFresh(cached)) return cached.data;

    const user = await this.apiClient.getUser(externalId);
    if (!user?.avatar_url) {
      return { externalId, small: null, medium: null, large: null, provider: 'tiktok' };
    }

    const normalized: Partial<NormalizedImages> = {
      externalId,
      small: user.avatar_url,
      medium: user.avatar_url,
      large: user.avatar_url,
      provider: 'tiktok',
    };

    cache.set('tiktok', 'images', cacheKey, normalized, this.config.cacheTTLMs);
    return normalized;
  }

  async fetchGenres(_externalId: string): Promise<string[]> {
    return [];
  }

  // ── TikTok-Specific Methods ──

  /**
   * Fetch recent videos for a TikTok user.
   */
  async fetchRecentVideos(
    externalId: string,
    maxCount = 10
  ): Promise<Array<{
    id: string;
    title: string | null;
    views: number;
    likes: number;
    comments: number;
    shares: number;
    coverImageUrl: string | null;
    createdAt: string | null;
  }>> {
    if (!this.apiClient.available) return [];

    const videos = await this.apiClient.getUserVideos(externalId, maxCount);
    if (!videos) return [];

    return videos.map(v => ({
      id: v.video_id,
      title: v.title ?? v.description ?? null,
      views: v.view_count ?? 0,
      likes: v.like_count ?? 0,
      comments: v.comment_count ?? 0,
      shares: v.share_count ?? 0,
      coverImageUrl: v.cover_image_url ?? null,
      createdAt: v.create_time ?? null,
    }));
  }

  async refresh(): Promise<void> {
    if (this.isDisabled()) return;
    this.log('info', 'Refreshing TikTok provider');
    getCacheManager().removeByProvider('tiktok');
    // Re-create client in case env changed
    this.apiClient = createTikTokClient();
    await this.initialize();
  }

  async cache(): Promise<{ hits: number; misses: number; size: number }> {
    const stats = getCacheManager().getStats();
    const ttStats = stats.byProvider['tiktok'];
    return { hits: ttStats?.hits ?? 0, misses: 0, size: ttStats?.entries ?? 0 };
  }
}

// ── Singleton ──

let instance: TikTokProvider | null = null;

export function getTikTokProvider(): TikTokProvider {
  if (!instance) {
    instance = new TikTokProvider();
  }
  return instance;
}
