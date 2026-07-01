/**
 * Music Provider MCP Tools — Spotify, Apple Music, YouTube Data connectors
 * Cada artista conecta sus propias APIs y jala datos reales.
 * Si no hay API key configurada, usa datos manuales como fallback.
 */

const fs = require('fs');
const path = require('path');
const http = require('http');
const https = require('https');

const CONFIG_FILE = path.join(__dirname, '..', '..', 'config', 'artists.json');
const DATA_FILE = path.join(__dirname, '..', '..', 'apps', 'webui', 'data', 'abe-music.json');
const EVENTS_FILE = path.join(__dirname, '..', '..', 'state', 'logs', 'events.jsonl');

function _loadArtists() {
  try {
    if (fs.existsSync(DATA_FILE)) {
      const raw = JSON.parse(fs.readFileSync(DATA_FILE, 'utf-8'));
      if (raw.artists && !Array.isArray(raw.artists)) return Object.values(raw.artists);
      if (Array.isArray(raw)) return raw;
      if (raw.artists && Array.isArray(raw.artists)) return raw.artists;
    }
  } catch {}
  return [];
}

function _loadConfig() {
  try {
    if (fs.existsSync(CONFIG_FILE)) return JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf-8'));
  } catch {}
  return { artists: {} };
}

function _saveConfig(config) {
  try { fs.writeFileSync(CONFIG_FILE, JSON.stringify(config, null, 2)); } catch {}
}

function _emit(event, detail) {
  try {
    const entry = JSON.stringify({ event, producer: 'music-providers', timestamp: new Date().toISOString(), payload: detail }) + '\n';
    fs.appendFileSync(EVENTS_FILE, entry);
  } catch {}
}

// ── Spotify API ──
async function _spotifyGet(accessToken, endpoint) {
  return new Promise((resolve) => {
    const req = https.get({ hostname: 'api.spotify.com', path: '/v1/' + endpoint, headers: { 'Authorization': 'Bearer ' + accessToken }, timeout: 10000 }, (res) => {
      let d = ''; res.on('data', c => d += c); res.on('end', () => { try { resolve(JSON.parse(d)); } catch { resolve({ error: 'parse_error' }); } });
    });
    req.on('error', (e) => resolve({ error: e.message }));
    req.end();
  });
}

async function _spotifyRefresh(clientId, clientSecret, refreshToken) {
  return new Promise((resolve) => {
    const body = 'grant_type=refresh_token&refresh_token=' + refreshToken;
    const req = https.request({ hostname: 'accounts.spotify.com', path: '/api/token', method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'Authorization': 'Basic ' + Buffer.from(clientId + ':' + clientSecret).toString('base64') }, timeout: 10000 }, (res) => {
      let d = ''; res.on('data', c => d += c); res.on('end', () => { try { const j = JSON.parse(d); resolve(j.access_token || null); } catch { resolve(null); } });
    });
    req.on('error', () => resolve(null));
    req.write(body); req.end();
  });
}

async function _fetchSpotifyData(artistConfig) {
  if (!artistConfig.spotify_refresh_token || !artistConfig.spotify_client_id || !artistConfig.spotify_client_secret) {
    return { source: 'spotify', status: 'not_configured' };
  }
  try {
    const token = await _spotifyRefresh(artistConfig.spotify_client_id, artistConfig.spotify_client_secret, artistConfig.spotify_refresh_token);
    if (!token) return { source: 'spotify', status: 'auth_failed' };
    const artistData = await _spotifyGet(token, 'artists/' + artistConfig.spotify_artist_id);
    const topTracks = await _spotifyGet(token, 'artists/' + artistConfig.spotify_artist_id + '/top-tracks?market=US');
    return {
      source: 'spotify', status: 'ok',
      monthly_listeners: artistData.followers?.total || 0,
      popularity: artistData.popularity || 0,
      genres: artistData.genres || [],
      top_tracks: (topTracks.tracks || []).map(t => ({ name: t.name, popularity: t.popularity, url: t.external_urls?.spotify })),
      fetched_at: new Date().toISOString(),
    };
  } catch (e) { return { source: 'spotify', status: 'error', error: e.message }; }
}

// ── Tools ──

