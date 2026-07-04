// ───────────────────────────────────────────────
// Instagram Data Provider (Meta Graph API)
// Provides: profile, bio, image, verified status,
// public metrics, posting frequency
// Gracefully degrades when API access is unavailable
// ───────────────────────────────────────────────

import { BaseProvider } from '../base-provider';
import { getCacheManager } from '../cache/cache-manager';
import type {
  ProviderHealth,
  NormalizedSearchResult,
  NormalizedProfile,
  NormalizedMetrics,
  NormalizedImages,
} from '../types';

const GRAPH_API_BASE = 'https://graph.facebook.com/v22.0';

// ── Internal Types ──

interface IGUserResponse {
  id: string;
  username?: string;
  name?: string;
  biography?: string;
  profile_picture_url?: string;
  followers_count?: number;
  follows_count?: number;
  media_count?: number;
  is_verified?: boolean;
  is_business?: boolean;
}

interface IGMediaItem {
  id: string;
  caption?: string;
  like_count?: number;
  comments_count?: number;
  timestamp?: string;
  media_type?: 'IMAGE' | 'VIDEO' | 'CAROUSEL_ALBUM';
  media_url?: string;
}

interface IGMediaResponse {
  data?: IGMediaItem[];
  paging?: { cursors?: { after?: string }; next?: string };
}

interface IGSearchResponse {
  data?: Array<{
    id: string;
    username?: string;
    name?: string;
    profile_picture_url?: string;
    followers_count?: number;
    is_verified?: boolean;
    is_business?: boolean;
  }>;
}

// ── Provider ──

export class InstagramProvider extends BaseProvider {
  readonly name = 'instagram';

  constructor() {
    super({
      name: 'instagram',
      rateLimitIntervalMs: parseInt(process.env.INSTAGRAM_RATE_LIMIT_INTERVAL || '500', 10),
      maxRetries: parseInt(process.env.INSTAGRAM_MAX_RETRIES || '2', 10),
      timeoutMs: parseInt(process.env.INSTAGRAM_REQUEST_TIMEOUT || '10000', 10),
      cacheTTLMs:
        parseInt(process.env.INSTAGRAM_CACHE_TTL_HOURS || '6', 10) * 60 * 60 * 1000,
    });

    if (process.env.INSTAGRAM_PROVIDER_ENABLED === 'false') {
      this.config.enabled = false;
    }
  }

  private getAccessToken(): string {
    return process.env.META_ACCESS_TOKEN || process.env.INSTAGRAM_ACCESS_TOKEN || '';
  }

  private getIGBusinessId(): string {
    return process.env.INSTAGRAM_BUSINESS_ID || process.env.IG_BUSINESS_ID || '';
  }

  private isDisabled(): boolean {
    return !this.config.enabled || process.env.INSTAGRAM_PROVIDER_ENABLED === 'false';
  }

  // ── Auth modes ──

  private hasBusinessAPI(): boolean {
    return !!(this.getAccessToken() && this.getIGBusinessId());
  }

  private hasBasicAPI(): boolean {
    return !!this.getAccessToken();
  }

  async initialize(): Promise<void> {
    if (this.isDisabled()) {
      this.log('info', 'Instagram provider disabled via INSTAGRAM_PROVIDER_ENABLED=false');
      this.initialized = false;
      return;
    }

    const token = this.getAccessToken();
    if (!token) {
      this.log('warn', 'Instagram provider not configured — set META_ACCESS_TOKEN or INSTAGRAM_ACCESS_TOKEN');
      this.initialized = false;
      return;
    }

    if (this.hasBusinessAPI()) {
      // Test Business API connectivity
      try {
        const result = await this.request<{ id: string }>(
          `${GRAPH_API_BASE}/${this.getIGBusinessId()}?fields=id&access_token=${token}`
        );
        if (result.ok) {
          this.initialized = true;
          this.log('info', 'Instagram provider initialized (Business API)');
          return;
        }
      } catch {
        // Fall through to Basic API
      }
    }

    // Try Basic Display API
    try {
      const result = await this.request<{ id: string }>(
        `${GRAPH_API_BASE}/me?fields=id&access_token=${token}`
      );
      if (result.ok) {
        this.initialized = true;
        this.log('info', 'Instagram provider initialized (Basic API — limited data)');
        return;
      }
    } catch (error) {
      this.log('warn', 'Instagram API test failed — provider will gracefully degrade', {
        error: error instanceof Error ? error.message : String(error),
      });
    }

    this.initialized = false;
  }

