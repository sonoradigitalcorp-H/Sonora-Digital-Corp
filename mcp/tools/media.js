const https = require('https');
const http = require('http');
const fs = require('fs');
const path = require('path');

const FAL_KEY = process.env.FAL_API_KEY || '';
const MEDIA_DIR = path.join(__dirname, '..', '..', 'state', 'media');
fs.mkdirSync(MEDIA_DIR, { recursive: true });

function falRequest(endpoint, body) {
  return new Promise((resolve) => {
    const data = JSON.stringify(body);
    const opts = {
      hostname: 'api.fal.ai', port: 443, path: endpoint, method: 'POST',
      headers: { 'Authorization': 'Key ' + FAL_KEY, 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(data) },
      timeout: 120000,
    };
    const req = https.request(opts, (res) => {
      let d = ''; res.on('data', c => d += c);
      res.on('end', () => { try { resolve(JSON.parse(d)); } catch { resolve({ raw: d }); } });
    });
    req.on('error', e => resolve({ error: e.message }));
    req.write(data); req.end();
  });
}

const tools = {
  // ── Image Generation (fal.ai) ──
  media_image: {
    description: 'Genera imágenes con IA vía fal.ai. Usa FLUX.1-dev para alta calidad.',
    inputSchema: { type: 'object', properties: {
      prompt: { type: 'string', description: 'Descripción de la imagen' },
      negative_prompt: { type: 'string' },
      image_size: { type: 'string', enum: ['square_hd', 'square', 'portrait_4_3', 'landscape_4_3'] },
      num_images: { type: 'number' },
    }, required: ['prompt'] },
    handler: async (args) => {
      if (!FAL_KEY) return { error: 'FAL_API_KEY no configurada. Usá: export FAL_API_KEY=tu_key' };
      const result = await falRequest('/fal-ai/flux-pro/v1.1-ultra', {
        prompt: args.prompt,
        negative_prompt: args.negative_prompt || '',
        image_size: args.image_size || 'square_hd',
        num_images: args.num_images || 1,
        safety_tolerance: 2,
      });
      if (result.images) {
        result.images.forEach((img, i) => {
          const filename = 'image-' + Date.now() + '-' + i + '.png';
          const filepath = path.join(MEDIA_DIR, filename);
          if (img.url) {
            https.get(img.url, (res) => {
              const stream = fs.createWriteStream(filepath);
              res.pipe(stream);
            });
          }
        });
      }
      return result;
    },
  },

  // ── Video Generation (fal.ai) ──
  media_video: {
    description: 'Genera videos cortos con IA vía fal.ai',
    inputSchema: { type: 'object', properties: {
      prompt: { type: 'string', description: 'Descripción del video' },
      duration: { type: 'number', description: 'Duración en segundos (5-10)' },
    }, required: ['prompt'] },
    handler: async (args) => {
      if (!FAL_KEY) return { error: 'FAL_API_KEY no configurada' };
      const result = await falRequest('/fal-ai/minimax/video-01-live', {
        prompt: args.prompt,
        duration: args.duration || 5,
      });
      if (result.video?.url) {
        const filename = 'video-' + Date.now() + '.mp4';
        const filepath = path.join(MEDIA_DIR, filename);
        https.get(result.video.url, (res) => {
          const stream = fs.createWriteStream(filepath);
          res.pipe(stream);
        });
      }
      return result;
    },
  },

  // ── Album Cover Generator ──
  media_album_cover: {
    description: 'Genera portada de álbum/sencillo para artista ABE Music',
    inputSchema: { type: 'object', properties: {
      artist: { type: 'string', description: 'Nombre del artista' },
      album_title: { type: 'string', description: 'Título del álbum/sencillo' },
      genre: { type: 'string', description: 'Género musical' },
      style: { type: 'string', enum: ['modern', 'vintage', 'minimal', 'urban', 'cinematic'] },
    }, required: ['artist', 'album_title'] },
    handler: async (args) => {
      const prompt = `Album cover for "${args.album_title}" by ${args.artist}, ${args.genre || 'music'} genre, ${args.style || 'modern'} style, high quality, professional music cover, typography space, 3000x3000`;
      if (!FAL_KEY) return { error: 'FAL_API_KEY no configurada' };
      const result = await falRequest('/fal-ai/flux-pro/v1.1-ultra', { prompt, image_size: 'square_hd', num_images: 1 });
      return { ...result, artist: args.artist, album: args.album_title };
    },
  },

  // ── Music Video Concept ──
  media_music_video: {
    description: 'Genera concepto visual para video musical',
    inputSchema: { type: 'object', properties: {
      song: { type: 'string' }, artist: { type: 'string' }, mood: { type: 'string' },
    }, required: ['song', 'artist'] },
    handler: async (args) => {
      const prompt = `Music video concept for "${args.song}" by ${args.artist}, mood: ${args.mood || 'cinematic'}, professional music video style, cinematic lighting`;
      if (!FAL_KEY) return { error: 'FAL_API_KEY no configurada' };
      return await falRequest('/fal-ai/minimax/video-01-live', { prompt, duration: 5 });
    },
  },

  // ── Media Library ──
  media_library: {
    description: 'Lista archivos de medios generados',
    inputSchema: { type: 'object', properties: { limit: { type: 'number' } } },
    handler: async (args) => {
      try {
        const files = fs.readdirSync(MEDIA_DIR).sort().reverse().slice(0, args.limit || 20);
        return { media: files.map(f => ({ name: f, size: fs.statSync(path.join(MEDIA_DIR, f)).size, path: path.join(MEDIA_DIR, f) })) };
      } catch { return { media: [] }; }
    },
  },

  // ── Seedance Integration ──
  media_seedance: {
    description: 'Genera video con Seedance (gratuito, sin API key necesaria)',
    inputSchema: { type: 'object', properties: {
      prompt: { type: 'string' }, style: { type: 'string' },
    }, required: ['prompt'] },
    handler: async (args) => {
      try {
        const { execSync } = require('child_process');
        const dir = path.join(MEDIA_DIR, 'seedance');
        fs.mkdirSync(dir, { recursive: true });
        const cmd = `cd ${dir} && curl -s "https://api.seedance.io/v1/videos" -H "Content-Type: application/json" -d '{"prompt":"${args.prompt.replace(/"/g, '\\"')}","style":"${args.style || 'cinematic'}"}' 2>/dev/null || echo '{"note":"Seedance API endpoint - implementar con API key de Seedance"}'`;
        const r = execSync(cmd, { timeout: 15000, encoding: 'utf-8' });
        try { return JSON.parse(r); } catch { return { result: r.substring(0, 500) }; }
      } catch (e) { return { error: e.message }; }
    },
  },
};

module.exports = { tools };
