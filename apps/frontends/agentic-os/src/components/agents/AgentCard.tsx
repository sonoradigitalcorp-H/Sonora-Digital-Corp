import React, { useState, useRef } from 'react';
import { motion, useMotionValue, useTransform, AnimatePresence } from 'framer-motion';
import { Bot, Brain, Zap, DollarSign, Clock, Activity, ChevronRight, RotateCcw } from 'lucide-react';

export interface Agent {
  id: string;
  name: string;
  type: 'research' | 'sales' | 'support' | 'content' | 'voice' | 'code' | 'monitor';
  status: 'idle' | 'working' | 'thinking' | 'speaking' | 'error';
  model: string;
  currentTask?: string;
  tasksCompleted: number;
  totalCost: number;
  avgResponseTime: number;
  lastActive: string;
  capabilities: string[];
  pipeline?: PipelineStage[];
}

export interface PipelineStage {
  name: string;
  description?: string;
  status: 'pending' | 'active' | 'completed' | 'error';
  duration?: number;
  cost?: number;
}

const TYPE_COLORS: Record<string, string> = {
  research: '#7c5cfc',
  sales: '#22c55e',
  support: '#06b6d4',
  content: '#ec4899',
  voice: '#f59e0b',
  code: '#8b5cf6',
  monitor: '#64748b',
};

const STATUS_ICONS: Record<string, React.ReactNode> = {
  idle: <Activity className="w-4 h-4" />,
  working: <Zap className="w-4 h-4 animate-pulse" />,
  thinking: <Brain className="w-4 h-4 animate-spin" />,
  speaking: <Bot className="w-4 h-4 animate-bounce" />,
  error: <RotateCcw className="w-4 h-4" />,
};

