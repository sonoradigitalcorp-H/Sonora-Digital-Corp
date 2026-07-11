# Sonora Platform

## Stack
- OpenCode v1.17+ con plugins: superpowers, power-pack, background-agents
- MCP: Stripe, GitHub, PostgreSQL, Neo4j, Qdrant, Telegram, ABE Service
- Python 3.11+ para lógica de negocio (src/abe/, src/voice/, src/collectors/)
- ABE Service en :5180 (CRM, revenue, contracts)

## Cliente activo: ABE Music Group
- Artistas: Hector Rubio, Jesus Urquijo, Javier Arvayo
- Asistente de voz: "Abe"
- Split regalías: 70% artista / 20% sello / 10% reserva
- Canales: Web, Telegram, Voz

## Metodología (vía superpowers)
Usa superpowers para todo desarrollo:
1. brainstorming -> diseño
2. writing-plans -> tareas 2-5 min
3. subagent-driven-development -> 1 subagente por tarea
4. test-driven-development -> RED-GREEN-REFACTOR
5. requesting-code-review -> revisión
6. finishing-a-development-branch -> merge

## Comandos
/status -> healthcheck general
/revenue -> reporte de regalías
/onboard -> wizard nuevo artista
/brainstorm -> iniciar diseño con superpowers
