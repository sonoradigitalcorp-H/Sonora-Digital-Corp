// ───────────────────────────────────────────────
// SIGNAL Intelligence API — GET /api/v1/intelligence/search?q=...
// Search artists by name, genre, city, or country
// Returns lightweight artist cards with optional cached scores
// ───────────────────────────────────────────────

import { NextRequest, NextResponse } from 'next/server';
import { getFeatureStore } from '@/scoring/feature-store';
import { getEngine } from '@/scoring/score-engine';
import { createDefaultScores } from '@/scoring/scores';
import { getRegistry } from '@/scoring/score-registry';
import { generateInsights, generateSummary } from '@/scoring/insights';

// ── Helpers ──

function buildUnifiedArtist(id: string): import('@/providers/types').UnifiedArtist | null {
  // eslint-disable-next-line @typescript-eslint/no-var-requires
  const { generateArtistById, ARTIST_POOL } = require('@/lib/data-generator');
  const poolEntry = ARTIST_POOL.find((a: { id: string }) => a.id === id);
  if (!poolEntry) return null;

  const generated = generateArtistById(id);
  if (!generated) return null;

  const unified: import('@/providers/types').UnifiedArtist = {
    id: generated.id,
    name: generated.name,
    profile: {
      externalId: id,
      name: generated.name,
      bio: generated.reason ?? null,
      genres: generated.genres ?? [],
      country: generated.country ?? null,
      city: generated.city ?? null,
      profileUrl: null,
      provider: 'generated',
    },
    metrics: {
      externalId: id,
      monthlyListeners: generated.listeners ?? null,
      followers: generated.followers ?? null,
      engagement: generated.engagement ?? null,
      growth: generated.growth ?? null,
      momentum: generated.momentum ?? null,
      provider: 'generated',
    },
    images: {
      externalId: id,
      small: generated.photoUrl ?? null,
      medium: generated.photoUrl ?? null,
      large: generated.photoUrl ?? null,
      provider: 'generated',
    },
    socials: {
      externalId: id,
      instagram: null,
      tiktok: null,
      twitter: null,
      youtube: null,
      spotify: null,
      appleMusic: null,
      provider: 'generated',
    },
    links: {
      externalId: id,
      deezer: null,
      soundcloud: null,
      bandcamp: null,
      website: null,
      provider: 'merged',
    },
    albums: [],
    primaryProvider: 'generated',
  };

  return unified;
}

function computeCachedScore(artistId: string): { score: number; confidence: number; scoresComputed: number } | null {
  const store = getFeatureStore();
  const featured = store.get(artistId);
  if (!featured) return null;

  // Scores are computed during intelligence/[id] calls and cached in the score registry
  const engine = getEngine();
  // We can't re-evaluate without the UnifiedArtist, so return the last known aggregate
  // from the registry's score history if available
  return null; // Full scoring requires a fresh /intelligence/[id] call
}

// ── Route Handler ──

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const query = searchParams.get('q')?.trim().toLowerCase();
  const limit = Math.min(Math.max(1, parseInt(searchParams.get('limit') ?? '20', 10) || 20), 50);

  if (!query || query.length < 2) {
    return NextResponse.json(
      { error: 'Query parameter "q" is required (min 2 characters)', results: [] },
      { status: 400 }
    );
  }

  // eslint-disable-next-line @typescript-eslint/no-var-requires
  const { ARTIST_POOL } = require('@/lib/data-generator');

  // Search across name, genres, city, country
  const results = ARTIST_POOL
    .filter((artist: { id: string; name: string; genres: string[]; city: string; country: string }) => {
      const name = artist.name.toLowerCase();
      const genres = artist.genres.map(g => g.toLowerCase());
      const city = (artist.city ?? '').toLowerCase();
      const country = (artist.country ?? '').toLowerCase();

      return (
        name.includes(query) ||
        genres.some(g => g.includes(query)) ||
        city.includes(query) ||
        country.includes(query)
      );
    })
    .slice(0, limit)
    .map((artist: { id: string; name: string; genres: string[]; city: string; country: string; image: string }) => {
      // Check if this artist has been scored (cached in feature store)
      const store = getFeatureStore();
      const featured = store.get(artist.id);
      const registry = getRegistry();

      return {
        id: artist.id,
        name: artist.name,
        genres: artist.genres,
        city: artist.city ?? null,
        country: artist.country ?? null,
        image: artist.image ?? null,
        hasIntelligence: !!featured,
        scoresRegistered: registry.size,
      };
    });

  return NextResponse.json({
    query,
    count: results.length,
    results,
    metadata: {
      version: '3.5.0',
      computedAt: new Date().toISOString(),
    },
  });
}
