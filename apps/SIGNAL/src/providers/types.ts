// ───────────────────────────────────────────────
// SIGNAL Provider System — Core Types & Schemas
// Enterprise-grade provider abstraction layer
// ───────────────────────────────────────────────

// ── Provider Health ──

export interface ProviderHealth {
  /** Provider name */
  name: string;
  /** Whether the provider is operational */
  status: 'healthy' | 'degraded' | 'unhealthy';
  /** Human-readable status message */
  message: string;
  /** Latency of last health check in ms */
  latencyMs: number;
  /** ISO timestamp of last check */
  lastChecked: string;
  /** Whether credentials are configured */
  configured: boolean;
  /** Configuration error if any */
  configurationError: string | null;
}

// ── Provider Configuration ──

export interface ProviderConfig {
  /** Unique provider name */
  name: string;
  /** Whether the provider is enabled */
  enabled: boolean;
  /** Request timeout in ms */
  timeoutMs: number;
  /** Min interval between requests for rate limiting (ms) */
  rateLimitIntervalMs: number;
  /** Max retries on failure */
  maxRetries: number;
  /** Retry backoff base in ms */
  retryBaseDelayMs: number;
  /** Health check interval in ms */
  healthCheckIntervalMs: number;
  /** Cache TTL in ms */
  cacheTTLMs: number;
}

// ── DataProvider Interface ──
// Every data source in SIGNAL must implement this contract.

export interface DataProvider {
  /** Unique provider identifier */
  readonly name: string;

  /** Initialize the provider (auth, connection pool, etc.) */
  initialize(): Promise<void>;

  /** Returns current provider health status */
  health(): Promise<ProviderHealth>;

  /**
   * Search for an artist by name.
   * Returns normalized search results or empty array.
   */
  searchArtist(query: string): Promise<NormalizedSearchResult[]>;

  /**
   * Fetch full artist profile from this provider.
   * Returns null if not found.
   */
  fetchProfile(externalId: string): Promise<Partial<NormalizedProfile> | null>;

  /**
   * Fetch metrics/fan data for an artist.
   * Returns null if not available.
   */
  fetchMetrics(externalId: string): Promise<Partial<NormalizedMetrics> | null>;

  /**
   * Fetch images for an artist at various sizes.
   * Returns empty object if not available.
   */
  fetchImages(externalId: string): Promise<Partial<NormalizedImages>>;

  /**
   * Fetch genres for an artist.
   * Returns empty array if not available.
   */
  fetchGenres(externalId: string): Promise<string[]>;

  /**
   * Fetch albums/discography for an artist.
   * Returns empty array if not available.
   */
  fetchAlbums?(externalId: string): Promise<NormalizedAlbum[]>;

  /**
   * Refresh any cached provider data.
   */
  refresh?(): Promise<void>;

  /**
   * Get cache statistics for this provider.
   */
  cache?(): Promise<{ hits: number; misses: number; size: number }>;
}

// ── Normalization Schemas ──
// Every provider must return data mapped into one of these schemas.
// The Intelligence Engine assembles them into a unified Artist.

/** Core profile — identity data every artist has */
export interface NormalizedProfile {
  /** Provider-specific ID */
  externalId: string;
  /** Artist name */
  name: string;
  /** Biography / description */
  bio: string | null;
  /** Primary genres (top 3-5) */
  genres: string[];
  /** Country of origin */
  country: string | null;
  /** City of origin */
  city: string | null;
  /** URL to profile on this platform */
  profileUrl: string | null;
  /** Provider name */
  provider: string;
}

/** Metrics / audience data */
export interface NormalizedMetrics {
  /** Provider-specific ID */
  externalId: string;
  /** Monthly listeners (Spotify) or equivalent */
  monthlyListeners: number | null;
  /** Follower count */
  followers: number | null;
  /** Engagement rate 0-100 */
  engagement: number | null;
  /** Growth rate % over 30 days */
  growth: number | null;
  /** Momentum score 0-100 */
  momentum: number | null;
  /** Provider name */
  provider: string;
}

/** Images at standard sizes */
export interface NormalizedImages {
  /** Provider-specific ID */
  externalId: string;
  /** Small image URL (≤ 160px) */
  small: string | null;
  /** Medium image URL (320px) */
  medium: string | null;
  /** Large image URL (640px) */
  large: string | null;
  /** Provider name */
  provider: string;
}

/** Social media links */
export interface NormalizedSocials {
  /** Provider-specific ID */
  externalId: string;
  instagram: string | null;
  tiktok: string | null;
  twitter: string | null;
  youtube: string | null;
  spotify: string | null;
  appleMusic: string | null;
  /** Provider name */
  provider: string;
}

/** External platform links */
export interface NormalizedLinks {
  /** Provider-specific ID */
  externalId: string;
  deezer: string | null;
  soundcloud: string | null;
  bandcamp: string | null;
  website: string | null;
  /** Provider name */
  provider: string;
}

/** Album / discography entry */
export interface NormalizedAlbum {
  /** Provider-specific album ID */
  externalId: string;
  title: string;
  releaseDate: string | null;
  imageUrl: string | null;
  trackCount: number | null;
  albumType: 'album' | 'single' | 'compilation' | 'unknown';
  /** Provider name */
  provider: string;
}

/** Search result — lightweight artist match */
export interface NormalizedSearchResult {
  /** Provider-specific ID */
  externalId: string;
  name: string;
  genres: string[];
  imageUrl: string | null;
  matchScore: number;
  /** Provider name */
  provider: string;
}

// ── Intelligence Engine Types ──

export interface IntelligenceConfig {
  /** Minimum number of providers needed for a high-confidence result */
  minProvidersForHighConfidence: number;
  /** Whether to allow partial results (some providers failed) */
  allowPartialResults: boolean;
  /** Score sources in priority order */
  scorePriority: ScoreSource[];
}

export type ScoreSource = 'spotify' | 'generated' | 'average';

export interface IntelligenceResult {
  /** The unified artist object */
  artist: UnifiedArtist;
  /** Sources that contributed data */
  sources: string[];
  /** Confidence level */
  confidence: 'high' | 'medium' | 'low';
  /** Any errors encountered during merging */
  errors: IntelligenceError[];
  /** Merge timestamp */
  mergedAt: string;
}

export interface IntelligenceError {
  provider: string;
  error: string;
  recoverable: boolean;
}

// ── Unified Artist (Intelligence Engine Output) ──

export interface UnifiedArtist {
  id: string;
  name: string;
  profile: NormalizedProfile;
  metrics: NormalizedMetrics;
  images: NormalizedImages;
  socials: NormalizedSocials;
  links: NormalizedLinks;
  albums: NormalizedAlbum[];
  /** Provider that was the primary source for the name */
  primaryProvider: string;
}

// ── Background Jobs ──

export type JobStatus = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';

export interface Job {
  id: string;
  type: JobType;
  status: JobStatus;
  progress: number;
  createdAt: string;
  startedAt: string | null;
  completedAt: string | null;
  error: string | null;
  result: unknown;
}

export type JobType =
  | 'refresh-provider'
  | 'refresh-cache'
  | 'invalidate-cache'
  | 'health-check';

export interface JobDefinition {
  type: JobType;
  providerName?: string;
  payload?: Record<string, unknown>;
}
