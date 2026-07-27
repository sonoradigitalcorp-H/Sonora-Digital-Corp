import { createContext, useContext, useState, useEffect, useCallback } from 'react'

const API = `${window.location.protocol === 'https:' ? '' : 'http:'}//${window.location.host}/api`

const AuthContext = createContext(null)

function getStoredToken() {
  try { return localStorage.getItem('platform_token') } catch { return null }
}

function setStoredToken(t) {
  try { if (t) localStorage.setItem('platform_token', t); else localStorage.removeItem('platform_token') } catch {}
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = getStoredToken()
    if (!token) { setLoading(false); return }

    fetch(`${API}/auth/me`, {
      headers: { authorization: `Bearer ${token}` },
    })
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then((data) => setUser({ email: data.email, sid: data.sid }))
      .catch(() => setStoredToken(null))
      .finally(() => setLoading(false))
  }, [])

  const signIn = useCallback(async (email) => {
    const res = await fetch(`${API}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email }),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({ error: 'Error de conexión' }))
      return { error: new Error(err.error) }
    }
    const data = await res.json()
    setStoredToken(data.token)
    setUser({ email: data.email, sid: data.sid })
    return { error: null }
  }, [])

  const signOut = useCallback(() => {
    setStoredToken(null)
    setUser(null)
  }, [])

  return (
    <AuthContext.Provider value={{ user, loading, signIn, signOut }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}
