// ───────────────────────────────────────────────
// GET /api/v1/artists
// Uses Intelligence Engine + Provider System
// Falls back to generated data for metrics
// ───────────────────────────────────────────────

import { NextRequest, NextResponse } from 'next/server';
import { generateArtists, generateArtistById } from '@/lib/data-generator';
import { getIntelligenceEngine } from '@/providers/intelligence/engine';
import { registerDefaultProviders } from '@/providers/registry';
import { isSpotifyConfigured } from '@/providers/spotify/spotify-auth';
import { fetchAllArtistImagesByName } from '@/providers/deezer/deezer-provider';

// Lazy-init provider system (first call only)
let providersInitialized = false;

async function ensureProviders() {
  if (!providersInitialized) {
    try {
      await registerDefaultProviders();
      providersInitialized = true;
    } catch (error) {
      console.error('[Artists API] Provider init failed:', error);
    }
  }
  return isSpotifyConfigured();
}

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const genre = searchParams.get('genre') || 'All';
  const count = parseInt(searchParams.get('count') || '10');

  // 1. Initialize provider system
  const spotifyAvailable = await ensureProviders();
  const engine = getIntelligenceEngine();

  // 2. Generate base artist data (backbone of metrics)
  let artists = genre === 'All'
    ? generateArtists(count)
    : generateArtists(count, genre);

  // 3. Always include AMG signed artists (Héctor Rubio & Jesús Urquijo)
  const amgIds = ['art-amg-01', 'art-amg-02'];
  const amgArtists = amgIds.map(id => generateArtistById(id));
  artists = artists.filter(a => !amgIds.includes(a.id));

  // 4. Enrich with provider data (Spotify + Deezer via Intelligence Engine)
  if (spotifyAvailable) {
    // Process in parallel batches using the intelligence engine
    const BATCH_SIZE = 5;

    for (let i = 0; i < artists.length; i += BATCH_SIZE) {
      const batch = artists.slice(i, i + BATCH_SIZE);

      const enrichmentResults = await Promise.allSettled(
        batch.map(async (artist) => {
          try {
            // Use Intelligence Engine to search for this artist
            const searchResults = await engine.search(artist.name);
            if (searchResults.length === 0) return null;

            const bestMatch = searchResults[0];

            // Fetch profile for genres
            const provider = bestMatch.provider;
            const extId = bestMatch.externalId;
            const externalIds: Record<string, string> = {};
            if (provider === 'spotify' || provider === 'deezer') {
              externalIds[provider] = extId;
            }

            // Build unified artist result
            const result = await engine.buildArtist(artist.id, artist.name, { externalIds });

            const unified = result.artist;
            return {
              name: artist.name,
              genres: unified.profile.genres.length > 0
                ? unified.profile.genres.slice(0, 3)
                : artist.genres,
              photoUrl: unified.images.large ?? unified.images.medium ?? unified.images.small ?? null,
              spotifyId: externalIds['spotify'] ?? null,
              spotifyUrl: unified.profile.profileUrl ?? null,
              confidence: result.confidence,
            };
          } catch {
            return null;
          }
        })
      );

      // Apply enrichment results
      for (const result of enrichmentResults) {
        if (result.status === 'fulfilled' && result.value) {
          const enrichment = result.value;
          const artistIndex = artists.findIndex(a => a.name === enrichment.name);
          if (artistIndex !== -1) {
            artists[artistIndex] = {
              ...artists[artistIndex],
              // Keep generated score/followers
              // Override genres and photo with provider data
              genres: enrichment.genres,
              photoUrl: enrichment.photoUrl || artists[artistIndex].photoUrl,
              contact: enrichment.spotifyId
                ? `Spotify: open.spotify.com/artist/${enrichment.spotifyId}`
                : artists[artistIndex].contact,
            };
          }
        }
      }
    }
  }

  // 5. Prepend AMG artists at the top
  artists = [...amgArtists, ...artists];

  // 6. Enrich with Deezer photos for artists without Spotify photos
  try {
    const namesNeedingPhotos = artists
      .filter(a => !a.photoUrl || a.photoUrl.includes('ui-avatars.com'))
      .map(a => a.name);

    if (namesNeedingPhotos.length > 0) {
      const imageMap = await fetchAllArtistImagesByName(namesNeedingPhotos);
      artists = artists.map(a => {
        const deezerImage = imageMap.get(a.name);
        if (deezerImage?.large || deezerImage?.medium) {
          return {
            ...a,
            photoUrl: deezerImage.large ?? deezerImage.medium ?? a.photoUrl,
          };
        }
        return a;
      });
    }
  } catch {
    // Keep existing photoUrl as fallback
  }

  return NextResponse.json({
    artists,
    total: artists.length,
    signedCount: amgArtists.length,
    spotifyConnected: spotifyAvailable,
    providerSystem: true,
    genres: ['All', 'Regional Mexicano', 'Corridos Tumbados', 'Corridos Bélicos', 'Norteño', 'Sierreño', 'Latin Trap', 'Reggaeton', 'Latin Urban', 'Latin Pop', 'Hip Hop', 'Rap', 'R&B', 'Indie Pop', 'Latin Alternative', 'Cumbia', 'Tropical', 'Fusión', 'Dembow', 'Latin Drill', 'Experimental', 'Indie Folk', 'Electropop', 'Flamenco', 'Freestyle', 'Drill', 'Producer'],
    updatedAt: new Date().toISOString(),
  });
}
