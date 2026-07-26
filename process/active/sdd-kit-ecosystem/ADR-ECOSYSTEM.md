# ADR — Arquitectura Ecosistema SDC

## Estado
Aceptado

## Contexto
SDC pasó de asistente de voz simple a plataforma white-label multi-tenant.
César (AztroTech) propuso 50/50 y factura $1M MXN/mes.
Se requiere arquitectura que soporte: partners con pricing propio, comisión oculta para SDC,
gamificación, red multinivel y agentes conscientes.

## Decisión

### 1. Telefonía: FreeSWITCH + SIP Trunk > Twilio
- FreeSWITCH es open source, escalable, con WebSocket nativo para IA
- SIP Trunk (Telnyx/VoIP.ms) cuesta $0.003/min vs $0.013/min Twilio
- 80% más barato, control total, sin vendor lock-in

### 2. Tokenomics: Partner fija precio, SDC comisión oculta
- Cada partner configura precios por acción
- SDC deduce su comisión ANTES de mostrar ganancia
- Dashboard partner ve solo su precio, nunca costos SDC

### 3. Gamificación: Play-Work-Learn to Earn
- XP + niveles + badges + retos diarios
- Entrenar agente → XP; Vender → Bonus; Aprender → Desbloqueos

### 4. Red Multinivel: Comisiones por referidos
- Trazabilidad total en cost_tracker + Engram
- Comisiones automáticas por nivel de referido

### 5. Agente Consciente: Memoria 7 capas + personalidad adaptativa
- Engram ya implementado
- Personalidad adaptativa pendiente (detección de tono/estilo)

## Consecuencias
- ✅ Múltiples fuentes de ingreso
- ✅ Partners motivados (gamificación + red)
- ✅ Usuarios retenidos (agente consciente)
- ⚠️ Complejidad técnica (5 capas)
- ⚠️ Partners pueden intentar saltarse la plataforma
- Mitigación: Comisión se deduce antes de mostrar dinero
