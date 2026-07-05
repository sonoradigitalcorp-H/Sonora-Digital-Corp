// ───────────────────────────────────────────────
// SIGNAL Intelligence API — GET /api/v1/intelligence/[id]/history
// Returns historical score trending for a scored artist
// Includes daily, weekly, monthly aggregates per score
// ───────────────────────────────────────────────

import { NextRequest, NextResponse } from 'next/server';
import { getRegistry } from '@/scoring/score-registry';
import { getHistoryManager } from '@/scoring/score-history';
import { getFeatureStore } from '@/scoring/feature-store';

// ── Helpers ──

function buildArtistName(id: string): string | null {
  // eslint-disable-next-line @typescript-eslint/no-var-requires
  const { generateArtistById } = require('@/lib/data-generator');
  const generated = generateArtistById(id);
  return generated?.name ?? null;
}

// ── Route Handler ──

export async function GET(
  _request: NextRequest,
  context: { params: Promise<{ id: string }> }
) {
  const { id } = await context.params;

  // 1. Check if artist exists
  const artistName = buildArtistName(id);
  if (!artistName) {
    return NextResponse.json(
      { error: 'Artist not found', id },
      { status: 404 }
    );
  }

  // 2. Check if artist has been scored
  const store = getFeatureStore();
  const featured = store.get(id);
  if (!featured) {
    return NextResponse.json(
      {
        error: 'No intelligence data found for this artist',
        id,
        message: 'Call GET /api/v1/intelligence/[id] first to compute scores',
      },
      { status: 404 }
    );
  }

  // 3. Get registry and history for all scores
  const registry = getRegistry();
  const allScores = registry.getAll();
  const historyManager = getHistoryManager();

  const scores = await Promise.all(allScores.map(async (score) => {
    const history = await historyManager.getHistory(score.identity.id, artistName);

    return {
      id: score.identity.id,
      name: score.identity.name,
      category: score.identity.category,
      version: score.identity.version,
      history: {
        trend: history.trend,
        volatility: history.volatility,
        daily: history.daily.map((entry) => ({
          score: entry.score,
          confidence: entry.confidence,
          timestamp: entry.timestamp,
          trend: entry.trend,
          change: entry.change,
          reason: entry.reason,
        })),
        weekly: history.weekly.map((entry) => ({
          score: entry.score,
          confidence: entry.confidence,
          timestamp: entry.timestamp,
          trend: entry.trend,
          change: entry.change,
        })),
        monthly: history.monthly.map((entry) => ({
          score: entry.score,
          confidence: entry.confidence,
          timestamp: entry.timestamp,
          trend: entry.trend,
          change: entry.change,
        })),
      },
    };
  }));

  // 4. Build aggregate trend from all scores
  const validHistories = scores.filter((s) => s.history.daily.length > 0);
  let aggregateTrend: 'up' | 'down' | 'stable' = 'stable';
  let aggregateVolatility = 0;

  if (validHistories.length > 0) {
    const upCount = validHistories.filter((s) => s.history.trend === 'up').length;
    const downCount = validHistories.filter((s) => s.history.trend === 'down').length;
    aggregateTrend = upCount > downCount ? 'up' : downCount > upCount ? 'down' : 'stable';
    aggregateVolatility = Math.round(
      validHistories.reduce((sum, s) => sum + s.history.volatility, 0) / validHistories.length
    );
  }

  return NextResponse.json({
    artist: {
      id,
      name: artistName,
    },
    summary: {
      scoresTracked: scores.length,
      scoresWithHistory: validHistories.length,
      aggregateTrend,
      aggregateVolatility,
    },
    scores,
    metadata: {
      version: '3.5.0',
      computedAt: new Date().toISOString(),
    },
  });
}
