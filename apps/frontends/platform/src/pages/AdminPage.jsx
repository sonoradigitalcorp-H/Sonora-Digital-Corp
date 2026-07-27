import { useState } from 'react'

const mockUsers = [
  { email: 'admin@sonora.com', role: 'admin', status: 'activo', lastSeen: 'hace 5 min' },
  { email: 'usuario@email.com', role: 'user', status: 'activo', lastSeen: 'hace 2 horas' },
  { email: 'cliente@empresa.com', role: 'user', status: 'activo', lastSeen: 'hace 1 día' },
]

const systemStats = [
  { label: 'LLM Requests hoy', value: '156' },
  { label: 'Tokens consumidos', value: '48.2K' },
  { label: 'Latencia promedio', value: '1.8s' },
  { label: 'Errores', value: '0' },
]

export default function AdminPage() {
  const [tab, setTab] = useState('users')

  return (
    <div className="p-6 overflow-y-auto">
      <header className="mb-6">
        <h2 className="text-2xl font-semibold">Admin</h2>
        <p className="text-sm text-[#6e6e73] mt-1">Gestión del sistema</p>
      </header>

      <div className="flex gap-2 mb-6">
        {[
          { key: 'users', label: 'Usuarios' },
          { key: 'system', label: 'Sistema' },
        ].map(({ key, label }) => (
          <button
            key={key}
            onClick={() => setTab(key)}
            className={`px-4 py-2 rounded-full text-sm transition-all ${
              tab === key
                ? 'bg-[#0071e3] text-white'
                : 'bg-[#1a1a1e] text-[#6e6e73] hover:text-[#f5f5f7]'
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {tab === 'users' && (
        <div className="bg-[#1a1a1e] border border-[#2a2a2e] rounded-xl overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-[#2a2a2e] text-[#6e6e73] text-xs uppercase tracking-wider">
                <th className="text-left px-4 py-3 font-medium">Email</th>
                <th className="text-left px-4 py-3 font-medium">Rol</th>
                <th className="text-left px-4 py-3 font-medium">Estado</th>
                <th className="text-left px-4 py-3 font-medium">Última vez</th>
              </tr>
            </thead>
            <tbody>
              {mockUsers.map((u) => (
                <tr key={u.email} className="border-b border-[#2a2a2e] last:border-0">
                  <td className="px-4 py-3">{u.email}</td>
                  <td className="px-4 py-3">
                    <span className={`text-xs px-2 py-0.5 rounded-full ${
                      u.role === 'admin' ? 'bg-[#0071e3]/10 text-[#0071e3]' : 'text-[#6e6e73]'
                    }`}>
                      {u.role}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span className="flex items-center gap-1.5">
                      <span className="w-1.5 h-1.5 rounded-full bg-[#22c55e]" />
                      {u.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-[#6e6e73]">{u.lastSeen}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {tab === 'system' && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {systemStats.map((s) => (
            <div key={s.label} className="bg-[#1a1a1e] border border-[#2a2a2e] rounded-xl p-4">
              <p className="text-xs text-[#6e6e73] uppercase tracking-wider">{s.label}</p>
              <p className="text-xl font-semibold mt-1">{s.value}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
