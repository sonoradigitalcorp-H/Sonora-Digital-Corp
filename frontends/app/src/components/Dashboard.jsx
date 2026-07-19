import { useState, useEffect } from 'react'
import { fetchStatus, fetchEvents, fetchMetrics } from '../lib/api'

function LiveMetrics() {
  const [status, setStatus] = useState(null)
  const [events, setEvents] = useState([])
  const [metrics, setMetrics] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    load()
    const interval = setInterval(load, 10000)
    return () => clearInterval(interval)
  }, [])

  async function load() {
    try {
      const [s, e, m] = await Promise.all([
        fetchStatus().catch(() => null),
        fetchEvents().catch(() => null),
        fetchMetrics().catch(() => null),
      ])
      if (s) setStatus(s)
      if (e) setEvents(e.events || [])
      if (m) setMetrics(m)
    } catch {}
    setLoading(false)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[40vh]">
        <div className="w-8 h-8 border-2 border-[#7c5cfc] border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  const operationalCount = status?.services?.filter((s) => s.status === 'operational').length || 0

  return (
    <div className="space-y-8">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="p-6 rounded-2xl bg-[#161b22] border border-[#30363d] text-center">
          <div className="text-3xl font-black text-white">{status?.services?.length || 0}</div>
          <div className="text-xs text-white/30 mt-1">Servicios</div>
        </div>
        <div className="p-6 rounded-2xl bg-[#161b22] border border-[#30363d] text-center">
          <div className="text-3xl font-black text-[#22c55e]">{operationalCount}</div>
          <div className="text-xs text-white/30 mt-1">Operacionales</div>
        </div>
        <div className="p-6 rounded-2xl bg-[#161b22] border border-[#30363d] text-center">
          <div className="text-3xl font-black text-white">{events.length}</div>
          <div className="text-xs text-white/30 mt-1">Eventos</div>
        </div>
        <div className="p-6 rounded-2xl bg-[#161b22] border border-[#30363d] text-center">
          <div className="text-3xl font-black text-[#7c5cfc]">{metrics?.agents || 0}</div>
          <div className="text-xs text-white/30 mt-1">Agentes</div>
        </div>
      </div>

      <div>
        <h3 className="text-lg font-semibold mb-4">Estado de Servicios</h3>
        <div className="rounded-2xl bg-[#161b22] border border-[#30363d] divide-y divide-[#21262d]">
          {status?.services?.map((s) => (
            <div key={s.name} className="flex items-center justify-between px-6 py-4">
              <span className="text-sm text-white/70">{s.name}</span>
              <span className="flex items-center gap-2 text-xs">
                <span
                  className={`w-2 h-2 rounded-full animate-pulse ${
                    s.status === 'operational'
                      ? 'bg-[#22c55e]'
                      : s.status === 'degraded'
                        ? 'bg-[#f59e0b]'
                        : 'bg-[#ef4444]'
                  }`}
                />
                {s.status}
              </span>
            </div>
          ))}
        </div>
      </div>

      <div>
        <h3 className="text-lg font-semibold mb-4">Eventos Recientes</h3>
        <div className="rounded-2xl bg-[#161b22] border border-[#30363d] max-h-64 overflow-y-auto">
          {events.length === 0 ? (
            <div className="px-6 py-12 text-center text-sm text-white/30">
              Esperando eventos del sistema...
            </div>
          ) : (
            events.map((e, i) => (
              <div
                key={e.id || i}
                className="flex items-start gap-3 px-6 py-3 border-b border-[#21262d] text-xs"
              >
                <span
                  className={`mt-1 w-2 h-2 rounded-full flex-shrink-0 ${
                    e.event?.includes('down') || e.type?.includes('down')
                      ? 'bg-[#ef4444]'
                      : e.event?.includes('warn') || e.type?.includes('warn')
                        ? 'bg-[#f59e0b]'
                        : 'bg-[#22c55e]'
                  }`}
                />
                <div className="flex-1 min-w-0">
                  <span className="text-white/80">{e.type || e.event}</span>
                  <span className="text-white/30 ml-2">
                    {JSON.stringify(e.payload || {}).slice(0, 80)}
                  </span>
                </div>
                <span className="text-white/20 flex-shrink-0">
                  {e.timestamp
                    ? new Date(e.timestamp).toLocaleTimeString()
                    : ''}
                </span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  )
}

export default function Dashboard() {
  return (
    <section
      id="dashboard"
      className="py-32 relative bg-white/[0.01] border-y border-white/[0.04]"
    >
      <div className="max-w-7xl mx-auto px-6">
        <div className="text-center mb-12">
          <span className="text-[#22c55e] text-sm font-medium tracking-widest uppercase">
            Panel en Vivo
          </span>
          <h2 className="text-4xl md:text-5xl font-bold mt-3">Dashboard</h2>
          <p className="text-white/30 mt-4 max-w-xl mx-auto">
            Monitorea tus agentes IA en tiempo real desde tu infraestructura.
          </p>
        </div>
        <LiveMetrics />
      </div>
    </section>
  )
}
