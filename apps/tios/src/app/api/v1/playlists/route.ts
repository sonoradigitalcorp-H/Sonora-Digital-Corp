import { NextResponse } from 'next/server';
import { generatePlaylists, generatePlaylistStats } from '@/lib/data-generator';

export async function GET() {
  return NextResponse.json({
    playlists: generatePlaylists(),
    stats: generatePlaylistStats(),
    updatedAt: new Date().toISOString(),
  });
}
