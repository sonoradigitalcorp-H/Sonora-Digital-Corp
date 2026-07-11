import 'dotenv/config'
import express from 'express'
import cors from 'cors'
import helmet from 'helmet'
import { pool } from './db/index.js'
import authRoutes from './routes/auth.js'
import lessonRoutes from './routes/lessons.js'
import paymentRoutes from './routes/payments.js'
import mediaRoutes from './routes/media.js'
import profileRoutes from './routes/profile.js'
import adminRoutes from './routes/admin.js'

const app = express()
const PORT = process.env.PORT || 4000

app.use(helmet({ crossOriginResourcePolicy: { policy: 'cross-origin' } }))
app.use(cors({ origin: process.env.FRONTEND_URL || '*' }))
app.use(express.json())

app.get('/health', (req, res) => {
  res.json({ status: 'ok', service: 'mystika-api', version: '1.0.0' })
})

app.use('/api/auth', authRoutes)
app.use('/api/lessons', lessonRoutes)
app.use('/api/payments', paymentRoutes)
app.use('/api/media', mediaRoutes)
app.use('/api/profile', profileRoutes)
app.use('/api/admin', adminRoutes)

app.use((err, req, res, next) => {
  console.error(err.stack)
  res.status(err.status || 500).json({
    error: err.message || 'Internal server error',
    ...(process.env.NODE_ENV === 'development' && { stack: err.stack })
  })
})

app.listen(PORT, () => {
  console.log(`Mystika API running on port ${PORT}`)
})

export default app
