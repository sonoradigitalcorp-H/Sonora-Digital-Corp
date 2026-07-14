"use client";
interface BotAvatarProps { name: string; tenant: "abe" | "sdc"; size?: number; pulse?: boolean }

const COLORS = {
  abe: { primary: "#FFD700", secondary: "#B8860B", glow: "#FFD70055", accent: "#FF8C00" },
  sdc: { primary: "#8b5cf6", secondary: "#6d28d9", glow: "#8b5cf655", accent: "#a78bfa" },
};

export function BotAvatar({ name, tenant, size = 48, pulse = false }: BotAvatarProps) {
  const c = COLORS[tenant];
  const half = size / 2;

  return (
    <div style={{
      width: size, height: size, position: "relative",
      display: "flex", alignItems: "center", justifyContent: "center",
      animation: pulse ? "pulseGlow 2s infinite" : undefined,
    }}>
      {/* Glow ring */}
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} style={{ position: "absolute" }}>
        <defs>
          <radialGradient id={`glow-${tenant}`} cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor={c.glow} />
            <stop offset="100%" stopColor="transparent" />
          </radialGradient>
        </defs>
        <circle cx={half} cy={half} r={half * 0.85} fill={`url(#glow-${tenant})`}>
          {pulse && <animate attributeName="r" values={`${half * 0.7};${half * 0.9};${half * 0.7}`} dur="2s" repeatCount="indefinite" />}
        </circle>
      </svg>

      {/* Avatar circle */}
      <svg width={size * 0.7} height={size * 0.7} viewBox="0 0 100 100" style={{ zIndex: 1 }}>
        <defs>
          <linearGradient id={`bg-${tenant}`} x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor={c.primary} />
            <stop offset="100%" stopColor={c.secondary} />
          </linearGradient>
        </defs>
        <circle cx="50" cy="50" r="48" fill={`url(#bg-${tenant})`} />

        {/* Futuristic face/head shape */}
        <ellipse cx="50" cy="48" rx="30" ry="32" fill="#111" opacity="0.9" />

        {/* Eyes - glowing */}
        <ellipse cx="38" cy="42" rx="5" ry="4" fill={c.primary}>
          {pulse && <animate attributeName="opacity" values="1;0.4;1" dur="3s" repeatCount="indefinite" />}
        </ellipse>
        <ellipse cx="62" cy="42" rx="5" ry="4" fill={c.primary}>
          {pulse && <animate attributeName="opacity" values="1;0.4;1" dur="3s" repeatCount="indefinite" />}
        </ellipse>

        {/* AI / HUD lines */}
        <line x1="20" y1="50" x2="32" y2="50" stroke={c.primary} strokeWidth="1.5" opacity="0.6" />
        <line x1="68" y1="50" x2="80" y2="50" stroke={c.primary} strokeWidth="1.5" opacity="0.6" />
        <path d="M30 65 Q50 75 70 65" fill="none" stroke={c.accent} strokeWidth="1.5" opacity="0.5" />

        {/* Top ornament */}
        <path d="M40 18 L50 8 L60 18" fill="none" stroke={c.primary} strokeWidth="2" opacity="0.8" />
        <circle cx="50" cy="16" r="2" fill={c.primary}>
          {pulse && <animate attributeName="r" values="2;3;2" dur="1.5s" repeatCount="indefinite" />}
        </circle>

        {/* Side decorations */}
        <circle cx="15" cy="30" r="2" fill={c.accent} opacity="0.6" />
        <circle cx="85" cy="30" r="2" fill={c.accent} opacity="0.6" />
        <circle cx="15" cy="65" r="1.5" fill={c.primary} opacity="0.4" />
        <circle cx="85" cy="65" r="1.5" fill={c.primary} opacity="0.4" />
      </svg>
    </div>
  );
}
