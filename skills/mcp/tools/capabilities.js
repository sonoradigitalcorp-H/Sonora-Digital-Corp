// SDC Capabilities MCP Tools — expose 8 capabilities as executable MCP tools
// Each tool calls the corresponding handler.py via CapabilityBus
const { execSync } = require('child_process');
const path = require('path');

const SDC_DIR = path.resolve(__dirname, '../../..');
const CAPABILITIES_DIR = path.join(SDC_DIR, 'skills');

function runCapability(id, params = {}) {
  const capDir = path.join(CAPABILITIES_DIR, id, 'skills');
  const handler = path.join(capDir, 'handler.py');
  try {
    const result = execSync(
      `cd ${SDC_DIR} && python3 ${handler} '${JSON.stringify(params)}'`,
      { encoding: 'utf-8', timeout: 30000 }
    );
    return JSON.parse(result.trim());
  } catch (e) {
    return { error: e.message, capability: id };
  }
}

module.exports = [
  {
    name: 'sync_artist_data',
    description: 'Sync artist data from all providers (Spotify, YouTube, Deezer, Apple Music, Instagram, TikTok)',
    inputSchema: { type: 'object', properties: { artist_id: { type: 'string' }, providers: { type: 'array', items: { type: 'string' } } } },
    handler: (params) => runCapability('sync-artist-data', params),
  },
  {
    name: 'analyze_artist',
    description: 'Analyze artist performance, trends, and opportunities',
    inputSchema: { type: 'object', properties: { artist_id: { type: 'string' } } },
    handler: (params) => runCapability('analyze-artist', params),
  },
  {
    name: 'search_knowledge',
    description: 'Search across all memory stores (semantic, graph, long-term, working)',
    inputSchema: { type: 'object', properties: { query: { type: 'string' }, stores: { type: 'array', items: { type: 'string' } } } },
    handler: (params) => runCapability('search-knowledge', params),
  },
  {
    name: 'score_artist',
    description: 'Compute artist scores (momentum, virality, tour readiness, engagement, revenue)',
    inputSchema: { type: 'object', properties: { artist_id: { type: 'string' } } },
    handler: (params) => runCapability('score-artist', params),
  },
  {
    name: 'generate_video',
    description: 'Generate talking head or lipsync videos from audio + image',
    inputSchema: { type: 'object', properties: { audio: { type: 'string' }, image: { type: 'string' }, text: { type: 'string' } } },
    handler: (params) => runCapability('generate-video', params),
  },
  {
    name: 'manage_crm',
    description: 'Manage artist CRM: contacts, leads, follow-ups, pipeline',
    inputSchema: { type: 'object', properties: { action: { type: 'string' }, artist_id: { type: 'string' }, data: { type: 'object' } } },
    handler: (params) => runCapability('manage-crm', params),
  },
  {
    name: 'publish_track',
    description: 'Publish tracks to distribution platforms (Spotify, Apple Music, YouTube, TikTok, Deezer)',
    inputSchema: { type: 'object', properties: { track_id: { type: 'string' }, platforms: { type: 'array', items: { type: 'string' } } } },
    handler: (params) => runCapability('publish-track', params),
  },
  {
    name: 'process_payment',
    description: 'Process payments via Stripe or Mercado Pago',
    inputSchema: { type: 'object', properties: { amount: { type: 'number' }, currency: { type: 'string' }, provider: { type: 'string' }, customer: { type: 'string' } } },
    handler: (params) => runCapability('process-payment', params),
  },
];
