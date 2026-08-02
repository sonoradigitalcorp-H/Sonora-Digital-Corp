/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
       colors: {
        cosmic: {
          bg: '#0a0a0f',
          bgSecondary: '#11111a',
          card: '#161b22',
          border: '#30363d',
          borderHover: '#7c5cfc',
          primary: '#7c5cfc',
          primaryHover: '#8a6aff',
          primaryGlow: '#a88cff',
          gold: '#c8a87c',
          goldGlow: '#e8c89c',
          green: '#22c55e',
          red: '#ef4444',
          amber: '#f59e0b',
          cyan: '#06b6d4',
        },
      },
      fontFamily: {
        sans: ['Space Grotesk', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'float': 'float 6s ease-in-out infinite',
        'orbit': 'orbit 20s linear infinite',
        'neural-pulse': 'neural-pulse 2s ease-in-out infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        orbit: {
          '0%': { transform: 'rotate(0deg)' },
          '100%': { transform: 'rotate(360deg)' },
        },
        'neural-pulse': {
          '0%, 100%': { opacity: '0.3', transform: 'scale(1)' },
          '50%': { opacity: '1', transform: 'scale(1.05)' },
        },
      },
      backgroundImage: {
        'cosmic-gradient': 'radial-gradient(ellipse at center, #1a1a2e 0%, #0a0a0f 70%, #050508 100%)',
        'neural-gradient': 'linear-gradient(135deg, #7c5cfc 0%, #c8a87c 100%)',
      },
    },
  },
  plugins: [],
}