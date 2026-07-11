import { Router } from 'express'
import path from 'path'
import fs from 'fs'
import jwt from 'jsonwebtoken'
import { query } from '../db/index.js'
import { generateStreamToken, validateStreamToken } from '../services/streaming.js'

const router = Router()
const VIDEO_PATH = process.env.VIDEO_STORAGE_PATH || '/data/videos/mystika'
const JWT_SECRET = process.env.JWT_SECRET || 'mystika-dev-secret'

router.get('/token/:lessonId', async (req, res, next) => {
  try {
    const auth = req.headers.authorization
    if (!auth) return res.status(401).json({ error: 'Auth required' })
    const token = auth.split(' ')[1]
    const user = jwt.verify(token, JWT_SECRET)
    const { lessonId } = req.params
    const access = await query(
      `SELECT
        at.id as token_id, at.max_views, at.view_count, at.expires_at,
        p.status as purchase_status,
        s.status as sub_status, s.plan as sub_plan
       FROM users u
       LEFT JOIN purchases p ON p.user_id = u.id AND p.lesson_id = $1 AND p.status = 'approved'
       LEFT JOIN subscriptions s ON s.user_id = u.id AND s.status = 'active'
       LEFT JOIN access_tokens at ON at.lesson_id = $1 AND at.user_id = u.id
       WHERE u.id = $2
       ORDER BY at.created_at DESC
       LIMIT 1`,
      [lessonId, user.id]
    )
    if (access.rows.length === 0) {
      return res.status(403).json({ error: 'No access. Purchase or subscribe first.' })
    }
    const a = access.rows[0]
    const isRitual = a.sub_plan === 'ritual'
    const hasPurchase = a.purchase_status === 'approved'
    const hasActiveSub = a.sub_status === 'active'
    if (!hasPurchase && !hasActiveSub) {
      return res.status(403).json({ error: 'No active access' })
    }
    let maxViews
    if (isRitual) {
      maxViews = -1
    } else if (a.token_id && a.view_count > 0) {
      maxViews = 0
    } else {
      maxViews = 1
    }
    if (maxViews === 0) {
      return res.status(403).json({
        error: 'Content consumed',
        can_retain: true,
        retain_price_usd: 7.49,
        retain_price_mxn: 149,
      })
    }
    const streamToken = generateStreamToken({ userId: user.id, lessonId, maxViews })
    const lesson = await query('SELECT video_filename FROM lessons WHERE id = $1', [lessonId])
    res.json({
      stream_url: `/api/media/stream/${streamToken}`,
      token: streamToken,
      max_views: maxViews,
      expires_at: new Date(Date.now() + 3600000).toISOString(),
    })
  } catch (err) {
    if (err.name === 'JsonWebTokenError') return res.status(401).json({ error: 'Invalid token' })
    next(err)
  }
})

router.get('/stream/:token', async (req, res, next) => {
  try {
    const payload = validateStreamToken(req.params.token)
    if (!payload) {
      return res.status(403).json({ error: 'Invalid or expired stream token' })
    }
    const lesson = await query('SELECT video_filename FROM lessons WHERE id = $1', [payload.lessonId])
    if (lesson.rows.length === 0) return res.status(404).json({ error: 'Video not found' })
    const videoPath = path.join(VIDEO_PATH, lesson.rows[0].video_filename)
    if (!fs.existsSync(videoPath)) return res.status(404).json({ error: 'File not found' })
    const stat = fs.statSync(videoPath)
    const range = req.headers.range
    if (range) {
      const parts = range.replace(/bytes=/, '').split('-')
      const start = parseInt(parts[0], 10)
      const end = parts[1] ? parseInt(parts[1], 10) : stat.size - 1
      const chunkSize = end - start + 1
      const stream = fs.createReadStream(videoPath, { start, end })
      res.writeHead(206, {
        'Content-Range': `bytes ${start}-${end}/${stat.size}`,
        'Accept-Ranges': 'bytes',
        'Content-Length': chunkSize,
        'Content-Type': 'video/mp4',
        'X-Accel-Redirect': `/protected/${lesson.rows[0].video_filename}`,
      })
      stream.pipe(res)
    } else {
      res.writeHead(200, {
        'Content-Length': stat.size,
        'Content-Type': 'video/mp4',
        'Accept-Ranges': 'bytes',
      })
      fs.createReadStream(videoPath).pipe(res)
    }
  } catch (err) { next(err) }
})

router.post('/report-viewed', async (req, res, next) => {
  try {
    const auth = req.headers.authorization
    if (!auth) return res.status(401).json({ error: 'Auth required' })
    const user = jwt.verify(auth.split(' ')[1], JWT_SECRET)
    const { lesson_id, progress } = req.body
    const result = await query(
      `UPDATE access_tokens
       SET view_count = view_count + 1, updated_at = NOW()
       WHERE lesson_id = $1 AND user_id = $2
       RETURNING id, max_views, view_count`,
      [lesson_id, user.id]
    )
    if (result.rows.length > 0) {
      const t = result.rows[0]
      const isConsumed = t.max_views > 0 && t.view_count >= t.max_views
      if (isConsumed) {
        await query(
          `UPDATE access_tokens SET expires_at = NOW() WHERE id = $1`,
          [t.id]
        )
      }
    }
    await query(
      `INSERT INTO lesson_progress (user_id, lesson_id, watched_seconds, is_completed)
       VALUES ($1, $2, $3, $4)
       ON CONFLICT (user_id, lesson_id)
       DO UPDATE SET watched_seconds = GREATEST(lesson_progress.watched_seconds, $3),
                     is_completed = $4 OR lesson_progress.is_completed,
                     updated_at = NOW()`,
      [user.id, lesson_id, progress?.watched_seconds || 0, progress?.is_completed || false]
    )
    res.json({ status: 'recorded' })
  } catch (err) { next(err) }
})

export default router
