// ───────────────────────────────────────────────
// SIGNAL Score Engine — Core Types
// Proprietary Intelligence Scoring System
// ───────────────────────────────────────────────

// ── Score Identity ──

export type ScoreCategory =
  | 'growth'
  | 'audience'
  | 'commercial'
  | 'discovery'
  | 'performance';

export interface ScoreIdentity {
  readonly id: string;
  readonly version: string;
  readonly name: string;
  readonly description: string;
  readonly category: ScoreCategory;
}

// ── Artist Features (Normalized Input) ──
// Scores NEVER read providers directly.
// They ONLY consume normalized features extracted from UnifiedArtist.

export interface ArtistFeatures {
  name: string;
  genre: string;
  genres: string[];
  /** Platform names where data exists */
  platforms: string[];
  /** Total followers across all platforms */
  followers: number;
  /** Follower growth rate % over 30 days */
  followerGrowth: number;
  /** Monthly listeners (Spotify) */
  monthlyListeners: number;
  /** Monthly listener growth % */
  monthlyListenerGrowth: number;
  /** Engagement rate 0-100 */
  engagementRate: number;
  /** Posts per week average */
  postingFrequency: number;
  /** Videos uploaded per year */
  videoUploadFrequency: number;
  /** Average views per video */
  avgViews: number;
  /** Average view growth % */
  avgViewGrowth: number;
  /** Subscriber count (YouTube) */
  subscriberCount: number;
  /** Total view count (YouTube) */
  totalViews: number;
  /** Channel age in years */
  channelAge: number;
  /** Total album/single count */
  albumCount: number;
  /** Releases in last 12 months */
  recentReleaseCount: number;
  /** Whether artist has an official website */
  hasWebsite: boolean;
  /** Whether artist sells merchandise */
  hasMerch: boolean;
  /** Whether artist has touring history */
  hasTouringHistory: boolean;
  /** Number of platforms with active presence (0-5) */
  crossPlatformPresence: number;
  /** How aligned the artist's genre is with current trends 0-100 */
  genreTrendAlignment: number;
  /** Whether the artist is verified on any platform */
  verificationStatus: boolean;
  /** Primary content language */
  primaryLanguage: string;
  /** Geographic markets present */
  markets: string[];
}

// ── Weight Configuration ──

export interface WeightConfig {
  /** Default weights for named inputs (lowercase, kebab-case) */
  global: Record<string, number>;
  /** Per-provider weight multipliers */
  providers: Record<string, number>;
  /** Per-market weight multipliers */
  markets: Record<string, number>;
  /** Per-genre weight multipliers */
  genres: Record<string, number>;
}

export type WeightOverrides = Partial<WeightConfig>;

// ── Score Result ──

export interface ContributingFactor {
  /** Factor name (human-readable) */
  name: string;
  /** Raw value of this factor */
  value: number;
  /** Net impact on final score (-100 to +100) */
  impact: number;
  /** Weight applied to this factor (0-1) */
  weight: number;
  /** Whether this helped or hurt */
  direction: 'positive' | 'negative';
  /** Human-readable explanation */
  reasoning: string;
}

export interface ScoreResult {
  /** Final score 0-100 */
  score: number;
  /** Confidence 0-100 */
  confidence: number;
  /** ISO timestamp */
  timestamp: string;
  /** All contributing factors with impacts */
  factors: ContributingFactor[];
  /** Actionable recommendations */
  recommendations: string[];
  /** Free-form metadata for debugging/extensibility */
  metadata: Record<string, unknown>;
}

export interface ScoreReasoning {
  /** One-line summary */
  summary: string;
  /** Contributing factors breakdown */
  factors: ContributingFactor[];
  /** Actionable recommendations */
  recommendations: string[];
  /** Data quality assessment */
  dataQuality: string;
}

// ── Input Specification ──

export interface ScoreInputSpec {
  /** Feature names required for calculation */
  required: string[];
  /** Feature names that improve accuracy but aren't required */
  optional: string[];
  /** Minimum confidence threshold to return a valid score */
  minimumConfidence: number;
  /** Default weight values for each input */
  defaultWeights: Record<string, number>;
}

// ── Validation ──

export interface ValidationResult {
  /** Whether the score can be calculated */
  valid: boolean;
  /** Required features missing from input */
  missingRequired: string[];
  /** Optional features missing from input */
  missingOptional: string[];
  /** Whether confidence will be below threshold */
  confidenceWarning: boolean;
  /** Human-readable validation message */
  message: string;
}

// ── Score History ──

export type TrendDirection = 'up' | 'down' | 'stable';

export interface ScoreHistoryEntry {
  /** Score value at this point */
  score: number;
  /** Confidence at this point */
  confidence: number;
  /** ISO timestamp */
  timestamp: string;
  /** Trend direction vs previous */
  trend: TrendDirection;
  /** Absolute change from previous */
  change: number;
  /** Reason for the change */
  reason: string;
  /** Factors at this point */
  factors: ContributingFactor[];
}

export interface ScoreHistory {
  /** Daily snapshots (last 30 days) */
  daily: ScoreHistoryEntry[];
  /** Weekly aggregates (last 12 weeks) */
  weekly: ScoreHistoryEntry[];
  /** Monthly aggregates (last 12 months) */
  monthly: ScoreHistoryEntry[];
  /** Overall trend */
  trend: TrendDirection;
  /** Volatility score 0-100 (how much the score fluctuates) */
  volatility: number;
}

// ── Registry Types ──

export interface ScoreRegistration {
  identity: ScoreIdentity;
  enabled: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface ScoreRegistryState {
  scores: Map<string, ScoreRegistration>;
  version: string;
}
