import { MercadoPagoConfig, Preference, PreApproval } from 'mercadopago'

const mpToken = process.env.MP_ACCESS_TOKEN
let client = null
if (mpToken) {
  client = new MercadoPagoConfig({ accessToken: mpToken })
}

export async function createMPPreference({ lesson_id, title, amount_mxn, user_id, email }) {
  if (!client) return { id: `mp_stub_${lesson_id}`, url: `https://example.com/mp/checkout/${lesson_id}` }
  const preference = new Preference(client)
  const result = await preference.create({
    body: {
      items: [{ title, quantity: 1, unit_price: amount_mxn, currency_id: 'MXN' }],
      payer: { email },
      back_urls: {
        success: `${process.env.FRONTEND_URL}/lesson/${lesson_id}`,
        failure: `${process.env.FRONTEND_URL}/lesson/${lesson_id}`,
        pending: `${process.env.FRONTEND_URL}/lesson/${lesson_id}`,
      },
      auto_return: 'approved',
      external_reference: String(lesson_id),
      metadata: { user_id, lesson_id, type: 'lesson' },
    },
  })
  return { id: result.id, url: result.init_point }
}

export async function createMPPreapproval({ plan, user_id, email, amount_mxn }) {
  if (!client) return { id: `mp_stub_sub_${plan}`, url: `https://example.com/mp/subscribe/${plan}` }
  const preapproval = new PreApproval(client)
  const result = await preapproval.create({
    body: {
      reason: `Mystika - Plan ${plan}`,
      auto_recurring: {
        frequency: 1,
        frequency_type: 'months',
        transaction_amount: amount_mxn,
        currency_id: 'MXN',
      },
      payer_email: email,
      back_url: `${process.env.FRONTEND_URL}/portal`,
      external_reference: String(user_id),
      metadata: { plan, user_id, type: 'subscription' },
    },
  })
  return { id: result.id, url: result.init_point }
}

export async function handleMPWebhook(notification) {
  if (notification.type === 'payment' || notification.topic === 'payment') {
    const paymentId = notification.data?.id || notification.id
    const { pool } = await import('../db/index.js')
    await pool.query(
      `UPDATE purchases SET status = 'approved', gateway_payment_id = $1
       WHERE gateway_preference_id = $2`,
      [paymentId, notification.preference_id]
    )
    return { handled: true, payment_id: paymentId }
  }
  if (notification.type === 'subscription' || notification.topic === 'subscription') {
    const { pool } = await import('../db/index.js')
    await pool.query(
      `UPDATE subscriptions SET status = 'active'
       WHERE gateway_subscription_id = $1`,
      [notification.data?.id]
    )
    return { handled: true, subscription_id: notification.data?.id }
  }
  return { handled: true, topic: notification.topic || notification.type }
}
