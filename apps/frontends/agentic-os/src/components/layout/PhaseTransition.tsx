import { useContext, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useGalaxy } from '@/contexts/GalaxyContext'
import { GALAXY_CONFIGS } from '@/types'

export function PhaseTransition() {
  const { phase, isTransitioning, currentGalaxy } = useGalaxy()

  if (!isTransitioning && phase === 'MACRO_VIEW') return null

  const config = currentGalaxy ? GALAXY_CONFIGS[currentGalaxy] : null

  return (
    <AnimatePresence mode="wait">
      {isTransitioning && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.3 }}
          className="fixed inset-0 z-50 flex items-center justify-center pointer-events-none"
          style={{ background: 'rgba(10, 10, 15, 0.95)' }}
        >
          <motion.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 1.2, opacity: 0 }}
            transition={{ type: 'spring', damping: 20, stiffness: 300 }}
            className="flex flex-col items-center gap-6 text-center"
          >
            {/* Wormhole animation */}
            <div className="relative w-48 h-48">
              {[0, 1, 2, 3].map(i => (
                <motion.div
                  key={i}
                  initial={{ scale: 0, opacity: 0 }}
                  animate={{ scale: 1, opacity: 0 }}
                  exit={{ scale: 1.5, opacity: 0 }}
                  transition={{ 
                    duration: 1.5, 
                    repeat: Infinity, 
                    delay: i * 0.2,
                    ease: 'easeOut'
                  }}
                  className="absolute inset-0 rounded-full border-2"
                  style={{ 
                    borderColor: config ? `${config.color}80` : '#7c5cfc80',
                    boxShadow: `0 0 40px ${config?.color || '#7c5cfc'}`
                  }}
                />
              ))}
              <div className="absolute inset-0 flex items-center justify-center">
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ type: 'spring', damping: 15, stiffness: 200 }}
                  className="w-24 h-24 rounded-full flex items-center justify-center"
                  style={{ 
                    background: config ? `linear-gradient(135deg, ${config.color}, ${config.secondaryColor})` : 'linear-gradient(135deg, #7c5cfc, #c8a87c)',
                    boxShadow: `0 0 60px ${config?.color || '#7c5cfc'}`
                  }}
                >
                  <span className="text-3xl text-white">{config?.icon || '🌌'}</span>
                </motion.div>
              </div>
            </div>

            {/* Phase Label */}
            <motion.div
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.2, duration: 0.4 }}
              className="flex flex-col items-center gap-2"
            >
              <p className="text-xs font-mono text-white/50 uppercase tracking-widest">
                {phase === 'GALAXY_ENTER' && 'ENTERING GALAXY'}
                {phase === 'SOLAR_SYSTEM' && 'SOLAR SYSTEM'}
                {phase === 'PLANET_SURFACE' && 'PLANET SURFACE'}
                {phase === 'MOON_DETAIL' && 'MOON DETAIL'}
              </p>
              {config && (
                <p className="text-2xl font-bold text-white">{config.name}</p>
              )}
              <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.4, duration: 0.3 }}
                className="text-sm text-white/50 max-w-xs"
              >
                {config?.descriptionShort}
              </motion.p>
            </motion.div>

            {/* Progress Ring */}
            <motion.svg
              initial={{ rotate: -90 }}
              animate={{ rotate: 270 }}
              transition={{ duration: 1.5, ease: 'linear', repeat: Infinity }}
              className="w-20 h-20"
            >
              <circle
                cx="50%"
                cy="50%"
                r="35"
                fill="none"
                stroke="currentColor"
                strokeWidth="3"
                strokeDasharray="220"
                strokeDashoffset="0"
                strokeLinecap="round"
                style={{ color: config?.color || '#7c5cfc' }}
                className="opacity-30"
              />
              <motion.circle
                cx="50%"
                cy="50%"
                r="35"
                fill="none"
                stroke="currentColor"
                strokeWidth="3"
                strokeDasharray="220"
                strokeDashoffset="0"
                strokeLinecap="round"
                style={{ color: config?.color || '#7c5cfc' }}
                initial={{ strokeDashoffset: 220 }}
                animate={{ strokeDashoffset: 0 }}
                transition={{ duration: 1.5, ease: 'linear', repeat: Infinity }}
              />
            </motion.svg>
          </motion.div>
        </motion.div>
      )}

      {/* Galaxy Enter Overlay - brief flash when entering galaxy */}
      {phase === 'GALAXY_ENTER' && config && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.1 }}
          className="fixed inset-0 z-40 pointer-events-none"
          style={{ 
            background: `radial-gradient(ellipse at center, ${config.color}30 0%, transparent 70%)` 
          }}
        />
      )}
    </AnimatePresence>
  )
}