const tools = {
  // Configure artist data sources
  artist_configure: {
    description: 'Configura fuentes de datos para un artista (Spotify, Apple Music, etc.)',
    inputSchema: { type: 'object', properties: {
      artist_id: { type: 'string' }, artist_name: { type: 'string' },
      spotify_artist_id: { type: 'string' }, spotify_client_id: { type: 'string' },
      spotify_client_secret: { type: 'string' }, spotify_refresh_token: { type: 'string' },
      manual_streams: { type: 'number' }, manual_revenue: { type: 'number' },
    }, required: ['artist_id', 'artist_name'] },
    handler: async (args) => {
      const config = _loadConfig();
      config.artists[args.artist_id] = {
        name: args.artist_name,
        spotify_artist_id: args.spotify_artist_id || null,
        spotify_client_id: args.spotify_client_id || null,
        spotify_client_secret: args.spotify_client_secret || null,
        spotify_refresh_token: args.spotify_refresh_token || null,
        manual_streams: args.manual_streams || 0,
        manual_revenue: args.manual_revenue || 0,
        last_sync: null,
        sources: [],
      };
      _saveConfig(config);
      _emit('artist_configured', { artist_id: args.artist_id, artist_name: args.artist_name });
      return { status: 'configured', artist_id: args.artist_id };
    },
  },

  // Sync data from all configured sources for an artist
  artist_sync: {
    description: 'Sincroniza datos reales desde Spotify, Apple Music, etc. para un artista',
    inputSchema: { type: 'object', properties: { artist_id: { type: 'string' } }, required: ['artist_id'] },
    handler: async (args) => {
      const config = _loadConfig();
      const artistConfig = config.artists[args.artist_id];
      if (!artistConfig) return { error: 'Artista no configurado. Usá artist_configure primero.' };

      const results = [];

      // Try Spotify
      if (artistConfig.spotify_refresh_token) {
        const spotifyData = await _fetchSpotifyData(artistConfig);
        results.push(spotifyData);
        if (spotifyData.status === 'ok') {
          // Update the artist data with real Spotify numbers
          const artists = _loadArtists();
          const artist = artists.find(a => a.id === args.artist_id || a.nombre === artistConfig.name || a.name === artistConfig.name);
          if (artist) {
            artist.spotify_listeners = spotifyData.monthly_listeners;
            artist.spotify_popularity = spotifyData.popularity;
            artist.spotify_genres = spotifyData.genres;
            artist.spotify_top_tracks = spotifyData.top_tracks;
            artist.last_spotify_sync = spotifyData.fetched_at;
            // Save back to data file
            try {
              const raw = JSON.parse(fs.readFileSync(DATA_FILE, 'utf-8'));
              if (raw.artists && !Array.isArray(raw.artists)) {
                for (const [id, a] of Object.entries(raw.artists)) {
                  if (id === args.artist_id || a.nombre === artistConfig.name) {
                    a.spotify_listeners = spotifyData.monthly_listeners;
                    a.spotify_popularity = spotifyData.popularity;
                    a.spotify_genres = spotifyData.genres;
                    a.spotify_top_tracks = spotifyData.top_tracks;
                    a.last_spotify_sync = spotifyData.fetched_at;
                  }
                }
              }
              fs.writeFileSync(DATA_FILE, JSON.stringify(raw, null, 2));
            } catch {}
          }
        }
      }

      // Update config with sync time and sources
      artistConfig.last_sync = new Date().toISOString();
      artistConfig.sources = results.map(r => r.source + ':' + r.status);
      _saveConfig(config);

      _emit('artist_synced', { artist_id: args.artist_id, sources: results.map(r => r.source + '=' + r.status) });
      return { artist_id: args.artist_id, sync_time: artistConfig.last_sync, results };
    },
  },

  // Get artist config and data sources status
  artist_status: {
    description: 'Muestra estado de las fuentes de datos configuradas para un artista',
    inputSchema: { type: 'object', properties: { artist_id: { type: 'string' } }, required: ['artist_id'] },
    handler: async (args) => {
      const config = _loadConfig();
      const ac = config.artists[args.artist_id];
      if (!ac) return { status: 'not_configured', message: 'Usá artist_configure primero con el artist_id' };
      return {
        artist_id: args.artist_id, artist_name: ac.name,
        spotify_connected: !!ac.spotify_refresh_token,
        manual_data: { streams: ac.manual_streams, revenue: ac.manual_revenue },
        last_sync: ac.last_sync,
        sources: ac.sources || [],
      };
    },
  },

  // List all configured artists  
  artist_list_configs: {
    description: 'Lista todos los artistas configurados con sus fuentes de datos',
    inputSchema: { type: 'object', properties: {} },
    handler: async () => {
      const config = _loadConfig();
      return { artists: Object.entries(config.artists || {}).map(([id, a]) => ({
        id, name: a.name,
        spotify: !!a.spotify_refresh_token,
        last_sync: a.last_sync,
        sources: a.sources || [],
        manual_streams: a.manual_streams,
        manual_revenue: a.manual_revenue,
      })) };
    },
  },

  // Sync ALL artists at once
  artist_sync_all: {
    description: 'Sincroniza datos de todos los artistas configurados',
    inputSchema: { type: 'object', properties: {} },
    handler: async () => {
      const config = _loadConfig();
      const results = {};
      for (const [id, ac] of Object.entries(config.artists || {})) {
        if (ac.spotify_refresh_token) {
          const spotifyData = await _fetchSpotifyData(ac);
          results[id] = { spotify: spotifyData.status };
          ac.last_sync = new Date().toISOString();
          ac.sources = ['spotify:' + spotifyData.status];
        }
      }
      _saveConfig(config);
      _emit('all_artists_synced', { count: Object.keys(results).length });
      return { synced: Object.keys(results).length, results };
    },
  },
};

module.exports = { tools };
