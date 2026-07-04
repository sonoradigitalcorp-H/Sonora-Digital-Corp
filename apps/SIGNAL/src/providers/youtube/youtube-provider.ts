// ───────────────────────────────────────────────
// YouTube Data Provider (YouTube Data API v3)
// Provides: subscriber metrics, video analytics,
// channel profile, upload frequency, engagement
// ───────────────────────────────────────────────

import { BaseProvider, logProvider } from '../base-provider';
import { getCacheManager } from '../cache/cache-manager';
import type {
  ProviderHealth,
  NormalizedSearchResult,
  NormalizedProfile,
  NormalizedMetrics,
  NormalizedImages,
} from '../types';

const YT_API_BASE = 'https://www.googleapis.com/youtube/v3';

// ── Internal Types ──

interface YTChannelSnippet {
  title: string;
  description: string;
  publishedAt: string;
  thumbnails: {
    default?: { url: string };
    medium?: { url: string };
    high?: { url: string };
  };
  country?: string;
}

interface YTChannelStatistics {
  subscriberCount: string;
  viewCount: string;
  videoCount: string;
  hiddenSubscriberCount: boolean;
}

interface YTChannelResponse {
  items?: Array<{
    id: string;
    snippet: YTChannelSnippet;
    statistics: YTChannelStatistics;
  }>;
}

interface YTSearchItem {
  id: { channelId?: string };
  snippet: {
    title: string;
    thumbnails: { default?: { url: string }; medium?: { url: string }; high?: { url: string } };
  };
}

interface YTSearchResponse {
  items?: YTSearchItem[];
}

interface YTVideoItem {
  id: string;
  snippet: {
    title: string;
    publishedAt: string;
    thumbnails: { default?: { url: string }; medium?: { url: string }; high?: { url: string } };
  };
  statistics?: {
    viewCount: string;
    likeCount: string;
    commentCount: string;
  };
}

interface YTVideoListResponse {
  items?: YTVideoItem[];
}

// ── Helpers ──

function parseNumber(val: string | undefined | null, fallback: number): number {
  if (!val) return fallback;
  const n = parseInt(val, 10);
  return isNaN(n) ? fallback : n;
}

function getChannelAge(publishedAt: string): number {
  const published = new Date(publishedAt).getTime();
  const now = Date.now();
  return Math.floor((now - published) / (365.25 * 24 * 60 * 60 * 1000));
}

function estimateEngagement(
  avgViews: number,
  subscriberCount: number,
  likeCount?: number,
  commentCount?: number
): number {
  if (subscriberCount === 0) return 0;
  // Weighted formula: views/subs + likes+comments factor
  const viewRatio = avgViews / subscriberCount;
  const interactionFactor = likeCount && commentCount
    ? (likeCount + commentCount) / (avgViews || 1)
    : 0;
  return Math.min(100, Math.round((viewRatio * 0.7 + interactionFactor * 0.3) * 50));
}

// ── Provider ──

export class YouTubeProvider extends BaseProvider {
  readonly name = 'youtube';

  constructor() {
    super({
      name: 'youtube',
      rateLimitIntervalMs: parseInt(process.env.YOUTUBE_RATE_LIMIT_INTERVAL || '300', 10),
      maxRetries: parseInt(process.env.YOUTUBE_MAX_RETRIES || '3', 10),
      timeoutMs: parseInt(process.env.YOUTUBE_REQUEST_TIMEOUT || '10000', 10),
      cacheTTLMs:
        parseInt(process.env.YOUTUBE_CACHE_TTL_HOURS || '6', 10) * 60 * 60 * 1000,
    });

    // Check if disabled via env var
    if (process.env.YOUTUBE_PROVIDER_ENABLED === 'false') {
      this.config.enabled = false;
    }
  }

  private getApiKey(): string {
    return process.env.GOOGLE_API_KEY || process.env.YOUTUBE_API_KEY || '';
  }

  private isDisabled(): boolean {
    return !this.config.enabled || process.env.YOUTUBE_PROVIDER_ENABLED === 'false';
  }

  async initialize(): Promise<void> {
    if (this.isDisabled()) {
      this.log('info', 'YouTube provider disabled via YOUTUBE_PROVIDER_ENABLED=false');
      this.initialized = false;
      return;
    }

    const apiKey = this.getApiKey();
    if (!apiKey) {
      this.log('warn', 'YouTube provider not configured — set GOOGLE_API_KEY or YOUTUBE_API_KEY');
      this.initialized = false;
      return;
    }

    // Test connectivity
    try {
      const result = await this.request<{ kind: string }>(
        `${YT_API_BASE}/channels?part=id&mine=false&maxResults=1&key=${apiKey}`
      );
      if (result.ok) {
        this.initialized = true;
        this.log('info', 'YouTube provider initialized successfully');
      } else {
        this.log('warn', 'YouTube API test failed', { error: result.error });
        this.initialized = false;
      }
    } catch (error) {
      this.log('error', 'YouTube provider initialization failed', {
        error: error instanceof Error ? error.message : String(error),
      });
      this.initialized = false;
    }
  }

