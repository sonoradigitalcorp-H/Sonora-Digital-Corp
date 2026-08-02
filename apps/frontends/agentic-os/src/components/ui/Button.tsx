import { forwardRef, ButtonHTMLAttributes } from 'react'
import { cn } from '@/lib/utils/helpers'

export const Button = forwardRef<HTMLButtonElement, ButtonHTMLAttributes<HTMLButtonElement>>(
  ({ className, variant = 'primary', size = 'md', disabled, loading, children, ...props }, ref) => {
    const baseStyles = 'inline-flex items-center justify-center font-semibold transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-cosmic-bg disabled:opacity-50 disabled:cursor-not-allowed'
    
    const variants = {
      primary: 'bg-cosmic-primary text-white hover:bg-cosmic-primaryGlow active:scale-[0.98] shadow-[0_0_20px_-5px_rgb(124_92_252_/_0.5)] focus:ring-cosmic-primary/50',
      secondary: 'bg-cosmic-card text-white border border-cosmic-border hover:border-cosmic-primaryHover hover:bg-cosmic-bgSecondary focus:ring-cosmic-primary/50',
      ghost: 'text-white/70 hover:text-white hover:bg-cosmic-card focus:ring-white/20',
      danger: 'bg-red-600/20 text-red-400 border border-red-500/30 hover:bg-red-600/30 hover:text-red-300 focus:ring-red-500/50',
      gold: 'bg-gradient-to-r from-cosmic-gold to-yellow-600 text-cosmic-bg hover:from-yellow-500 hover:to-cosmic-gold focus:ring-yellow-500/50',
    }
    
    const sizes = {
      sm: 'px-3 py-1.5 text-xs rounded-lg',
      md: 'px-5 py-2.5 text-sm rounded-xl',
      lg: 'px-7 py-3.5 text-base rounded-xl',
      xl: 'px-10 py-4 text-lg rounded-2xl',
    }

    return (
      <button
        ref={ref}
        className={cn(baseStyles, variants[variant], sizes[size], className)}
        disabled={disabled || loading}
        {...props}
      >
        {loading && (
          <svg className="animate-spin -ml-1 mr-2 h-4 w-4" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
        )}
        {children}
      </button>
    )
  }
)

Button.displayName = 'Button'

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger' | 'gold'
  size?: 'sm' | 'md' | 'lg' | 'xl'
  loading?: boolean
}