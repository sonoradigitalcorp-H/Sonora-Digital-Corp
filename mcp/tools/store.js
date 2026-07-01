const http = require('http');
const FASTAPI = { host: '127.0.0.1', port: 8000 };

function api(method, path, body) {
  return new Promise((resolve) => {
    const data = body ? JSON.stringify(body) : null;
    const req = http.request({ hostname: FASTAPI.host, port: FASTAPI.port, path, method,
      headers: { 'Content-Type': 'application/json' }, timeout: 15000 }, (res) => {
      let d = ''; res.on('data', c => d += c); res.on('end', () => { try { resolve(JSON.parse(d)); } catch { resolve({ raw: d }); } });
    });
    req.on('error', (e) => resolve({ error: e.message }));
    if (data) req.write(data);
    req.end();
  });
}

const tools = {
  store_products: {
    description: 'Lista productos de la tienda',
    inputSchema: { type: 'object', properties: {} },
    handler: async () => await api('GET', '/api/store/products'),
  },
  store_featured: {
    description: 'Obtiene productos destacados',
    inputSchema: { type: 'object', properties: {} },
    handler: async () => await api('GET', '/api/store/featured'),
  },
  store_create_order: {
    description: 'Crea una orden en la tienda',
    inputSchema: { type: 'object', properties: {
      product_id: { type: 'string' }, customer: { type: 'object' }, payment: { type: 'object' },
    }, required: ['product_id'] },
    handler: async (args) => await api('POST', '/api/store/order', args),
  },
  store_get_order: {
    description: 'Obtiene detalle de una orden',
    inputSchema: { type: 'object', properties: { order_id: { type: 'string' } }, required: ['order_id'] },
    handler: async (args) => await api('GET', '/api/store/orders/' + args.order_id),
  },
};

module.exports = { tools };
