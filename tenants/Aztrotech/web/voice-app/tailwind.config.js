/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts}'],
  theme: {
    extend: {
      colors: {
        aztrotech: { primary: '#00d4ff', accent: '#7c3aed', success: '#10b981', warm: '#f59e0b', bg: '#0a0a12' }
      },
      fontFamily: { sans: ['Inter', 'sans-serif'] }
    }
  },
  plugins: []
}
