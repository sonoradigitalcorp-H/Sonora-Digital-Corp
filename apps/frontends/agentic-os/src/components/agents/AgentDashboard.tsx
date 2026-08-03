import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Bot, Brain, Zap, DollarSign, Activity, Grid, List } from 'lucide-react';
import { AgentCard, Agent } from './AgentCard';
import { CostTracker } from './CostTracker';
import { AgentPipeline } from './AgentPipeline';

const MOCK_AGENTS: Agent[] = [
  {
    id: 'ce-son',
    name: 'Ce-Son Bot',
    type: 'sales',
    status: 'working',
    model: 'deepseek-v4-flash',
    currentTask: 'Procesando pedido #ORD-8F3A — 2x Uva, 1x Fresa',
    tasksCompleted: 1247,
    totalCost: 0.0032,
    avgResponseTime: 320,
    lastActive: '2m ago',
    capabilities: ['order-processing', 'payment', 'dispatch', 'llm-parsing'],
    pipeline: [
      { name: 'Intent Detection', status: 'completed', duration: 12, cost: 0 },
      { name: 'LLM Order Parse', status: 'completed', duration: 280, cost: 0.00028 },
      { name: 'Menu Validation', status: 'completed', duration: 5, cost: 0 },
      { name: 'Cart Update', status: 'completed', duration: 8, cost: 0 },
      { name: 'DB Create Order', status: 'active', duration: 45, cost: 0.00001 },
      { name: 'Dispatch to Group', status: 'pending', cost: 0 },
    ],
  },
  {
    id: 'mystic',
    name: 'Mystic',
    type: 'support',
    status: 'idle',
    model: 'deepseek-v4-flash',
    tasksCompleted: 892,
    totalCost: 0.0045,
    avgResponseTime: 450,
    lastActive: '15m ago',
    capabilities: ['personal-assistant', 'voice', 'image', 'video'],
    pipeline: [
      { name: 'Message Received', status: 'completed', duration: 2, cost: 0 },
      { name: 'Kill Switch Check', status: 'completed', duration: 1, cost: 0 },
      { name: 'Intent Detection', status: 'completed', duration: 8, cost: 0 },
      { name: 'LLM Response', status: 'completed', duration: 420, cost: 0.00042 },
      { name: 'Send Response', status: 'completed', duration: 15, cost: 0 },
    ],
  },
  {
    id: 'jarvis',
    name: 'JARVIS',
    type: 'voice',
    status: 'thinking',
    model: 'gpt-4o-mini',
    currentTask: 'Analizando métricas del sistema...',
    tasksCompleted: 456,
    totalCost: 0.0018,
    avgResponseTime: 580,
    lastActive: '5m ago',
    capabilities: ['voice-chat', 'tts', 'stt', 'system-monitor'],
    pipeline: [
      { name: 'Voice Input (STT)', status: 'completed', duration: 850, cost: 0 },
      { name: 'Context Build', status: 'completed', duration: 15, cost: 0 },
      { name: 'LLM Reasoning', status: 'active', duration: 520, cost: 0.00052 },
      { name: 'TTS Generation', status: 'pending', cost: 0 },
      { name: 'Voice Output', status: 'pending', cost: 0 },
    ],
  },
  {
    id: 'research',
    name: 'Research Agent',
    type: 'research',
    status: 'working',
    model: 'gemini-2.5-flash',
    currentTask: 'Investigando tendencias de mercado Q3 2026',
    tasksCompleted: 234,
    totalCost: 0.0089,
    avgResponseTime: 1200,
    lastActive: '1m ago',
    capabilities: ['web-search', 'article-analysis', 'market-research'],
    pipeline: [
      { name: 'Query Analysis', status: 'completed', duration: 20, cost: 0 },
      { name: 'Web Search', status: 'completed', duration: 350, cost: 0.0001 },
      { name: 'Content Extract', status: 'completed', duration: 180, cost: 0 },
      { name: 'LLM Synthesis', status: 'active', duration: 950, cost: 0.00095 },
      { name: 'Report Generate', status: 'pending', cost: 0 },
    ],
  },
  {
    id: 'nathy-conta',
    name: 'Nathy Conta',
    type: 'support',
    status: 'working',
    model: 'deepseek-v4-flash-free',
    currentTask: 'Calculando nómina quincenal — 15 empleados',
    tasksCompleted: 156,
    totalCost: 0.0001,
    avgResponseTime: 280,
    lastActive: '30s ago',
    capabilities: ['cfdi', 'sat', 'nominas', 'resico', 'contpaq'],
    pipeline: [
      { name: 'Parse Request', status: 'completed', duration: 10, cost: 0 },
      { name: 'SAT Validation', status: 'completed', duration: 120, cost: 0 },
      { name: 'Calculate Payroll', status: 'completed', duration: 85, cost: 0 },
      { name: 'Generate CFDI', status: 'active', duration: 200, cost: 0.00001 },
      { name: 'Send to Client', status: 'pending', cost: 0 },
    ],
  },
  {
    id: 'sales',
    name: 'Sales Agent',
    type: 'sales',
    status: 'idle',
    model: 'deepseek-v4-flash',
    tasksCompleted: 312,
    totalCost: 0.0025,
    avgResponseTime: 350,
    lastActive: '8m ago',
    capabilities: ['lead-scoring', 'crm', 'follow-up', 'pipeline'],
    pipeline: [
      { name: 'Lead Detect', status: 'completed', duration: 5, cost: 0 },
      { name: 'Score Lead', status: 'completed', duration: 45, cost: 0.00005 },
      { name: 'CRM Update', status: 'completed', duration: 30, cost: 0 },
      { name: 'Follow-up', status: 'completed', duration: 180, cost: 0.00018 },
    ],
  },
  {
    id: 'content',
    name: 'Content Agent',
    type: 'content',
    status: 'idle',
    model: 'llama3.2:3b',
    tasksCompleted: 189,
    totalCost: 0.0000,
    avgResponseTime: 890,
    lastActive: '20m ago',
    capabilities: ['content-gen', 'social-media', 'blog', 'email'],
    pipeline: [
      { name: 'Topic Research', status: 'completed', duration: 120, cost: 0 },
      { name: 'Draft Generate', status: 'completed', duration: 750, cost: 0 },
      { name: 'Format & Polish', status: 'completed', duration: 20, cost: 0 },
    ],
  },
  {
    id: 'monitor',
    name: 'Monitor Agent',
    type: 'monitor',
    status: 'working',
    model: 'local-rules',
    currentTask: 'Escaneando 9 containers Docker...',
    tasksCompleted: 5678,
    totalCost: 0.0000,
    avgResponseTime: 15,
    lastActive: 'ahora',
    capabilities: ['health-check', 'auto-restart', 'alerting', 'metrics'],
    pipeline: [
      { name: 'Check Containers', status: 'completed', duration: 8, cost: 0 },
      { name: 'Check Services', status: 'completed', duration: 12, cost: 0 },
      { name: 'Check Memory', status: 'active', duration: 5, cost: 0 },
      { name: 'Alert if Down', status: 'pending', cost: 0 },
    ],
  },
];

