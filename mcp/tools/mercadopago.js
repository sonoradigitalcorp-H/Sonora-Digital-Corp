/**
 * Mercado Pago MCP Tool
 * Integración de pagos para la plataforma SaaS.
 * Soporta: crear preferencia, verificar pago, webhook, suscripciones.
 */
const https = require('https');
const MP_ACCESS_TOKEN = process.env.MERCADO_PAGO_ACCESS_TOKEN || '';
const MP_API = 'api.mercadopago.com';

function mpRequest(method, path, data = null) {
  return new Promise((resolve) => {
    if (!MP_ACCESS_TOKEN) return resolve({ error: 'MERCADO_PAGO_ACCESS_TOKEN no configurado' });
    const body = data ? JSON.stringify(data) : '';
    const options = {
      hostname: MP_API,
      path,
      method,
      headers: {
        'Authorization': `Bearer ${MP_ACCESS_TOKEN}`,
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(body),
        'X-Idempotency-Key': `${Date.now()}-${Math.random().toString(36).substring(2, 8)}`,
      },
      timeout: 15000,
    };
    const req = https.request(options, (res) => {
      let r = '';
      res.on('data', c => r += c);
      res.on('end', () => { try { resolve(JSON.parse(r)); } catch { resolve({ error: r }); } });
    });
    req.on('error', (e) => resolve({ error: e.message }));
    req.write(body);
    req.end();
  });
}

module.exports = [
  {
    name: 'mercadopago_create_preference',
    description: 'Crea una preferencia de pago en Mercado Pago para cobrar un plan.',
    input_schema: {
      type: 'object',
      properties: {
        title: { type: 'string', description: 'Nombre del producto/plan' },
        price: { type: 'number', description: 'Precio en USD/MXN' },
        quantity: { type: 'number', description: 'Cantidad (default: 1)' },
        email: { type: 'string', description: 'Email del comprador' },
        plan_id: { type: 'string', description: 'ID del plan (starter/pro/enterprise)' },
        tenant_id: { type: 'string', description: 'ID del tenant' },
        back_urls: {
          type: 'object',
          properties: {
            success: { type: 'string' },
            failure: { type: 'string' },
            pending: { type: 'string' },
          },
        },
      },
      required: ['title', 'price', 'email', 'plan_id'],
    },
    handler: async (args) => {
      const preference = {
        items: [{
          title: args.title,
          unit_price: Number(args.price),
          quantity: args.quantity || 1,
          currency_id: 'MXN',
        }],
        payer: { email: args.email },
        back_urls: args.back_urls || {
          success: `https://abe.sonoradigitalcorp.com/dashboard?plan=${args.plan_id}&status=success`,
          failure: `https://abe.sonoradigitalcorp.com/pricing?status=failure`,
          pending: `https://abe.sonoradigitalcorp.com/dashboard?plan=${args.plan_id}&status=pending`,
        },
        auto_return: 'approved',
        external_reference: JSON.stringify({ plan_id: args.plan_id, tenant_id: args.tenant_id || '' }),
        notification_url: 'https://abe.sonoradigitalcorp.com/api/payments/webhook',
        purpose: 'plan_subscription',
      };
      const result = await mpRequest('POST', '/checkout/preferences', preference);
      if (result.error) return result;
      return {
        id: result.id,
        init_point: result.init_point,
        sandbox_init_point: result.sandbox_init_point,
        status: 'created',
        price: args.price,
        plan: args.plan_id,
      };
    },
  },

  {
    name: 'mercadopago_get_payment',
    description: 'Obtiene información de un pago por ID.',
    input_schema: {
      type: 'object',
      properties: {
        payment_id: { type: 'string', description: 'ID del pago en MP' },
      },
      required: ['payment_id'],
    },
    handler: async (args) => {
      return await mpRequest('GET', `/v1/payments/${args.payment_id}`);
    },
  },

  {
    name: 'mercadopago_create_subscription',
    description: 'Crea una suscripción recurrente para un plan.',
    input_schema: {
      type: 'object',
      properties: {
        email: { type: 'string', description: 'Email del comprador' },
        plan_id: { type: 'string', description: 'ID del plan' },
        price: { type: 'number', description: 'Precio mensual' },
        tenant_id: { type: 'string', description: 'ID del tenant' },
      },
      required: ['email', 'plan_id', 'price'],
    },
    handler: async (args) => {
      const subscription = {
        reason: `Suscripción ${args.plan_id} - Sonora Digital Corp`,
        external_reference: JSON.stringify({ plan_id: args.plan_id, tenant_id: args.tenant_id || '' }),
        payer_email: args.email,
        auto_recurring: {
          frequency: 1,
          frequency_type: 'months',
          transaction_amount: Number(args.price),
          currency_id: 'MXN',
          repetitions: 12,
        },
        back_url: 'https://abe.sonoradigitalcorp.com/dashboard',
        notification_url: 'https://abe.sonoradigitalcorp.com/api/payments/webhook',
      };
      return await mpRequest('POST', '/preapproval', subscription);
    },
  },

  {
    name: 'mercadopago_webhook_handler',
    description: 'Procesa notificaciones de webhook de Mercado Pago.',
    input_schema: {
      type: 'object',
      properties: {
        type: { type: 'string', description: 'Tipo de notificación (payment, plan, subscription)' },
        action: { type: 'string', description: 'Acción (created, updated, approved, etc.)' },
        data_id: { type: 'string', description: 'ID del recurso' },
      },
    },
    handler: async (args) => {
      if (args.type === 'payment') {
        const payment = await mpRequest('GET', `/v1/payments/${args.data_id}`);
        return { status: payment.status, payment };
      }
      if (args.type === 'subscription' || args.type === 'plan') {
        const sub = await mpRequest('GET', `/preapproval/${args.data_id}`);
        return { status: sub.status, subscription: sub };
      }
      return { received: true, type: args.type, action: args.action };
    },
  },

  {
    name: 'mercadopago_get_plans',
    description: 'Lista los planes de suscripción disponibles.',
    input_schema: { type: 'object', properties: {} },
    handler: async () => {
      return {
        plans: [
          { id: 'starter', name: 'Starter', price: 0, period: 'month', description: 'Para empezar' },
          { id: 'pro', name: 'Pro', price: 49, period: 'month', description: 'Para negocios' },
          { id: 'enterprise', name: 'Enterprise', price: 199, period: 'month', description: 'Para empresas' },
        ],
      };
    },
  },
];
