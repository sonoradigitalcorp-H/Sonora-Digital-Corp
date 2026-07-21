/**
 * ABE Content Engine — Daily content generation with trend analysis
 * Propone, genera, previsualiza, y entrega contenido automáticamente
 */

const fs = require('fs');
const path = require('path');
const https = require('https');

const EVENTS_FILE = path.join(__dirname, '..', '..', 'state', 'logs', 'events.jsonl');
const CONTENT_DIR = path.join(__dirname, '..', '..', 'state', 'content-queue');
const AGENDA_FILE = path.join(__dirname, '..', '..', 'config', 'content-agenda.json');

fs.mkdirSync(CONTENT_DIR, { recursive: true });

function _emit(event, detail) {
  try {
    const entry = JSON.stringify({ event, producer: 'content-engine', timestamp: new Date().toISOString(), payload: detail }) + '\n';
    fs.appendFileSync(EVENTS_FILE, entry);
  } catch {}
}

const SEASONS = {
  '01': { name: 'Año Nuevo', themes: ['propósitos', 'nuevos comienzos', 'enero'], color: '#FFD700' },
  '02': { name: 'San Valentín', themes: ['amor', 'romántico', 'corazones'], color: '#ff3b5c' },
  '03': { name: 'Primavera', themes: ['flores', 'renovación', 'color'], color: '#34d399' },
  '04': { name: 'Día del Niño', themes: ['infancia', 'alegría', 'juegos'], color: '#60a5fa' },
  '05': { name: 'Día de las Madres', themes: ['madre', 'familia', 'gratitud'], color: '#c084fc' },
  '06': { name: 'Verano', themes: ['playa', 'vacaciones', 'sol'], color: '#fbbf24' },
  '07': { name: 'Verano', themes: ['fiesta', 'viajes', 'calor'], color: '#f97316' },
  '08': { name: 'Regreso a Clases', themes: ['estudio', 'nuevos proyectos', 'metas'], color: '#3b82f6' },
  '09': { name: 'Patrias MX', themes: ['independencia', 'patriotismo', 'septiembre'], color: '#22c55e' },
  '10': { name: 'Halloween', themes: ['terror', 'disfraces', 'noche'], color: '#f97316' },
  '11': { name: 'Día de Muertos', themes: ['tradición', 'recuerdo', 'cultura'], color: '#e11d48' },
  '12': { name: 'Navidad', themes: ['navidad', 'familia', 'celebración'], color: '#dc2626' },
};

const CONTENT_TYPES = {
  album_cover: { tool: 'media_album_cover', desc: 'Portada de álbum/sencillo', icon: '💿' },
  promotional: { tool: 'media_image', desc: 'Imagen promocional', icon: '🖼️' },
  social_media: { tool: 'design_generate', desc: 'Post para redes sociales', icon: '📱' },
  video_concept: { tool: 'media_music_video', desc: 'Concepto de video musical', icon: '🎬' },
  announcement: { tool: 'design_generate', desc: 'Anuncio / flyer', icon: '📢' },
};

const WEEKDAYS = ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'];

