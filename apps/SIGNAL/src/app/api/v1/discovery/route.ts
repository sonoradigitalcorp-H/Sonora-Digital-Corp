import { NextRequest, NextResponse } from 'next/server';
import { generateDiscoveryResults } from '@/lib/data-generator';
import { fetchAllArtistImages } from '@/lib/artist-images';

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const query = searchParams.get('q') || '';
  const genre = searchParams.get('genre') || 'all';

  let results = generateDiscoveryResults(query, genre, 12);

  // Enrich with real photos from Deezer
  try {
    const names = results.map((a: any) => a.name);
    const imageMap = await fetchAllArtistImages(names);
    results = results.map((a: any) => ({
      ...a,
      photoUrl: imageMap[a.name] || a.photoUrl,
    }));
  } catch {
    // Keep default photoUrl
  }

  return NextResponse.json({
    results,
    total: results.length,
    sources: ['Spotify Algorithm', 'TikTok Trending', 'Billboard Radar', 'YouTube Discovery', 'Chartmetric Alert', 'Instagram Viral'],
    genres: ['All', 'Regional Mexicano', 'Corridos Tumbados', 'Corridos Bélicos', 'Norteño', 'Sierreño', 'Latin Trap', 'Reggaeton', 'Latin Urban', 'Latin Pop', 'Hip Hop', 'Rap', 'R&B', 'Indie Pop', 'Latin Alternative', 'Cumbia', 'Tropical', 'Fusión', 'Dembow', 'Latin Drill', 'Experimental', 'Indie Folk', 'Electropop'],
    query,
    genre,
    discovered24h: results.length,
    updatedAt: new Date().toISOString(),
  });
}
