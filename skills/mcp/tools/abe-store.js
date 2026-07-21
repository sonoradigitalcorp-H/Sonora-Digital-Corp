/**
 * ABE Store — Monetization System
 * Merch · Events · Commissions · Tokens · Gamification
 * Play-to-earn · Work-to-earn · Learn-to-earn
 */

const fs = require('fs');
const path = require('path');

const STORE_FILE = path.join(__dirname, '..', '..', 'state', 'abe-store.json');
const EVENTS_FILE = path.join(__dirname, '..', '..', 'state', 'logs', 'events.jsonl');
const CONTENT_DIR = path.join(__dirname, '..', '..', 'state', 'merch-designs');

fs.mkdirSync(CONTENT_DIR, { recursive: true });

function _loadStore() {
  try {
    if (fs.existsSync(STORE_FILE)) return JSON.parse(fs.readFileSync(STORE_FILE, 'utf-8'));
  } catch {}
  return { products: [], orders: [], commissions: [], tokens: {}, events: [], gamification: { players: {}, leaderboard: [] }, revenue: { total: 0, artist_paid: 0 } };
}

function _saveStore(data) {
  try { fs.writeFileSync(STORE_FILE, JSON.stringify(data, null, 2)); } catch {}
}

function _emit(event, detail) {
  try {
    fs.appendFileSync(EVENTS_FILE, JSON.stringify({ event, producer: 'abe-store', timestamp: new Date().toISOString(), payload: detail }) + '\n');
  } catch {}
}

const PRODUCT_TYPES = {
  tshirt: { name: 'Playera', base_price: 25, commission: 0.15, icon: '👕' },
  hoodie: { name: 'Hoodie', base_price: 55, commission: 0.15, icon: '🧥' },
  cap: { name: 'Gorra', base_price: 20, commission: 0.15, icon: '🧢' },
  poster: { name: 'Póster', base_price: 15, commission: 0.20, icon: '🖼️' },
  digital: { name: 'Contenido Digital', base_price: 10, commission: 0.25, icon: '💿' },
  ticket: { name: 'Boleto Evento', base_price: 35, commission: 0.10, icon: '🎫' },
  token: { name: 'Token $RESO', base_price: 1, commission: 0, icon: '🪙' },
};

const TOKEN_ACTIONS = {
  daily_login: { xp: 10, tokens: 5, desc: 'Login diario' },
  share_content: { xp: 25, tokens: 10, desc: 'Compartir contenido' },
  create_content: { xp: 50, tokens: 25, desc: 'Crear contenido' },
  buy_merch: { xp: 100, tokens: 50, desc: 'Comprar merch' },
  attend_event: { xp: 200, tokens: 100, desc: 'Asistir a evento' },
  refer_friend: { xp: 150, tokens: 75, desc: 'Referir amigo' },
  review_product: { xp: 30, tokens: 15, desc: 'Reseñar producto' },
  complete_profile: { xp: 20, tokens: 10, desc: 'Completar perfil' },
};

