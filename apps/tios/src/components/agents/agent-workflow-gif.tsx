'use client';

import { useEffect, useState, useMemo } from 'react';
import {
  Brain,
  FileText,
  Scale,
  Users,
  CheckCircle2,
  TrendingUp,
  Shield,
  Music,
} from 'lucide-react';

interface AgentWorkflowGifProps {
  artistName: string;
  score: number;
  growth: number;
  listeners: number;
  dealValue: number;
  showAnimation?: boolean;
}

const STAGES = [
  {
    id: 'analyst',
    name: 'Analyst Agent',
    subtitle: 'Data Analysis',
    icon: Brain,
    color: '#3B82F6',
    textClass: 'text-blue-400',
    bgClass: 'bg-blue-500/10',
    borderClass: 'border-blue-500/30',
    glowClass: 'shadow-blue-500/25',
  },
  {
    id: 'writer',
    name: 'Writer Agent',
    subtitle: 'Brief & Pitch',
    icon: FileText,
    color: '#10B981',
    textClass: 'text-emerald-400',
    bgClass: 'bg-emerald-500/10',
    borderClass: 'border-emerald-500/30',
    glowClass: 'shadow-emerald-500/25',
  },
  {
    id: 'legal',
    name: 'Legal Agent',
    subtitle: 'Compliance Review',
    icon: Scale,
    color: '#EF4444',
    textClass: 'text-red-400',
    bgClass: 'bg-red-500/10',
    borderClass: 'border-red-500/30',
    glowClass: 'shadow-red-500/25',
  },
  {
    id: 'consensus',
    name: 'Consensus',
    subtitle: 'Final Decision',
    icon: Users,
    color: '#8B5CF6',
    textClass: 'text-purple-400',
    bgClass: 'bg-purple-500/10',
    borderClass: 'border-purple-500/30',
    glowClass: 'shadow-purple-500/25',
  },
] as const;

const ARROW_COLORS = ['#3B82F6', '#10B981', '#EF4444'];

function formatCurrency(v: number) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(v);
}

function formatNumber(v: number) {
  return new Intl.NumberFormat('en-US').format(v);
}

function CostBreakdown({ dealValue }: { dealValue: number }) {
  const costs = [
    { label: 'Advance', pct: 0.45, color: 'bg-blue-500' },
    { label: 'Marketing', pct: 0.25, color: 'bg-emerald-500' },
    { label: 'Production', pct: 0.18, color: 'bg-amber-500' },
    { label: 'Legal & IP', pct: 0.07, color: 'bg-red-500' },
    { label: 'Operations', pct: 0.05, color: 'bg-purple-500' },
  ];

  return (
    <div className="rounded-lg bg-accent/30 p-4">
      <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">
        Cost Breakdown
      </h4>
      <div className="space-y-2">
        {costs.map((c) => (
          <div key={c.label} className="flex items-center gap-3">
            <span className="text-xs font-medium w-20 text-muted-foreground">{c.label}</span>
            <div className="flex-1 h-2 rounded-full bg-muted overflow-hidden">
              <div
                className={`h-full rounded-full ${c.color} transition-all duration-700`}
                style={{ width: `${c.pct * 100}%` }}
              />
            </div>
            <span className="text-xs font-mono text-muted-foreground w-10 text-right">
              {Math.round(c.pct * 100)}%
            </span>
            <span className="text-xs font-mono font-medium w-24 text-right">
              {formatCurrency(dealValue * c.pct)}
            </span>
          </div>
        ))}
      </div>
      <div className="flex items-center justify-between mt-2 pt-2 border-t border-border">
        <span className="text-xs font-medium text-muted-foreground">Total Investment</span>
        <span className="text-xs font-mono font-bold">{formatCurrency(dealValue)}</span>
      </div>
    </div>
  );
}

function ScoreBadge({ label, value, color }: { label: string; value: string; color: string }) {
  return (
    <div className="flex items-center justify-between p-2.5 rounded-lg bg-accent/20 border border-border/50">
      <span className="text-xs text-muted-foreground">{label}</span>
      <span className={`text-sm font-mono font-semibold ${color}`}>{value}</span>
    </div>
  );
}

