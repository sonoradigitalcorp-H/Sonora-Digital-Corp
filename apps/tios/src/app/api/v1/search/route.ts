import { NextRequest, NextResponse } from 'next/server';
import { generateArtists, generateSearchPages, generateSearchSuggestions } from '@/lib/data-generator';

// All 16 navigation modules for global search
const NAV_MODULES = [
  { id: 'nav-dashboard', type: 'page', label: 'Mission Control', description: 'Executive overview of the intelligence operation', href: '/dashboard' },
  { id: 'nav-command-center', type: 'page', label: 'Command Center', description: 'Centralized mission control for all intelligence operations', href: '/command-center' },
  { id: 'nav-workflows', type: 'workflow', label: 'Workflows', description: 'Automated agent workflows and processes', href: '/workflows' },
  { id: 'nav-agents', type: 'page', label: 'Agent Performance', description: 'AI agent activity, metrics and performance', href: '/agents' },
  { id: 'nav-artists', type: 'page', label: 'Artist Radar', description: 'Complete intelligence dossiers on all artists', href: '/artists' },
  { id: 'nav-discovery', type: 'page', label: 'Discovery Engine', description: 'Emerging opportunities detected by SIGNAL', href: '/discovery' },
  { id: 'nav-analytics', type: 'page', label: 'Analytics', description: 'Deep analytics and market intelligence', href: '/analytics' },
  { id: 'nav-alerts', type: 'page', label: 'Alerts', description: 'Intelligence alerts and notifications', href: '/alerts' },
  { id: 'nav-reports', type: 'page', label: 'Reports', description: 'Executive briefings ready for leadership', href: '/reports' },
  { id: 'nav-contracts', type: 'page', label: 'Contracts', description: 'Legal intelligence and contract lifecycle', href: '/contracts' },
  { id: 'nav-signings', type: 'page', label: 'Signing Pipeline', description: 'Artist signing pipeline and deal tracking', href: '/signings' },
  { id: 'nav-warrooms', type: 'warroom', label: 'War Rooms', description: 'High-priority negotiations and strategic operations', href: '/war-rooms' },
  { id: 'nav-market', type: 'page', label: 'Market Intelligence', description: 'Market trends and competitive analysis', href: '/market' },
  { id: 'nav-playlists', type: 'page', label: 'Playlist Monitor', description: 'Playlist performance and tracking', href: '/playlists' },
  { id: 'nav-finance', type: 'page', label: 'Financial View', description: 'Financial intelligence and budget overview', href: '/finance' },
  { id: 'nav-settings', type: 'page', label: 'Settings', description: 'System configuration and preferences', href: '/settings' },
];

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const q = searchParams.get('q')?.toLowerCase() || '';

  const allArtists = generateArtists(20);
  const pages = generateSearchPages();
  const suggestions = generateSearchSuggestions();

  // Filter artists by query
  const matchedArtists = allArtists.filter(a =>
    a.name.toLowerCase().includes(q) ||
    a.genres.some(g => g.toLowerCase().includes(q)) ||
    a.city.toLowerCase().includes(q) ||
    a.country.toLowerCase().includes(q)
  );

  // Map artists to search result format with rich info
  const artistResults = matchedArtists.map(a => ({
    id: `artist-${a.id}`,
    type: 'artist' as const,
    label: a.name,
    description: `${a.genres.slice(0, 2).join(', ')} · ${a.city}, ${a.country} · Score: ${a.score}`,
    href: `/artists/${a.id}`,
    image: a.photoUrl || a.image,
    score: a.score,
    growth: a.growth,
    status: a.status,
    genres: a.genres,
  }));

  // Filter navigation modules by query
  const moduleResults = NAV_MODULES.filter(m =>
    m.label.toLowerCase().includes(q) ||
    m.description.toLowerCase().includes(q)
  ).map(m => ({ ...m }));

  // Filter extra pages by query
  const pageResults = pages
    .filter(p => p.title.toLowerCase().includes(q) || p.description.toLowerCase().includes(q))
    .map(p => ({
      id: `page-${p.id}`,
      type: 'page' as const,
      label: p.title,
      description: p.description,
      href: p.path,
    }));

  // Merge all results sorted by relevance
  const results = [
    ...moduleResults,
    ...pageResults,
    ...artistResults,
  ];

  return NextResponse.json({ results, suggestions });
}
