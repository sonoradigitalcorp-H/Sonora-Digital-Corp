// ───────────────────────────────────────────────
// /api/v1/artists/refresh
// Background job integration for provider cache
// ───────────────────────────────────────────────

import { NextResponse } from 'next/server';
import { ARTIST_POOL } from '@/lib/data-generator';
import { isSpotifyConfigured, validateSpotifyCredentials } from '@/providers/spotify/spotify-auth';
import { getSpotifyProvider } from '@/providers/spotify/spotify-provider';
import { getCacheManager } from '@/providers/cache/cache-manager';
import { getJobManager, refreshProvider, invalidateCache } from '@/providers/jobs/job-manager';

/**
 * POST /api/v1/artists/refresh
 * Triggers a background refresh of all provider caches.
 * Returns immediately with job ID.
 */
export async function POST() {
  if (!isSpotifyConfigured()) {
    return NextResponse.json({
      success: false,
      error: 'Spotify API not configured. Set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET.',
      cacheStats: getCacheManager().getStats(),
    }, { status: 400 });
  }

  // Submit a background refresh job
  const jobId = refreshProvider('spotify');

  // Also invalidate cache for next read
  invalidateCache();

  // Extract unique artist names from the pool
  const artistNames = ARTIST_POOL
    .filter(a => a.id !== 'art-amg-01' && a.id !== 'art-amg-02')
    .map(a => a.name)
    .filter((name, i, arr) => arr.indexOf(name) === i);

  // Return immediately with job info
  return NextResponse.json({
    success: true,
    message: `Provider refresh triggered in background. Job: ${jobId}`,
    jobId,
    cacheStats: getCacheManager().getStats(),
    artistCount: artistNames.length,
    note: 'New data will be available on next GET /api/v1/artists call',
  });
}

/**
 * GET /api/v1/artists/refresh
 * Returns cache status, provider health, and configuration info.
 */
export async function GET() {
  const configured = isSpotifyConfigured();
  const validationError = configured ? null : validateSpotifyCredentials();

  // Get provider health
  const spotifyProvider = getSpotifyProvider();

  let providerHealth = null;
  try {
    providerHealth = await spotifyProvider.health();
  } catch {
    providerHealth = null;
  }

  // Get recent jobs
  const recentJobs = getJobManager().recent(5);

  return NextResponse.json({
    configured,
    validationError,
    providerHealth,
    cacheStats: getCacheManager().getStats(),
    providerSystemVersion: '3.0',
    recentJobs: recentJobs.map(j => ({
      id: j.id,
      type: j.type,
      status: j.status,
      createdAt: j.createdAt,
      error: j.error,
    })),
    setupInstructions: configured
      ? 'Spotify API is configured and ready.'
      : 'Create a Spotify App at https://developer.spotify.com/dashboard/ and set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET in .env',
  });
}