function scoreColor(s: number) {
  if (s >= 80) return 'text-green-400';
  if (s >= 50) return 'text-yellow-400';
  return 'text-red-400';
}

function growthColor(g: number) {
  if (g >= 25) return 'text-green-400';
  if (g >= 10) return 'text-yellow-400';
  return 'text-red-400';
}

export function AgentWorkflowGif({
  artistName,
  score,
  growth,
  listeners,
  dealValue,
  showAnimation = true,
}: AgentWorkflowGifProps) {
  const [activeStage, setActiveStage] = useState(showAnimation ? -1 : 0);

  useEffect(() => {
    if (!showAnimation) {
      setActiveStage(0);
      return;
    }

    const t1 = setTimeout(() => setActiveStage(0), 600);
    const interval = setInterval(() => {
      setActiveStage((prev) => (prev + 1) % 4);
    }, 2600);

    return () => {
      clearTimeout(t1);
      clearInterval(interval);
    };
  }, [showAnimation]);

  const decision = useMemo(() => {
    if (score >= 80) return 'APPROVED' as const;
    if (score >= 50) return 'FLAGGED' as const;
    return 'REJECTED' as const;
  }, [score]);

  const decisionConfig = useMemo(() => {
    if (decision === 'APPROVED')
      return {
        text: 'text-green-400',
        bg: 'bg-green-500/10',
        border: 'border-green-500/40',
        glow: 'shadow-green-500/40',
        label: 'Approved',
        icon: CheckCircle2,
      };
    if (decision === 'FLAGGED')
      return {
        text: 'text-yellow-400',
        bg: 'bg-yellow-500/10',
        border: 'border-yellow-500/40',
        glow: 'shadow-yellow-500/40',
        label: 'Flagged',
        icon: TrendingUp,
      };
    return {
      text: 'text-red-400',
      bg: 'bg-red-500/10',
      border: 'border-red-500/40',
      glow: 'shadow-red-500/40',
      label: 'Rejected',
      icon: Shield,
    };
  }, [decision]);

  const pipelineMetrics = useMemo(() => {
    const analystMetrics = [
      { label: 'Market Score', value: `${score}/100`, color: scoreColor(score) },
      { label: 'Growth Rate', value: `+${growth}%`, color: growthColor(growth) },
      {
        label: 'Listeners',
        value: formatNumber(listeners),
        color: 'text-foreground',
      },
      {
        label: 'Momentum',
        value: growth >= 30 ? 'Strong' : growth >= 15 ? 'Steady' : 'Weak',
        color: growthColor(growth),
      },
    ];

    const writerMetrics = [
      { label: 'Executive Brief', value: 'Ready', color: 'text-green-400' },
      {
        label: 'Narrative Quality',
        value: score >= 80 ? 'Exceptional' : score >= 60 ? 'Strong' : 'Standard',
        color: 'text-emerald-400',
      },
      {
        label: 'Pitch Strength',
        value: `${Math.min(100, Math.round(score * 0.85 + growth * 0.3))}%`,
        color: 'text-foreground',
      },
      {
        label: 'Deal Summary',
        value: formatCurrency(dealValue),
        color: 'text-foreground',
      },
    ];

    const legalMetrics = [
      {
        label: 'Compliance',
        value: score >= 70 ? 'Passed' : 'Flagged',
        color: score >= 70 ? 'text-green-400' : 'text-yellow-400',
      },
      {
        label: 'Risk Score',
        value: `${Math.max(0, Math.min(100, 100 - score))}%`,
        color: score >= 70 ? 'text-green-400' : 'text-red-400',
      },
      {
        label: 'Contract Terms',
        value: dealValue >= 100000 ? 'Custom' : 'Standard',
        color: 'text-foreground',
      },
      {
        label: 'IP Clearance',
        value: score >= 60 ? 'Cleared' : 'Review',
        color: score >= 60 ? 'text-green-400' : 'text-yellow-400',
      },
    ];

    const consensusMetrics = [
      {
        label: 'Analyst Vote',
        value: score >= 70 ? '✓ Approve' : '⚠ Flag',
        color: 'text-blue-400',
      },
      {
        label: 'Writer Vote',
        value: score >= 65 ? '✓ Approve' : '⚠ Flag',
        color: 'text-emerald-400',
      },
      {
        label: 'Legal Vote',
        value: score >= 75 ? '✓ Approve' : '⚠ Flag',
        color: 'text-red-400',
      },
      {
        label: 'Confidence',
        value: `${Math.min(100, Math.round(score * 0.65 + growth * 0.35))}%`,
        color: 'text-foreground',
      },
    ];

    return { analystMetrics, writerMetrics, legalMetrics, consensusMetrics };
  }, [score, growth, listeners, dealValue]);

  const nodeLeftPct = [12.5, 37.5, 62.5, 87.5];

  return (
    <div className="rounded-xl border bg-card overflow-hidden">
      <style>{`
        @keyframes flowDash {
          to { stroke-dashoffset: -16; }
        }
        @keyframes glowPulse {
          0%, 100% { box-shadow: 0 0 8px var(--glow-color); }
          50% { box-shadow: 0 0 24px var(--glow-color); }
        }
        @keyframes fadeSlideIn {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        @keyframes decisionPulse {
          0%, 100% { box-shadow: 0 0 12px var(--dec-glow); }
          50% { box-shadow: 0 0 36px var(--dec-glow); }
        }
        .arrow-flow {
          stroke-dasharray: 4 8;
          animation: flowDash 0.9s linear infinite;
        }
        .arrow-completed {
          opacity: 1 !important;
        }
        .arrow-hidden {
          opacity: 0 !important;
        }
        .stage-glow {
          animation: glowPulse 2s ease-in-out infinite;
        }
        .detail-enter {
          animation: fadeSlideIn 0.45s ease-out;
        }
        .decision-glow {
          animation: decisionPulse 2s ease-in-out infinite;
        }
      `}</style>

      {/* Header */}
      <div className="flex items-center justify-between px-5 pt-5 pb-3">
        <div>
          <h3 className="font-semibold text-sm flex items-center gap-2">
            <Music className="h-4 w-4 text-primary" />
            {artistName}
          </h3>
          <p className="text-xs text-muted-foreground mt-0.5">Agent Workflow Pipeline</p>
        </div>
        <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
          {[0, 1, 2, 3].map((i) => (
            <button
              key={i}
              onClick={() => setActiveStage(i)}
              className={`w-2.5 h-2.5 rounded-full transition-all duration-300 ${
                i === activeStage
                  ? 'scale-125'
                  : activeStage > i
                    ? 'opacity-60'
                    : 'opacity-25'
              }`}
              style={{
                backgroundColor:
                  i <= activeStage ? STAGES[i].color : 'var(--muted-foreground)',
              }}
            />
          ))}
        </div>
      </div>

      {/* Pipeline Visualization */}
      <div className="relative mx-5" style={{ height: '140px' }}>
        {/* SVG Arrows */}
        <svg
          className="absolute inset-0 w-full h-full pointer-events-none"
          viewBox="0 0 760 140"
          preserveAspectRatio="xMidYMid meet"
        >
          <defs>
            <marker id="arr-base" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">
              <path d="M0,0 L6,3 L0,6 Z" fill="#6B7280" />
            </marker>
            {ARROW_COLORS.map((color, i) => (
              <marker
                key={i}
                id={`arr-${i}`}
                markerWidth="7"
                markerHeight="7"
                refX="6"
                refY="3.5"
                orient="auto"
              >
                <path d="M0,0 L7,3.5 L0,7 Z" fill={color} />
              </marker>
            ))}
          </defs>

          {/* Base arrows (always visible, gray) */}
          {[0, 1, 2].map((i) => (
            <line
              key={`base-${i}`}
              x1={125 + i * 190}
              y1="70"
              x2={255 + i * 190}
              y2="70"
              stroke="#374151"
              strokeWidth="2"
              markerEnd="url(#arr-base)"
            />
          ))}

          {/* Flow overlay arrows */}
          {[0, 1, 2].map((i) => {
            const isActive = activeStage === i;
            const isCompleted = activeStage > i;
            const isFuture = activeStage < i;
            return (
              <line
                key={`flow-${i}`}
                x1={125 + i * 190}
                y1="70"
                x2={255 + i * 190}
                y2="70"
                stroke={ARROW_COLORS[i]}
                strokeWidth="2.5"
                className={
                  isFuture
                    ? 'arrow-hidden'
                    : isActive
                      ? 'arrow-flow'
                      : 'arrow-completed'
                }
                markerEnd={isCompleted ? `url(#arr-${i})` : undefined}
              />
            );
          })}
        </svg>

        {/* Stage Nodes */}
        {STAGES.map((stage, i) => {
          const Icon = stage.icon;
          const isActive = activeStage === i;
          const isCompleted = activeStage > i;
          const isFuture = activeStage < i || activeStage === -1;

          return (
            <button
              key={stage.id}
              onClick={() => setActiveStage(i)}
              className="absolute flex flex-col items-center transition-all duration-500 cursor-pointer"
              style={{
                left: `${nodeLeftPct[i]}%`,
                top: '50%',
                transform: 'translate(-50%, -50%)',
                opacity: isFuture ? 0.35 : 1,
              }}
            >
              <div
                className={`w-14 h-14 rounded-full flex items-center justify-center border-2 transition-all duration-500 ${
                  isActive
                    ? `${stage.borderClass} stage-glow`
                    : isCompleted
                      ? 'border-green-500/50 bg-green-500/20'
                      : 'border-border bg-accent/20'
                }`}
                style={
                  isActive ? ({ '--glow-color': `${stage.color}60` } as React.CSSProperties) : {}
                }
              >
                {isCompleted ? (
                  <CheckCircle2 className="w-6 h-6 text-green-400" />
                ) : (
                  <Icon
                    className={`w-6 h-6 ${isActive ? '' : 'text-muted-foreground'}`}
                    style={{ color: isActive ? stage.color : undefined }}
                  />
                )}
              </div>
              <span
                className={`text-xs font-semibold mt-2 transition-colors duration-300 ${
                  isActive ? stage.textClass : isCompleted ? 'text-green-400' : 'text-muted-foreground'
                }`}
              >
                {stage.name.split(' ')[0]}
              </span>
              <span className="text-[10px] text-muted-foreground leading-none">
                {isCompleted ? 'Done' : stage.subtitle}
              </span>
            </button>
          );
        })}
      </div>

      {/* Detail Panel */}
      {activeStage >= 0 && (
        <div key={activeStage} className="detail-enter px-5 pb-5 pt-2">
          {/* Stage Header */}
          <div className="flex items-center gap-3 mb-4">
            {(() => {
              const stage = STAGES[activeStage];
              const Icon = stage.icon;
              return (
                <>
                  <div className={`p-2 rounded-lg ${stage.bgClass} ${stage.borderClass} border`}>
                    <Icon className={`w-5 h-5 ${stage.textClass}`} />
                  </div>
                  <div>
                    <p className="text-sm font-semibold">{stage.name}</p>
                    <p className="text-xs text-muted-foreground">{stage.subtitle}</p>
                  </div>
                </>
              );
            })()}
          </div>

          {/* Metrics */}
          {activeStage < 3 && (
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 mb-4">
              {(
                [
                  pipelineMetrics.analystMetrics,
                  pipelineMetrics.writerMetrics,
                  pipelineMetrics.legalMetrics,
                ] as const
              )[activeStage].map((m) => (
                <ScoreBadge key={m.label} label={m.label} value={m.value} color={m.color} />
              ))}
            </div>
          )}

          {/* Consensus Detail */}
          {activeStage === 3 && (
            <>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 mb-4">
                {pipelineMetrics.consensusMetrics.map((m) => (
                  <ScoreBadge key={m.label} label={m.label} value={m.value} color={m.color} />
                ))}
              </div>

              {/* Decision Badge */}
              <div
                className={`decision-glow flex items-center justify-center gap-3 py-4 rounded-xl border-2 ${decisionConfig.bg} ${decisionConfig.border} ${decisionConfig.text}`}
                style={{ '--dec-glow': `${decisionConfig.border.split(' ')[0].replace('border-', '').replace('/40', '')}60` } as React.CSSProperties}
              >
                <decisionConfig.icon className="w-8 h-8" />
                <span className="text-2xl font-bold tracking-wider">{decision}</span>
              </div>
            </>
          )}

          {/* Cost Breakdown */}
          <div className="mt-4">
            <CostBreakdown dealValue={dealValue} />
          </div>
        </div>
      )}
    </div>
  );
}
