import { NextRequest, NextResponse } from 'next/server'
import { signToken } from '@/lib/auth'

export async function POST(req: NextRequest) {
  const { email, password } = await req.json()

  const validEmail = process.env.ADMIN_EMAIL
  const validPassword = process.env.ADMIN_PASSWORD

  if (email !== validEmail || password !== validPassword) {
    return NextResponse.json({ error: 'Credenciales incorrectas' }, { status: 401 })
  }

  const token = await signToken({ email, role: 'admin', name: 'Abraham' })

  const res = NextResponse.json({ ok: true })
  res.cookies.set('abe-token', token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'lax',
    maxAge: 60 * 60 * 24, // 24 horas
    path: '/',
  })
  return res
}
