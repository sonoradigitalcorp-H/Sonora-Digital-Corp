import type { Config } from 'tailwindcss'

const config: Config = {
  content: ['./app/**/*.{ts,tsx}', './components/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        gold: '#D4AF37',
        'gold-dark': '#B8962E',
        dark: '#0A0A0A',
        dark2: '#111111',
        dark3: '#1A1A1A',
      },
    },
  },
  plugins: [],
}

export default config