const TYPE_FILTERS = [
  { key: 'all', label: 'Todos', icon: Grid },
  { key: 'working', label: 'Activos', icon: Zap },
  { key: 'sales', label: 'Ventas', icon: DollarSign },
  { key: 'support', label: 'Soporte', icon: Bot },
  { key: 'research', label: 'Investigación', icon: Brain },
];

export function AgentDashboard() {
  const [filter, setFilter] = useState('all');
  const [view, setView] = useState<'grid' | 'pipeline'>('grid');
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);

  const filteredAgents = MOCK_AGENTS.filter(agent => {
    if (filter === 'all') return true;
    if (filter === 'working') return agent.status === 'working' || agent.status === 'thinking';
    return agent.type === filter;
  });

  const totalCost = MOCK_AGENTS.reduce((sum, a) => sum + a.totalCost, 0);
  const activeAgents = MOCK_AGENTS.filter(a => a.status === 'working' || a.status === 'thinking').length;
  const totalTasks = MOCK_AGENTS.reduce((sum, a) => sum + a.tasksCompleted, 0);

  return (
    <div className="min-h-screen p-6" style={{ backgroundColor: '#0a0a0f' }}>
      {/* Header */}
      <motion.div
        className="mb-8"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-white mb-1">
              Agent Dashboard
            </h1>
            <p className="text-gray-400">Monitoreo en tiempo real de agentes IA</p>
          </div>
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 px-4 py-2 rounded-xl border" style={{ backgroundColor: '#161b22', borderColor: '#30363d' }}>
              <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
              <span className="text-sm text-gray-300">{activeAgents} activos</span>
            </div>
            <div className="flex items-center gap-2 px-4 py-2 rounded-xl border" style={{ backgroundColor: '#161b22', borderColor: '#30363d' }}>
              <DollarSign className="w-4 h-4 text-green-400" />
              <span className="text-sm text-gray-300">${totalCost.toFixed(4)}</span>
            </div>
            <div className="flex items-center gap-2 px-4 py-2 rounded-xl border" style={{ backgroundColor: '#161b22', borderColor: '#30363d' }}>
              <Activity className="w-4 h-4 text-purple-400" />
              <span className="text-sm text-gray-300">{totalTasks.toLocaleString()} tareas</span>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Filters */}
      <motion.div
        className="flex items-center gap-2 mb-6"
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
      >
        {TYPE_FILTERS.map(f => {
          const Icon = f.icon;
          return (
            <button
              key={f.key}
              onClick={() => setFilter(f.key)}
              className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all ${
                filter === f.key
                  ? 'bg-purple-500/20 text-purple-400 border border-purple-500/30'
                  : 'bg-white/5 text-gray-400 border border-transparent hover:bg-white/10'
              }`}
            >
              <Icon className="w-4 h-4" />
              {f.label}
            </button>
          );
        })}
        <div className="flex-1" />
        <div className="flex items-center gap-1 p-1 rounded-xl bg-white/5">
          <button
            onClick={() => setView('grid')}
            className={`p-2 rounded-lg transition-colors ${view === 'grid' ? 'bg-purple-500/20 text-purple-400' : 'text-gray-400 hover:text-white'}`}
          >
            <Grid className="w-4 h-4" />
          </button>
          <button
            onClick={() => setView('pipeline')}
            className={`p-2 rounded-lg transition-colors ${view === 'pipeline' ? 'bg-purple-500/20 text-purple-400' : 'text-gray-400 hover:text-white'}`}
          >
            <List className="w-4 h-4" />
          </button>
        </div>
      </motion.div>

      {/* Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Agent Grid */}
        <div className="lg:col-span-2">
          <AnimatePresence mode="wait">
            {view === 'grid' ? (
              <motion.div
                key="grid"
                className="grid grid-cols-1 md:grid-cols-2 gap-4"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
              >
                {filteredAgents.map((agent, i) => (
                  <motion.div
                    key={agent.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.05 }}
                    onClick={() => setSelectedAgent(selectedAgent?.id === agent.id ? null : agent)}
                  >
                    <AgentCard agent={agent} />
                  </motion.div>
                ))}
              </motion.div>
            ) : (
              <motion.div
                key="pipeline"
                className="space-y-4"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
              >
                {filteredAgents.map((agent, i) => (
                  <motion.div
                    key={agent.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.05 }}
                  >
                    <AgentPipeline
                      agentName={agent.name}
                      steps={agent.pipeline || []}
                      totalCost={agent.totalCost}
                      totalDuration={agent.avgResponseTime}
                    />
                  </motion.div>
                ))}
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Cost Tracker Sidebar */}
        <div className="lg:col-span-1">
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <CostTracker />
          </motion.div>
        </div>
      </div>
    </div>
  );
}
