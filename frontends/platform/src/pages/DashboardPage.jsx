const statCards = [
  { label: 'Conversaciones hoy', value: '12', change: '+3', up: true },
  { label: 'Usuarios activos', value: '48', change: '+8', up: true },
  { label: 'Respuestas generadas', value: '234', change: '+17', up: true },
  { label: 'Tiempo promedio', value: '2.4s', change: '-0.3s', up: true },
]

const recentActivity = [
  { user: 'usuario@email.com', action: 'Consultó sobre precios', time: 'hace 2 min' },
  { user: 'cliente@empresa.com', action: 'Solicitó demo', time: 'hace 15 min' },
  { user: 'artista@email.com', action: 'Preguntó por distribución', time: 'hace 1 hora' },
]

export default function DashboardPage() {
  return (
    <div className="p-6 overflow-y-auto">
      <header className="mb-8">
        <h2 className="text-2xl font-semibold">Dashboard</h2>
        <p className="text-sm text-[#6e6e73] mt-1">Resumen de actividad en tiempo real</p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {statCards.map((card) => (
          <div key={card.label} className="bg-[#1a1a1e] border border-[#2a2a2e] rounded-xl p-5">
            <p className="text-xs text-[#6e6e73] uppercase tracking-wider mb-1">{card.label}</p>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-semibold">{card.value}</span>
              <span className={`text-xs ${card.up ? 'text-[#22c55e]' : 'text-[#ef4444]'}`}>
                {card.change}
              </span>
            </div>
          </div>
        ))}
      </div>

      <div className="bg-[#1a1a1e] border border-[#2a2a2e] rounded-xl p-5">
        <h3 className="text-sm font-medium mb-4">Actividad reciente</h3>
        <div className="space-y-3">
          {recentActivity.map((item, i) => (
            <div key={i} className="flex items-center justify-between py-2 border-b border-[#2a2a2e] last:border-0">
              <div>
                <p className="text-sm">{item.action}</p>
                <p className="text-xs text-[#6e6e73]">{item.user}</p>
              </div>
              <span className="text-xs text-[#6e6e73] shrink-0">{item.time}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
