import { SignJWT, jwtVerify } from 'jose'
import { cookies } from 'next/headers'

const SECRET = () => new TextEncoder().encode(process.env.JWT_SECRET!)

export async function signToken(payload: Record<string, unknown>) {
  return new SignJWT(payload)
    .setProtectedHeader({ alg: 'HS256' })
    .setIssuedAt()
    .setExpirationTime('24h')
    .sign(SECRET())
}

export async function verifyToken(token: string) {
  const { payload } = await jwtVerify(token, SECRET())
  return payload
}

export async function getSession() {
  const cookieStore = await cookies()
  const token = cookieStore.get('abe-token')?.value
  if (!token) return null
  try {
    return await verifyToken(token)
  } catch {
    return null
  }
}