  async health(): Promise<ProviderHealth> {
    const start = Date.now();
    const apiKey = this.getApiKey();

    if (this.isDisabled()) {
      return this.buildHealthResult('unhealthy', 'Provider disabled via config', Date.now() - start, false, 'YOUTUBE_PROVIDER_ENABLED=false');
    }

    if (!apiKey) {
      return this.buildHealthResult('unhealthy', 'API key not configured', Date.now() - start, false, 'Set GOOGLE_API_KEY or YOUTUBE_API_KEY');
    }

    try {
      const result = await this.request<{ kind: string }>(
        `${YT_API_BASE}/channels?part=id&mine=false&maxResults=1&key=${apiKey}`
      );

      if (result.ok) {
        return this.buildHealthResult('healthy', 'YouTube API operational', Date.now() - start, true, null);
      }
      return this.buildHealthResult('degraded', `API error: ${result.error}`, Date.now() - start, true, null);
    } catch (error) {
      return this.buildHealthResult('unhealthy', error instanceof Error ? error.message : String(error), Date.now() - start, true, null);
    }
  }

  async searchArtist(query: string): Promise<NormalizedSearchResult[]> {
    if (!this.initialized || this.isDisabled()) return [];

    const cache = getCacheManager();
    const cacheKey = `search:${query.toLowerCase().trim()}`;
    const cached = cache.get<NormalizedSearchResult[]>('youtube', 'search', cacheKey);
    if (cached && cache.isFresh(cached)) return cached.data;

    const apiKey = this.getApiKey();
    const result = await this.request<YTSearchResponse>(
      `${YT_API_BASE}/search?part=snippet&q=${encodeURIComponent(query)}&type=channel&maxResults=5&key=${apiKey}`
    );

    if (!result.ok || !result.data?.items) return [];

    const searchResults: NormalizedSearchResult[] = result.data.items
      .filter(item => item.id?.channelId)
      .map((item, index) => ({
        externalId: item.id.channelId!,
        name: item.snippet.title,
        genres: [],
        imageUrl: item.snippet.thumbnails?.medium?.url ?? item.snippet.thumbnails?.default?.url ?? null,
        matchScore: Math.max(0, 100 - index * 20),
        provider: 'youtube',
      }));

    cache.set('youtube', 'search', cacheKey, searchResults, 60 * 60 * 1000);
    return searchResults;
  }

  async fetchProfile(externalId: string): Promise<Partial<NormalizedProfile> | null> {
    if (!this.initialized || this.isDisabled()) return null;

    const cache = getCacheManager();
    const cached = cache.get<Partial<NormalizedProfile>>('youtube', 'profile', externalId);
    if (cached && cache.isFresh(cached)) return cached.data;

    const apiKey = this.getApiKey();
    const result = await this.request<YTChannelResponse>(
      `${YT_API_BASE}/channels?part=snippet&id=${externalId}&key=${apiKey}`
    );

    if (!result.ok || !result.data?.items?.[0]) return null;

    const raw = result.data.items[0];
    const snippet = raw.snippet;

    const profile: Partial<NormalizedProfile> = {
      externalId,
      name: snippet.title,
      bio: snippet.description || null,
      genres: [],
      country: snippet.country ?? null,
      city: null,
      profileUrl: `https://www.youtube.com/channel/${externalId}`,
      provider: 'youtube',
    };

    cache.set('youtube', 'profile', externalId, profile, this.config.cacheTTLMs);
    return profile;
  }