const tools = {
  // ─── Store Products ───
  store_products: {
    description: 'Productos en la tienda ABE Music por artista',
    inputSchema: { type: 'object', properties: { artist: { type: 'string' }, category: { type: 'string', enum: Object.keys(PRODUCT_TYPES) } } },
    handler: async (args) => {
      const store = _loadStore();
      let products = store.products || [];
      if (args.artist) products = products.filter(p => p.artist === args.artist);
      if (args.category) products = products.filter(p => p.type === args.category);
      return { products, total: products.length, artist: args.artist || 'all' };
    },
  },

  // ─── Create Product ───
  store_create_product: {
    description: 'Crea producto de merch para un artista',
    inputSchema: { type: 'object', properties: {
      artist: { type: 'string' }, name: { type: 'string' }, type: { type: 'string', enum: Object.keys(PRODUCT_TYPES) },
      price: { type: 'number' }, description: { type: 'string' }, event_id: { type: 'string' },
      design_prompt: { type: 'string' }, limited_edition: { type: 'boolean' },
    }, required: ['artist', 'name', 'type'] },
    handler: async (args) => {
      const store = _loadStore();
      const productType = PRODUCT_TYPES[args.type] || PRODUCT_TYPES.tshirt;
      const price = args.price || productType.base_price;
      const commission = price * productType.commission;

      const product = {
        id: `merch-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`,
        artist: args.artist, name: args.name, type: args.type, icon: productType.icon,
        price, commission_amount: commission, commission_pct: productType.commission * 100,
        description: args.description || `${productType.name} de ${args.artist}`,
        event_id: args.event_id || null,
        limited_edition: args.limited_edition || false,
        design_prompt: args.design_prompt || null,
        created_at: new Date().toISOString(),
        sales: 0, revenue: 0, status: 'active',
      };

      store.products.push(product);
      _saveStore(store);
      _emit('product_created', { product_id: product.id, artist: args.artist, type: args.type });

      return { status: 'created', product };
    },
  },

  // ─── Record Sale ───
  store_sale: {
    description: 'Registra venta de merch, calcula comisión del artista automáticamente',
    inputSchema: { type: 'object', properties: {
      product_id: { type: 'string' }, buyer: { type: 'string' }, quantity: { type: 'number' },
      payment_method: { type: 'string', enum: ['spei', 'crypto', 'card', 'tokens'] },
    }, required: ['product_id', 'buyer'] },
    handler: async (args) => {
      const store = _loadStore();
      const product = store.products.find(p => p.id === args.product_id);
      if (!product) return { error: 'Producto no encontrado' };

      const qty = args.quantity || 1;
      const total = product.price * qty;
      const commission = product.commission_amount * qty;

      const order = {
        id: `order-${Date.now()}`,
        product_id: args.product_id, product_name: product.name, artist: product.artist,
        buyer: args.buyer, quantity: qty, unit_price: product.price,
        total, artist_commission: commission, label_earns: total - commission,
        payment_method: args.payment_method || 'card',
        status: 'completed', created_at: new Date().toISOString(),
      };

      store.orders.push(order);
      product.sales += qty;
      product.revenue += total;
      store.revenue.total += total;
      store.revenue.artist_paid += commission;

      // Award tokens to buyer
      if (!store.tokens[args.buyer]) store.tokens[args.buyer] = { balance: 0, xp: 0, level: 1 };
      store.tokens[args.buyer].balance += Math.round(total * 0.1);
      store.tokens[args.buyer].xp += 100;

      _saveStore(store);
      _emit('sale_completed', { order_id: order.id, artist: product.artist, total });

      return {
        status: 'completed', order,
        buyer_tokens_earned: Math.round(total * 0.1),
        artist_earns: commission,
        label_earns: total - commission,
      };
    },
  },

  // ─── Commission Report ───
  store_commissions: {
    description: 'Reporte de comisiones por artista',
    inputSchema: { type: 'object', properties: { artist: { type: 'string' } } },
    handler: async (args) => {
      const store = _loadStore();
      const orders = args.artist ? store.orders.filter(o => o.artist === args.artist) : store.orders;
      const byArtist = {};
      orders.forEach(o => {
        if (!byArtist[o.artist]) byArtist[o.artist] = { sales: 0, revenue: 0, commission: 0, orders: 0 };
        byArtist[o.artist].sales += o.quantity;
        byArtist[o.artist].revenue += o.total;
        byArtist[o.artist].commission += o.artist_commission;
        byArtist[o.artist].orders += 1;
      });
      return { total_orders: orders.length, total_revenue: store.revenue.total, total_commissions: store.revenue.artist_paid, by_artist: byArtist };
    },
  },

  // ─── Token System ───
  store_tokens: {
    description: 'Sistema de tokens $RESO — balance, acciones, rewards',
    inputSchema: { type: 'object', properties: { user: { type: 'string' }, action: { type: 'string', enum: [...Object.keys(TOKEN_ACTIONS), 'balance', 'redeem'] }, amount: { type: 'number' } } },
    handler: async (args) => {
      const store = _loadStore();
      if (!store.tokens[args.user]) store.tokens[args.user] = { balance: 0, xp: 0, level: 1 };

      if (args.action === 'balance') {
        return { user: args.user, ...store.tokens[args.user], next_level_xp: store.tokens[args.user].level * 500 };
      }

      if (TOKEN_ACTIONS[args.action]) {
        const action = TOKEN_ACTIONS[args.action];
        store.tokens[args.user].balance += action.tokens;
        store.tokens[args.user].xp += action.xp;
        // Level up every 500 XP
        store.tokens[args.user].level = Math.floor(store.tokens[args.user].xp / 500) + 1;
        _saveStore(store);
        _emit('tokens_earned', { user: args.user, action: args.action, tokens: action.tokens, xp: action.xp });
        return { user: args.user, action: args.action, tokens_earned: action.tokens, xp_earned: action.xp, balance: store.tokens[args.user].balance, level: store.tokens[args.user].level };
      }

      if (args.action === 'redeem') {
        if (store.tokens[args.user].balance < (args.amount || 0)) return { error: 'Saldo insuficiente' };
        store.tokens[args.user].balance -= args.amount || 0;
        _saveStore(store);
        // Redeem tokens for discount on next purchase
        const discountValue = (args.amount || 0) * 0.01;
        return { user: args.user, redeemed: args.amount, discount_value: discountValue, new_balance: store.tokens[args.user].balance };
      }

      return { user: args.user, ...store.tokens[args.user] };
    },
  },

  // ─── Event Merch Generator ───
  store_event_merch: {
    description: 'Genera merch automático para un evento de artista',
    inputSchema: { type: 'object', properties: {
      artist: { type: 'string' }, event_name: { type: 'string' }, event_date: { type: 'string' },
      venue: { type: 'string' }, theme: { type: 'string' },
    }, required: ['artist', 'event_name'] },
    handler: async (args) => {
      const store = _loadStore();
      const products = [];

      // Generate multiple merch items for the event
      const merchTypes = ['tshirt', 'hoodie', 'cap', 'poster'];
      for (const type of merchTypes) {
        const pt = PRODUCT_TYPES[type];
        const name = `${args.event_name} ${pt.name}`;
        const price = pt.base_price + 5; // Event premium
        const product = {
          id: `merch-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`,
          artist: args.artist, name, type, icon: pt.icon, price,
          commission_amount: price * pt.commission, commission_pct: pt.commission * 100,
          description: `${pt.name} conmemorativo del evento "${args.event_name}" en ${args.venue || 'por definir'}. Edición limitada.`,
          event_id: `event-${args.event_name.toLowerCase().replace(/\s/g, '-')}`,
          event_name: args.event_name, event_date: args.event_date || null, venue: args.venue || null,
          theme: args.theme || 'music', limited_edition: true,
          design_prompt: `Merch design for ${args.artist} - ${args.event_name}, theme: ${args.theme || 'music'}`,
          created_at: new Date().toISOString(), sales: 0, revenue: 0, status: 'active',
        };
        store.products.push(product);
        products.push(product);
      }

      // Register event
      const eventEntry = { id: `event-${Date.now()}`, artist: args.artist, name: args.event_name, date: args.event_date || null, venue: args.venue || null, merch_count: products.length, created_at: new Date().toISOString() };
      store.events.push(eventEntry);

      _saveStore(store);
      _emit('event_merch_generated', { artist: args.artist, event: args.event_name, products: products.length });

      return {
        status: 'generated', event: eventEntry,
        products: products.map(p => ({ id: p.id, name: p.name, price: p.price, commission: p.commission_amount, icon: p.icon })),
        total_value: products.reduce((s, p) => s + p.price, 0),
        note: 'Merch generado. Revisa en store_products para ver detalles.',
      };
    },
  },

  // ─── Store Dashboard ───
  store_dashboard: {
    description: 'Dashboard completo de la tienda ABE Music',
    inputSchema: { type: 'object', properties: {} },
    handler: async () => {
      const store = _loadStore();
      const totalProducts = store.products.length;
      const totalOrders = store.orders.length;
      const totalRevenue = store.revenue.total;
      const totalCommissions = store.revenue.artist_paid;
      const activeArtists = [...new Set(store.products.filter(p => p.status === 'active').map(p => p.artist))];
      const tokenHolders = Object.keys(store.tokens).length;
      const totalTokens = Object.values(store.tokens).reduce((s, t) => s + t.balance, 0);

      return {
        stats: {
          products: totalProducts, orders: totalOrders, revenue: totalRevenue,
          artist_commissions: totalCommissions, active_artists: activeArtists.length,
          token_holders: tokenHolders, total_tokens_circulation: totalTokens,
        },
        top_products: store.products.sort((a, b) => b.sales - a.sales).slice(0, 5),
        recent_orders: store.orders.slice(-10).reverse(),
        revenue_split: {
          artists: Math.round(totalRevenue * 0.7),
          label: Math.round(totalRevenue * 0.2),
          platform: Math.round(totalRevenue * 0.1),
        },
        artists: activeArtists,
      };
    },
  },

  // ─── Gamification Leaderboard ───
  store_leaderboard: {
    description: 'Leaderboard de gamificación — play, work, learn to earn',
    inputSchema: { type: 'object', properties: { limit: { type: 'number' } } },
    handler: async (args) => {
      const store = _loadStore();
      const players = Object.entries(store.tokens).map(([user, data]) => ({ user, ...data }));
      players.sort((a, b) => b.xp - a.xp);
      return { leaderboard: players.slice(0, args.limit || 20), total_players: players.length };
    },
  },

  // ─── Artist Payout ───
  store_payout: {
    description: 'Calcula y registra pago a artista por comisiones',
    inputSchema: { type: 'object', properties: { artist: { type: 'string' }, period: { type: 'string' } } },
    handler: async (args) => {
      const store = _loadStore();
      const orders = store.orders.filter(o => o.artist === args.artist && !o.paid);
      const totalCommission = orders.reduce((s, o) => s + o.artist_commission, 0);

      if (totalCommission === 0) return { artist: args.artist, message: 'No hay comisiones pendientes' };

      orders.forEach(o => o.paid = true);
      _saveStore(store);
      _emit('artist_paid', { artist: args.artist, amount: totalCommission, orders: orders.length });

      return {
        status: 'paid', artist: args.artist, amount: totalCommission, orders_processed: orders.length,
        period: args.period || 'all',
      };
    },
  },
};

module.exports = { tools };
