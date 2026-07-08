import type { Metadata, Viewport } from 'next';
import { Inter, JetBrains_Mono } from 'next/font/google';
import './globals.css';
import { ThemeProvider } from '@/components/theme-provider';
import { Toaster } from 'sonner';

export const viewport: Viewport = {
  themeColor: [
    { media: '(prefers-color-scheme: dark)', color: '#0a0a0f' },
    { media: '(prefers-color-scheme: light)', color: '#ffffff' },
  ],
};

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ['latin'],
  variable: '--font-jetbrains-mono',
});

export const metadata: Metadata = {
  title: {
    default: 'SIGNAL — Music Intelligence Platform',
    template: '%s | SIGNAL',
  },
  description: 'AI-powered music intelligence platform for the music industry. Discover, evaluate, and sign the next generation of artists.',
  keywords: ['music intelligence', 'A&R', 'artist discovery', 'AI agents', 'music industry', 'talent acquisition', 'SIGNAL'],
  authors: [{ name: 'Abe Music Group' }],
  openGraph: {
    title: 'SIGNAL — Music Intelligence Platform',
    description: 'AI-powered music intelligence for the music industry.',
    type: 'website',
    siteName: 'SIGNAL',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'SIGNAL — Music Intelligence Platform',
    description: 'AI-powered music intelligence for the music industry.',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning className="dark">
      <body className={`${inter.variable} ${jetbrainsMono.variable} font-sans antialiased`}>
        <ThemeProvider attribute="class" defaultTheme="dark" enableSystem>
          {children}
          <Toaster position="top-right" richColors />
        </ThemeProvider>
      </body>
    </html>
  );
}
