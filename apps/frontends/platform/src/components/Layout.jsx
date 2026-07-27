import { NavLink } from 'react-router-dom'
import { useAuth } from '../lib/auth'

const NAV = [
  { to: '/chat', label: 'Chat', icon: '💬' },
  { to: '/dashboard', label: 'Dashboard', icon: '📊' },
  { to: '/history', label: 'Historial', icon: '📋' },
  { to: '/profile', label: 'Perfil', icon: '👤' },
  { to: '/admin', label: 'Admin', icon: '⚙️' },
]

export default function Layout({ children }) {
  const { user, signOut } = useAuth()

  return (
    <div className="min-h-screen bg-black text-[#f5f5f7] flex">
      <nav className="w-56 border-r border-[#2a2a2e] flex flex-col bg-[#0a0a0a] shrink-0">
        <div className="px-5 py-6 border-b border-[#2a2a2e]">
          <h1 className="text-lg font-semibold tracking-tight">
            SONORA<span className="text-[#6e6e73]"> DIGITAL</span>
          </h1>
          <p className="text-xs text-[#6e6e73] mt-0.5">Platform</p>
        </div>
        <div className="flex-1 py-3 px-2 space-y-0.5">
          {NAV.map(({ to, label, icon }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all ${
                  isActive
                    ? 'bg-[#0071e3] text-white font-medium'
                    : 'text-[#6e6e73] hover:text-[#f5f5f7] hover:bg-[#1a1a1e]'
                }`
              }
            >
              <span className="text-base">{icon}</span>
              {label}
            </NavLink>
          ))}
        </div>
        {user && (
          <div className="p-4 border-t border-[#2a2a2e]">
            <div className="text-xs text-[#6e6e73] truncate mb-2">{user.email}</div>
            <button
              onClick={signOut}
              className="text-xs text-[#6e6e73] hover:text-[#ef4444] transition-colors"
            >
              Cerrar sesión
            </button>
          </div>
        )}
      </nav>
      <main className="flex-1 flex flex-col min-w-0">
        {children}
      </main>
    </div>
  )
}
