// ───────────────────────────────────────────────
// SIGNAL Provider System — Public API
// ───────────────────────────────────────────────

// Types & Interfaces
export type {
  DataProvider,
  ProviderConfig,
  ProviderHealth,
  NormalizedSearchResult,
  NormalizedProfile,
  NormalizedMetrics,
  NormalizedImages,
  NormalizedSocials,
  NormalizedLinks,
  NormalizedAlbum,
  UnifiedArtist,
  IntelligenceResult,
  IntelligenceConfig,
  Job,
  JobType,
  JobDefinition,
} from './types';

// Provider Registry
export { ProviderRegistry, getProviderRegistry, registerDefaultProviders } from './registry';

// Intelligence Engine
export { IntelligenceEngine, getIntelligenceEngine } from './intelligence/engine';
export { mergeProfiles, mergeMetrics, mergeImages, mergeAlbums } from './intelligence/merger';

// Spotify Provider
export { SpotifyProvider, getSpotifyProvider } from './spotify/spotify-provider';
export { isConfigured as isSpotifyConfigured, validateCredentials as validateSpotifyCredentials } from './spotify/spotify-auth';

// Deezer Provider
export { DeezerProvider, getDeezerProvider, fetchArtistImageByName, fetchAllArtistImagesByName } from './deezer/deezer-provider';

// Cache
export { CacheManager, getCacheManager } from './cache/cache-manager';

// Jobs
export { JobManager, getJobManager, refreshProvider, refreshCache, invalidateCache, runHealthCheck } from './jobs/job-manager';

// Base
export { BaseProvider, logProvider } from './base-provider';
