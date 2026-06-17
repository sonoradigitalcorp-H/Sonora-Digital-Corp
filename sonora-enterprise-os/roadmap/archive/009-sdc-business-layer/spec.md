# Feature Specification: SDC Business Layer

**Feature**: 009-sdc-business-layer
**Created**: 2026-06-09
**Status**: Implemented
**Input**: Conectar infraestructura JARVIS con modelo de negocio SaaS: 4 planes + pagos + onboarding Mystic + CRM en grafos.

---

## Clarifications

| # | Question | Answer | Session |
|---|----------|--------|---------|
| 1 | ¿Stripe o Mercado Pago? | Mercado Pago primario + Bitso crypto | 009-01 |
| 2 | ¿Multiplicador adulto? | x2 sobre precio base | 009-01 |
| 3 | ¿Planes en MXN o USD? | MXN (Mercado Pago) + USD (Stripe) | 009-01 |

---

## Infrastructure Mapping

### JARVIS Components Used

| Component | File | Role in SDC |
|-----------|------|-------------|
| AgentOrchestrator | `src/core/orchestrator.py` | Rutear clientes, activar skills por nicho |
| HermesBridge | `src/core/unified_bridge.py` | WhatsApp, Telegram, Discord |
| OpenClawGateway | `src/core/unified_bridge.py` | Stripe, contenido, redes |
| Neo4j | `docker/neo4j/` | CRM en grafos |
| Web UI | `webui/fastapp.py` | Dashboard, onboarding, planes |
| n8n | `config/n8n-sdc/` | Workflows de pago, onboarding |

---

## User Stories

### US1 — Onboarding Inteligente con Mystic (Priority: P1)

**Why This Priority**: Sin onboarding no hay clientes. Es la puerta de entrada.
**Dependencies**: None

**Independent Test**: POST /api/sdc/onboarding con datos de persona → verificar plan asignado correctamente.

**Acceptance Scenarios**:

1. **Given** un usuario que llega a la web, **When** Mystic hace 3 preguntas (quién eres, nicho, necesidad), **Then** se asigna plan correcto.
2. **Given** un usuario de nicho adulto, **When** se calcula el precio, **Then** se aplica multiplicador x2.
3. **Given** datos inválidos, **When** se envía el onboarding, **Then** se devuelve error sin crear cliente.

### US2 — Sistema de Planes con Pago (Priority: P1)

**Why This Priority**: Sin cobro no hay negocio.
**Dependencies**: US1

**Independent Test**: Crear preferencia de pago en Mercado Pago → verificar URL de checkout generada.

**Acceptance Scenarios**:

1. **Given** un plan seleccionado, **When** se crea el pago, **Then** se genera URL de checkout.
2. **Given** un pago aprobado, **When** llega el webhook, **Then** se activa el plan.
3. **Given** Mercado Pago no disponible, **When** se intenta pagar, **Then** se muestra Bitso como alternativa.

### US3 — CRM en Grafos (Priority: P2)

**Why This Priority**: El CRM es diferencial frente a competidores.
**Dependencies**: US1

**Independent Test**: Crear cliente → agregar interacciones → consultar grafo → verificar relaciones.

**Acceptance Scenarios**:

1. **Given** un cliente creado, **When** se consulta su perfil, **Then** se ven sus datos y plan.
2. **Given** múltiples clientes, **When** se busca por email, **Then** se encuentra rápidamente.
3. **Given** clientes referidos, **When** se ve el grafo, **Then** se muestra la cadena de referidos.

---

## Edge Cases

- ¿Qué pasa si Mercado Pago no está disponible? Se muestra Bitso como alternativa + mensaje informativo.
- ¿Qué pasa si el onboarding queda incompleto? Se guarda como lead para follow-up de Mystic.
- ¿Qué pasa si el webhook de pago no llega? Sistema de polling cada 5 min para verificar estado.

---

## Requirements

### Functional Requirements *(mandatory)*

- **FR-001**: Sistema MUST tener 4 planes: Explorador ($0), Conquistador ($39), Agente IA ($69), Imperio ($149).
- **FR-002**: Sistema MUST aplicar multiplicador x2 para nicho adulto.
- **FR-003**: Sistema MUST soportar Mercado Pago (cards, OXXO, SPEI, wallet) y Bitso (USDC, BTC).
- **FR-004**: Sistema MUST almacenar clientes en Neo4j como nodos Customer.
- **FR-005**: Sistema MUST exponer onboarding interactivo de Mystic en 3 preguntas.

### Key Entities

- **Customer**: Cliente con tipo (persona/empresa), nicho, plan, status.
- **Subscription**: Suscripción activa con plan, precio, fechas.
- **Transaction**: Pago con proveedor, monto, estado.
- **Lead**: Prospecto no convertido con fuente y score.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Onboarding completo asigna plan correcto en < 2s.
- **SC-002**: Pago con Mercado Pago genera URL de checkout en < 1s.
- **SC-003**: Multiplicador adulto x2 aplicado correctamente en todos los cálculos.
- **SC-004**: CRM almacena y recupera clientes con y sin Neo4j.
- **SC-005**: 42 tests de unidad pasando.

---

## Assumptions

- Mercado Pago es el proveedor de pago primario para México.
- Clientes tienen acceso a internet para completar pago.
- Nicho adulto requiere KYC y age verification.
