'use client';

import { useEffect, useState } from 'react';

interface ScoreRingProps {
  score: number;
  size?: number;
  strokeWidth?: number;
  className?: string;
  animated?: boolean;
  label?: string;
  sublabel?: string;
}

export function ScoreRing({
  score,
  size = 80,
  strokeWidth = 4,
  className = '',
  animated = true,
  label,
  sublabel,
}: ScoreRingProps) {
  const [displayScore, setDisplayScore] = useState(animated ? 0 : score);

  useEffect(() => {
    if (!animated) { setDisplayScore(score); return; }

    const duration = 1000; // ms
    const steps = 30;
    const increment = score / steps;
    let current = 0;
    const timer = setInterval(() => {
      current += increment;
      if (current >= score) {
        setDisplayScore(score);
        clearInterval(timer);
      } else {
        setDisplayScore(Math.round(current));
      }
    }, duration / steps);

    return () => clearInterval(timer);
  }, [score, animated]);

  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const offset = circumference - (displayScore / 100) * circumference;

  const scoreColor = score >= 80 ? '#22c55e'
    : score >= 60 ? '#3B82F6'
    : score >= 40 ? '#f59e0b'
    : '#ef4444';

  const scoreGlow = score >= 80 ? '0 0 20px rgba(34,197,94,0.2)'
    : score >= 60 ? '0 0 20px rgba(59,130,246,0.2)'
    : score >= 40 ? '0 0 20px rgba(245,158,11,0.2)'
    : '0 0 20px rgba(239,68,68,0.2)';

  const textColor = score >= 80 ? 'text-green-400'
    : score >= 60 ? 'text-primary'
    : score >= 40 ? 'text-amber-400'
    : 'text-rose-400';

  return (
    <div className={`relative inline-flex items-center justify-center ${className}`} style={{ width: size, height: size }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} className="transform -rotate-90">
        {/* Background circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="hsl(var(--muted))"
          strokeWidth={strokeWidth}
        />
        {/* Score arc */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={scoreColor}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          style={{
            transition: 'stroke-dashoffset 1s cubic-bezier(0.16, 1, 0.3, 1)',
            filter: `drop-shadow(${scoreGlow})`,
          }}
        />
      </svg>
      {/* Center text */}
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className={`text-lg font-black leading-none ${textColor}`} style={{ fontSize: size * 0.28 }}>
          {displayScore}
        </span>
        {sublabel && (
          <span className="text-[8px] text-muted-foreground leading-none mt-0.5">{sublabel}</span>
        )}
        {label && (
          <span className="text-[7px] text-muted-foreground/60 leading-none mt-0.5 uppercase tracking-wider">{label}</span>
        )}
      </div>
    </div>
  );
}