  async health(): Promise<ProviderHealth> {
    const start = Date.now();

    if (this.isDisabled()) {
      return this.buildHealthResult('unhealthy', 'Provider disabled via config', Date.now() - start, false, 'INSTAGRAM_PROVIDER_ENABLED=false');
    }

    const token = this.getAccessToken();
    if (!token) {
      return this.buildHealthResult('unhealthy', 'Access token not configured', Date.now() - start, false, 'Set META_ACCESS_TOKEN or INSTAGRAM_ACCESS_TOKEN');
    }

    try {
      if (this.hasBusinessAPI()) {
        const result = await this.request<{ id: string }>(
          `${GRAPH_API_BASE}/${this.getIGBusinessId()}?fields=id&access_token=${token}`
        );
        if (result.ok) {
          return this.buildHealthResult('healthy', 'Instagram Business API operational', Date.now() - start, true, null);
        }
      }

      const result = await this.request<{ id: string }>(
        `${GRAPH_API_BASE}/me?fields=id&access_token=${token}`
      );
      if (result.ok) {
        return this.buildHealthResult('degraded', 'Instagram Basic API — limited data', Date.now() - start, true, null);
      }
      return this.buildHealthResult('degraded', `API error: ${result.error}`, Date.now() - start, true, null);
    } catch (error) {
      return this.buildHealthResult('unhealthy', error instanceof Error ? error.message : String(error), Date.now() - start, true, null);
    }
  }

  async searchArtist(query: string): Promise<NormalizedSearchResult[]> {
    if (!this.initialized || this.isDisabled()) return [];
    if (!this.hasBusinessAPI()) {
      // Basic API doesn't support search
      return [];
    }

    const cache = getCacheManager();
    const cacheKey = `search:${query.toLowerCase().trim()}`;
    const cached = cache.get<NormalizedSearchResult[]>('instagram', 'search', cacheKey);
    if (cached && cache.isFresh(cached)) return cached.data;

    const token = this.getAccessToken();
    // Instagram Graph API search (limited)
    const result = await this.request<IGSearchResponse>(
      `${GRAPH_API_BASE}/ig_search?q=${encodeURIComponent(query)}&access_token=${token}&type=user&limit=5`
    );

    if (!result.ok || !result.data?.data) return [];

    const searchResults: NormalizedSearchResult[] = result.data.data
      .filter(item => item.username || item.name)
      .map((item, index) => ({
        externalId: item.id,
        name: item.name ?? item.username ?? query,
        genres: [],
        imageUrl: item.profile_picture_url ?? null,
        matchScore: Math.max(0, 100 - index * 20),
        provider: 'instagram',
      }));

    cache.set('instagram', 'search', cacheKey, searchResults, 60 * 60 * 1000);
    return searchResults;
  }

