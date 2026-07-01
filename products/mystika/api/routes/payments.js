import { Router } from 'express'
import { query } from '../db/index.js'
import { authenticate } from '../middleware/auth.js'
import { createStripeCheckout, createStripeSubscription, handleStripeWebhook } from '../services/stripe.js'
import { createMPPreference, createMPPreapproval, handleMPWebhook } from '../services/mercadopago.js'

const router = Router()

router.post('/checkout/lesson', authenticate, async (req, res, next) => {
  try {
    const { lesson_id, gateway } = req.body
    if (!lesson_id || !gateway) return res.status(400).json({ error: 'lesson_id and gateway required' })
    const lesson = await query('SELECT * FROM lessons WHERE id = $1 AND is_published = true', [lesson_id])
    if (lesson.rows.length === 0) return res.status(404).json({ error: 'Lesson not found' })
    const data = lesson.rows[0]
    let checkout
    if (gateway === 'stripe') {
      checkout = await createStripeCheckout({
        lesson_id: data.id,
        title: data.title,
        amount_usd: data.price_usd,
        user_id: req.user.id,
        email: req.user.email,
      })
    } else if (gateway === 'mercadopago') {
      checkout = await createMPPreference({
        lesson_id: data.id,
        title: data.title,
        amount_mxn: data.price_mxn,
        user_id: req.user.id,
        email: req.user.email,
      })
    } else {
      return res.status(400).json({ error: 'Invalid gateway. Use: stripe, mercadopago' })
    }
    await query(
      `INSERT INTO purchases (user_id, lesson_id, amount_mxn, amount_usd, gateway, gateway_preference_id, status)
       VALUES ($1, $2, $3, $4, $5, $6, 'pending')`,
      [req.user.id, data.id, data.price_mxn, data.price_usd, gateway, checkout.id]
    )
    res.json({ checkout_url: checkout.url, gateway, preference_id: checkout.id })
  } catch (err) { next(err) }
})

router.post('/checkout/subscription', authenticate, async (req, res, next) => {
  try {
    const { plan, gateway } = req.body
    if (!plan || !gateway) return res.status(400).json({ error: 'plan and gateway required' })
    if (!['mysteria', 'ritual'].includes(plan)) return res.status(400).json({ error: 'Invalid plan' })
    let checkout
    const prices = { mysteria: { usd: 14.99, mxn: 299 }, ritual: { usd: 49.99, mxn: 999 } }
    if (gateway === 'stripe') {
      checkout = await createStripeSubscription({
        plan, user_id: req.user.id, email: req.user.email,
      })
    } else if (gateway === 'mercadopago') {
      checkout = await createMPPreapproval({
        plan, user_id: req.user.id, email: req.user.email,
        amount_mxn: prices[plan].mxn,
      })
    } else {
      return res.status(400).json({ error: 'Invalid gateway' })
    }
    res.json({ checkout_url: checkout.url, gateway, preference_id: checkout.id })
  } catch (err) { next(err) }
})

router.post('/retain', authenticate, async (req, res, next) => {
  try {
    const { lesson_id, gateway } = req.body
    if (!lesson_id || !gateway) return res.status(400).json({ error: 'lesson_id and gateway required' })
    const user = await query('SELECT plan FROM users WHERE id = $1', [req.user.id])
    const discount = user.rows[0]?.plan === 'mysteria' ? 0.8 : user.rows[0]?.plan === 'ritual' ? 0.6 : 1
    const lesson = await query('SELECT * FROM lessons WHERE id = $1', [lesson_id])
    if (lesson.rows.length === 0) return res.status(404).json({ error: 'Lesson not found' })
    const data = lesson.rows[0]
    const retain_price_usd = parseFloat((data.price_usd * 0.5 * discount).toFixed(2))
    const retain_price_mxn = parseFloat((data.price_mxn * 0.5 * discount).toFixed(2))
    let checkout
    if (gateway === 'stripe') {
      checkout = await createStripeCheckout({
        lesson_id: data.id, title: `Retener: ${data.title}`,
        amount_usd: retain_price_usd, user_id: req.user.id, email: req.user.email,
        metadata: { type: 'retain', lesson_id: data.id },
      })
    } else if (gateway === 'mercadopago') {
      checkout = await createMPPreference({
        lesson_id: data.id, title: `Retener: ${data.title}`,
        amount_mxn: retain_price_mxn, user_id: req.user.id, email: req.user.email,
      })
    }
    await query(
      `INSERT INTO content_retentions (user_id, lesson_id, gateway, amount_mxn, amount_usd, retention_type, status)
       VALUES ($1, $2, $3, $4, $5, 'retain', 'pending')`,
      [req.user.id, data.id, gateway, retain_price_mxn, retain_price_usd]
    )
    res.json({ checkout_url: checkout.url, gateway, amount_usd: retain_price_usd, amount_mxn: retain_price_mxn })
  } catch (err) { next(err) }
})

router.post('/webhook/stripe', async (req, res) => {
  try {
    const event = req.body
    const result = await handleStripeWebhook(event)
    res.json({ received: true, ...result })
  } catch (err) {
    console.error('Stripe webhook error:', err)
    res.status(400).json({ error: err.message })
  }
})

router.post('/webhook/mercadopago', async (req, res) => {
  try {
    const result = await handleMPWebhook(req.body)
    res.json({ received: true, ...result })
  } catch (err) {
    console.error('MP webhook error:', err)
    res.status(400).json({ error: err.message })
  }
})

export default router
