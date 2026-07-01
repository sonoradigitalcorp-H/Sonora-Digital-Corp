const BASE = process.env.NEXT_PUBLIC_HERMES_API_URL || 'http://localhost:8000'

async function apiFetch<T>(path: string): Promise<T | null> {
  try {
    const res = await fetch(`${BASE}${path}`, {
      next: { revalidate: 60 },
      headers: { 'Content-Type': 'application/json' },
    })
    if (!res.ok) return null
    return res.json() as Promise<T>
  } catch {
    return null
  }
}

export const api = {
  stats: () => apiFetch<any>('/hub/stats'),
  fans: () => apiFetch<any[]>('/artist-fans?limit=10'),
  leaderboard: () => apiFetch<any[]>('/hub/leaderboard/weekly'),
  bookings: () => apiFetch<any[]>('/hub/bookings?limit=8'),
  events: () => apiFetch<any[]>('/hub/events'),
}
