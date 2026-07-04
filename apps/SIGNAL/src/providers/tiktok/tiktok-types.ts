// ───────────────────────────────────────────────
// TikTok API Types & Abstraction Layer
// Official APIs only — no scraping
// ───────────────────────────────────────────────

/**
 * TikTok Research API — Available to approved academic/research
 * and business partners. Read-only access to public data.
 * https://developers.tiktok.com/products/research-api/
 */

export interface TikTokResearchUser {
  user_id: string;
  display_name?: string;
  username?: string;
  bio_description?: string;
  avatar_url?: string;
  follower_count?: number;
  following_count?: number;
  likes_count?: number;
  video_count?: number;
  is_verified?: boolean;
  bio_link?: string;
  profile_deep_link?: string;
}

export interface TikTokResearchVideo {
  video_id: string;
  title?: string;
  description?: string;
  create_time?: string;
  like_count?: number;
  comment_count?: number;
  share_count?: number;
  view_count?: number;
  cover_image_url?: string;
  duration?: number;
  music_title?: string;
  music_author?: string;
}

export interface TikTokResearchResponse<T> {
  data?: T;
  error?: {
    code: string;
    message: string;
  };
}

/**
 * TikTok Business API — For official business partners.
 * Provides analytics and advertising data.
 */

export interface TikTokBusinessUser {
  open_id: string;
  username?: string;
  display_name?: string;
  avatar_url?: string;
  follower_count?: number;
  video_count?: number;
  likes_count?: number;
}

export interface TikTokBusinessVideo {
  video_id: string;
  title?: string;
  create_time?: number;
  like_count?: number;
  comment_count?: number;
  share_count?: number;
  view_count?: number;
  cover_image_url?: string;
}

/**
 * Abstract TikTok API Client
 *
 * Uses Research API as primary source,
 * falls back to Business API,
 * gracefully degrades to placeholder if neither available.
 */
export interface TikTokAPIClient {
  name: string;
  available: boolean;
  searchUsers(query: string): Promise<TikTokResearchUser[]>;
  getUser(userId: string): Promise<TikTokResearchUser | null>;
  getUserVideos(userId: string, maxCount: number): Promise<TikTokResearchVideo[]>;
  health(): Promise<{ ok: boolean; message: string }>;
}

/**
 * Placeholder client for when official API access is unavailable.
 */
export class TikTokPlaceholderClient implements TikTokAPIClient {
  name = 'placeholder';
  available = false;

  async searchUsers(_query: string): Promise<TikTokResearchUser[]> {
    return [];
  }

  async getUser(_userId: string): Promise<TikTokResearchUser | null> {
    return null;
  }

  async getUserVideos(_userId: string, _maxCount: number): Promise<TikTokResearchVideo[]> {
    return [];
  }

  async health(): Promise<{ ok: boolean; message: string }> {
    return {
      ok: false,
      message: 'TikTok API not configured. Set TIKTOK_ACCESS_TOKEN for Research API or TIKTOK_BUSINESS_TOKEN for Business API.',
    };
  }
}

/**
 * Research API client — primary implementation.
 */
export class TikTokResearchClient implements TikTokAPIClient {
  name = 'research';
  available = true;
  private baseUrl = 'https://open.tiktokapis.com/v2/research';
  private accessToken: string;

  constructor(accessToken: string) {
    this.accessToken = accessToken;
  }

  private async request<T>(
    endpoint: string,
    params?: Record<string, string>
  ): Promise<T | null> {
    const url = new URL(`${this.baseUrl}${endpoint}`);
    if (params) {
      Object.entries(params).forEach(([k, v]) => url.searchParams.set(k, v));
    }

    try {
      const response = await fetch(url.toString(), {
        headers: {
          Authorization: `Bearer ${this.accessToken}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        console.warn(`[TikTok] Research API: ${response.status} ${response.statusText}`);
        return null;
      }

      const body = await response.json() as TikTokResearchResponse<T>;
      if (body.error) {
        console.warn(`[TikTok] Research API error: ${body.error.code} — ${body.error.message}`);
        return null;
      }

      return body.data ?? null;
    } catch (error) {
      console.error(`[TikTok] Research API request failed:`, error);
      return null;
    }
  }

  async searchUsers(query: string): Promise<TikTokResearchUser[]> {
    const data = await this.request<{ users: TikTokResearchUser[] }>(
      '/user/search/',
      { q: query, max_count: '5' }
    );
    return data?.users ?? [];
  }

  async getUser(userId: string): Promise<TikTokResearchUser | null> {
    const data = await this.request<{ user: TikTokResearchUser }>(
      `/user/info/`,
      { user_id: userId }
    );
    return data?.user ?? null;
  }

  async getUserVideos(userId: string, maxCount: number): Promise<TikTokResearchVideo[]> {
    const data = await this.request<{ videos: TikTokResearchVideo[] }>(
      `/user/videos/`,
      { user_id: userId, max_count: String(Math.min(maxCount, 20)) }
    );
    return data?.videos ?? [];
  }

  async health(): Promise<{ ok: boolean; message: string }> {
    const data = await this.request<{ users: TikTokResearchUser[] }>(
      '/user/search/',
      { q: 'test', max_count: '1' }
    );
    return {
      ok: data !== null,
      message: data !== null ? 'Research API operational' : 'Research API endpoint responded with error',
    };
  }
}

/**
 * Factory: picks the best available client.
 */
export function createTikTokClient(): TikTokAPIClient {
  const researchToken = process.env.TIKTOK_ACCESS_TOKEN || '';
  const businessToken = process.env.TIKTOK_BUSINESS_TOKEN || '';

  if (researchToken) {
    console.log('[TikTok] Using Research API');
    return new TikTokResearchClient(researchToken);
  }

  if (businessToken) {
    console.log('[TikTok] Using Business API (limited Research API alternative)');
    // Business API would be implemented similarly
    // For now, fall through to placeholder
  }

  console.log('[TikTok] No API credentials — using placeholder (see docs/TIKTOK_PROVIDER.md)');
  return new TikTokPlaceholderClient();
}
