/**
 * Knowledge Graph — Agent memory system (like Obsidian but for agents)
 * Neo4j + Qdrant + JSON fallback
 * Agents record what they learn, the graph connects everything
 * Context: who learned what, when, why, connected to what
 */

const fs = require('fs');
const path = require('path');
const http = require('http');

const NEO4J_HOST = '127.0.0.1';
const NEO4J_PORT = 7687;
const NEO4J_AUTH = 'Basic ' + Buffer.from('neo4j:jarvis2026').toString('base64');

const GRAPH_FILE = path.join(__dirname, '..', '..', 'state', 'knowledge-graph.json');
const EVENTS_FILE = path.join(__dirname, '..', '..', 'state', 'logs', 'events.jsonl');

function _load() {
  try { if (fs.existsSync(GRAPH_FILE)) return JSON.parse(fs.readFileSync(GRAPH_FILE, 'utf-8')); } catch {}
  return { nodes: [], edges: [], agents: {}, sessions: 0 };
}

function _save(data) { try { fs.writeFileSync(GRAPH_FILE, JSON.stringify(data, null, 2)); } catch {} }

function _emit(event, detail) {
  try { fs.appendFileSync(EVENTS_FILE, JSON.stringify({ event, producer: 'knowledge-graph', timestamp: new Date().toISOString(), payload: detail }) + '\n'); } catch {}
}

const tools = {
  // ─── Record Agent Learning ───
  graph_learn: {
    description: 'Un agente aprende algo y lo guarda en el grafo de conocimiento',
    inputSchema: { type: 'object', properties: {
      agent: { type: 'string', description: 'Nombre del agente que aprendió' },
      topic: { type: 'string', description: 'Topic o capability aprendida' },
      content: { type: 'string', description: 'Qué aprendió (máx 1000 chars)' },
      context: { type: 'string', description: 'Contexto: tarea, error, descubrimiento' },
      related_to: { type: 'array', items: { type: 'string' }, description: 'Nodos relacionados' },
      importance: { type: 'number', enum: [0, 1, 2, 3] },
    }, required: ['agent', 'topic', 'content'] },
    handler: async (args) => {
      const graph = _load();
      const nodeId = `knowledge-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`;

      const node = {
        id: nodeId, type: 'knowledge',
        agent: args.agent, topic: args.topic,
        content: args.content.substring(0, 1000),
        context: args.context || '',
        importance: args.importance || 1,
        created_at: new Date().toISOString(),
        access_count: 0,
        last_accessed: null,
      };

      graph.nodes.push(node);
      graph.sessions = (graph.sessions || 0) + 1;

      // Track per-agent learning
      if (!graph.agents[args.agent]) graph.agents[args.agent] = { learnings: 0, topics: [], last_active: null };
      graph.agents[args.agent].learnings++;
      if (!graph.agents[args.agent].topics.includes(args.topic)) graph.agents[args.agent].topics.push(args.topic);
      graph.agents[args.agent].last_active = new Date().toISOString();

      // Create edges to related nodes
      if (args.related_to) {
        for (const rel of args.related_to) {
          graph.edges.push({
            from: nodeId, to: rel,
            relation: 'related_to',
            created_at: new Date().toISOString(),
            weight: 1,
          });
        }
      }

      _save(graph);
      _emit('knowledge_stored', { agent: args.agent, topic: args.topic, importance: args.importance });

      return {
        status: 'learned', node_id: nodeId,
        agent: args.agent, topic: args.topic,
        total_knowledge: graph.nodes.length,
        agent_total: graph.agents[args.agent].learnings,
      };
    },
  },

  // ─── Query Knowledge Graph ───
  graph_query: {
    description: 'Busca en el grafo de conocimiento por topic, agente, o palabra clave',
    inputSchema: { type: 'object', properties: {
      query: { type: 'string' }, agent: { type: 'string' }, topic: { type: 'string' },
      limit: { type: 'number' }, min_importance: { type: 'number' },
    }},
    handler: async (args) => {
      const graph = _load();
      let results = [...graph.nodes];

      if (args.agent) results = results.filter(n => n.agent === args.agent);
      if (args.topic) results = results.filter(n => n.topic === args.topic);
      if (args.query) {
        const q = args.query.toLowerCase();
        results = results.filter(n => n.content.toLowerCase().includes(q) || n.topic.toLowerCase().includes(q));
      }
      if (args.min_importance) results = results.filter(n => n.importance >= args.min_importance);

      results.sort((a, b) => b.importance - a.importance);
      results = results.slice(0, args.limit || 20);

      // Mark accessed
      results.forEach(n => { n.access_count++; n.last_accessed = new Date().toISOString(); });
      _save(graph);

      // Find connections
      const enriched = results.map(n => ({
        ...n,
        connections: graph.edges.filter(e => e.from === n.id || e.to === n.id).map(e => ({
          to: e.from === n.id ? e.to : e.from,
          relation: e.relation,
        })),
      }));

      return {
        query: args.query || 'all',
        total_results: enriched.length,
        total_knowledge: graph.nodes.length,
        results: enriched,
      };
    },
  },

  // ─── Get Agent Profile ───
  graph_profile: {
    description: 'Perfil completo de un agente: qué sabe, qué ha aprendido, conexiones',
    inputSchema: { type: 'object', properties: { agent: { type: 'string' } }, required: ['agent'] },
    handler: async (args) => {
      const graph = _load();
      const agentData = graph.agents[args.agent];
      if (!agentData) return { agent: args.agent, status: 'unknown', message: 'No learning data yet' };

      const learnings = graph.nodes.filter(n => n.agent === args.agent);
      const connections = graph.edges.filter(e => {
        const n = graph.nodes.find(n => n.id === e.from || n.id === e.to);
        return n && n.agent === args.agent;
      });

      return {
        agent: args.agent,
        total_learnings: agentData.learnings,
        topics: agentData.topics,
        last_active: agentData.last_active,
        recent_learnings: learnings.sort((a, b) => new Date(b.created_at) - new Date(a.created_at)).slice(0, 10),
        connections_count: connections.length,
        influence: learnings.reduce((s, n) => s + n.access_count, 0),
      };
    },
  },

  // ─── Graph Stats ───
  graph_stats: {
    description: 'Estadísticas del grafo de conocimiento multiagente',
    inputSchema: { type: 'object', properties: {} },
    handler: async () => {
      const graph = _load();
      const agents = Object.entries(graph.agents).map(([name, data]) => ({
        name, learnings: data.learnings, topics: data.topics.length, last_active: data.last_active,
      })).sort((a, b) => b.learnings - a.learnings);

      return {
        total_knowledge_nodes: graph.nodes.length,
        total_connections: graph.edges.length,
        active_agents: agents.length,
        total_sessions: graph.sessions,
        top_agents: agents.slice(0, 10),
        most_learned_topics: Object.entries(
          graph.nodes.reduce((acc, n) => { acc[n.topic] = (acc[n.topic] || 0) + 1; return acc; }, {})
        ).sort((a, b) => b[1] - a[1]).slice(0, 10),
        network_density: graph.nodes.length > 1 ? (graph.edges.length / (graph.nodes.length * (graph.nodes.length - 1) / 2) * 100).toFixed(2) : 0,
      };
    },
  },
};

module.exports = { tools };