  async fetchMetrics(externalId: string): Promise<Partial<NormalizedMetrics> | null> {
    if (!this.initialized || this.isDisabled()) return null;

    const cache = getCacheManager();
    const cacheKey = `metrics:${externalId}`;
    const cached = cache.get<Partial<NormalizedMetrics>>('youtube', 'metrics', cacheKey);
    if (cached && cache.isFresh(cached)) return cached.data;

    const apiKey = this.getApiKey();

    // Fetch channel statistics
    const channelResult = await this.request<YTChannelResponse>(
      `${YT_API_BASE}/channels?part=statistics,snippet&id=${externalId}&key=${apiKey}`
    );

    if (!channelResult.ok || !channelResult.data?.items?.[0]) return null;

    const stats = channelResult.data.items[0].statistics;
    const snippet = channelResult.data.items[0].snippet;
    const subscriberCount = parseNumber(stats.subscriberCount, 0);
    const totalViews = parseNumber(stats.viewCount, 0);
    const totalVideos = parseNumber(stats.videoCount, 0);
    const channelAge = getChannelAge(snippet.publishedAt);

    // Fetch latest videos for engagement estimates
    const videosResult = await this.request<YTVideoListResponse>(
      `${YT_API_BASE}/search?part=snippet&channelId=${externalId}&order=date&maxResults=10&type=video&key=${apiKey}`
    );

    let avgViews = 0;
    let totalLikes = 0;
    let totalComments = 0;
    let videoCount = 0;

    if (videosResult.ok && videosResult.data?.items) {
      const videoIds = videosResult.data.items.map(v => v.id).filter(Boolean);
      if (videoIds.length > 0) {
        const statsResult = await this.request<YTVideoListResponse>(
          `${YT_API_BASE}/videos?part=statistics,snippet&id=${videoIds.join(',')}&key=${apiKey}`
        );

        if (statsResult.ok && statsResult.data?.items) {
          for (const video of statsResult.data.items) {
            const views = parseNumber(video.statistics?.viewCount, 0);
            const likes = parseNumber(video.statistics?.likeCount, 0);
            const comments = parseNumber(video.statistics?.commentCount, 0);
            avgViews += views;
            totalLikes += likes;
            totalComments += comments;
            videoCount++;
          }
          if (videoCount > 0) avgViews = Math.round(avgViews / videoCount);
        }
      }
    }

    // Upload frequency: videos per year
    const uploadFrequency = channelAge > 0 ? Math.round(totalVideos / channelAge) : totalVideos;

    // Engagement estimate
    const engagement = estimateEngagement(avgViews, subscriberCount, totalLikes, totalComments);

    const metrics: Partial<NormalizedMetrics> = {
      externalId,
      monthlyListeners: null, // YouTube doesn't have "monthly listeners"
      followers: subscriberCount,
      engagement,
      growth: null, // Would need historical data
      momentum: null, // Would need trend data
      provider: 'youtube',
    };

    // Store additional computed data in a side channel via the cache as context
    cache.set('youtube', 'metrics', cacheKey, {
      ...metrics,
      _extra: {
        totalViews,
        totalVideos,
        avgViews,
        totalLikes,
        totalComments,
        uploadFrequency,
        channelAge,
        hiddenSubscriberCount: stats.hiddenSubscriberCount,
      },
    }, this.config.cacheTTLMs);

    return metrics;
  }

  async fetchImages(externalId: string): Promise<Partial<NormalizedImages>> {
    if (!this.initialized || this.isDisabled()) {
      return { externalId, small: null, medium: null, large: null, provider: 'youtube' };
    }

    const cache = getCacheManager();
    const cacheKey = `images:${externalId}`;
    const cached = cache.get<Partial<NormalizedImages>>('youtube', 'images', cacheKey);
    if (cached && cache.isFresh(cached)) return cached.data;

    const apiKey = this.getApiKey();
    const result = await this.request<YTChannelResponse>(
      `${YT_API_BASE}/channels?part=snippet&id=${externalId}&key=${apiKey}`
    );

    if (!result.ok || !result.data?.items?.[0]) {
      return { externalId, small: null, medium: null, large: null, provider: 'youtube' };
    }

    const thumbs = result.data.items[0].snippet.thumbnails;
    const normalized: Partial<NormalizedImages> = {
      externalId,
      small: thumbs.default?.url ?? null,
      medium: thumbs.medium?.url ?? thumbs.default?.url ?? null,
      large: thumbs.high?.url ?? thumbs.medium?.url ?? thumbs.default?.url ?? null,
      provider: 'youtube',
    };

    cache.set('youtube', 'images', cacheKey, normalized, this.config.cacheTTLMs);
    return normalized;
  }

  async fetchGenres(_externalId: string): Promise<string[]> {
    // YouTube doesn't have genre taxonomy
    return [];
  }

  // ── YouTube-Specific Methods ──

