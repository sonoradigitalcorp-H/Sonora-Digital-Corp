// ───────────────────────────────────────────────
// SIGNAL Intelligence API — GET /api/v1/intelligence/[id]
// The ONLY public interface for intelligence data
// All provider data, features, and scoring are INTERNAL
// ───────────────────────────────────────────────

import { NextRequest, NextResponse } from 'next/server';
import { getFeatureStore } from '@/scoring/feature-store';
import { getEngine } from '@/scoring/score-engine';
import { createDefaultScores } from '@/scoring/scores';
import { getRegistry } from '@/scoring/score-registry';
import { generateInsights, generateSummary } from '@/scoring/insights';
import type { UnifiedArtist } from '@/providers/types';

// ── Generated Artist → UnifiedArtist Converter ──
// Bridges the data generator output into the scoring pipeline

function buildUnifiedArtist(id: string): UnifiedArtist | null {
  // Dynamic import to avoid hard bundling
  // eslint-disable-next-line @typescript-eslint/no-var-requires
  const { generateArtistById } = require('@/lib/data-generator');
  const generated = generateArtistById(id);
  if (!generated) return null;

  // Extract platform info from generated data
  const platformMap: Record<string, string> = {
    spotify: 'https://open.spotify.com/artist/',
    youtube: 'https://www.youtube.com/',
    instagram: 'https://www.instagram.com/',
    tiktok: 'https://www.tiktok.com/',
    appleMusic: 'https://music.apple.com/',
  };

  // Detect social profiles from contact string
  const contact = generated.contact ?? '';
  const socials: UnifiedArtist['socials'] = {
    externalId: id,
    instagram: contact.includes('IG:') || contact.includes('instagram')
      ? 'https://www.instagram.com/' : null,
    tiktok: contact.includes('TikTok') || contact.includes('tiktok')
      ? 'https://www.tiktok.com/' : null,
    twitter: null,
    youtube: contact.includes('youtube') ? 'https://www.youtube.com/' : null,
    spotify: contact.includes('Spotify') ? 'https://open.spotify.com/artist/' : null,
    appleMusic: null,
    provider: 'generated',
  };

  // Detect platforms from generated data
  const generatedPlatforms = Object.keys(generated.platforms ?? {});
  for (const p of generatedPlatforms) {
    if (p === 'spotify') socials.spotify = 'https://open.spotify.com/artist/';
    if (p === 'youtube') socials.youtube = 'https://www.youtube.com/';
    if (p === 'instagram') socials.instagram = 'https://www.instagram.com/';
    if (p === 'tiktok') socials.tiktok = 'https://www.tiktok.com/';
  }

  // Build unified artist
  const unified: UnifiedArtist = {
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
    socials,
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

// ── Route Handler ──

export async function GET(
  _request: NextRequest,
  context: { params: Promise<{ id: string }> }
) {
  const { id } = await context.params;

  // 1. Build the artist from generated data
  const artist = buildUnifiedArtist(id);
  if (!artist) {
    return NextResponse.json(
      { error: 'Artist not found', id },
      { status: 404 }
    );
  }

  // 2. Ingest into Feature Store
  const store = getFeatureStore();
  const featured = await store.ingest(artist);

  // 3. Run Score Engine
  const registry = getRegistry();
  const scores = registry.getAll();
  if (scores.length === 0) {
    // Register default scores on first call
    const defaultScores = createDefaultScores();
    for (const score of defaultScores) {
      registry.register(score);
    }
  }

  const engine = getEngine();
  const engineResult = engine.evaluate(featured.raw);

  // 4. Generate insights
  const insights = generateInsights(featured.raw, engineResult);
  const summary = generateSummary(insights);

  // 5. Build response
  const response = {
    artist: {
      id: artist.id,
      name: artist.name,
      genres: artist.profile.genres,
      country: artist.profile.country,
      image: artist.images.large,
      primaryProvider: artist.primaryProvider,
    },
    scores: engineResult.scores.map((s) => ({
      id: s.id,
      name: s.name,
      category: s.category,
      version: s.version,
      score: s.score,
      confidence: s.confidence,
      summary: s.summary,
      factors: s.factors,
      recommendations: s.recommendations,
      dataQuality: s.dataQuality,
      trend: s.trend,
      volatility: s.volatility,
      valid: s.valid,
      validationMessage: s.validationMessage,
    })),
    aggregate: {
      score: engineResult.aggregateScore,
      confidence: engineResult.aggregateConfidence,
      scoresComputed: engineResult.scoresComputed,
      scoresSkipped: engineResult.scoresSkipped,
    },
    features: {
      platforms: featured.features.map((f) => ({
        name: f.name,
        value: f.value,
        quality: f.quality,
        provider: f.provider,
        source: f.source,
      })),
      summary: engineResult.features,
    },
    insights: {
      items: insights,
      summary,
    },
    metadata: {
      computedAt: engineResult.timestamp,
      version: '3.5.0',
    },
  };

  return NextResponse.json(response, {
    headers: {
      'Cache-Control': 'public, s-maxage=60, stale-while-revalidate=300',
    },
  });
}
