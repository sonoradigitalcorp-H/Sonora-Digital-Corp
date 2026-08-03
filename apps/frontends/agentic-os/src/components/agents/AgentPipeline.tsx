import { motion } from 'framer-motion';
import { CheckCircle, Circle, AlertCircle, Loader, Clock } from 'lucide-react';

interface PipelineStep {
  name: string;
  description?: string;
  status: 'pending' | 'active' | 'completed' | 'error';
  duration?: number;
  cost?: number;
  model?: string;
}

interface AgentPipelineProps {
  agentName: string;
  steps: PipelineStep[];
  totalCost: number;
  totalDuration: number;
}

const STATUS_CONFIG = {
  completed: { icon: CheckCircle, color: '#22c55e', bg: '#22c55e22' },
  active: { icon: Loader, color: '#7c5cfc', bg: '#7c5cfc22' },
  pending: { icon: Circle, color: '#6b7280', bg: '#ffffff11' },
  error: { icon: AlertCircle, color: '#ef4444', bg: '#ef444422' },
};

export function AgentPipeline({ agentName, steps, totalCost, totalDuration }: AgentPipelineProps) {
  const completedCount = steps.filter(s => s.status === 'completed').length;
  const progress = steps.length > 0 ? (completedCount / steps.length) * 100 : 0;

  return (
    <div className="rounded-2xl border p-5" style={{ backgroundColor: '#161b22', borderColor: '#30363d' }}>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-base font-semibold text-white">{agentName}</h3>
          <p className="text-xs text-gray-400 mt-0.5">Pipeline de ejecución</p>
        </div>
        <div className="flex items-center gap-4">
          <div className="text-right">
            <div className="text-xs text-gray-400">Costo</div>
            <div className="text-sm font-mono text-white">${totalCost.toFixed(4)}</div>
          </div>
          <div className="text-right">
            <div className="text-xs text-gray-400">Duración</div>
            <div className="text-sm font-mono text-white">{totalDuration}ms</div>
          </div>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="h-1.5 bg-white/5 rounded-full overflow-hidden mb-5">
        <motion.div
          className="h-full rounded-full"
          style={{
            background: 'linear-gradient(90deg, #7c5cfc, #c8a87c)',
          }}
          initial={{ width: 0 }}
          animate={{ width: `${progress}%` }}
          transition={{ duration: 0.5, ease: 'easeOut' }}
        />
      </div>

      {/* Pipeline Steps */}
      <div className="space-y-0">
        {steps.map((step, i) => {
          const config = STATUS_CONFIG[step.status];
          const Icon = config.icon;
          const isLast = i === steps.length - 1;

          return (
            <div key={i} className="flex gap-3">
              {/* Timeline */}
              <div className="flex flex-col items-center">
                <motion.div
                  className="w-8 h-8 rounded-full flex items-center justify-center shrink-0 relative z-10"
                  style={{ backgroundColor: config.bg }}
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ delay: i * 0.1, type: 'spring' }}
                >
                  <Icon
                    className="w-4 h-4"
                    style={{
                      color: config.color,
                      ...(step.status === 'active' ? { animation: 'spin 1s linear infinite' } : {}),
                    }}
                  />
                </motion.div>
                {!isLast && (
                  <div
                    className="w-0.5 flex-1 min-h-[20px]"
                    style={{
                      backgroundColor: step.status === 'completed' ? '#22c55e44' : '#ffffff11',
                    }}
                  />
                )}
              </div>

              {/* Content */}
              <motion.div
                className={`flex-1 pb-4 ${isLast ? '' : ''}`}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.1 + 0.05 }}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <span className="text-sm font-medium text-white">{step.name}</span>
                    <span className="text-xs text-gray-500 ml-2">{step.description}</span>
                  </div>
                  <div className="flex items-center gap-3 shrink-0">
                    {step.model && (
                      <span className="text-xs px-2 py-0.5 rounded bg-white/5 text-gray-400">{step.model}</span>
                    )}
                    {step.duration !== undefined && (
                      <div className="flex items-center gap-1 text-xs text-gray-500">
                        <Clock className="w-3 h-3" />
                        {step.duration}ms
                      </div>
                    )}
                    {step.cost !== undefined && (
                      <span className="text-xs font-mono text-gray-400">${step.cost.toFixed(4)}</span>
                    )}
                  </div>
                </div>
              </motion.div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
