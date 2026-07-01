const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:4000'

async function request(path, options = {}) {
  const token = typeof window !== 'undefined' ? localStorage.getItem('mystika_token') : null
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  }
  const res = await fetch(`${API_URL}${path}`, { ...options, headers })
  const data = await res.json()
  if (!res.ok) throw new Error(data.error || `Request failed: ${res.status}`)
  return data
}

export const api = {
  // Auth
  register: (body) => request('/api/auth/register', { method: 'POST', body: JSON.stringify(body) }),
  login: (body) => request('/api/auth/login', { method: 'POST', body: JSON.stringify(body) }),
  getMe: () => request('/api/auth/me'),
  updateMe: (body) => request('/api/auth/me', { method: 'PUT', body: JSON.stringify(body) }),
  linkTelegram: (body) => request('/api/auth/link-telegram', { method: 'POST', body: JSON.stringify(body) }),

  // Lessons
  getLessons: (params) => request(`/api/lessons?${new URLSearchParams(params || {})}`),
  getLesson: (id) => request(`/api/lessons/${id}`),
  getInstruments: () => request('/api/lessons/instruments'),

  // Payments
  checkoutLesson: (body) => request('/api/payments/checkout/lesson', { method: 'POST', body: JSON.stringify(body) }),
  checkoutSubscription: (body) => request('/api/payments/checkout/subscription', { method: 'POST', body: JSON.stringify(body) }),
  retainLesson: (body) => request('/api/payments/retain', { method: 'POST', body: JSON.stringify(body) }),

  // Media
  getStreamToken: (lessonId) => request(`/api/media/token/${lessonId}`),
  reportViewed: (body) => request('/api/media/report-viewed', { method: 'POST', body: JSON.stringify(body) }),

  // Profile
  getProfile: () => request('/api/profile'),
  getAltar: () => request('/api/profile/altar'),
  getHistory: () => request('/api/profile/history'),
}
