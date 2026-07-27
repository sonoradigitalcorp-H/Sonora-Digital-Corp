export const tokens = {
  brand: {
    name: 'Sonora Digital Corp',
    tagline: 'Agentes IA que trabajan por ti 24/7',
    domain: 'sonoradigitalcorp.com',
  },

  colors: {
    primary: '#7c5cfc',
    primaryLight: '#a88aff',
    primaryDark: '#5a3cd4',
    accent: '#c8a87c',
    accentLight: '#e0c99e',
    success: '#22c55e',
    warning: '#f59e0b',
    error: '#ef4444',
    surface: '#0a0a0a',
    surfaceLight: '#161b22',
    surfaceLighter: '#1c2128',
    border: '#30363d',
    borderLight: '#21262d',
    text: '#c9d1d9',
    textDim: '#8b949e',
    textMuted: '#484f58',
    white: '#ffffff',
    black: '#000000',
  },

  fonts: {
    sans: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
    mono: "'JetBrains Mono', 'Fira Code', monospace",
    display: "'Inter', sans-serif",
  },

  spacing: {
    xs: '0.25rem',
    sm: '0.5rem',
    md: '1rem',
    lg: '1.5rem',
    xl: '2rem',
    '2xl': '3rem',
    '3xl': '4rem',
    '4xl': '6rem',
  },

  radius: {
    sm: '0.5rem',
    md: '0.75rem',
    lg: '1rem',
    xl: '1.5rem',
    '2xl': '2rem',
    full: '9999px',
  },

  shadows: {
    sm: '0 1px 2px rgba(0,0,0,0.3)',
    md: '0 4px 12px rgba(0,0,0,0.4)',
    lg: '0 8px 24px rgba(0,0,0,0.5)',
    glow: '0 0 40px rgba(124,92,252,0.08)',
    glowStrong: '0 0 60px rgba(124,92,252,0.15)',
  },

  animation: {
    fast: '150ms ease',
    normal: '250ms ease',
    slow: '400ms ease',
    float: 'float 20s linear infinite',
    pulse: 'pulse 2s ease-in-out infinite',
    gradient: 'gradient 8s ease infinite',
  },

  breakpoints: {
    sm: '640px',
    md: '768px',
    lg: '1024px',
    xl: '1280px',
    '2xl': '1536px',
  },

  gradients: {
    hero: 'linear-gradient(135deg, #fff 30%, #7c5cfc 70%, #c8a87c)',
    card: 'linear-gradient(135deg, rgba(124,92,252,0.05), rgba(200,168,124,0.05))',
    button: 'linear-gradient(135deg, #7c5cfc, #5a3cd4)',
    glow: 'radial-gradient(circle at 50% 50%, rgba(124,92,252,0.1), transparent 70%)',
  },
}

export const componentStyles = {
  glass: `bg-[${tokens.colors.surfaceLight}]/80 backdrop-blur-xl border border-[${tokens.colors.border}]/50`,
  card: `bg-[${tokens.colors.surfaceLight}] border border-[${tokens.colors.border}] rounded-xl hover:border-[${tokens.colors.primary}]/30 transition-all ${tokens.shadows.glow}`,
  button: {
    primary: `bg-[${tokens.colors.primary}] hover:bg-[${tokens.colors.primaryDark}] text-white font-semibold rounded-xl transition-all`,
    ghost: `border border-white/10 hover:border-[${tokens.colors.primary}]/40 text-white/70 hover:text-white rounded-xl transition-all`,
  },
  input: `w-full px-5 py-3.5 rounded-xl bg-white/[0.04] border border-white/[0.08] text-white placeholder-white/20 focus:outline-none focus:border-[${tokens.colors.primary}]/40 transition-all text-sm`,
}
