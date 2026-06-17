# Feature Specification: Mysticverse

**Feature**: 010-mysticverse
**Created**: 2026-06-09
**Status**: Implemented
**Input**: Marca separada para nicho adulto sobre infraestructura JARVIS. Clon digital, KYC, gamificación, bots Telegram.

---

## Clarifications

| # | Question | Answer | Session |
|---|----------|--------|---------|
| 1 | ¿Misma infraestructura que SDC? | Sí, mismo JARVIS, diferente marca y dominio | 010-01 |
| 2 | ¿Hosting NSFW? | VPS propio, no Vercel | 010-01 |
| 3 | ¿Multiplicador adulto? | x2 sobre planes SDC base | 010-01 |

---

## Infrastructure Mapping

| Component | File | Role |
|-----------|------|------|
| AgentOrchestrator | `src/core/orchestrator.py` | Perfil "adulto" routing |
| HermesBridge | `src/core/unified_bridge.py` | Telegram bots |
| OpenClawGateway | `src/core/unified_bridge.py` | fal-ai, stripe, printful |
| Gamification | `src/core/gamification.py` | XP, niveles, badges |
| Mysticverse | `src/core/mysticverse.py` | Twin pipeline, KYC, bots |
| Neo4j | `docker/neo4j/` | Relaciones creadora-fan |

---

## User Stories

### US1 — Crear Clon Digital (Priority: P1)

**Why This Priority**: El clon es el producto principal

**Independent Test**: Subir 5 fotos → crear twin → verificar pipeline de 4 pasos.

**Acceptance Scenarios**:

1. **Given** fotos de una creadora, **When** se crea el twin, **Then** el pipeline inicia en "processing".
2. **Given** los 4 pasos completados, **When** se verifica el twin, **Then** su estado es "active".
3. **Given** un twin existente, **When** se consulta por creadora, **Then** se listan todos sus twins.

### US2 — KYC Automático (Priority: P1)

**Why This Priority**: Requisito legal para nicho adulto

**Independent Test**: Flujo completo: edad → identidad → consentimiento → verificado.

**Acceptance Scenarios**:

1. **Given** un documento de identidad, **When** se verifica edad, **Then** status = "age_verified".
2. **Given** age_verified, **When** se verifica identidad con selfie, **Then** status = "identity_verified".
3. **Given** identity_verified, **When** se firma consentimiento, **Then** status = "completed" e is_verified = true.

### US3 — Gamificación (Priority: P2)

**Why This Priority**: Retención de usuarios

**Independent Test**: Enviar XP → subir nivel → recibir badge.

**Acceptance Scenarios**:

1. **Given** un jugador nuevo, **When** recibe 100 XP, **Then** sube a nivel 2.
2. **Given** un badge no adquirido, **When** se otorga, **Then** se añade al jugador.
3. **Given** múltiples jugadores, **When** se consulta leaderboard, **Then** están ordenados por XP descendente.

---

## Edge Cases

- ¿Qué pasa si fal-ai no está disponible? El pipeline de clon queda en "processing" hasta que se restaure.
- ¿Qué pasa si el KYC falla? Se notifica a la creadora qué documento corregir.
- ¿Qué pasa si un fan ya tiene el badge? No se duplica, se informa "already awarded".

---

## Requirements

### Functional Requirements *(mandatory)*

- **FR-001**: Sistema MUST generar clon digital desde fotos en pipeline de 4 pasos.
- **FR-002**: Sistema MUST verificar edad + identidad + consentimiento antes de activar cuenta.
- **FR-003**: Sistema MUST tener motor de gamificación con XP, niveles (1-8), badges (12).
- **FR-004**: Sistema MUST exponer leaderboard y progreso por jugador.
- **FR-005**: Sistema MUST aplicar multiplicador x2 en precios para nicho adulto.

### Key Entities

- **DigitalTwin**: Clon digital con fotos, voz, personalidad, bot asociado.
- **KYC Record**: Verificación de edad, identidad y consentimiento.
- **Player**: Usuario con XP, nivel, badges, streak.
- **Badge**: Logro con nombre, ícono, XP asociado.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Pipeline de clon completado en < 5min.
- **SC-002**: KYC completo en 3 fases verificable por API.
- **SC-003**: Gamificación engine con 8 niveles, 12 badges, XP tracking.
- **SC-004**: 29 tests de unidad pasando.

---

## Assumptions

- Fal.ai disponible para generación de imágenes.
- Creadoras tienen fotos de calidad para el clon.
- Usuarios finales tienen Telegram para interactuar con bots.
