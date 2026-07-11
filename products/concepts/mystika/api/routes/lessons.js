import { Router } from 'express'
import { query } from '../db/index.js'
import { authenticate } from '../middleware/auth.js'

const router = Router()

router.get('/', async (req, res, next) => {
  try {
    const { instrument, difficulty } = req.query
    let sql = `SELECT id, title, description, instrument, difficulty,
                      price_mxn, price_usd, thumbnail_filename,
                      video_duration_seconds, is_published, created_at
               FROM lessons WHERE is_published = true`
    const params = []
    if (instrument) {
      params.push(instrument)
      sql += ` AND instrument = $${params.length}`
    }
    if (difficulty) {
      params.push(difficulty)
      sql += ` AND difficulty = $${params.length}`
    }
    sql += ' ORDER BY created_at DESC'
    const result = await query(sql, params)
    res.json({ lessons: result.rows })
  } catch (err) { next(err) }
})

router.get('/instruments', async (req, res, next) => {
  try {
    const result = await query(
      `SELECT instrument, COUNT(*) as count
       FROM lessons WHERE is_published = true
       GROUP BY instrument ORDER BY instrument`
    )
    res.json(result.rows)
  } catch (err) { next(err) }
})

router.get('/:id', async (req, res, next) => {
  try {
    const result = await query(
      `SELECT l.*, c.title as course_title
       FROM lessons l
       LEFT JOIN course_lessons cl ON cl.lesson_id = l.id
       LEFT JOIN courses c ON c.id = cl.course_id
       WHERE l.id = $1`,
      [req.params.id]
    )
    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'Lesson not found' })
    }
    const lesson = result.rows[0]
    let has_access = false
    let can_retain = false
    let can_download = false
    if (req.headers.authorization) {
      try {
        const tokenResult = await query(
          `SELECT at.max_views, at.view_count, at.is_retained,
                  cp.status as purchase_status, s.status as sub_status
           FROM access_tokens at
           LEFT JOIN purchases cp ON cp.lesson_id = at.lesson_id AND cp.user_id = at.user_id
           LEFT JOIN subscriptions s ON s.user_id = at.user_id AND s.status = 'active'
           WHERE at.lesson_id = $1 AND at.user_id = $2
           LIMIT 1`,
          [req.params.id, req.user?.id]
        )
        if (tokenResult.rows.length > 0) {
          const t = tokenResult.rows[0]
          has_access = t.view_count < t.max_views || t.max_views === -1
          can_retain = t.view_count >= t.max_views && t.max_views > 0 && !t.is_retained
          can_download = has_access || can_retain
        }
      } catch {}
    }
    res.json({ lesson, access: { has_access, can_retain, can_download } })
  } catch (err) { next(err) }
})

router.get('/:id/preview', async (req, res, next) => {
  try {
    const result = await query(
      'SELECT preview_filename FROM lessons WHERE id = $1',
      [req.params.id]
    )
    if (result.rows.length === 0) return res.status(404).json({ error: 'Lesson not found' })
    const { preview_filename } = result.rows[0]
    if (!preview_filename) return res.status(404).json({ error: 'No preview available' })
    res.json({ preview_url: `/api/media/preview/${preview_filename}` })
  } catch (err) { next(err) }
})

export default router
