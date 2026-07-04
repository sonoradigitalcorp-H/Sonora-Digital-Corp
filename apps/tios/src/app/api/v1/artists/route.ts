import { NextRequest, NextResponse } from 'next/server';
import { generateArtists, generateArtistById } from '@/lib/data-generator';
import { fetchAllArtistImages } from '@/lib/artist-images';
import { searchArtist, isSpotifyConfigured, validateSpotifyCredentials } from '@/lib/spotify-service';
import { getCachedArtist, setCachedArtist, isFresh } from '@/lib/artist-cache';

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const genre = searchParams.get('genre') || 'All';
  const count = parseInt(searchParams.get('count') || '10');

  // 1. Generate base artist data (seeded random fallback)
  let artists = genre === 'All'
    ? generateArtists(count)
    : generateArtists(count, genre);

  // 2. Always include AMG signed artists (Héctor Rubio & Jesús Urquijo)
  const amgIds = ['art-amg-01', 'art-amg-02'];
  const amgArtists = amgIds.map(id => generateArtistById(id));
  artists = artists.filter(a => !amgIds.includes(a.id));

  // 3. Try to enrich with real Spotify data (if configured)
  const spotifyAvailable = isSpotifyConfigured();

  if (spotifyAvailable) {
    // Collect names that need Spotify lookup (not in cache or stale)
    const namesToRefresh: string[] = [];
    const spotifyOverrides = new Map<string, { genres: string[]; photoUrl: string | null; spotifyId: string }>();

    for (const artist of artists) {
      const cached = getCachedArtist(artist.name);
      if (cached && isFresh(cached) && cached.spotify) {
        // Use cached Spotify data (followers/popularity no longer available since Feb 2026)
        spotifyOverrides.set(artist.name, {
          genres: cached.spotify.genres,
          photoUrl: cached.spotify.imageUrl,
          spotifyId: cached.spotify.id,
        });
      } else if (!cached || !isFresh(cached)) {
        namesToRefresh.push(artist.name);
      }
    }

    // Fetch missing data from Spotify (background, non-blocking per artist)
    if (namesToRefresh.length > 0) {
      // Process in small batches to avoid overwhelming the API
      const batchSize = 5;
      for (let i = 0; i < namesToRefresh.length; i += batchSize) {
        const batch = namesToRefresh.slice(i, i + batchSize);
        const results = await Promise.allSettled(
          batch.map(async (name) => {
            const spotifyData = await searchArtist(name);
            if (spotifyData) {
              setCachedArtist(name, spotifyData);
              return { name, data: spotifyData };
            } else {
              // Mark as not found on Spotify to avoid repeated lookups
              setCachedArtist(name, null);
              return null;
            }
          })
        );

        // Apply results (followers/popularity no longer available from Spotify since Feb 2026)
        for (const result of results) {
          if (result.status === 'fulfilled' && result.value) {
            const { name, data } = result.value;
            spotifyOverrides.set(name, {
              genres: data.genres,
              photoUrl: data.imageUrl,
              spotifyId: data.id,
            });
          }
        }
      }
    }

    // Apply Spotify overrides to generated artists
    // ⚠️ Since Feb 2026: popularity and followers fields REMOVED by Spotify.
    // Score/followers come from generated data; Spotify used for genres, image, contact.
    if (spotifyOverrides.size > 0) {
      artists = artists.map(artist => {
        const override = spotifyOverrides.get(artist.name);
        if (!override) return artist;

        return {
          ...artist,
          // Keep generated score (popularity no longer available from Spotify)
          // Keep generated followers (followers no longer available from Spotify)
          // Use Spotify genres if available
          genres: override.genres.length > 0 ? override.genres.slice(0, 3) : artist.genres,
          photoUrl: override.photoUrl || artist.photoUrl,
          contact: artist.contact || `Spotify: open.spotify.com/artist/${override.spotifyId}`,
        };
      });
    }
  }

  // 4. Prepend AMG artists at the top
  artists = [...amgArtists, ...artists];

  // 5. Enrich with real photos from Deezer (async, non-blocking — for artists Spotify didn't have)
  try {
    const names = artists.map(a => a.name);
    const imageMap = await fetchAllArtistImages(names);
    artists = artists.map(a => ({
      ...a,
      photoUrl: imageMap[a.name] || a.photoUrl,
    }));
  } catch {
    // Keep existing photoUrl as fallback
  }

  return NextResponse.json({
    artists,
    total: artists.length,
    signedCount: amgArtists.length,
    spotifyConnected: spotifyAvailable,
    genres: ['All', 'Regional Mexicano', 'Corridos Tumbados', 'Corridos Bélicos', 'Norteño', 'Sierreño', 'Latin Trap', 'Reggaeton', 'Latin Urban', 'Latin Pop', 'Hip Hop', 'Rap', 'R&B', 'Indie Pop', 'Latin Alternative', 'Cumbia', 'Tropical', 'Fusión', 'Dembow', 'Latin Drill', 'Experimental', 'Indie Folk', 'Electropop', 'Flamenco', 'Freestyle', 'Drill', 'Producer'],
    updatedAt: new Date().toISOString(),
  });
}
