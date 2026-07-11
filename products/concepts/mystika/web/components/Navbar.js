'use client'
import Link from 'next/link'
import { useAuth } from '@/lib/auth'

export default function Navbar() {
  const { user, logout } = useAuth()

  return (
    <nav className="fixed top-0 w-full z-50 bg-black/80 backdrop-blur-md border-b border-gold/20">
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2">
          <span className="text-gold font-display text-xl tracking-wider">MYSTIKA</span>
        </Link>
        <div className="flex items-center gap-6 font-sans text-sm uppercase tracking-wider">
          <Link href="/lessons" className="text-white/70 hover:text-gold transition-colors">Lecciones</Link>
          <Link href="/subscribe" className="text-white/70 hover:text-gold transition-colors">Planes</Link>
          <Link href="/about" className="text-white/70 hover:text-gold transition-colors">Lilith</Link>
          {user ? (
            <div className="flex items-center gap-4">
              <Link href="/portal" className="text-gold hover:text-gold-light transition-colors">
                {user.first_name || user.username}
              </Link>
              <button onClick={logout} className="text-white/50 hover:text-red-400 transition-colors">Salir</button>
            </div>
          ) : (
            <Link href="/login" className="btn-primary !py-2 !px-5">Iniciar</Link>
          )}
        </div>
      </div>
    </nav>
  )
}