  /**
   * Fetch detailed channel analytics (beyond standard metrics).
   */
  async fetchChannelAnalytics(
    externalId: string
  ): Promise<{
    channelAge: number;
    totalViews: number;
    totalVideos: number;
    uploadFrequency: number;
    avgViews: number;
    totalLikes: number;
    totalComments: number;
    hiddenSubscriberCount: boolean;
  } | null> {
    const apiKey = this.getApiKey();
    const result = await this.request<YTChannelResponse>(
      `${YT_API_BASE}/channels?part=statistics,snippet&id=${externalId}&key=${apiKey}`
    );

    if (!result.ok || !result.data?.items?.[0]) return null;

    const item = result.data.items[0];
    const stats = item.statistics;
    const snippet = item.snippet;

    return {
      channelAge: getChannelAge(snippet.publishedAt),
      totalViews: parseNumber(stats.viewCount, 0),
      totalVideos: parseNumber(stats.videoCount, 0),
      uploadFrequency: 0, // computed below
      avgViews: 0,
      totalLikes: 0,
      totalComments: 0,
      hiddenSubscriberCount: stats.hiddenSubscriberCount,
    };
  }

  /**
   * Fetch latest N videos for a channel.
   */
  async fetchLatestVideos(
    externalId: string,
    maxResults = 10
  ): Promise<Array<{
    id: string;
    title: string;
    publishedAt: string;
    views: number;
    likes: number;
    comments: number;
    thumbnailUrl: string | null;
  }>> {
    const apiKey = this.getApiKey();

    // Search for latest videos
    const searchResult = await this.request<YTVideoListResponse>(
      `${YT_API_BASE}/search?part=snippet&channelId=${externalId}&order=date&maxResults=${maxResults}&type=video&key=${apiKey}`
    );

    if (!searchResult.ok || !searchResult.data?.items) return [];

    const videoIds = searchResult.data.items.map(v => v.id).filter(Boolean);
    if (videoIds.length === 0) return [];

    // Fetch statistics
    const statsResult = await this.request<YTVideoListResponse>(
      `${YT_API_BASE}/videos?part=statistics,snippet&id=${videoIds.join(',')}&key=${apiKey}`
    );

    if (!statsResult.ok || !statsResult.data?.items) return [];

    return statsResult.data.items.map(v => ({
      id: v.id,
      title: v.snippet.title,
      publishedAt: v.snippet.publishedAt,
      views: parseNumber(v.statistics?.viewCount, 0),
      likes: parseNumber(v.statistics?.likeCount, 0),
      comments: parseNumber(v.statistics?.commentCount, 0),
      thumbnailUrl: v.snippet.thumbnails?.high?.url ?? v.snippet.thumbnails?.medium?.url ?? null,
    }));
  }

  /**
   * Fetch top N videos by view count.
   */
  async fetchTopVideos(
    externalId: string,
    maxResults = 10
  ): Promise<Array<{
    id: string;
    title: string;
    views: number;
    likes: number;
    comments: number;
    thumbnailUrl: string | null;
  }>> {
    const apiKey = this.getApiKey();

    const searchResult = await this.request<YTVideoListResponse>(
      `${YT_API_BASE}/search?part=snippet&channelId=${externalId}&order=viewCount&maxResults=${maxResults}&type=video&key=${apiKey}`
    );

    if (!searchResult.ok || !searchResult.data?.items) return [];

    const videoIds = searchResult.data.items.map(v => v.id).filter(Boolean);
    if (videoIds.length === 0) return [];

    const statsResult = await this.request<YTVideoListResponse>(
      `${YT_API_BASE}/videos?part=statistics,snippet&id=${videoIds.join(',')}&key=${apiKey}`
    );

    if (!statsResult.ok || !statsResult.data?.items) return [];

    return statsResult.data.items.map(v => ({
      id: v.id,
      title: v.snippet.title,
      views: parseNumber(v.statistics?.viewCount, 0),
      likes: parseNumber(v.statistics?.likeCount, 0),
      comments: parseNumber(v.statistics?.commentCount, 0),
      thumbnailUrl: v.snippet.thumbnails?.high?.url ?? v.snippet.thumbnails?.medium?.url ?? null,
    }));
  }

  async refresh(): Promise<void> {
    if (this.isDisabled()) return;
    this.log('info', 'Refreshing YouTube provider');
    getCacheManager().removeByProvider('youtube');
    await this.initialize();
  }

  async cache(): Promise<{ hits: number; misses: number; size: number }> {
    const stats = getCacheManager().getStats();
    const ytStats = stats.byProvider['youtube'];
    return { hits: ytStats?.hits ?? 0, misses: 0, size: ytStats?.entries ?? 0 };
  }
}

// ── Singleton ──

let instance: YouTubeProvider | null = null;

export function getYouTubeProvider(): YouTubeProvider {
  if (!instance) {
    instance = new YouTubeProvider();
  }
  return instance;
}
