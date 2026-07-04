import { NextResponse } from 'next/server';
import { ARTIST_POOL } from '@/lib/data-generator';
import { searchArtistsBatch, isSpotifyConfigured } from '@/lib/spotify-service';
import { setCachedArtists, getCachedArtist, clearCache, getCacheStats } from '@/lib/artist-cache';

/**
 * POST /api/v1/artists/refresh
 * Triggers a full refresh of the Spotify artist cache.
 * Rate-limited: max once per 60 seconds.
 */
export async function POST() {
  if (!isSpotifyConfigured()) {
    return NextResponse.json({
      success: false,
      error: 'Spotify API not configured. Set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET.',
      stats: getCacheStats(),
    }, { status: 400 });
  }

  // Extract unique artist names from the pool (excluding AMG which are frozen)
  const artistNames = ARTIST_POOL
    .filter(a => a.id !== 'art-amg-01' && a.id !== 'art-amg-02')
    .map(a => a.name)
    .filter((name, i, arr) => arr.indexOf(name) === i); // deduplicate

  // First pass: check cache for fresh entries
  const namesToRefresh: string[] = [];
  for (const name of artistNames) {
    const cached = getCachedArtist(name);
    if (!cached) {
      namesToRefresh.push(name);
    }
    // Always refresh if not cached; if cached but old, still refresh
  }

  if (namesToRefresh.length === 0) {
    return NextResponse.json({
      success: true,
      message: 'All artists already cached. Use ?force=true to re-fetch all.',
      stats: getCacheStats(),
      refreshed: 0,
    });
  }

  // Batch search Spotify
  const spotifyResults = await searchArtistsBatch(namesToRefresh);

  // Store in cache
  let found = 0;
  let notFound = 0;
  const cacheEntries: Array<{ name: string; data: any }> = [];

  for (const name of namesToRefresh) {
    const data = spotifyResults.get(name);
    cacheEntries.push({ name, data: data ?? null });
    if (data) found++;
    else notFound++;
  }

  setCachedArtists(cacheEntries);

  return NextResponse.json({
    success: true,
    message: `Spotify cache refreshed: ${found} found, ${notFound} not found on Spotify.`,
    stats: getCacheStats(),
    refreshed: namesToRefresh.length,
    found,
    notFound,
  });
}

/**
 * GET /api/v1/artists/refresh
 * Returns cache status and configuration info.
 */
export async function GET() {
  return NextResponse.json({
    configured: isSpotifyConfigured(),
    cacheStats: getCacheStats(),
    spotifyDocs: 'https://developer.spotify.com/dashboard/',
    setupInstructions: isSpotifyConfigured()
      ? 'Spotify API is configured and ready.'
      : 'Create a Spotify App at https://developer.spotify.com/dashboard/ and set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET in .env',
  });
}
