const API = '/api'

export async function fetchStatus() {
  const res = await fetch(`${API}/status`)
  if (!res.ok) throw new Error('Failed to fetch status')
  return res.json()
}

export async function fetchEvents(limit = 50) {
  const res = await fetch(`${API}/events?limit=${limit}`)
  if (!res.ok) throw new Error('Failed to fetch events')
  return res.json()
}

export async function fetchMetrics() {
  const res = await fetch(`${API}/metrics`)
  if (!res.ok) throw new Error('Failed to fetch metrics')
  return res.json()
}