export function AgentCard({ agent }: { agent: Agent }) {
  const [isFlipped, setIsFlipped] = useState(false);
  const constraintsRef = useRef(null);

  const x = useMotionValue(0);
  const y = useMotionValue(0);
  const rotateX = useTransform(y, [-100, 100], [5, -5]);
  const rotateY = useTransform(x, [-100, 100], [-5, 5]);

  const typeColor = TYPE_COLORS[agent.type] || '#7c5cfc';

  return (
    <div ref={constraintsRef} className="relative w-80 h-52 perspective-1000">
      <motion.div
        className="w-full h-full relative"
        style={{ rotateX, rotateY, transformStyle: 'preserve-3d' }}
        drag
        dragConstraints={constraintsRef}
        dragElastic={0.1}
        whileDrag={{ scale: 1.05, zIndex: 50 }}
      >
        <AnimatePresence mode="wait">
          {!isFlipped ? (
            <motion.div
              key="front"
              className="absolute inset-0 rounded-2xl border overflow-hidden"
              style={{
                backgroundColor: '#161b22',
                borderColor: `${typeColor}33`,
                boxShadow: `0 0 20px ${typeColor}22, inset 0 1px 0 ${typeColor}22`,
              }}
              initial={{ rotateY: 180 }}
              animate={{ rotateY: 0 }}
              exit={{ rotateY: -180 }}
              transition={{ duration: 0.5, type: 'spring' }}
            >
              {/* Header */}
              <div className="flex items-center justify-between p-4 border-b" style={{ borderColor: `${typeColor}22` }}>
                <div className="flex items-center gap-3">
                  <div
                    className="w-10 h-10 rounded-xl flex items-center justify-center"
                    style={{ backgroundColor: `${typeColor}22`, color: typeColor }}
                  >
                    {STATUS_ICONS[agent.status]}
                  </div>
                  <div>
                    <h3 className="font-semibold text-white text-sm">{agent.name}</h3>
                    <p className="text-xs text-gray-400">{agent.model}</p>
                  </div>
                </div>
                <button
                  onClick={(e) => { e.stopPropagation(); setIsFlipped(true); }}
                  className="w-8 h-8 rounded-lg flex items-center justify-center hover:bg-white/5 transition-colors"
                >
                  <RotateCcw className="w-4 h-4 text-gray-400" />
                </button>
              </div>

              {/* Status Badge */}
              <div className="px-4 pt-3">
                <span
                  className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium"
                  style={{
                    backgroundColor: agent.status === 'working' ? `${typeColor}22` :
                      agent.status === 'error' ? '#ef444422' : '#ffffff11',
                    color: agent.status === 'working' ? typeColor :
                      agent.status === 'error' ? '#ef4444' : '#9ca3af',
                  }}
                >
                  <span className={`w-1.5 h-1.5 rounded-full ${
                    agent.status === 'working' ? 'animate-pulse' : ''
                  }`} style={{
                    backgroundColor: agent.status === 'working' ? typeColor :
                      agent.status === 'error' ? '#ef4444' : '#6b7280',
                  }} />
                  {agent.status}
                </span>
              </div>

              {/* Current Task */}
              {agent.currentTask && (
                <div className="px-4 pt-2">
                  <p className="text-xs text-gray-300 truncate">
                    <ChevronRight className="w-3 h-3 inline mr-1" style={{ color: typeColor }} />
                    {agent.currentTask}
                  </p>
                </div>
              )}

              {/* Stats Footer */}
              <div className="absolute bottom-0 left-0 right-0 flex items-center justify-between px-4 py-3 border-t" style={{ borderColor: `${typeColor}22` }}>
                <div className="flex items-center gap-4">
                  <div className="flex items-center gap-1 text-xs text-gray-400">
                    <DollarSign className="w-3 h-3" />
                    <span>${agent.totalCost.toFixed(4)}</span>
                  </div>
                  <div className="flex items-center gap-1 text-xs text-gray-400">
                    <Clock className="w-3 h-3" />
                    <span>{agent.avgResponseTime}ms</span>
                  </div>
                  <div className="flex items-center gap-1 text-xs text-gray-400">
                    <Zap className="w-3 h-3" />
                    <span>{agent.tasksCompleted}</span>
                  </div>
                </div>
                <div className="text-xs text-gray-500">{agent.lastActive}</div>
              </div>

              {/* Animated border glow */}
              {agent.status === 'working' && (
                <motion.div
                  className="absolute inset-0 rounded-2xl pointer-events-none"
                  style={{ border: `1px solid ${typeColor}` }}
                  animate={{ opacity: [0.3, 0.8, 0.3] }}
                  transition={{ duration: 2, repeat: Infinity }}
                />
              )}
            </motion.div>
          ) : (
            <motion.div
              key="back"
              className="absolute inset-0 rounded-2xl border overflow-hidden p-4"
              style={{
                backgroundColor: '#161b22',
                borderColor: `${typeColor}33`,
                boxShadow: `0 0 20px ${typeColor}22`,
              }}
              initial={{ rotateY: -180 }}
              animate={{ rotateY: 0 }}
              exit={{ rotateY: 180 }}
              transition={{ duration: 0.5, type: 'spring' }}
            >
              {/* Back header */}
              <div className="flex items-center justify-between mb-3">
                <h3 className="font-semibold text-white text-sm">{agent.name} — Pipeline</h3>
                <button
                  onClick={(e) => { e.stopPropagation(); setIsFlipped(false); }}
                  className="w-8 h-8 rounded-lg flex items-center justify-center hover:bg-white/5 transition-colors"
                >
                  <RotateCcw className="w-4 h-4 text-gray-400" />
                </button>
              </div>

              {/* Pipeline Stages */}
              {agent.pipeline && agent.pipeline.length > 0 ? (
                <div className="space-y-2">
                  {agent.pipeline.map((stage, i) => (
                    <div key={i} className="flex items-center gap-2">
                      <div
                        className="w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold shrink-0"
                        style={{
                          backgroundColor: stage.status === 'completed' ? `${typeColor}33` :
                            stage.status === 'active' ? `${typeColor}` :
                            stage.status === 'error' ? '#ef444433' : '#ffffff11',
                          color: stage.status === 'completed' ? typeColor :
                            stage.status === 'active' ? '#fff' :
                            stage.status === 'error' ? '#ef4444' : '#6b7280',
                        }}
                      >
                        {i + 1}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between">
                          <span className="text-xs text-gray-300 truncate">{stage.name}</span>
                          {stage.cost !== undefined && (
                            <span className="text-xs text-gray-500 ml-2">${stage.cost.toFixed(4)}</span>
                          )}
                        </div>
                        {stage.status === 'active' && (
                          <motion.div
                            className="h-0.5 rounded-full mt-1"
                            style={{ backgroundColor: typeColor }}
                            initial={{ width: '0%' }}
                            animate={{ width: '100%' }}
                            transition={{ duration: 2, repeat: Infinity }}
                          />
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="flex items-center justify-center h-20 text-gray-500 text-xs">
                  No active pipeline
                </div>
              )}

              {/* Capabilities */}
              <div className="mt-3 pt-3 border-t" style={{ borderColor: `${typeColor}22` }}>
                <div className="flex flex-wrap gap-1">
                  {agent.capabilities.map((cap, i) => (
                    <span
                      key={i}
                      className="px-2 py-0.5 rounded text-xs"
                      style={{ backgroundColor: `${typeColor}11`, color: `${typeColor}cc` }}
                    >
                      {cap}
                    </span>
                  ))}
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </div>
  );
}
