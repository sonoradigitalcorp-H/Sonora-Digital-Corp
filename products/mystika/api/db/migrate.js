import 'dotenv/config'
import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'
import { pool } from './index.js'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const schemaPath = path.resolve(__dirname, '../../db/schema.sql')

async function migrate() {
  console.log('Running Mystika DB migration...')
  const sql = fs.readFileSync(schemaPath, 'utf-8')
  try {
    await pool.query(sql)
    console.log('Migration completed successfully')
  } catch (err) {
    console.error('Migration failed:', err.message)
    process.exit(1)
  } finally {
    await pool.end()
  }
}

migrate()
