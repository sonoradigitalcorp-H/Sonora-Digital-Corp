export const products = [
  {
    id: 'call-engine',
    name: 'AI Call Engine',
    tagline: 'Agente telefónico que llama, califica y cierra',
    description: 'Agente IA que realiza llamadas simultáneas desde WhatsApp, maneja objeciones con metodología Brian Tracy, califica leads automáticamente y agenda citas.',
    icon: '📞',
    color: '#22c55e',
    features: [
      'Llamadas paralelas desde tu WhatsApp',
      'Manejo de objeciones en 5 pasos',
      'Scoring automático de leads',
      'Resiste "no cuelgues" y "llama después"',
      'Post-seguimiento vía WhatsApp',
    ],
    metrics: { calls: '500+', conversion: '34%', avgDuration: '4:30' },
  },
  {
    id: 'clone',
    name: 'Clone Publicitario',
    tagline: 'Tu réplica digital para contenido sin grabar',
    description: 'Entrenamos un modelo LoRA de tu rostro y clonamos tu voz con 5 audios. Genera fotos, talking heads y locuciones con tu identidad.',
    icon: '🎭',
    color: '#c8a87c',
    features: [
      'LoRA facial entrenado en minutos',
      'Clonación de voz con 5 audios',
      'Fotos + Talking Head + TTS',
      'Entrega por WhatsApp directo',
      'Re-entrenable con nuevo contenido',
    ],
    metrics: { faces: '47', voices: '32', assets: '1,280' },
  },
  {
    id: 'whatsapp',
    name: 'WhatsApp AI Agent',
    tagline: 'Bot inteligente que vende 24/7',
    description: 'Bot WhatsApp con IA en español mexicano. Atiende clientes, toma pedidos, resuelve dudas y procesa pagos — sin intervención humana.',
    icon: '💬',
    color: '#7c5cfc',
    features: [
      'Respuestas instantáneas desde tu número',
      'Catálogo de productos integrado',
      'Pagos vía Stripe / Mercado Pago',
      'Escala a miles de conversaciones',
      'Dashboard de métricas en vivo',
    ],
    metrics: { conversations: '12.4K', satisfaction: '94%', avgResponse: '1.2s' },
  },
]

export const metrics = {
  agents: 10,
  capabilities: 12,
  tools: 49,
  skills: 164,
  uptime: '99.9',
  events: { total: 93, active: true },
}

export const team = [
  { name: 'Luis Daniel Guerrero', role: 'Founder & CTO', initials: 'LG' },
  { name: 'Noel Nichols', role: 'Creative Partner', initials: 'NN' },
  { name: 'Abraham Ortega', role: 'CEO ABE Music', initials: 'AO' },
]

export const plans = [
  {
    name: 'Starter',
    price: 299,
    description: 'Para negocios que empiezan',
    features: ['1 agente IA', '500 llamadas/mes', 'WhatsApp integrado', 'Dashboard básico'],
    popular: false,
  },
  {
    name: 'Pro',
    price: 499,
    description: 'Para equipos en crecimiento',
    features: ['3 agentes IA', '2,000 llamadas/mes', 'Clone + WhatsApp + Call Engine', 'Dashboard avanzado + KPIs', 'Stripe/Mercado Pago'],
    popular: true,
  },
  {
    name: 'Enterprise',
    price: 999,
    description: 'Para empresas con volumen',
    features: ['Agentes ilimitados', 'Llamadas ilimitadas', 'Todos los productos', 'Agente dedicado + onboarding', 'API personalizada', 'SLA 99.99%'],
    popular: false,
  },
]