  async fetchProfile(externalId: string): Promise<Partial<NormalizedProfile> | null> {
    if (!this.initialized || this.isDisabled()) return null;

    const cache = getCacheManager();
    const cached = cache.get<Partial<NormalizedProfile>>('instagram', 'profile', externalId);
    if (cached && cache.isFresh(cached)) return cached.data;

    const token = this.getAccessToken();

    if (this.hasBusinessAPI()) {
      const result = await this.request<IGUserResponse>(
        `${GRAPH_API_BASE}/${externalId}?fields=id,username,name,biography,profile_picture_url,is_verified,followers_count,follows_count,media_count&access_token=${token}`
      );

      if (result.ok && result.data) {
        const profile: Partial<NormalizedProfile> = {
          externalId,
          name: result.data.name ?? result.data.username ?? 'Unknown',
          bio: result.data.biography ?? null,
          genres: [],
          country: null,
          city: null,
          profileUrl: result.data.username
            ? `https://www.instagram.com/${result.data.username}/`
            : null,
          provider: 'instagram',
        };
        cache.set('instagram', 'profile', externalId, profile, this.config.cacheTTLMs);
        return profile;
      }
    }

    // Basic API fallback — limited fields
    const result = await this.request<IGUserResponse>(
      `${GRAPH_API_BASE}/${externalId}?fields=id,username,name&access_token=${token}`
    );

    if (!result.ok || !result.data) return null;

    const profile: Partial<NormalizedProfile> = {
      externalId,
      name: result.data.name ?? result.data.username ?? 'Unknown',
      bio: null, // Not available via Basic API
      genres: [],
      country: null,
      city: null,
      profileUrl: result.data.username
        ? `https://www.instagram.com/${result.data.username}/`
        : null,
      provider: 'instagram',
    };

    cache.set('instagram', 'profile', externalId, profile, this.config.cacheTTLMs);
    return profile;
  }

  async fetchMetrics(externalId: string): Promise<Partial<NormalizedMetrics> | null> {
    if (!this.initialized || this.isDisabled()) return null;
    if (!this.hasBusinessAPI()) {
      // Basic API doesn't have metrics access
      this.log('debug', 'Metrics not available: Basic API mode');
      return null;
    }

    const cache = getCacheManager();
    const cacheKey = `metrics:${externalId}`;
    const cached = cache.get<Partial<NormalizedMetrics>>('instagram', 'metrics', cacheKey);
    if (cached && cache.isFresh(cached)) return cached.data;

    const token = this.getAccessToken();

    // Fetch user + media count for posting frequency
    const userResult = await this.request<IGUserResponse>(
      `${GRAPH_API_BASE}/${externalId}?fields=id,username,followers_count,follows_count,media_count&access_token=${token}`
    );

    if (!userResult.ok || !userResult.data) return null;

    // Fetch recent media for engagement calculation
    const mediaResult = await this.request<IGMediaResponse>(
      `${GRAPH_API_BASE}/${externalId}/media?fields=id,like_count,comments_count,timestamp&access_token=${token}&limit=10`
    );

    let totalLikes = 0;
    let totalComments = 0;
    let mediaCount = 0;
    let postingFrequency = 0;

    if (mediaResult.ok && mediaResult.data?.data) {
      for (const item of mediaResult.data.data) {
        totalLikes += item.like_count ?? 0;
        totalComments += item.comments_count ?? 0;
        mediaCount++;
      }

      // Posting frequency: average posts per week (over last 10 posts)
      if (mediaCount >= 2 && mediaResult.data.data[0]?.timestamp && mediaResult.data.data[mediaCount - 1]?.timestamp) {
        const newest = new Date(mediaResult.data.data[0].timestamp).getTime();
        const oldest = new Date(mediaResult.data.data[mediaCount - 1].timestamp).getTime();
        const daysSpan = Math.max(1, (newest - oldest) / (24 * 60 * 60 * 1000));
        postingFrequency = Math.round((mediaCount / daysSpan) * 7); // per week
      }

      // If only 1 post, use media_count to estimate
      if (postingFrequency === 0 && userResult.data.media_count) {
        postingFrequency = Math.round(userResult.data.media_count / 52); // posts per week (year avg)
      }
    }

    // Engagement rate: (likes + comments) / followers per post
    const followers = userResult.data.followers_count ?? 0;
    const engagement = followers > 0 && mediaCount > 0
      ? Math.min(100, Math.round(((totalLikes + totalComments) / mediaCount / followers) * 1000))
      : 0;

    const metrics: Partial<NormalizedMetrics> = {
      externalId,
      monthlyListeners: null,
      followers,
      engagement,
      growth: null,
      momentum: null,
      provider: 'instagram',
    };

    // Store extra context
    cache.set('instagram', 'metrics', cacheKey, {
      ...metrics,
      _extra: {
        follows: userResult.data.follows_count ?? 0,
        mediaCount: userResult.data.media_count ?? 0,
        postingFrequency,
        recentLikes: totalLikes,
        recentComments: totalComments,
      },
    }, this.config.cacheTTLMs);

    return metrics;
  }

