import { api } from '@/lib/api'
import KPICard from '@/components/KPICard'

export const revalidate = 60

function nivelColor(nivel: string) {
  const map: Record<string, string> = {
    EMERGENTE: 'bg-[#1e1e1e] text-[#888]',
    LOCAL: 'bg-green-500/10 text-green-400',
    REGIONAL: 'bg-gold/10 text-gold',
    NACIONAL: 'bg-red-500/10 text-red-400',
  }
  return map[nivel] || 'bg-[#1e1e1e] text-[#888]'
}

export default async function DashboardPage() {
  const [stats, fans, leaderboard, bookings] = await Promise.all([
    api.stats(),
    api.fans(),
    api.leaderboard(),
    api.bookings(),
  ])

  const now = new Date().toLocaleDateString('es-MX', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })

  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-black tracking-tight">Dashboard — Abe Music Hub</h1>
        <p className="text-[#888] text-sm mt-1 capitalize">{now}</p>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <KPICard label="Fans totales" value={stats?.total_fans ?? '—'} />
        <KPICard label="Reservas este mes" value={stats?.bookings_mes ?? '—'} />
        <KPICard label="$RESO circulación" value={stats?.reso_circulacion?.toLocaleString() ?? '—'} gold />
        <KPICard label="Ingresos MXN/mes" value={stats?.ingresos_mes ? `$${Number(stats.ingresos_mes).toLocaleString()}` : '—'} />
      </div>

      {/* Two col */}
      <div className="grid lg:grid-cols-2 gap-6 mb-6">
        {/* Top Fans $RESO */}
        <div className="bg-dark2 border border-[#1a1a1a] rounded-2xl p-6">
          <h2 className="font-bold text-sm mb-5">🏆 Top Fans $RESO — Esta semana</h2>
          {leaderboard && leaderboard.length > 0 ? (
            <table className="w-full text-sm">
              <thead>
                <tr className="text-xs text-[#888] uppercase tracking-wider">
                  <th className="text-left pb-3">#</th>
                  <th className="text-left pb-3">Fan</th>
                  <th className="text-left pb-3">Nivel</th>
                  <th className="text-right pb-3">$RESO</th>
                </tr>
              </thead>
              <tbody>
                {leaderboard.slice(0, 8).map((f: any, i: number) => (
                  <tr key={f.fan_id || i} className="border-t border-[#111]">
                    <td className="py-2.5 text-[#888]">{i === 0 ? '🥇' : i === 1 ? '🥈' : i === 2 ? '🥉' : i + 1}</td>
                    <td className="py-2.5">{f.nombre}</td>
                    <td className="py-2.5">
                      <span className={`text-xs font-bold px-2 py-0.5 rounded ${nivelColor(f.nivel)}`}>{f.nivel}</span>
                    </td>
                    <td className="py-2.5 text-right font-bold text-gold">{f.balance?.toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p className="text-[#555] text-sm text-center py-8">Sin datos — conecta HERMES OS</p>
          )}
        </div>

        {/* Reservas */}
        <div className="bg-dark2 border border-[#1a1a1a] rounded-2xl p-6">
          <h2 className="font-bold text-sm mb-5">📅 Próximas reservas</h2>
          {bookings && bookings.length > 0 ? (
            <table className="w-full text-sm">
              <thead>
                <tr className="text-xs text-[#888] uppercase tracking-wider">
                  <th className="text-left pb-3">Servicio</th>
                  <th className="text-left pb-3">Cliente</th>
                  <th className="text-left pb-3">Fecha</th>
                  <th className="text-left pb-3">Estado</th>
                </tr>
              </thead>
              <tbody>
                {bookings.slice(0, 8).map((b: any, i: number) => (
                  <tr key={b.id || i} className="border-t border-[#111]">
                    <td className="py-2.5 text-[#ccc]">{b.servicio_nombre || '—'}</td>
                    <td className="py-2.5">{b.nombre_cliente || '—'}</td>
                    <td className="py-2.5 text-[#888] text-xs">{b.fecha_reserva}</td>
                    <td className="py-2.5">
                      <span className={`text-xs font-bold px-2 py-0.5 rounded ${b.estado === 'confirmada' ? 'bg-green-500/10 text-green-400' : 'bg-[#1e1e1e] text-[#888]'}`}>
                        {b.estado}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p className="text-[#555] text-sm text-center py-8">Sin reservas — conecta HERMES OS</p>
          )}
        </div>
      </div>

      {/* Fans recientes */}
      <div className="bg-dark2 border border-[#1a1a1a] rounded-2xl p-6">
        <h2 className="font-bold text-sm mb-5">👥 Fans recientes</h2>
        {fans && fans.length > 0 ? (
          <table className="w-full text-sm">
            <thead>
              <tr className="text-xs text-[#888] uppercase tracking-wider border-b border-[#1a1a1a]">
                <th className="text-left pb-3">Nombre</th>
                <th className="text-left pb-3">Nivel</th>
                <th className="text-left pb-3">Puntos</th>
                <th className="text-left pb-3">Eventos</th>
                <th className="text-left pb-3">Fuente</th>
              </tr>
            </thead>
            <tbody>
              {fans.map((f: any, i: number) => (
                <tr key={f.fan_id || i} className="border-t border-[#111]">
                  <td className="py-2.5 font-medium">{f.nombre}</td>
                  <td className="py-2.5">
                    <span className={`text-xs font-bold px-2 py-0.5 rounded ${nivelColor(f.nivel)}`}>{f.nivel}</span>
                  </td>
                  <td className="py-2.5 text-gold font-bold">{f.puntos}</td>
                  <td className="py-2.5 text-[#888]">{f.eventos_asistidos}</td>
                  <td className="py-2.5 text-xs text-[#666]">{f.source || '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p className="text-[#555] text-sm text-center py-8">Sin fans registrados aún</p>
        )}
      </div>
    </div>
  )
}
