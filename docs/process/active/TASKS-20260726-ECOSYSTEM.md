# TASKS — SDC Ecosystem Implementation

## Fase 1: Twilio Voice Bridge (Semana 1)
- [ ] Configurar cuenta Twilio + comprar número MX
- [ ] Iniciar `python3 -m apps.twilio_voice.server` en VPS
- [ ] Configurar webhook en Twilio Console
- [ ] Probar llamada entrante: cliente llama → Kokoro responde
- [ ] Probar llamada saliente: API → Twilio llama → lead escucha Kokoro
- [ ] Integrar cost_tracker: cada llamada registra costo real
- [ ] E2E: Llamada completa con transcripción en Engram

## Fase 2: Tokenomics & Dashboard (Semana 1-2)
- [ ] Token Engine: partners CRUD + precios por acción
- [ ] Comisión oculta: descuento antes de mostrar ganancia
- [ ] Dashboard partner: ingreso, clientes, agentes (sin costos SDC)
- [ ] Dashboard admin (tú): costos reales, márgenes, alertas

## Fase 3: Gamificación (Semana 2-3)
- [ ] Gamification Engine: XP + niveles + badges
- [ ] Play to Earn: entrenar agente → XP
- [ ] Work to Earn: ventas → bonus
- [ ] Learn to Earn: cursos → desbloqueos
- [ ] Retos diarios + notificaciones

## Fase 4: Red Multinivel (Semana 3-4)
- [ ] Multinivel Engine: grafos de referidos en Neo4j
- [ ] Comisiones automáticas por nivel
- [ ] Trazabilidad total: cada transacción en Engram
- [ ] Dashboard de red para partners

## Fase 5: Agente Consciente (Semana 4+)
- [ ] Memoria 7 capas por usuario final
- [ ] Personalidad adaptativa por tono/estilo
- [ ] Detección emocional básica (tono, ritmo, pausas)
- [ ] "Sabe quién eres" en cada interacción
