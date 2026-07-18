# ADR-20260718-ONBOARDING — Decisiones de Arquitectura del Onboarding

| Campo | Valor |
|-------|-------|
| **ID** | ADR-20260718-ONBOARDING |
| **Dominio** | Onboarding |
| **Estado** | accepted |

---

## Decisiones

### 1. Códigos alfanuméricos vs UUID

**Decisión**: Formato `SDC-XXXXXX` (6 caracteres alfanuméricos mayúsculas)
**Razón**: Más corto y legible que un UUID. Fácil de escribir en WhatsApp.
**Consecuencia**: 36 millones de combinaciones posibles. Suficiente para MVP.

### 2. Expiración de 6 horas vs 24 horas

**Decisión**: 6 horas
**Razón**: Seguridad. Suficiente tiempo para que el cliente active, pero expira rápido si no se usa.
**Consecuencia**: El partner debe enviar el link cuando el cliente está listo para activar.

### 3. Routing por número vs por código permanentemente

**Decisión**: Routing por número de teléfono (después de la activación inicial)
**Razón**: El código es solo para la activación inicial. Después, el número identifica al cliente automáticamente.
**Consecuencia**: Cada número solo puede tener un tenant activo.

### 4. Sin Twilio

**Decisión**: Usar wa.me links + OpenClaw gateway existente
**Razón**: Twilio no es necesario porque los clientes escriben al número SDC. El routing es automático.
**Consecuencia**: No hay costo adicional por mensajería.

### 5. Memoria en Engram + Qdrant + Neo4j

**Decisión**: Las 3 capas de memoria se alimentan automáticamente al activar un cliente
**Razón**: El agente necesita memoria conversacional (Engram), búsqueda semántica (Qdrant), y relaciones (Neo4j)
**Consecuencia**: Más complejidad en la activación, pero el cliente tiene un cerebro completo desde el día 1.
