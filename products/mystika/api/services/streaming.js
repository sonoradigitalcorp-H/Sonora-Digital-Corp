import jwt from 'jsonwebtoken'

const STREAM_SECRET = process.env.STREAM_SECRET || process.env.JWT_SECRET || 'mystika-stream-secret'

export function generateStreamToken({ userId, lessonId, maxViews }) {
  return jwt.sign(
    { userId, lessonId, maxViews, type: 'stream' },
    STREAM_SECRET,
    { expiresIn: '1h' }
  )
}

export function validateStreamToken(token) {
  try {
    const payload = jwt.verify(token, STREAM_SECRET)
    if (payload.type !== 'stream') return null
    return payload
  } catch {
    return null
  }
}

export function generateDownloadToken({ userId, lessonId, retentionId }) {
  return jwt.sign(
    { userId, lessonId, retentionId, type: 'download' },
    STREAM_SECRET,
    { expiresIn: '7d' }
  )
}
