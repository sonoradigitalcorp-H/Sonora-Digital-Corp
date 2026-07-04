// ───────────────────────────────────────────────
// ⚠️ DEPRECATED — Backward Compatibility Shim
// This file re-exports from the new provider system.
// Please import directly from '@/providers/...' in new code.
// ───────────────────────────────────────────────

import type {
  ProviderHealth,
  NormalizedSearchResult,
  NormalizedProfile,
  NormalizedImages,
  NormalizedAlbum,
} from '@/providers/types';
import {
  getSpotifyProvider,
} from '@/providers/spotify/spotify-provider';
import {
  isConfigured,
  validateCredentials,
  getTokenStatus as getAuthTokenStatus,
} from '@/providers/spotify/spotify-auth';

// ── Re-exported Types (kept for backward compatibility) ──

export interface SpotifyArtistData {
  id: string;
  name: string;
  /** ⚠️ Feb 2026: This field is REMOVED from Spotify API responses. Only available for Extended Quota Mode. */
  followers: number;
  /** ⚠️ Feb 2026: This field is REMOVED from Spotify API responses. */
  popularity: number;
  genres: string[];
  imageUrl: string | null;
  spotifyUrl: string;
}

export interface SpotifyTrack {
  id: string;
  name: string;
  popularity: number;
  durationMs: number;
  album: string;
  albumImage: string | null;
  spotifyUrl: string;
}

export interface SpotifyError {
  status: number;
  message: string;
  context: string;
}

export interface BatchResult {
  found: number;
  notFound: number;
  errors: SpotifyError[];
  total: number;
}

// ── Re-exported Functions ──

export function validateSpotifyCredentials(): string | null {
  return validateCredentials();
}

export function isSpotifyConfigured(): boolean {
  return isConfigured();
}

export function getTokenStatus(): { configured: boolean; cached: boolean; expiresAt: number | null } {
  return getAuthTokenStatus();
}

/**
 * Search for an artist on Spotify by name.
 * Uses the new provider system internally.
 */
export async function searchArtist(name: string): Promise<SpotifyArtistData | null> {
  try {
    const provider = getSpotifyProvider();
    const results = await provider.searchArtist(name);

    if (results.length === 0) return null;

    const best = results[0];
    const profile = await provider.fetchProfile(best.externalId);
    const images = await provider.fetchImages(best.externalId);

    // Build backward-compatible response
    return {
      id: best.externalId,
      name: best.name,
      followers: 0, // ⚠️ Removed by Spotify Feb 2026
      popularity: 0, // ⚠️ Removed by Spotify Feb 2026
      genres: profile?.genres ?? best.genres,
      imageUrl: images.large ?? images.medium ?? images.small,
      spotifyUrl: profile?.profileUrl ?? `https://open.spotify.com/artist/${best.externalId}`,
    };
  } catch {
    return null;
  }
}

/**
 * Search multiple artists in batch.
 */
export async function searchArtistsBatch(names: string[]): Promise<Map<string, SpotifyArtistData>> {
  const results = new Map<string, SpotifyArtistData>();

  const batchSize = 3;
  for (let i = 0; i < names.length; i += batchSize) {
    const batch = names.slice(i, i + batchSize);
    const batchResults = await Promise.allSettled(
      batch.map(async (name) => {
        const data = await searchArtist(name);
        return { name, data };
      })
    );

    for (const result of batchResults) {
      if (result.status === 'fulfilled' && result.value.data) {
        results.set(result.value.name, result.value.data);
      }
    }

    if (i + batchSize < names.length) {
      await new Promise(resolve => setTimeout(resolve, 300));
    }
  }

  return results;
}

/**
 * Get full artist details by Spotify ID.
 */
export async function getArtist(spotifyId: string): Promise<SpotifyArtistData | null> {
  try {
    const provider = getSpotifyProvider();
    const profile = await provider.fetchProfile(spotifyId);
    const images = await provider.fetchImages(spotifyId);

    if (!profile) return null;

    return {
      id: spotifyId,
      name: profile.name,
      followers: 0,
      popularity: 0,
      genres: profile.genres,
      imageUrl: images.large ?? images.medium ?? images.small,
      spotifyUrl: profile.profileUrl ?? `https://open.spotify.com/artist/${spotifyId}`,
    };
  } catch {
    return null;
  }
}

/**
 * ⚠️ DEPRECATED — Endpoint removed by Spotify (Feb 2026).
 * Always returns empty array.
 */
export async function getArtistTopTracks(
  _spotifyId: string,
  _market?: string
): Promise<SpotifyTrack[]> {
  console.warn('[Spotify] getArtistTopTracks() called but endpoint was REMOVED in Feb 2026');
  return [];
}
