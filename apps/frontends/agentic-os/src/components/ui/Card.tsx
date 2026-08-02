import { forwardRef, HTMLAttributes } from 'react'
import { cn } from '@/lib/utils/helpers'

export const Card = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement>>(
  ({ className, variant = 'default', hover = false, children, ...props }, ref) => {
    const variants = {
      default: 'bg-cosmic-card border border-cosmic-border',
      glass: 'glass',
      hologram: 'hologram',
      elevated: 'bg-cosmic-card border border-cosmic-border shadow-[0_10px_40px_-10px_rgb(0_0_0_/_0.5)]',
    }

    const hoverStyles = hover 
      ? 'transition-all duration-300 hover:border-cosmic-primaryHover hover:shadow-[0_0_30px_-5px_rgb(124_92_252_/_0.3)] cursor-pointer'
      : ''

    return (
      <div
        ref={ref}
        className={cn('rounded-2xl backdrop-blur-xl', variants[variant], hoverStyles, className)}
        {...props}
      >
        {children}
      </div>
    )
  }
)

Card.displayName = 'Card'

export const CardHeader = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={cn('px-6 py-4 border-b border-cosmic-border', className)} {...props} />
  )
)

CardHeader.displayName = 'CardHeader'

export const CardTitle = forwardRef<HTMLHeadingElement, HTMLAttributes<HTMLHeadingElement>>(
  ({ className, ...props }, ref) => (
    <h3 ref={ref} className={cn('text-lg font-bold text-white', className)} {...props} />
  )
)

CardTitle.displayName = 'CardTitle'

export const CardDescription = forwardRef<HTMLParagraphElement, HTMLAttributes<HTMLParagraphElement>>(
  ({ className, ...props }, ref) => (
    <p ref={ref} className={cn('text-sm text-white/50 mt-1', className)} {...props} />
  )
)

CardDescription.displayName = 'CardDescription'

export const CardContent = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={cn('px-6 py-4', className)} {...props} />
  )
)

CardContent.displayName = 'CardContent'

export const CardFooter = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={cn('px-6 py-4 border-t border-cosmic-border flex items-center gap-2', className)} {...props} />
  )
)

CardFooter.displayName = 'CardFooter'