  async fetchImages(externalId: string): Promise<Partial<NormalizedImages>> {
    if (!this.initialized || this.isDisabled()) {
      return { externalId, small: null, medium: null, large: null, provider: 'instagram' };
    }

    const cache = getCacheManager();
    const cacheKey = `images:${externalId}`;
    const cached = cache.get<Partial<NormalizedImages>>('instagram', 'images', cacheKey);
    if (cached && cache.isFresh(cached)) return cached.data;

    const token = this.getAccessToken();

    if (this.hasBusinessAPI()) {
      const result = await this.request<IGUserResponse>(
        `${GRAPH_API_BASE}/${externalId}?fields=id,profile_picture_url&access_token=${token}`
      );

      if (result.ok && result.data?.profile_picture_url) {
        const normalized: Partial<NormalizedImages> = {
          externalId,
          small: result.data.profile_picture_url,
          medium: result.data.profile_picture_url,
          large: result.data.profile_picture_url,
          provider: 'instagram',
        };
        cache.set('instagram', 'images', cacheKey, normalized, this.config.cacheTTLMs);
        return normalized;
      }
    }

    return { externalId, small: null, medium: null, large: null, provider: 'instagram' };
  }

  async fetchGenres(_externalId: string): Promise<string[]> {
    return [];
  }

  // ── Instagram-Specific Methods ──

  async fetchRecentMedia(
    externalId: string,
    limit = 10
  ): Promise<Array<{
    id: string;
    caption: string | null;
    likeCount: number;
    commentsCount: number;
    timestamp: string;
    mediaType: string;
    mediaUrl: string | null;
  }>> {
    if (!this.initialized || !this.hasBusinessAPI()) return [];

    const token = this.getAccessToken();
    const result = await this.request<IGMediaResponse>(
      `${GRAPH_API_BASE}/${externalId}/media?fields=id,caption,like_count,comments_count,timestamp,media_type,media_url&access_token=${token}&limit=${limit}`
    );

    if (!result.ok || !result.data?.data) return [];

    return result.data.data.map(item => ({
      id: item.id,
      caption: item.caption ?? null,
      likeCount: item.like_count ?? 0,
      commentsCount: item.comments_count ?? 0,
      timestamp: item.timestamp ?? '',
      mediaType: item.media_type ?? 'IMAGE',
      mediaUrl: item.media_url ?? null,
    }));
  }

  /**
   * Estimate posting frequency (posts per week).
   */
  async estimatePostingFrequency(externalId: string): Promise<number | null> {
    const token = this.getAccessToken();
    const result = await this.request<IGMediaResponse>(
      `${GRAPH_API_BASE}/${externalId}/media?fields=id,timestamp&access_token=${token}&limit=20`
    );

    if (!result.ok || !result.data?.data || result.data.data.length < 2) return null;

    const timestamps = result.data.data
      .map(m => m.timestamp)
      .filter(Boolean)
      .sort()
      .reverse();

    if (timestamps.length < 2) return null;

    const newest = new Date(timestamps[0]).getTime();
    const oldest = new Date(timestamps[timestamps.length - 1]).getTime();
    const daysSpan = Math.max(1, (newest - oldest) / (24 * 60 * 60 * 1000));

    return Math.round((timestamps.length / daysSpan) * 7);
  }

  async refresh(): Promise<void> {
    if (this.isDisabled()) return;
    this.log('info', 'Refreshing Instagram provider');
    getCacheManager().removeByProvider('instagram');
    await this.initialize();
  }

  async cache(): Promise<{ hits: number; misses: number; size: number }> {
    const stats = getCacheManager().getStats();
    const igStats = stats.byProvider['instagram'];
    return { hits: igStats?.hits ?? 0, misses: 0, size: igStats?.entries ?? 0 };
  }
}

// ── Singleton ──

let instance: InstagramProvider | null = null;

export function getInstagramProvider(): InstagramProvider {
  if (!instance) {
    instance = new InstagramProvider();
  }
  return instance;
}
