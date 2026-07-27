import { useState } from 'react'

const mockHistory = [
  { id: 1, user: 'usuario@email.com', preview: '¿Qué servicios ofrecen?', date: '2026-07-21', status: 'completada' },
  { id: 2, user: 'cliente@empresa.com', preview: 'Quiero contratar un agente IA para atención...', date: '2026-07-20', status: 'completada' },
  { id: 3, user: 'artista@email.com', preview: 'Necesito distribuir mi música en plataformas...', date: '2026-07-19', status: 'completada' },
  { id: 4, user: 'manager@label.com', preview: '¿Tienen planes enterprise?', date: '2026-07-18', status: 'pendiente' },
]

export default function HistoryPage() {
  const [search, setSearch] = useState('')

  const filtered = mockHistory.filter(
    (h) =>
      h.user.toLowerCase().includes(search.toLowerCase()) ||
      h.preview.toLowerCase().includes(search.toLowerCase()),
  )

  return (
    <div className="p-6 overflow-y-auto">
      <header className="mb-6">
        <h2 className="text-2xl font-semibold">Historial</h2>
        <p className="text-sm text-[#6e6e73] mt-1">Conversaciones anteriores</p>
      </header>

      <input
        type="text"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        placeholder="Buscar conversaciones..."
        className="w-full max-w-md px-4 py-2.5 rounded-full bg-[#1a1a1e] border border-[#2a2a2e] text-sm text-[#f5f5f7] placeholder-[#6e6e73] focus:outline-none focus:border-[#0071e3]/50 mb-6"
      />

      <div className="space-y-2">
        {filtered.map((item) => (
          <div
            key={item.id}
            className="bg-[#1a1a1e] border border-[#2a2a2e] rounded-xl p-4 hover:border-[#0071e3]/30 transition-colors cursor-pointer"
          >
            <div className="flex items-start justify-between gap-4">
              <div className="min-w-0">
                <p className="text-sm truncate">{item.preview}</p>
                <p className="text-xs text-[#6e6e73] mt-1">{item.user}</p>
              </div>
              <div className="flex items-center gap-3 shrink-0">
                <span className={`text-xs px-2 py-0.5 rounded-full ${
                  item.status === 'completada'
                    ? 'bg-[#22c55e]/10 text-[#22c55e]'
                    : 'bg-[#f59e0b]/10 text-[#f59e0b]'
                }`}>
                  {item.status}
                </span>
                <span className="text-xs text-[#6e6e73]">{item.date}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
