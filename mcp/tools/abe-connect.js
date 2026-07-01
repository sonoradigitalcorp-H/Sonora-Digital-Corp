/**
 * ABE Connect — Comunicación directa artista ↔ fan
 * CRM de fans, mensajes, notificaciones, segmentación
 */
const fs = require('fs');
const path = require('path');

const EVENTS_FILE = path.join(__dirname, '..', '..', 'state', 'logs', 'events.jsonl');
const FANS_FILE = path.join(__dirname, '..', '..', 'data', 'abe-fans.json');

function _loadFans() {
  try {
    if (fs.existsSync(FANS_FILE)) {
      const raw = JSON.parse(fs.readFileSync(FANS_FILE, 'utf-8'));
      return raw.fans || raw || [];
    }
  } catch {}
  return [];
}

function _saveFans(fans) {
  try {
    fs.writeFileSync(FANS_FILE, JSON.stringify({ fans: fans || [] }, null, 2));
  } catch {}
}

function _emit(event, detail) {
  try {
    const entry = JSON.stringify({
      event, producer: 'abe-connect', timestamp: new Date().toISOString(), payload: detail,
    }) + '\n';
    fs.appendFileSync(EVENTS_FILE, entry);
  } catch {}
}

const tools = {
  abe_connect_fan_list: {
    description: 'Lista fans, opcionalmente filtrados por artista o status',
    inputSchema: {
      type: 'object', properties: {
        artist_id: { type: 'string' }, status: { type: 'string' }, limit: { type: 'number' },
      },
    },
    handler: async (args) => {
      const fans = _loadFans();
      let filtered = fans;
      if (args.status) filtered = filtered.filter(f => f.status === args.status);
      if (args.artist_id) filtered = filtered.filter(f => f.artist_id === args.artist_id);
      return { fans: filtered.slice(0, args.limit || 50) };
    },
  },

  abe_connect_fan_create: {
    description: 'Registra un nuevo fan en el CRM',
    inputSchema: {
      type: 'object', properties: {
        name: { type: 'string' }, phone: { type: 'string' }, email: { type: 'string' },
        artist_id: { type: 'string' }, source: { type: 'string' },
      }, required: ['name'],
    },
    handler: async (args) => {
      const fans = _loadFans();
      const fan = {
        id: `fan_${Date.now()}`,
        name: args.name,
        phone: args.phone || '',
        email: args.email || '',
        artist_id: args.artist_id || 'all',
        source: args.source || 'manual',
        status: 'active',
        message_count: 0,
        last_interaction: null,
        created_at: new Date().toISOString(),
      };
      fans.push(fan);
      _saveFans(fans);
      _emit('fan_created', { fan_id: fan.id, name: fan.name });
      return { fan, message: `✅ Fan ${args.name} registrado` };
    },
  },

  abe_connect_notify: {
    description: 'Envía notificación a fans por artista (broadcast segmentado)',
    inputSchema: {
      type: 'object', properties: {
        artist_id: { type: 'string' }, message: { type: 'string' },
        channel: { type: 'string', enum: ['pwa', 'whatsapp', 'all'] },
      }, required: ['artist_id', 'message'],
    },
    handler: async (args) => {
      const fans = _loadFans();
      const targets = args.artist_id === 'all'
        ? fans : fans.filter(f => f.artist_id === args.artist_id || !f.artist_id);

      _emit('fan_broadcast', {
        artist_id: args.artist_id, total: targets.length,
        channel: args.channel || 'pwa', preview: args.message.substring(0, 100),
      });

      return {
        status: 'queued', total_fans: targets.length,
        channels: args.channel || 'pwa',
        message: `📢 Notificación encolada para ${targets.length} fans`,
      };
    },
  },

  abe_connect_stats: {
    description: 'Estadísticas de fans: total, activos, por artista',
    inputSchema: { type: 'object', properties: {} },
    handler: async () => {
      const fans = _loadFans();
      const byArtist = {};
      fans.forEach(f => {
        const aid = f.artist_id || 'all';
        byArtist[aid] = (byArtist[aid] || 0) + 1;
      });
      return {
        total_fans: fans.length,
        active_fans: fans.filter(f => f.status === 'active').length,
        by_artist: byArtist,
        total_messages: fans.reduce((s, f) => s + (f.message_count || 0), 0),
      };
    },
  },
};

module.exports = { tools };
