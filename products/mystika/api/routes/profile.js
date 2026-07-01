import { Router } from 'express'
import { query } from '../db/index.js'
import { authenticate } from '../middleware/auth.js'

const router = Router()

router.get('/', authenticate, async (req, res, next) => {
  try {
    const userResult = await query(
      `SELECT id, email, username, first_name, plan, preferred_language, created_at
       FROM users WHERE id = $1`,
      [req.user.id]
    )
    if (userResult.rows.length === 0) return res.status(404).json({ error: 'User not found' })
    const user = userResult.rows[0]
    const purchases = await query(
      `SELECT p.id, p.amount_usd, p.gateway, p.status, p.created_at,
              l.title as lesson_title, l.instrument
       FROM purchases p
       JOIN lessons l ON l.id = p.lesson_id
       WHERE p.user_id = $1 AND p.status = 'approved'
       ORDER BY p.created_at DESC`,
      [req.user.id]
    )
    const subscription = await query(
      `SELECT plan, status, current_period_end, created_at
       FROM subscriptions
       WHERE user_id = $1 AND status = 'active'
       ORDER BY created_at DESC LIMIT 1`,
      [req.user.id]
    )
    const retained = await query(
      `SELECT cr.id, cr.retention_type, cr.created_at,
              l.title as lesson_title, l.instrument
       FROM content_retentions cr
       JOIN lessons l ON l.id = cr.lesson_id
       WHERE cr.user_id = $1 AND cr.status = 'approved'
       ORDER BY cr.created_at DESC`,
      [req.user.id]
    )
    const progress = await query(
      `SELECT lp.lesson_id, l.title, lp.watched_seconds, lp.is_completed, lp.completed_at
       FROM lesson_progress lp
       JOIN lessons l ON l.id = lp.lesson_id
       WHERE lp.user_id = $1
       ORDER BY lp.updated_at DESC LIMIT 20`,
      [req.user.id]
    )
    res.json({ user, purchases: purchases.rows, subscription: subscription.rows[0] || null, retained: retained.rows, progress: progress.rows })
  } catch (err) { next(err) }
})

router.get('/altar', authenticate, async (req, res, next) => {
  try {
    const retained = await query(
      `SELECT cr.id, cr.retention_type, cr.created_at,
              l.id as lesson_id, l.title, l.instrument, l.difficulty, l.thumbnail_filename,
              l.video_duration_seconds
       FROM content_retentions cr
       JOIN lessons l ON l.id = cr.lesson_id
       WHERE cr.user_id = $1 AND cr.status = 'approved'
       ORDER BY cr.created_at DESC`,
      [req.user.id]
    )
    res.json({ altar: retained.rows })
  } catch (err) { next(err) }
})

router.get('/history', authenticate, async (req, res, next) => {
  try {
    const tips = await query(
      `SELECT id, amount_usd, message, is_public, created_at
       FROM tips WHERE user_id = $1 AND status = 'approved'
       ORDER BY created_at DESC`,
      [req.user.id]
    )
    const orders = await query(
      `SELECT id, total_usd, status, created_at
       FROM shop_orders WHERE user_id = $1
       ORDER BY created_at DESC`,
      [req.user.id]
    )
    res.json({ tips: tips.rows, orders: orders.rows })
  } catch (err) { next(err) }
})

export default router
