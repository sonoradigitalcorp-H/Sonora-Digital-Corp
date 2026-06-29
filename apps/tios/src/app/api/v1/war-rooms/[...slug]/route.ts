import { NextRequest, NextResponse } from 'next/server';
import {
  generateArtistById, generateGrowthHistory, generateAlerts,
  generateWarRoomTeamMembers, generateWarRoomDocuments,
  generateWarRoomMeetings, generateWarRoomOffers,
} from '@/lib/data-generator';

export async function GET(
  request: NextRequest,
  context: any
) {
  const params = await context.params;
  const slug: string[] = params.slug;
  const [id, section] = slug;

  // Find the artist deterministically by ID (same ID = same data within session)
  const artist = generateArtistById(id);

  // Generate war room data for this artist
  const growthData = generateGrowthHistory(artist.score, artist.listeners);
  const alerts = generateAlerts(3);
  const dealBreakdown = {
    advance: Math.round(artist.deal * 0.45),
    marketing: Math.round(artist.deal * 0.25),
    production: Math.round(artist.deal * 0.18),
    legal: Math.round(artist.deal * 0.07),
    operations: Math.round(artist.deal * 0.05),
    total: artist.deal,
  };

  const teamMembers = generateWarRoomTeamMembers();

  // Section-specific responses
  if (section === 'documents') {
    return NextResponse.json({
      documents: generateWarRoomDocuments(id, artist.name),
    });
  }

  if (section === 'meetings') {
    return NextResponse.json({
      meetings: generateWarRoomMeetings(id, artist.name, teamMembers),
    });
  }

  if (section === 'offers') {
    return NextResponse.json({
      offers: generateWarRoomOffers(artist.deal),
    });
  }

  // Full war room response
  return NextResponse.json({
    id,
    artist,
    growthData,
    dealBreakdown,
    teamMembers,
    alerts,
    status: 'active',
    lastUpdated: new Date().toISOString(),
  });
}
