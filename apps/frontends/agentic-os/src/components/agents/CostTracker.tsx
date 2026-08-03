import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { DollarSign, TrendingUp, TrendingDown, Minus, Zap, Brain, Bot, Mic } from 'lucide-react';

interface CostEntry {
  id: string;
  agent: string;
  type: 'text' | 'voice' | 'llm' | 'api';
  model: string;
  inputTokens: number;
  outputTokens: number;
  cost: number;
  timestamp: Date;
}

interface CostSummary {
  totalToday: number;
  totalMonth: number;
  byAgent: Record<string, number>;
  byType: Record<string, number>;
  trend: 'up' | 'down' | 'stable';
}

const TYPE_CONFIG: Record<string, { icon: React.ReactNode; color: string; label: string }> = {
  text: { icon: <Bot className="w-3 h-3" />, color: '#22c55e', label: 'Texto' },
  voice: { icon: <Mic className="w-3 h-3" />, color: '#f59e0b', label: 'Voz' },
  llm: { icon: <Brain className="w-3 h-3" />, color: '#7c5cfc', label: 'LLM' },
  api: { icon: <Zap className="w-3 h-3" />, color: '#06b6d4', label: 'API' },
};

const MOCK_COSTS: CostEntry[] = [
  { id: '1', agent: 'Ce-Son Bot', type: 'llm', model: 'deepseek-v4-flash', inputTokens: 245, outputTokens: 180, cost: 0.00032, timestamp: new Date(Date.now() - 60000) },
  { id: '2', agent: 'JARVIS', type: 'text', model: 'gpt-4o-mini', inputTokens: 120, outputTokens: 95, cost: 0.00018, timestamp: new Date(Date.now() - 120000) },
  { id: '3', agent: 'Mystic', type: 'llm', model: 'deepseek-v4-flash', inputTokens: 310, outputTokens: 220, cost: 0.00045, timestamp: new Date(Date.now() - 180000) },
  { id: '4', agent: 'Nathy Conta', type: 'api', model: 'internal-api', inputTokens: 0, outputTokens: 0, cost: 0.00001, timestamp: new Date(Date.now() - 240000) },
  { id: '5', agent: 'ABE Agent', type: 'voice', model: 'edge-tts', inputTokens: 0, outputTokens: 0, cost: 0.00000, timestamp: new Date(Date.now() - 300000) },
  { id: '6', agent: 'Research Agent', type: 'llm', model: 'gemini-2.5-flash', inputTokens: 520, outputTokens: 380, cost: 0.00089, timestamp: new Date(Date.now() - 360000) },
  { id: '7', agent: 'Sales Agent', type: 'llm', model: 'deepseek-v4-flash', inputTokens: 180, outputTokens: 140, cost: 0.00025, timestamp: new Date(Date.now() - 420000) },
  { id: '8', agent: 'Content Agent', type: 'text', model: 'llama3.2:3b', inputTokens: 95, outputTokens: 210, cost: 0.00000, timestamp: new Date(Date.now() - 480000) },
];

function formatCost(cost: number): string {
  if (cost === 0) return '$0.00';
  if (cost < 0.001) return `$${cost.toFixed(6)}`;
  if (cost < 0.01) return `$${cost.toFixed(4)}`;
  return `$${cost.toFixed(2)}`;
}

function formatTime(date: Date): string {
  const now = new Date();
  const diff = Math.floor((now.getTime() - date.getTime()) / 1000);
  if (diff < 60) return `${diff}s ago`;
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  return `${Math.floor(diff / 3600)}h ago`;
}

