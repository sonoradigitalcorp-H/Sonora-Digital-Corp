import Stripe from 'stripe'

const stripeKey = process.env.STRIPE_SECRET_KEY
let stripe = null
if (stripeKey) {
  stripe = new Stripe(stripeKey)
}

export async function createStripeCheckout({ lesson_id, title, amount_usd, user_id, email, metadata = {} }) {
  if (!stripe) return { id: `stub_${lesson_id}`, url: `https://example.com/checkout/${lesson_id}` }
  const session = await stripe.checkout.sessions.create({
    payment_method_types: ['card'],
    line_items: [{
      price_data: {
        currency: 'usd',
        product_data: { name: title },
        unit_amount: Math.round(amount_usd * 100),
      },
      quantity: 1,
    }],
    mode: 'payment',
    success_url: `${process.env.FRONTEND_URL}/lesson/${lesson_id}?session_id={CHECKOUT_SESSION_ID}`,
    cancel_url: `${process.env.FRONTEND_URL}/lesson/${lesson_id}`,
    client_reference_id: String(user_id),
    customer_email: email,
    metadata: { ...metadata, lesson_id, user_id },
  })
  return { id: session.id, url: session.url }
}

export async function createStripeSubscription({ plan, user_id, email }) {
  if (!stripe) return { id: `stub_sub_${plan}`, url: `https://example.com/subscribe/${plan}` }
  const priceId = plan === 'mysteria'
    ? process.env.STRIPE_MYSTERIA_PRICE_ID
    : process.env.STRIPE_RITUAL_PRICE_ID
  const session = await stripe.checkout.sessions.create({
    payment_method_types: ['card'],
    line_items: [{ price: priceId, quantity: 1 }],
    mode: 'subscription',
    success_url: `${process.env.FRONTEND_URL}/portal?subscription=success`,
    cancel_url: `${process.env.FRONTEND_URL}/subscribe`,
    client_reference_id: String(user_id),
    customer_email: email,
    metadata: { plan, user_id, type: 'subscription' },
    subscription_data: { metadata: { plan, user_id } },
  })
  return { id: session.id, url: session.url }
}

export async function handleStripeWebhook(event) {
  const sig = event.headers?.['stripe-signature']
  if (!stripe || !sig) return { mode: 'stub' }
  let verified
  try {
    verified = stripe.webhooks.constructEvent(event.body, sig, process.env.STRIPE_WEBHOOK_SECRET)
  } catch {
    return { error: 'Webhook signature verification failed' }
  }
  if (verified.type === 'checkout.session.completed') {
    const session = verified.data.object
    const { pool } = await import('../db/index.js')
    if (session.mode === 'subscription') {
      await pool.query(
        `INSERT INTO subscriptions (user_id, plan, gateway, gateway_subscription_id, status, current_period_end)
         VALUES ($1, $2, 'stripe', $3, 'active', NOW() + INTERVAL '1 month')
         ON CONFLICT DO NOTHING`,
        [session.metadata.user_id, session.metadata.plan, session.subscription]
      )
    } else {
      await pool.query(
        "UPDATE purchases SET status = 'approved', gateway_payment_id = $1 WHERE gateway_preference_id = $2",
        [session.payment_intent, session.id]
      )
    }
    return { handled: true, type: verified.type }
  }
  return { handled: true, type: verified.type }
}
