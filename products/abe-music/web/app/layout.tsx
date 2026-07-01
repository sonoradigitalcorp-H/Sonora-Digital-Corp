import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Abe Music Hub — Hermosillo, Sonora',
  description: 'El hogar del músico sonorense. Salas de ensayo, estudio, VR, eventos y más.',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es">
      <body>{children}</body>
    </html>
  )
}
