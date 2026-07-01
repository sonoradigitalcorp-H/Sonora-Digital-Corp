import './globals.css'
import { AuthProvider } from '@/lib/auth'

export const metadata = {
  title: 'Mystika — El Ritual Musical',
  description: 'Donde el sonido despierta el alma. Aprende música con Lilith Mystika.',
  icons: { icon: '/favicon.svg' },
}

export default function RootLayout({ children }) {
  return (
    <html lang="es" className="dark">
      <body className="bg-black text-white font-serif antialiased">
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  )
}
