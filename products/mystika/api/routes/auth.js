import { Router } from 'express'
import bcrypt from 'bcryptjs'
import { query } from '../db/index.js'
import { generateToken, authenticate } from '../middleware/auth.js'

const router = Router()

router.post('/register', async (req, res, next) => {
  try {
    const { email, password, username, first_name, age_verified } = req.body
    if (!email || !password) {
      return res.status(400).json({ error: 'Email and password required' })
    }
    if (!age_verified) {
      return res.status(400).json({ error: 'Age verification required (18+)' })
    }
    const existing = await query('SELECT id FROM users WHERE email = $1', [email])
    if (existing.rows.length > 0) {
      return res.status(409).json({ error: 'Email already registered' })
    }
    const hash = await bcrypt.hash(password, 12)
    const result = await query(
      `INSERT INTO users (email, password_hash, username, first_name, age_verified, is_verified)
       VALUES ($1, $2, $3, $4, $5, $6)
       RETURNING id, email, username, first_name, plan, is_admin, created_at`,
      [email, hash, username || email.split('@')[0], first_name || '', age_verified, true]
    )
    const user = result.rows[0]
    const token = generateToken(user)
    res.status(201).json({ user, token })
  } catch (err) { next(err) }
})

router.post('/login', async (req, res, next) => {
  try {
    const { email, telegram_id } = req.body
    if (!email && !telegram_id) {
      return res.status(400).json({ error: 'Email or telegram_id required' })
    }
    let user
    if (email) {
      const { password } = req.body
      if (!password) return res.status(400).json({ error: 'Password required' })
      const result = await query('SELECT * FROM users WHERE email = $1', [email])
      if (result.rows.length === 0) {
        return res.status(401).json({ error: 'Invalid credentials' })
      }
      user = result.rows[0]
      const valid = await bcrypt.compare(password, user.password_hash)
      if (!valid) return res.status(401).json({ error: 'Invalid credentials' })
    } else {
      const result = await query('SELECT * FROM users WHERE telegram_id = $1', [telegram_id])
      if (result.rows.length === 0) {
        return res.status(401).json({ error: 'Telegram account not linked' })
      }
      user = result.rows[0]
    }
    await query('UPDATE users SET last_login_at = NOW() WHERE id = $1', [user.id])
    const token = generateToken(user)
    const { password_hash, ...safeUser } = user
    res.json({ user: safeUser, token })
  } catch (err) { next(err) }
})

router.get('/me', authenticate, async (req, res, next) => {
  try {
    const result = await query(
      `SELECT id, email, username, first_name, plan, is_admin, preferred_language,
              age_verified, created_at, last_login_at
       FROM users WHERE id = $1`,
      [req.user.id]
    )
    if (result.rows.length === 0) return res.status(404).json({ error: 'User not found' })
    res.json(result.rows[0])
  } catch (err) { next(err) }
})

router.put('/me', authenticate, async (req, res, next) => {
  try {
    const { first_name, username, preferred_language } = req.body
    const result = await query(
      `UPDATE users SET
        first_name = COALESCE($1, first_name),
        username = COALESCE($2, username),
        preferred_language = COALESCE($3, preferred_language)
       WHERE id = $4 RETURNING id, email, username, first_name, plan, preferred_language`,
      [first_name, username, preferred_language, req.user.id]
    )
    res.json(result.rows[0])
  } catch (err) { next(err) }
})

router.post('/link-telegram', authenticate, async (req, res, next) => {
  try {
    const { telegram_id } = req.body
    if (!telegram_id) return res.status(400).json({ error: 'telegram_id required' })
    await query('UPDATE users SET telegram_id = $1 WHERE id = $2', [telegram_id, req.user.id])
    res.json({ message: 'Telegram account linked' })
  } catch (err) { next(err) }
})

export default router