export function CostTracker() {
  const [costs] = useState<CostEntry[]>(MOCK_COSTS);
  const [summary] = useState<CostSummary>({
    totalToday: 0.0021,
    totalMonth: 0.0847,
    byAgent: { 'Ce-Son Bot': 0.0032, 'JARVIS': 0.0018, 'Mystic': 0.0045, 'Nathy Conta': 0.0001, 'ABE Agent': 0.0000 },
    byType: { text: 0.0018, voice: 0.0000, llm: 0.0091, api: 0.0001 },
    trend: 'down',
  });

  const [showDetail, setShowDetail] = useState(false);

  return (
    <div className="space-y-4">
      {/* Summary Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <motion.div
          className="rounded-xl border p-4"
          style={{ backgroundColor: '#161b22', borderColor: '#7c5cfc33' }}
          whileHover={{ scale: 1.02 }}
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-gray-400">Hoy</span>
            <DollarSign className="w-4 h-4 text-green-400" />
          </div>
          <div className="text-2xl font-bold text-white">{formatCost(summary.totalToday)}</div>
          <div className="flex items-center gap-1 mt-1">
            {summary.trend === 'down' ? (
              <TrendingDown className="w-3 h-3 text-green-400" />
            ) : summary.trend === 'up' ? (
              <TrendingUp className="w-3 h-3 text-red-400" />
            ) : (
              <Minus className="w-3 h-3 text-gray-400" />
            )}
            <span className={`text-xs ${summary.trend === 'down' ? 'text-green-400' : summary.trend === 'up' ? 'text-red-400' : 'text-gray-400'}`}>
              vs ayer
            </span>
          </div>
        </motion.div>

        <motion.div
          className="rounded-xl border p-4"
          style={{ backgroundColor: '#161b22', borderColor: '#c8a87c33' }}
          whileHover={{ scale: 1.02 }}
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-gray-400">Mes</span>
            <TrendingUp className="w-4 h-4 text-gold" />
          </div>
          <div className="text-2xl font-bold text-white">{formatCost(summary.totalMonth)}</div>
          <div className="text-xs text-gray-500 mt-1">de $5.00 presupuesto</div>
        </motion.div>

        <motion.div
          className="rounded-xl border p-4"
          style={{ backgroundColor: '#161b22', borderColor: '#22c55e33' }}
          whileHover={{ scale: 1.02 }}
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-gray-400">Local (Ollama)</span>
            <Zap className="w-4 h-4 text-green-400" />
          </div>
          <div className="text-2xl font-bold text-green-400">$0.00</div>
          <div className="text-xs text-gray-500 mt-1">60% interacciones</div>
        </motion.div>

        <motion.div
          className="rounded-xl border p-4"
          style={{ backgroundColor: '#161b22', borderColor: '#ec489933' }}
          whileHover={{ scale: 1.02 }}
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-gray-400">Cloud (OpenRouter)</span>
            <Brain className="w-4 h-4 text-pink-400" />
          </div>
          <div className="text-2xl font-bold text-white">{formatCost(summary.byType.llm)}</div>
          <div className="text-xs text-gray-500 mt-1">40% interacciones</div>
        </motion.div>
      </div>

      {/* Cost by Type Bar */}
      <div className="rounded-xl border p-4" style={{ backgroundColor: '#161b22', borderColor: '#30363d' }}>
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-semibold text-white">Costo por Tipo</h3>
          <button
            onClick={() => setShowDetail(!showDetail)}
            className="text-xs text-gray-400 hover:text-white transition-colors"
          >
            {showDetail ? 'Ocultar' : 'Detalles'}
          </button>
        </div>
        <div className="flex h-3 rounded-full overflow-hidden gap-0.5">
          {Object.entries(summary.byType).map(([type, cost]) => {
            const total = Object.values(summary.byType).reduce((a, b) => a + b, 0);
            const pct = total > 0 ? (cost / total) * 100 : 0;
            const config = TYPE_CONFIG[type];
            return (
              <motion.div
                key={type}
                className="h-full rounded-full"
                style={{ backgroundColor: config?.color || '#6b7280', width: `${Math.max(pct, 2)}%` }}
                initial={{ width: 0 }}
                animate={{ width: `${Math.max(pct, 2)}%` }}
                transition={{ duration: 0.5, delay: 0.1 }}
              />
            );
          })}
        </div>
        <div className="flex flex-wrap gap-3 mt-2">
          {Object.entries(summary.byType).map(([type, cost]) => {
            const config = TYPE_CONFIG[type];
            return (
              <div key={type} className="flex items-center gap-1.5">
                <div className="w-2 h-2 rounded-full" style={{ backgroundColor: config?.color }} />
                <span className="text-xs text-gray-400">{config?.label}</span>
                <span className="text-xs text-gray-500">{formatCost(cost)}</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Recent Transactions */}
      <AnimatePresence>
        {showDetail && (
          <motion.div
            className="rounded-xl border overflow-hidden"
            style={{ backgroundColor: '#161b22', borderColor: '#30363d' }}
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
          >
            <div className="p-4 border-b" style={{ borderColor: '#30363d' }}>
              <h3 className="text-sm font-semibold text-white">Transacciones Recientes</h3>
            </div>
            <div className="divide-y" style={{ borderColor: '#30363d' }}>
              {costs.slice(0, 8).map((entry) => {
                const config = TYPE_CONFIG[entry.type];
                return (
                  <motion.div
                    key={entry.id}
                    className="flex items-center gap-3 px-4 py-3 hover:bg-white/5 transition-colors"
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.2 }}
                  >
                    <div
                      className="w-8 h-8 rounded-lg flex items-center justify-center shrink-0"
                      style={{ backgroundColor: `${config?.color}22`, color: config?.color }}
                    >
                      {config?.icon}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-white font-medium truncate">{entry.agent}</span>
                        <span className="text-sm font-mono text-white ml-2">{formatCost(entry.cost)}</span>
                      </div>
                      <div className="flex items-center gap-2 mt-0.5">
                        <span className="text-xs text-gray-500">{entry.model}</span>
                        {entry.inputTokens > 0 && (
                          <span className="text-xs text-gray-600">
                            {entry.inputTokens}→{entry.outputTokens} tokens
                          </span>
                        )}
                      </div>
                    </div>
                    <span className="text-xs text-gray-600 shrink-0">{formatTime(entry.timestamp)}</span>
                  </motion.div>
                );
              })}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
