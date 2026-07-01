import jwt from 'jsonwebtoken'

const JWT_SECRET = process.env.JWT_SECRET || 'mystika-dev-secret'

export function authenticate(req, res, next) {
  const header = req.headers.authorization
  if (!header || !header.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'Token required' })
  }
  try {
    const token = header.split(' ')[1]
    const decoded = jwt.verify(token, JWT_SECRET)
    req.user = decoded
    next()
  } catch (err) {
    return res.status(401).json({ error: 'Invalid or expired token' })
  }
}

export function requireAdmin(req, res, next) {
  if (!req.user || !req.user.is_admin) {
    return res.status(403).json({ error: 'Admin access required' })
  }
  next()
}

export function generateToken(user) {
  return jwt.sign(
    {
      id: user.id,
      telegram_id: user.telegram_id,
      email: user.email,
      username: user.username,
      plan: user.plan,
      is_admin: user.is_admin,
    },
    JWT_SECRET,
    { expiresIn: process.env.JWT_EXPIRES_IN || '7d' }
  )
}
