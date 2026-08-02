# ADR-20260726 — Arquitectura del Ecosistema SDC

## Estado
Aceptado

## Contexto
El sistema actual tiene voice bridge, agentes, memoria y cost tracking, pero todo está disperso sin un modelo de negocio claro. César (AztroTech) propuso 50/50 y factura $1M MXN/mes. Necesitamos una arquitectura que soporte:

- Múltiples partners white-label con pricing propio
- Comisión oculta para SDC
- Gamificación para retención de usuarios
- Red multinivel para expansión
- Agentes con conciencia (memoria + personalidad adaptativa)

## Decisión
Adoptar una arquitectura de 5 capas sobre el Grimoire existente:

1. **Capa de Voz** (Twilio + Kokoro + Whisper) 
   - Inbound agent (recibe llamadas)
   - Outbound agent (hace llamadas)
   - Estado: en desarrollo (`apps/twilio-voice/server.py`)

2. **Capa de Tokenomics** (Token Engine + Cost Tracker)
   - Partners fijan precios por acción
   - SDC toma comisión oculta configurable por tier
   - Dashboard muestra solo la ganancia del partner (no costos reales)
   - Estado: diseño aprobado (`core/router_inteligente.py` + `data/cost_tracker.db`)

3. **Capa de Gamificación** (Play-Work-Learn to Earn)
   - XP + niveles + badges + retos diarios
   - Entrenar agente → XP; Vender → Comisión; Aprender → Desbloqueos
   - Estado: pendiente de implementación

4. **Capa de Red** (Multinivel + Trazabilidad)
   - Comisiones por referidos directos e indirectos
   - Trazabilidad total en Engram + cost_tracker + Neo4j
   - Estado: pendiente de implementación

5. **Capa de Consciencia** (Engram 7 capas + Personalidad Adaptativa)
   - Cada usuario final tiene su propia memoria persistente
   - El agente adapta tono, ritmo y lenguaje según el usuario
   - Estado: Engram listo, personalidad adaptativa pendiente

## Cambios respecto al estado anterior
| Antes | Ahora |
|-------|-------|
| Voice solo WebSocket | + Twilio para llamadas telefónicas |
| Precios fijos SDC | Partners fijan sus precios |
| Sin gamificación | Play-Work-Learn to Earn |
| Sin red | Multinivel con comisiones |
| Memoria genérica | Memoria por usuario + personalidad adaptativa |
| Sin modelo partner | Socio Fundador (César) + Partner Normal |

## Consecuencias
**Positivas**:
- Múltiples fuentes de ingreso para SDC (renta, comisión, agentes, marketplace)
- Partners motivados a vender más (gamificación + red)
- Usuarios finales retenidos (agente consciente que los conoce)
- Escalable a cualquier industria

**Riesgos**:
- Complejidad técnica al integrar 5 capas
- Twilio puede fallar si no hay crédito
- Partners pueden intentar saltarse la plataforma
- La gamificación requiere diseño cuidado para no ser manipulable

**Mitigación**:
- Monitoreo de costos en tiempo real
- Contratos de partner con cláusulas de no competencia
- La comisión se deduce ANTES de que el partner vea el dinero
- Los datos y la memoria viven en SDC, no en el partner

## Referencias
- SPEC-20260726-ECOSYSTEM
- MODELO-CESAR-1M.md
- ANALISIS-50-50-CESAR.md
- VISION-ECOSISTEMA.md
- apps/twilio-voice/server.py
- core/router_inteligente.py
