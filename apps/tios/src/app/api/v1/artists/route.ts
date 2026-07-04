import { NextRequest, NextResponse } from 'next/server';
import { generateArtists, generateArtistById } from '@/lib/data-generator';
import { fetchAllArtistImages } from '@/lib/artist-images';

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const genre = searchParams.get('genre') || 'All';
  const count = parseInt(searchParams.get('count') || '10');

  let artists = genre === 'All'
    ? generateArtists(count)
    : generateArtists(count, genre);

  // Always include AMG signed artists (Héctor Rubio & Jesús Urquijo)
  const amgIds = ['art-amg-01', 'art-amg-02'];
  const amgArtists = amgIds.map(id => generateArtistById(id));
  // Remove duplicates if they were randomly selected
  artists = artists.filter(a => !amgIds.includes(a.id));
  // Prepend AMG artists at the top
  artists = [...amgArtists, ...artists];

  // Enrich with real photos from Deezer (async, non-blocking)
  try {
    const names = artists.map(a => a.name);
    const imageMap = await fetchAllArtistImages(names);
    artists = artists.map(a => ({
      ...a,
      photoUrl: imageMap[a.name] || a.photoUrl,
    }));
  } catch {
    // Keep generated photoUrl as fallback
  }

  return NextResponse.json({
    artists,
    total: artists.length,
    signedCount: amgArtists.length,
    genres: ['All', 'Regional Mexicano', 'Corridos Tumbados', 'Corridos Bélicos', 'Norteño', 'Sierreño', 'Latin Trap', 'Reggaeton', 'Latin Urban', 'Latin Pop', 'Hip Hop', 'Rap', 'R&B', 'Indie Pop', 'Latin Alternative', 'Cumbia', 'Tropical', 'Fusión', 'Dembow', 'Latin Drill', 'Experimental', 'Indie Folk', 'Electropop', 'Flamenco', 'Freestyle', 'Drill', 'Producer'],
    updatedAt: new Date().toISOString(),
  });
}
