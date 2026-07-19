// Supabase solo para datos públicos (service_status, agent_events)
// Auth eliminado. Usamos Cloudflare Turnstile para bot detection.
// Los datos se sirven vía API Bridge (/api/).

export const supabase = null

export async function signInWithGoogle() {
  console.warn('Google Auth disabled — usando Turnstile + rate limiting')
  return { error: new Error('Auth disabled') }
}

export async function signOut() {
  return {}
}

export async function getSession() {
  return { session: null }
}

export function onAuthChange() {
  return { data: { unsubscribe: () => {} } }
}

export function subscribeToEvents() {
  return { unsubscribe: () => {} }
}
