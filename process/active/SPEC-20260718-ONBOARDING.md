# SPEC-20260718-ONBOARDING — Sistema de Onboarding por Código

| Campo | Valor |
|-------|-------|
| **ID** | `SPEC-20260718-ONBOARDING` |
| **Fecha** | 2026-07-18 |
| **Autor** | Mystic (SDC Orchestrator) |
| **Tier** | 3 |
| **Score requerido** | ≥75 |

---

## 1. Objetivo

Crear un sistema de onboarding donde los clientes reciben un código único por wa.me, lo envían por WhatsApp, y su cerebro digital se activa automáticamente — sin QR, sin configuraciones, sin fricción.

## 2. Value Driver

- **Retention**: onboarding en <5 minutos sin fricción
- **Revenue**: clientes activos más rápido = facturación más rápido
- **Founder-independence**: el sistema onborda solo, sin intervención humana

## 3. FRs

| FR# | Descripción |
|-----|-------------|
| **FR-01** | **Generación de códigos**: Crear códigos únicos de 6 caracteres (SDC-XXXXXX) con expiración de 6h |
| **FR-02** | **Validación de códigos**: Recibir código por WhatsApp, validar expiración, asociar número al tenant |
| **FR-03** | **Routing por número**: Detectar automáticamente el tenant por el número de teléfono del cliente |
| **FR-04** | **Onboarding flow**: Mensajes automáticos de bienvenida en 5 pasos |
| **FR-05** | **Memoria persistente en Engram + vectores + grafos** |
| **FR-06** | **Skills agenticos activados por tenant** |

## 4. Gherkin

Ver `gherkin/onboarding-*.feature` (5 features, 19 escenarios)

## 5. Edge Cases

| EC# | Descripción |
|-----|-------------|
| EC1 | Código expirado (>6h) → mensaje: "Tu código expiró. Solicita uno nuevo con tu asesor." |
| EC2 | Código ya usado → mensaje: "Este código ya fue activado. Tu asistente te espera." |
| EC3 | Número desconocido escribe al bot → mensaje de bienvenida + opción de registro |
| EC4 | Código inválido (formato incorrecto) → mensaje: "Código no reconocido. Verifica e intenta de nuevo." |
| EC5 | Cliente no completa onboarding flow → recordatorio automático a las 2h |

## 6. Technical Approach

### Flujo

```
Partner crea cliente → onboarding.py generate → wa.me link
    → código en SQLite (expira 6h)
    → link enviado al cliente

Cliente hace clic → wa.me con código pre-escrito
    → bot valida código
    → asocia número al tenant
    → activa plan
    → guarda en Engram + Qdrant + Neo4j
    → inicia onboarding flow de 5 pasos
```

### Routing

```yaml
OpenClaw recibe mensaje:
  → detecta número de teléfono
  → consulta routing.yaml
  → si existe → carga tenant + skills
  → si no existe → responde con onboarding
```

## 7. Dependencies

- OpenClaw Gateway (puerto 18789)
- Engram (puerto 7437)
- Qdrant (puerto 6333)
- Neo4j (puerto 7687)
- Supabase Storage

## 8. Events

| Evento | Cuándo |
|--------|--------|
| `onboarding.code_generated` | Código creado |
| `onboarding.code_validated` | Código validado correctamente |
| `onboarding.tenant_activated` | Tenant activado |
| `onboarding.flow_step` | Cada paso del onboarding flow |

## 9. Kill Criteria

- Validación de código > 2 segundos
- Onboarding flow con más de 10% de abandono en paso 1
- Routing por número con latencia > 500ms

## 10. Scale Criteria

- >100 clientes/día → worker separado para validación de códigos
- >1000 clientes/día → PostgreSQL en vez de SQLite para códigos
