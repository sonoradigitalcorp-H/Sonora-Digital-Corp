# Lección — SPEC-20260726-4PILARES

| Campo | Valor |
|-------|-------|
| **Spec** | `SPEC-20260726-4PILARES` |
| **Tier** | 3 |
| **Fecha** | 2026-07-26 |

---

## ¿Qué pasó?

Se diseñó la transformación arquitectónica de Sonora Digital Corp de monorepo a plataforma SaaS multi-tenant con 4 pilares (Products, Capabilities, Agents, Infrastructure). La iniciativa cubre 4 sprints (8 semanas) con 10 FRs, 8 edge cases, 8 gherkin scenarios, y un Enterprise Score de 81/100.

---

## ¿Qué salió bien?

- La estructura 4 pilares refleja lo que el código YA hace de manera implícita (products usan apps/core, agents orquestan)
- RLS en Postgres es la solución más pragmática: no añade infraestructura nueva, solo política
- Los FRs cubren todos los aspectos: estructura, multi-tenant, agents, capabilities, partners, channels, plans, marketplace
- Gherkin scenarios cubren 8 casos incluyendo happy path + edge (prorrateo, grace period, rate limiting, cross-tenant isolation)
- El score de 81/100 refleja que la iniciativa ataca directamente los value drivers correctos

---

## ¿Qué salió mal?

- La estimación de 40 días puede ser optimista: migrar `apps/` a `capabilities/` requiere tocar ~38 subdirectorios de apps
- Stripe Connect tiene complejidades que no se reflejan en los FRs (webhooks idempotentes, manejo de fallos de pago, dunning emails)
- El Sprint 1 (Products + Capabilities) es el más riesgoso porque hay que mantener compatibilidad hacia atrás mientras se refactoriza
- No se consideró el costo de migración de datos existentes (clientes actuales en tablas sin tenant_id)

---

## ¿Qué haríamos diferente?

- Añadir un Sprint 0 de 1 semana solo para diagnóstico: mapear cada tabla de Postgres, cada ruta de API, cada import de `apps/` para saber exactamente qué migrar
- Stripe Connect debería tener su propia spec detallada (los webhooks son un mundo)
- La migración de datos debería tener su propia tarea: `ALTER TABLE ... ADD COLUMN tenant_id` con backfill para clientes existentes
- Incluir en el budget 1 semana de buffer por sprint (total 12 semanas realistas vs 8 ideales)

---

## Engram Tags

arquitectura, multi-tenant, 4-pilares, refactor, saas, rls, stripe, partners, white-label, marketplace, gamification, enterprise-score, sdd-pipeline
