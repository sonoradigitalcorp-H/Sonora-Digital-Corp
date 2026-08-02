import { forwardRef, HTMLAttributes } from 'react'
import { cn } from '@/lib/utils/helpers'

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'info' | 'cosmic' | 'gold'
  size?: 'sm' | 'md' | 'lg'
  dot?: boolean
}

export const Badge = forwardRef<HTMLSpanElement, BadgeProps>(
  ({ className, variant = 'default', size = 'md', dot = false, children, ...props }, ref) => {
    const variants = {
      default: 'bg-cosmic-border text-white/70',
      success: 'bg-green-500/20 text-green-400 border border-green-500/30',
      warning: 'bg-amber-500/20 text-amber-400 border border-amber-500/30',
      danger: 'bg-red-500/20 text-red-400 border border-red-500/30',
      info: 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30',
      cosmic: 'bg-cosmic-primary/20 text-cosmic-primary border border-cosmic-primary/30',
      gold: 'bg-cosmic-gold/20 text-cosmic-gold border border-cosmic-gold/30',
    }

    const sizes = {
      sm: 'px-2 py-0.5 text-xs',
      md: 'px-2.5 py-1 text-xs',
      lg: 'px-3 py-1.5 text-sm',
    }

    return (
      <span
        ref={ref}
        className={cn(
          'inline-flex items-center gap-1.5 font-medium rounded-full',
          variants[variant],
          sizes[size],
          className
        )}
        {...props}
      >
        {dot && <span className={cn('w-1.5 h-1.5 rounded-full', {
          'bg-green-400': variant === 'success',
          'bg-amber-400': variant === 'warning',
          'bg-red-400': variant === 'danger',
          'bg-cyan-400': variant === 'info',
          'bg-cosmic-primary': variant === 'cosmic',
          'bg-cosmic-gold': variant === 'gold',
          'bg-white/50': variant === 'default',
        })} />}
        {children}
      </span>
    )
  }
)

Badge.displayName = 'Badge'

interface AvatarProps extends HTMLAttributes<HTMLDivElement> {
  src?: string
  alt?: string
  name?: string
  size?: 'sm' | 'md' | 'lg' | 'xl'
  status?: 'online' | 'busy' | 'away' | 'offline'
  shape?: 'circle' | 'square'
}

export const Avatar = forwardRef<HTMLDivElement, AvatarProps>(
  ({ className, src, alt, name, size = 'md', status, shape = 'circle', ...props }, ref) => {
    const sizes = {
      sm: 'w-8 h-8 text-xs',
      md: 'w-10 h-10 text-sm',
      lg: 'w-12 h-12 text-base',
      xl: 'w-16 h-16 text-lg',
    }

    const statusSizes = {
      sm: 'w-2 h-2',
      md: 'w-2.5 h-2.5',
      lg: 'w-3 h-3',
      xl: 'w-4 h-4',
    }

    const statusColors = {
      online: 'bg-green-400',
      busy: 'bg-red-400',
      away: 'bg-amber-400',
      offline: 'bg-white/30',
    }

    const getInitials = (name: string) => {
      return name
        .split(' ')
        .map(n => n[0])
        .join('')
        .toUpperCase()
        .slice(0, 2)
    }

    const bgColors = [
      'bg-cosmic-primary/30',
      'bg-cosmic-gold/30',
      'bg-green-500/30',
      'bg-cyan-500/30',
      'bg-pink-500/30',
      'bg-purple-500/30',
    ]

    const colorIndex = name ? name.charCodeAt(0) % bgColors.length : 0

    return (
      <div ref={ref} className={cn('relative inline-flex shrink-0', className)} {...props}>
        <div className={cn(
          sizes[size],
          'rounded-full' /* shape === 'circle' ? 'rounded-full' : 'rounded-xl' */,
          'overflow-hidden bg-gradient-to-br',
          bgColors[colorIndex],
          'flex items-center justify-center font-medium text-white select-none'
        )}>
          {src ? (
            <img src={src} alt={alt || name || 'Avatar'} className="w-full h-full object-cover" />
          ) : (
            name ? getInitials(name) : '?'
          )}
        </div>
        {status && (
          <span className={cn(
            'absolute bottom-0 right-0 rounded-full border-2 border-cosmic-bg',
            statusSizes[size],
            statusColors[status]
          )} />
        )}
      </div>
    )
  }
)

Avatar.displayName = 'Avatar'