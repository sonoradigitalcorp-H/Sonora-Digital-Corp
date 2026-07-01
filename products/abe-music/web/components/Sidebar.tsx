'use client'
import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'

const NAV = [
  { href: '/dashboard', label: 'Overview', icon: '📊' },
  { href: '/dashboard/fans', label: 'Fans CRM', icon: '👥' },
  { href: '/dashboard/bookings', label: 'Reservas', icon: '📅' },
  { href: '/dashboard/events', label: 'Eventos', icon: '🎤' },
  { href: '/dashboard/tokens', label: '$RESO', icon: '🪙' },
  { href: '/dashboard/merch', label: 'Merch', icon: '🎁' },
]

export default function Sidebar() {
  const pathname = usePathname()
  const router = useRouter()

  async function handleLogout() {
    await fetch('/api/auth/logout', { method: 'POST' })
    router.push('/login')
    router.refresh()
  }

  return (
    <aside className="w-56 min-h-screen bg-dark2 border-r border-[#1a1a1a] flex flex-col py-6 px-3 sticky top-0">
      <div className="text-sm font-black text-gold px-3 mb-6">🎸 Abe Music Hub</div>
      <nav className="flex-1 space-y-1">
        {NAV.map(item => (
          <Link
            key={item.href}
            href={item.href}
            className={`flex items-center gap-2.5 px-3 py-2.5 rounded-xl text-sm transition-colors ${
              pathname === item.href
                ? 'bg-gold/10 text-gold font-semibold'
                : 'text-[#888] hover:text-[#F0EDE8] hover:bg-[#1a1a1a]'
            }`}
          >
            <span>{item.icon}</span>
            {item.label}
          </Link>
        ))}
      </nav>
      <div className="border-t border-[#1a1a1a] pt-4 space-y-1">
        <Link href="/" className="flex items-center gap-2.5 px-3 py-2.5 rounded-xl text-sm text-[#888] hover:text-[#F0EDE8] hover:bg-[#1a1a1a] transition-colors">
          🌐 Sitio público
        </Link>
        <button
          onClick={handleLogout}
          className="w-full flex items-center gap-2.5 px-3 py-2.5 rounded-xl text-sm text-[#888] hover:text-red-400 hover:bg-red-500/10 transition-colors">
          🚪 Cerrar sesión
        </button>
      </div>
    </aside>
  )
}
