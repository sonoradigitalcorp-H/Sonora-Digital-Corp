const fs = require('fs');
const path = require('path');

const DATA_FILE = path.join(__dirname, '..', '..', 'apps', 'webui', 'data', 'abe-music.json');
const LEGACY_FILE = path.join(__dirname, '..', '..', 'config', 'abe-music.json');
const EVENTS_FILE = path.join(__dirname, '..', '..', 'state', 'logs', 'events.jsonl');

function _normalize(raw) {
  // Handle dict with artists key (abe-music.json format)
  if (raw && raw.artists && !Array.isArray(raw.artists)) {
    return Object.values(raw.artists).map(a => ({
      id: a.id, name: a.nombre || a.name, genre: a.genero || a.genre,
      status: a.status || 'active', streams: a.streams || 0,
      revenue: a.revenue || a.income || 0,
      releases: (a.releases || []).map(r => ({
        id: r.id, title: r.titulo || r.title, type: r.tipo || r.type,
        streams: r.streams || 0, revenue: r.revenue || 0,
        release_date: r.fecha_lanzamiento || r.release_date,
        platform: r.plataforma || r.platform || 'all',
      })),
      social: a.social || {}, pais: a.pais || '',
    }));
  }
  // Handle array of artists
  if (Array.isArray(raw)) return raw;
  // Handle array in artists key
  if (raw && raw.artists && Array.isArray(raw.artists)) return raw.artists;
  return [];
}

function _load() {
  try {
    if (fs.existsSync(DATA_FILE)) return _normalize(JSON.parse(fs.readFileSync(DATA_FILE, 'utf-8')));
    if (fs.existsSync(LEGACY_FILE)) {
      const raw = JSON.parse(fs.readFileSync(LEGACY_FILE, 'utf-8'));
      // config/abe-music.json has different structure
      if (Array.isArray(raw)) return raw;
      if (raw.artists) return Object.values(raw.artists);
      return [];
    }
  } catch (e) { console.error('ABE load error:', e.message); }
  return [];
}

function _save(artists) {
  try { fs.writeFileSync(DATA_FILE, JSON.stringify(artists, null, 2)); } catch {}
}

function _emit(event, detail) {
  try {
    const entry = JSON.stringify({ event, producer: 'abe-tools', timestamp: new Date().toISOString(), payload: detail }) + '\n';
    fs.appendFileSync(EVENTS_FILE, entry);
  } catch {}
}

const ROYALTY_SPLIT = {
  streaming: { artist: 0.7, label: 0.2, distributor: 0.1 },
  merch: { artist: 0.6, label: 0.3, distributor: 0.1 },
  sync_license: { artist: 0.5, label: 0.4, distributor: 0.1 },
};

