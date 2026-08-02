import { useState, useRef, useEffect, ReactNode } from 'react'
import { createPortal } from 'react-dom'
import { cn } from '@/lib/utils/helpers'

interface TooltipProps {
  content: ReactNode
  children: ReactNode
  position?: 'top' | 'bottom' | 'left' | 'right'
  delay?: number
  className?: string
}

export function Tooltip({ content, children, position = 'top', delay = 200, className }: TooltipProps) {
  const [visible, setVisible] = useState(false)
  const timeoutRef = useRef<ReturnType<typeof setTimeout>>()
  const triggerRef = useRef<HTMLElement>(null)
  const tooltipRef = useRef<HTMLDivElement>(null)

  const show = () => {
    timeoutRef.current = setTimeout(() => setVisible(true), delay)
  }

  const hide = () => {
    if (timeoutRef.current) clearTimeout(timeoutRef.current)
    setVisible(false)
  }

  useEffect(() => {
    const el = triggerRef.current
    if (!el) return
    el.addEventListener('mouseenter', show)
    el.addEventListener('mouseleave', hide)
    el.addEventListener('focus', show)
    el.addEventListener('blur', hide)
    return () => {
      el.removeEventListener('mouseenter', show)
      el.removeEventListener('mouseleave', hide)
      el.removeEventListener('focus', show)
      el.removeEventListener('blur', hide)
    }
  }, [show, hide])

  const positions = {
    top: 'bottom-full left-1/2 -translate-x-1/2 mb-2',
    bottom: 'top-full left-1/2 -translate-x-1/2 mt-2',
    left: 'right-full top-1/2 -translate-y-1/2 mr-2',
    right: 'left-full top-1/2 -translate-y-1/2 ml-2',
  }

  const arrows = {
    top: 'top-full left-1/2 -translate-x-1/2 border-t-cosmic-card',
    bottom: 'bottom-full left-1/2 -translate-x-1/2 border-b-cosmic-card',
    left: 'left-full top-1/2 -translate-y-1/2 border-l-cosmic-card',
    right: 'right-full top-1/2 -translate-y-1/2 border-r-cosmic-card',
  }

  if (!visible) {
    return <span ref={triggerRef}>{children}</span>
  }

  const tooltip = (
    <div
      ref={tooltipRef}
      className={cn(
        'fixed z-50 px-3 py-2 text-xs text-white bg-cosmic-card border border-cosmic-border rounded-lg shadow-lg whitespace-nowrap pointer-events-none animate-fade-in',
        positions[position],
        className
      )}
      role="tooltip"
    >
      {content}
      <div className={cn('absolute w-0 h-0 border-4 border-transparent', arrows[position])} />
    </div>
  )

  if (typeof window === 'undefined') return <span ref={triggerRef}>{children}</span>
  return createPortal(tooltip, document.body)
}