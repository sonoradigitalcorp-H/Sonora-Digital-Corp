# ADR-0008: A2A Cowork hub-and-spoke
Estado: ACEPTADO 2026-08-17
Contexto: Los agentes deben coordinarse y hablar al jefe sin procesos nuevos
que tumben el sistema (trauma: 409, crash-loops, CPU 100%).
Decisión:
1. Hermes = ÚNICO hub que delega. Agentes NUNCA spawnean agentes/procesos.
2. Mensajería inter-agentes = kanban.db existente (card: tenant/owner/tarea/
   salida/deadline). Cero sockets, cero MCPs nuevos.
3. Delegación = delegate_task + hermes_agents_mcp (leer persona/rules ANTES).
4. Voz proactiva al jefe: voice_reply.py (people.json). Máx 3 voces/día/tenant.
5. Memoria aislada por tenant: viaja la tarea, no la memoria.
Consecuencias: sdc-cowork-orchestrator se llena con Flujos A/B/C.
Cron nativo 6h revisa leads hot y citas → voz al jefe.