const tools = {
  abe_list_artists: {
    description: 'Lista artistas ABE Music con datos reales',
    inputSchema: { type: 'object', properties: { status: { type: 'string' } } },
    handler: async (args) => {
      const artists = _load();
      const filtered = args.status ? artists.filter(a => a.status === args.status) : artists;
      return { artists: filtered.map(a => ({
        id: a.id, name: a.name, genre: a.genre, status: a.status,
        streams: a.streams || 0, revenue: a.revenue || a.income || 0,
        releases: (a.releases || []).length,
        social: a.social || {},
      })) };
    },
  },

  abe_get_artist: {
    description: 'Obtiene artista por ID con detalle completo',
    inputSchema: { type: 'object', properties: { artist_id: { type: 'string' } }, required: ['artist_id'] },
    handler: async (args) => {
      const artists = _load();
      const artist = artists.find(a => a.id === args.artist_id || a.name === args.artist_id);
      return artist || { error: 'Artista no encontrado' };
    },
  },

  abe_ceo_dashboard: {
    description: 'Dashboard CEO con KPIs agregados de ABE Music',
    inputSchema: { type: 'object', properties: {} },
    handler: async () => {
      const artists = _load();
      const totalStreams = artists.reduce((s, a) => s + (a.streams || 0), 0);
      const totalRevenue = artists.reduce((s, a) => s + (a.revenue || a.income || 0), 0);
      const totalReleases = artists.reduce((s, a) => s + (a.releases || []).length, 0);
      const activeArtists = artists.filter(a => a.status === 'active' || !a.status).length;
      return {
        total_artists: artists.length, active_artists: activeArtists,
        total_streams: totalStreams, total_revenue: totalRevenue,
        total_releases: totalReleases, avg_streams_per_artist: artists.length > 0 ? Math.round(totalStreams / artists.length) : 0,
        top_artist: artists.sort((a, b) => (b.streams || 0) - (a.streams || 0))[0]?.name || null,
        royalty_split: ROYALTY_SPLIT, artist_revenue_share: Math.round(totalRevenue * 0.7),
        label_revenue_share: Math.round(totalRevenue * 0.2),
        distributor_revenue_share: Math.round(totalRevenue * 0.1),
        generated_at: new Date().toISOString(),
      };
    },
  },

  abe_artist_kpi: {
    description: 'KPI detallado de un artista específico',
    inputSchema: { type: 'object', properties: { artist_id: { type: 'string' } }, required: ['artist_id'] },
    handler: async (args) => {
      const artists = _load();
      const artist = artists.find(a => a.id === args.artist_id || a.name === args.artist_id);
      if (!artist) return { error: 'Artista no encontrado' };
      const releases = (artist.releases || []).map(r => ({
        title: r.title, type: r.type, release_date: r.release_date,
        streams: r.streams || 0, revenue: r.revenue || 0, platform: r.platform || 'all',
      }));
      const totalStreams = releases.length > 0 ? releases.reduce((s, r) => s + r.streams, 0) : (artist.streams || 0);
      const totalRevenue = releases.length > 0 ? releases.reduce((s, r) => s + r.revenue, 0) : (artist.revenue || 0);
      return {
        artist: artist.name, genre: artist.genre, status: artist.status,
        total_streams: totalStreams, total_revenue: totalRevenue,
        releases, release_count: releases.length,
        royalty_estimate: {
          artist_share: Math.round(totalRevenue * ROYALTY_SPLIT.streaming.artist),
          label_share: Math.round(totalRevenue * ROYALTY_SPLIT.streaming.label),
          distributor_share: Math.round(totalRevenue * ROYALTY_SPLIT.streaming.distributor),
        },
      };
    },
  },

  abe_record_stream: {
    description: 'Registra stream en release',
    inputSchema: { type: 'object', properties: { release_id: { type: 'string' }, amount: { type: 'number' } }, required: ['release_id'] },
    handler: async (args) => {
      const artists = _load();
      let found = false;
      for (const a of artists) {
        const release = (a.releases || []).find(r => r.id === args.release_id || r.title === args.release_id);
        if (release) {
          release.streams = (release.streams || 0) + (args.amount || 1);
          a.streams = (a.streams || 0) + (args.amount || 1);
          found = true;
          break;
        }
      }
      if (!found) return { error: 'Release no encontrado' };
      _save(artists);
      _emit('stream_recorded', { release_id: args.release_id, amount: args.amount || 1 });
      return { status: 'recorded', release_id: args.release_id, amount: args.amount || 1 };
    },
  },

  abe_record_revenue: {
    description: 'Registra revenue',
    inputSchema: { type: 'object', properties: { release_id: { type: 'string' }, amount: { type: 'number' }, source: { type: 'string' } }, required: ['release_id'] },
    handler: async (args) => {
      const artists = _load();
      let found = false;
      for (const a of artists) {
        const release = (a.releases || []).find(r => r.id === args.release_id || r.title === args.release_id);
        if (release) {
          release.revenue = (release.revenue || 0) + (args.amount || 0);
          a.revenue = (a.revenue || 0) + (args.amount || 0);
          found = true;
          break;
        }
      }
      if (!found) return { error: 'Release no encontrado' };
      _save(artists);
      _emit('revenue_recorded', { release_id: args.release_id, amount: args.amount || 0, source: args.source || 'unknown' });
      return { status: 'recorded', release_id: args.release_id, amount: args.amount || 0 };
    },
  },
};

module.exports = { tools };