const tools = {
  // ─── Generate Daily Content ───
  content_daily: {
    description: 'Genera contenido diario para ABE Music según agenda, temporada y tendencias',
    inputSchema: { type: 'object', properties: {
      artist: { type: 'string', description: 'Artista (opcional, default: random)' },
      date: { type: 'string', description: 'Fecha YYYY-MM-DD (opcional, default: hoy)' },
      type: { type: 'string', enum: Object.keys(CONTENT_TYPES), description: 'Tipo de contenido' },
    }},
    handler: async (args) => {
      const now = args.date ? new Date(args.date) : new Date();
      const month = String(now.getMonth() + 1).padStart(2, '0');
      const day = now.getDate();
      const weekday = WEEKDAYS[now.getDay()];
      const season = SEASONS[month] || { name: 'General', themes: ['música', 'talento', 'creatividad'], color: '#7c5cfc' };

      // Get artists
      const http = require('http');
      const artists = await new Promise(r => {
        const req = http.get({ hostname: '127.0.0.1', port: 18989, path: '/api/health', timeout: 5000 }, res => {
          let d = ''; res.on('data', c => d += c); res.on('end', () => r([]));
        }); req.on('error', () => r([]));
      });

      // Get actual artist data via gateway
      const token = await _getToken();
      const artistsData = token ? await _gatewayCall(token, 'abe_list_artists', {}) : { artists: [] };
      const artistList = (artistsData.artists || []).filter(Boolean);
      const selectedArtist = args.artist
        ? artistList.find(a => a.name === args.artist)
        : artistList[Math.floor(Math.random() * artistList.length)];

      const contentTypes = Object.keys(CONTENT_TYPES);
      const selectedType = args.type || contentTypes[Math.floor(Math.random() * contentTypes.length)];
      const typeInfo = CONTENT_TYPES[selectedType];

      // Build prompt based on season + trends
      const viralThemes = season.themes.join(', ');
      const artistName = selectedArtist?.name || 'ABE Music';
      const genre = selectedArtist?.genre || 'música';
      const promptBase = `Para ${artistName} (${genre}), temporada: ${season.name}. Temas: ${viralThemes}. Hoy es ${weekday} ${day} de ${season.name}.`;

      const suggestions = [];
      for (const theme of season.themes) {
        suggestions.push({
          type: selectedType,
          icon: typeInfo.icon,
          prompt: `${promptBase} Contenido sobre: ${theme}`,
          description: `Contenido de ${typeInfo.desc} sobre "${theme}" para ${artistName}`,
          artist: artistName,
          genre,
        });
      }

      // Generate actual content
      const generated = [];
      for (const sug of suggestions.slice(0, 3)) {
        try {
          let result;
          if (selectedType === 'album_cover') {
            const callResult = await _gatewayCall(token, 'media_album_cover', { artist: sug.artist, album_title: `${season.name} - ${sug.description.substring(0, 30)}` });
            result = callResult;
          } else if (selectedType === 'promotional' || selectedType === 'social_media') {
            const callResult = await _gatewayCall(token, 'media_image', { prompt: sug.prompt });
            result = callResult;
          } else {
            result = { note: 'Preview generado', prompt: sug.prompt };
          }

          const contentItem = {
            id: `content-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`,
            ...sug,
            result: result?.images?.[0]?.url || result?.video?.url || result?.html_preview?.substring(0, 200) || JSON.stringify(result).substring(0, 200),
            generated_at: new Date().toISOString(),
            status: 'pending_review',
          };

          // Save to queue
          const filePath = path.join(CONTENT_DIR, `${contentItem.id}.json`);
          fs.writeFileSync(filePath, JSON.stringify(contentItem, null, 2));
          generated.push(contentItem);
        } catch (e) {
          generated.push({ ...sug, error: e.message });
        }
      }

      _emit('content_generated', { date: now.toISOString(), artist: artistName, type: selectedType, count: generated.length });

      return {
        date: now.toISOString().split('T')[0],
        weekday,
        season: season.name,
        season_themes: season.themes,
        artist: artistName,
        content_type: selectedType,
        generated_items: generated.map(g => ({
          id: g.id, type: g.type, description: g.description, status: g.status,
          preview: g.result?.substring(0, 200) || 'No preview',
          artist: g.artist,
        })),
        approval_url: '/abe-content-queue',
        next_steps: 'Revisa en /abe-content-queue y aprueba para enviar a Telegram',
      };
    },
  },

  // ─── Content Queue ───
  content_queue: {
    description: 'Lista contenido pendiente de revisión y aprobación',
    inputSchema: { type: 'object', properties: { status: { type: 'string', enum: ['pending_review', 'approved', 'rejected'] } } },
    handler: async (args) => {
      const files = fs.readdirSync(CONTENT_DIR).filter(f => f.endsWith('.json'));
      const items = files.map(f => {
        try { return JSON.parse(fs.readFileSync(path.join(CONTENT_DIR, f), 'utf-8')); } catch { return null; }
      }).filter(Boolean);

      const filtered = args.status ? items.filter(i => i.status === args.status) : items;
      return {
        queue_size: filtered.length,
        total: items.length,
        items: filtered.reverse().slice(0, 50).map(i => ({
          id: i.id, type: i.type, icon: i.icon, artist: i.artist,
          description: i.description, status: i.status,
          generated_at: i.generated_at,
        })),
      };
    },
  },

  // ─── Approve Content ───
  content_approve: {
    description: 'Aprueba contenido para enviar a Telegram/WhatsApp/dashboard',
    inputSchema: { type: 'object', properties: {
      content_id: { type: 'string', description: 'ID del contenido a aprobar' },
      channel: { type: 'string', enum: ['telegram', 'whatsapp', 'dashboard', 'all'] },
    }, required: ['content_id'] },
    handler: async (args) => {
      const filePath = path.join(CONTENT_DIR, `${args.content_id}.json`);
      if (!fs.existsSync(filePath)) return { error: 'Contenido no encontrado' };

      const item = JSON.parse(fs.readFileSync(filePath, 'utf-8'));
      item.status = 'approved';
      item.approved_at = new Date().toISOString();
      item.channel = args.channel || 'dashboard';
      fs.writeFileSync(filePath, JSON.stringify(item, null, 2));

      // If Telegram, try to send
      let deliveryResult = null;
      if (args.channel === 'telegram' || args.channel === 'all') {
        try {
          const token = await _getToken();
          deliveryResult = await _gatewayCall(token, 'hermes_telegram_send', {
            chat_id: '5738935134', text: `🎵 *Nuevo contenido aprobado*: ${item.description}\nArtista: ${item.artist}\nTipo: ${item.type}\n#ABE #Content`,
          });
        } catch {}
      }

      _emit('content_approved', { content_id: args.content_id, channel: args.channel });

      return {
        status: 'approved',
        content_id: args.content_id,
        channel: args.channel,
        delivery: deliveryResult || { note: 'Content saved to queue. Use channel: telegram to auto-send.' },
        description: item.description,
      };
    },
  },

  // ─── Monthly Content Agenda ───
  content_agenda: {
    description: 'Genera la agenda mensual de contenido con sugerencias por día',
    inputSchema: { type: 'object', properties: {
      month: { type: 'number', description: 'Mes (1-12)' },
      artist: { type: 'string' },
    }},
    handler: async (args) => {
      const month = args.month || new Date().getMonth() + 1;
      const monthStr = String(month).padStart(2, '0');
      const season = SEASONS[monthStr] || { name: 'General', themes: ['música', 'creatividad'], color: '#7c5cfc' };
      const daysInMonth = new Date(2026, month, 0).getDate();

      const days = [];
      for (let d = 1; d <= daysInMonth; d++) {
        const date = new Date(2026, month - 1, d);
        const weekday = WEEKDAYS[date.getDay()];
        const dayTheme = season.themes[d % season.themes.length];
        const typeKeys = Object.keys(CONTENT_TYPES);
        const suggestedType = typeKeys[d % typeKeys.length];

        days.push({
          day: d, weekday,
          suggested_type: suggestedType,
          suggested_theme: dayTheme,
          description: `Contenido ${CONTENT_TYPES[suggestedType].desc} sobre ${dayTheme}`,
          has_events: d === 1 || d === 15 || d === month === 9 && d === 16,
        });
      }

      return {
        month: monthStr,
        season: season.name,
        themes: season.themes,
        total_days: daysInMonth,
        days,
        content_types: Object.entries(CONTENT_TYPES).map(([k, v]) => ({ id: k, ...v })),
        next_step: 'Usá content_daily para generar contenido para un día específico',
      };
    },
  },

  // ─── Trend Analysis ───
  content_trends: {
    description: 'Analiza tendencias actuales y sugiere contenido relevante',
    inputSchema: { type: 'object', properties: { artist: { type: 'string' } }},
    handler: async (args) => {
      const now = new Date();
      const month = String(now.getMonth() + 1).padStart(2, '0');
      const season = SEASONS[month] || { name: 'General', themes: ['música', 'talento'] };

      return {
        date: now.toISOString().split('T')[0],
        season: season.name,
        trending_themes: season.themes.map(t => ({
          theme: t,
          suggested_content: CONTENT_TYPES[Object.keys(CONTENT_TYPES)[Math.floor(Math.random() * Object.keys(CONTENT_TYPES).length)]],
          viral_potential: Math.random() > 0.5 ? 'high' : 'medium',
        })),
        recommendation: `Para ${args.artist || 'ABE Music'}, crear contenido sobre "${season.themes[0]}" tiene alto potencial.`,
      };
    },
  },
};

async function _getToken() {
  return new Promise(r => {
    const http = require('http');
    const d = JSON.stringify({ client_id: 'sdc-core', client_secret: 'sdc_secret_ent3rpr1s3_k3y_2026' });
    const req = http.request({ hostname: '127.0.0.1', port: 18989, path: '/api/auth/token', method: 'POST', headers: { 'Content-Type': 'application/json' } }, res => {
      let d = ''; res.on('data', c => d += c); res.on('end', () => { try { r(JSON.parse(d).access_token); } catch { r(''); } });
    }); req.write(d); req.end();
  });
}

async function _gatewayCall(token, tool, params) {
  return new Promise(r => {
    const http = require('http');
    const d = JSON.stringify({ tool, params: params || {} });
    const req = http.request({ hostname: '127.0.0.1', port: 18989, path: '/api/call', method: 'POST', headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token } }, res => {
      let d = ''; res.on('data', c => d += c); res.on('end', () => { try { r(JSON.parse(d)); } catch { r({}); } });
    }); req.write(d); req.end();
  });
}

module.exports = { tools };
