import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './app/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        'mds-blue': '#1A3A5C',
        'mds-orange': '#E85D04',
        'mds-white': '#F8F9FA',
      },
    },
  },
  plugins: [],
}
export default config
