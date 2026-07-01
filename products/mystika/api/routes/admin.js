import { Router } from 'express'
import { query } from '../db/index.js'
import { authenticate, requireAdmin } from '../middleware/auth.js'

const router = Router()

router.use(authenticate, requireAdmin)

router.get('/dashboard', async (req, res, next) => {
  try {
    const totalUsers = await query('SELECT COUNT(*) FROM users')
    const activeSubs = await query("SELECT COUNT(*) FROM subscriptions WHERE status = 'active'")
    const totalRevenue = await query("SELECT COALESCE(SUM(amount_usd), 0) FROM purchases WHERE status = 'approved'")
    const recentPurchases = await query(
      `SELECT p.id, p.amount_usd, p.gateway, p.created_at, u.email, l.title
       FROM purchases p
       JOIN users u ON u.id = p.user_id
       JOIN lessons l ON l.id = p.lesson_id
       WHERE p.status = 'approved'
       ORDER BY p.created_at DESC LIMIT 10`
    )
    const plans = await query(
      `SELECT plan, COUNT(*) FROM subscriptions WHERE status = 'active' GROUP BY plan`
    )
    res.json({
      total_users: parseInt(totalUsers.rows[0].count),
      active_subscriptions: parseInt(activeSubs.rows[0].count),
      total_revenue_usd: parseFloat(totalRevenue.rows[0].coalesce),
      plans: plans.rows,
      recent_purchases: recentPurchases.rows,
    })
  } catch (err) { next(err) }
})

router.post('/lessons', async (req, res, next) => {
  try {
    const { title, description, instrument, difficulty, price_mxn, price_usd, video_filename } = req.body
    if (!title || !instrument || !video_filename) {
      return res.status(400).json({ error: 'title, instrument, and video_filename required' })
    }
    const result = await query(
      `INSERT INTO lessons (title, description, instrument, difficulty, price_mxn, price_usd, video_filename, status)
       VALUES ($1, $2, $3, $4, $5, $6, $7, 'draft')
       RETURNING *`,
      [title, description, instrument, difficulty, price_mxn || 0, price_usd || 0, video_filename]
    )
    res.status(201).json(result.rows[0])
  } catch (err) { next(err) }
})

router.put('/lessons/:id', async (req, res, next) => {
  try {
    const fields = ['title', 'description', 'instrument', 'difficulty', 'price_mxn', 'price_usd', 'status']
    const updates = []
    const params = []
    let i = 1
    for (const field of fields) {
      if (req.body[field] !== undefined) {
        updates.push(`${field} = $${i}`)
        params.push(req.body[field])
        i++
      }
    }
    if (updates.length === 0) return res.status(400).json({ error: 'No fields to update' })
    params.push(req.params.id)
    const result = await query(
      `UPDATE lessons SET ${updates.join(', ')}, updated_at = NOW() WHERE id = $${i} RETURNING *`,
      params
    )
    if (result.rows.length === 0) return res.status(404).json({ error: 'Lesson not found' })
    res.json(result.rows[0])
  } catch (err) { next(err) }
})

router.post('/lessons/:id/publish', async (req, res, next) => {
  try {
    const result = await query(
      "UPDATE lessons SET is_published = true, status = 'published' WHERE id = $1 RETURNING *",
      [req.params.id]
    )
    if (result.rows.length === 0) return res.status(404).json({ error: 'Lesson not found' })
    res.json({ message: 'Lesson published', lesson: result.rows[0] })
  } catch (err) { next(err) }
})

router.get('/lessons', async (req, res, next) => {
  try {
    const result = await query(
      `SELECT l.*, COUNT(p.id) as purchase_count,
              COALESCE(SUM(p.amount_usd) FILTER (WHERE p.status = 'approved'), 0) as revenue
       FROM lessons l
       LEFT JOIN purchases p ON p.lesson_id = l.id
       GROUP BY l.id
       ORDER BY l.created_at DESC`
    )
    res.json(result.rows)
  } catch (err) { next(err) }
})

router.get('/users', async (req, res, next) => {
  try {
    const result = await query(
      `SELECT id, email, username, plan, is_verified, created_at, last_login_at
       FROM users ORDER BY created_at DESC LIMIT 100`
    )
    res.json(result.rows)
  } catch (err) { next(err) }
})

export default router
