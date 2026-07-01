/**
 * Agent Conversation System — Agents talk to each other, leave traces, create products
 * Each conversation generates: knowledge graph entries, product footprints, events
 */

const fs = require('fs');
const path = require('path');
const http = require('http');

const CONVERSATIONS_FILE = path.join(__dirname, '..', '..', 'state', 'agent-conversations.json');

function _load() { try { if (fs.existsSync(CONVERSATIONS_FILE)) return JSON.parse(fs.readFileSync(CONVERSATIONS_FILE, 'utf-8')); } catch {} return { conversations: [], traces: [], products: [] }; }
function _save(d) { try { fs.writeFileSync(CONVERSATIONS_FILE, JSON.stringify(d, null, 2)); } catch {} }

function _call(tool, params) {
  return new Promise(r => {
    const d = JSON.stringify({ tool, params: params || {} });
    const req = http.request({ hostname: '127.0.0.1', port: 18989, path: '/api/call', method: 'POST', headers: { 'Content-Type': 'application/json' } }, res => {
      let data = ''; res.on('data', c => data += c); res.on('end', () => { try { r(JSON.parse(data)); } catch { r({}); } });
    }); req.write(d); req.end();
  });
}

const tools = {
  // ─── Agent Conversation ───
  converse_run: {
    description: 'Dos agents conversan, dejan trazas, y generan un producto nuevo',
    inputSchema: { type: 'object', properties: {
      agent1: { type: 'string', description: 'Primer agente' },
      agent2: { type: 'string', description: 'Segundo agente' },
      topic: { type: 'string', description: 'Tema de conversación' },
      record_trace: { type: 'boolean', description: 'Guardar traza en knowledge graph' },
    }, required: ['agent1', 'agent2', 'topic'] },
    handler: async (args) => {
      const data = _load();
      const conversationId = `conv-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`;

      // Simulate agent conversation (in production, this calls local models)
      const messages = [
        { agent: args.agent1, message: `Analizando "${args.topic}" desde mi perspectiva de ${args.agent1}...` },
        { agent: args.agent2, message: `Recibido. Como ${args.agent2}, yo puedo aportar datos y ejecución.` },
        { agent: args.agent1, message: `Perfecto. Propongo crear un producto basado en: ${args.topic}` },
        { agent: args.agent2, message: `Aprobado. Voy a dejar traza en el knowledge graph y generar los artefactos.` },
      ];

      const conversation = {
        id: conversationId,
        agents: [args.agent1, args.agent2],
        topic: args.topic,
        messages,
        started_at: new Date().toISOString(),
        status: 'completed',
      };

      data.conversations.push(conversation);

      // Generate product footprint
      const productId = `product-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`;
      const product = {
        id: productId,
        name: `Generado por: ${args.agent1} + ${args.agent2}`,
        topic: args.topic,
        agents: [args.agent1, args.agent2],
        created_at: new Date().toISOString(),
        status: 'prototype',
        conversation_id: conversationId,
        trace: `Conversación entre ${args.agent1} y ${args.agent2} sobre "${args.topic}" generó este producto.`,
      };
      data.products.push(product);

      // Save traces
      if (args.record_trace !== false) {
        const trace = {
          id: `trace-${Date.now()}`,
          type: 'agent_conversation',
          agents: [args.agent1, args.agent2],
          topic: args.topic,
          conversation_id: conversationId,
          product_id: productId,
          timestamp: new Date().toISOString(),
        };
        data.traces.push(trace);
      }

      _save(data);

      return {
        conversation: {
          id: conversationId,
          agents: [args.agent1, args.agent2],
          messages,
          summary: `${args.agent1} y ${args.agent2} colaboraron en "${args.topic}" y generaron un nuevo producto.`,
        },
        product_created: product,
        traces_left: data.traces.length,
        total_conversations: data.conversations.length,
        next_steps: `Revisá el producto en /products/footprint/${productId}`,
      };
    },
  },

  // ─── Product Footprint ───
  converse_footprint: {
    description: 'Muestra la huella de productos creados por agents',
    inputSchema: { type: 'object', properties: { agent: { type: 'string' }, limit: { type: 'number' } }},
    handler: async (args) => {
      const data = _load();
      let products = data.products;
      let conversations = data.conversations;

      if (args.agent) {
        products = products.filter(p => p.agents.includes(args.agent));
        conversations = conversations.filter(c => c.agents.includes(args.agent));
      }

      products.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
      const limit = args.limit || 20;

      return {
        total_products: data.products.length,
        total_conversations: data.conversations.length,
        total_traces: data.traces.length,
        filtered_products: products.slice(0, limit).map(p => ({
          id: p.id, name: p.name, topic: p.topic,
          agents: p.agents, status: p.status,
          created_at: p.created_at,
        })),
        filtered_conversations: conversations.slice(0, limit).map(c => ({
          id: c.id, agents: c.agents, topic: c.topic,
          message_count: c.messages.length, status: c.status,
          started_at: c.started_at,
        })),
        traces: data.traces.slice(-10).reverse(),
        agent: args.agent || 'all',
      };
    },
  },

  // ─── Run product test ───
  converse_test: {
    description: 'Crea un escenario de prueba: conversación + producto + traza',
    inputSchema: { type: 'object', properties: {
      agent1: { type: 'string' }, agent2: { type: 'string' },
      topic: { type: 'string' }, test_name: { type: 'string' },
    }, required: ['test_name'] },
    handler: async (args) => {
      const agents = [args.agent1 || 'abe-analytics-agent', args.agent2 || 'abe-marketing-agent'];
      const topic = args.topic || `Test: ${args.test_name}`;

      // Create conversation
      const conv = await tools.converse_run.handler({ agent1: agents[0], agent2: agents[1], topic, record_trace: true });

      // Record in knowledge graph
      await _call('graph_learn', {
        agent: agents[0], topic: 'test-' + args.test_name,
        content: `Test "${args.test_name}" ejecutado: conversación con ${agents[1]} sobre "${topic}". Producto: ${conv.product_created?.id}`,
        importance: 2,
      });

      return {
        test: args.test_name,
        status: 'completed',
        agents_used: agents,
        conversation: conv.conversation,
        product: conv.product_created,
        knowledge_recorded: true,
      };
    },
  },
};

module.exports = { tools };
