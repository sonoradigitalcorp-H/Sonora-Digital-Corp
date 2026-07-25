import { useAuth } from '../lib/auth'

export default function ProfilePage() {
  const { user } = useAuth()

  return (
    <div className="p-6 overflow-y-auto">
      <header className="mb-8">
        <h2 className="text-2xl font-semibold">Perfil</h2>
        <p className="text-sm text-[#6e6e73] mt-1">Tu información de cuenta</p>
      </header>

      <div className="bg-[#1a1a1e] border border-[#2a2a2e] rounded-xl p-6 max-w-lg">
        <div className="flex items-center gap-4 mb-6">
          <div className="w-14 h-14 rounded-full bg-[#0071e3] flex items-center justify-center text-xl font-semibold">
            {user?.email?.charAt(0).toUpperCase() || '?'}
          </div>
          <div>
            <p className="font-medium">{user?.email || 'Sin sesión'}</p>
            <p className="text-xs text-[#6e6e73]">Usuario verificado</p>
          </div>
        </div>

        <div className="space-y-4">
          <div>
            <label className="text-xs text-[#6e6e73] uppercase tracking-wider">Email</label>
            <p className="text-sm mt-1">{user?.email || '—'}</p>
          </div>
          <div>
            <label className="text-xs text-[#6e6e73] uppercase tracking-wider">ID</label>
            <p className="text-sm mt-1 font-mono text-xs">{user?.id || '—'}</p>
          </div>
          <div>
            <label className="text-xs text-[#6e6e73] uppercase tracking-wider">Último ingreso</label>
            <p className="text-sm mt-1">
              {user?.last_sign_in_at
                ? new Date(user.last_sign_in_at).toLocaleDateString('es-MX', {
                    dateStyle: 'long',
                  })
                : '—'}
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
