// ───────────────────────────────────────────────
// SIGNAL Score Engine — Feature Extractor
// Transforms UnifiedArtist → normalized ArtistFeatures
// Scores NEVER read providers directly.
// ───────────────────────────────────────────────

import type { UnifiedArtist } from '@/providers/types';
import type { ArtistFeatures } from './types';

/**
 * Extract normalized features from a UnifiedArtist.
 * This is the ONLY bridge between provider data and the scoring system.
 * All scores consume these features — never raw provider data.
 */
export function extractFeatures(artist: UnifiedArtist): ArtistFeatures {
  const { profile, metrics, socials, links, albums } = artist;

  // ── Platform detection ──
  const platforms: string[] = [];
  if (socials?.spotify) platforms.push('spotify');
  if (socials?.youtube) platforms.push('youtube');
  if (socials?.instagram) platforms.push('instagram');
  if (socials?.tiktok) platforms.push('tiktok');
  if (socials?.appleMusic) platforms.push('appleMusic');
  if (links?.deezer) platforms.push('deezer');
  if (links?.soundcloud) platforms.push('soundcloud');
  if (links?.bandcamp) platforms.push('bandcamp');
  // Deduplicate
  const uniquePlatforms = [...new Set(platforms)];

  // ── Genre detection ──
  const genres = profile?.genres ?? [];
  const primaryGenre = genres.length > 0 ? genres[0] : 'unknown';

  // ── Metrics ──
  const followers = metrics?.followers ?? 0;
  const monthlyListeners = metrics?.monthlyListeners ?? 0;
  const engagementRate = metrics?.engagement ?? 0;
  const followerGrowth = metrics?.growth ?? 0;

  // ── Album stats ──
  const albumList = albums ?? [];
  const albumCount = albumList.length;
  const recentReleaseCount = albumList.filter((a) => {
    if (!a.releaseDate) return false;
    const releaseDate = new Date(a.releaseDate);
    const oneYearAgo = new Date();
    oneYearAgo.setFullYear(oneYearAgo.getFullYear() - 1);
    return releaseDate >= oneYearAgo;
  }).length;

  // ── Social / Link presence ──
  const hasWebsite = !!links?.website;
  const hasMerch = !!links?.bandcamp; // bandcamp implies merch capability
  const verificationStatus = false; // Not currently tracked in normalized data

  // ── Cross-platform presence (0-5) ──
  const majorPlatforms = ['spotify', 'youtube', 'instagram', 'tiktok', 'appleMusic'];
  const crossPlatformPresence = majorPlatforms.filter((p) =>
    uniquePlatforms.includes(p)
  ).length;

  // ── Market detection ──
  const markets: string[] = [];
  if (profile?.country) markets.push(profile.country);
  if (profile?.city) markets.push(`${profile.city}, ${profile.country ?? 'unknown'}`);

  return {
    name: profile?.name ?? artist.name,
    genre: primaryGenre,
    genres,
    platforms: uniquePlatforms,
    followers,
    followerGrowth,
    monthlyListeners,
    monthlyListenerGrowth: 0, // Not tracked in current metrics schema
    engagementRate,
    postingFrequency: 0, // Not available from normalized data
    videoUploadFrequency: 0, // YouTube-specific, not in normalized
    avgViews: 0,
    avgViewGrowth: 0,
    subscriberCount: 0,
    totalViews: 0,
    channelAge: 0,
    albumCount,
    recentReleaseCount,
    hasWebsite,
    hasMerch,
    hasTouringHistory: false, // Not tracked
    crossPlatformPresence,
    genreTrendAlignment: 50, // Neutral default — would come from trend analysis
    verificationStatus,
    primaryLanguage: 'en', // Default — would come from profile
    markets,
  };
}

/**
 * Apply default values for features that have zero/null.
 * This prevents division by zero and scoring anomalies.
 */
export function normalizeFeatures(features: ArtistFeatures): ArtistFeatures {
  return {
    ...features,
    followers: Math.max(0, features.followers),
    followerGrowth: Math.max(-100, Math.min(1000, features.followerGrowth)),
    monthlyListeners: Math.max(0, features.monthlyListeners),
    monthlyListenerGrowth: Math.max(-100, Math.min(1000, features.monthlyListenerGrowth)),
    engagementRate: Math.max(0, Math.min(100, features.engagementRate)),
    postingFrequency: Math.max(0, features.postingFrequency),
    videoUploadFrequency: Math.max(0, features.videoUploadFrequency),
    avgViews: Math.max(0, features.avgViews),
    avgViewGrowth: Math.max(-100, Math.min(1000, features.avgViewGrowth)),
    subscriberCount: Math.max(0, features.subscriberCount),
    totalViews: Math.max(0, features.totalViews),
    channelAge: Math.max(0, features.channelAge),
    albumCount: Math.max(0, features.albumCount),
    recentReleaseCount: Math.max(0, features.recentReleaseCount),
    crossPlatformPresence: Math.max(0, Math.min(5, features.crossPlatformPresence)),
    genreTrendAlignment: Math.max(0, Math.min(100, features.genreTrendAlignment)),
  };
}
