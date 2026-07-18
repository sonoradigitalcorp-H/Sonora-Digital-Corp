# ADR-20260718-CLONE-SERVICE — Clone Service Architecture Decisions

| Campo | Valor |
|-------|-------|
| **ID** | ADR-20260718-CLONE-SERVICE |
| **Fecha** | 2026-07-18 |
| **Dominio** | Clone Service |
| **Estado** | accepted |

---

## Context

Necesitamos un servicio de clon publicitario donde clientes envíen fotos/audio y reciban contenido con su identidad. Las opciones son: GPU local (VPS), GPU cloud (FAL.ai), o API externa.

## Decisiones

### 1. Backend de IA: FAL.ai (no GPU local)

**Opción**: Usar FAL.ai para todo el procesamiento GPU (LoRA training, image gen, video gen, lip sync)
**Razón**: El VPS no tiene GPU. FAL_KEY ya está configurado. Costo por entrenamiento LoRA ~$3-5, por asset ~$0.01-0.15.
**Consecuencia**: Dependencia externa, pero sin inversión en hardware. Margen >90%.

### 2. Voice cloning: OmniVoice (local) + MiniMax (FAL)

**Opción**: OmniVoice en puerto 3900 para clones de voz, FAL MiniMax como respaldo
**Razón**: OmniVoice ya está desplegado y no tiene costo por uso. MiniMax da mejor calidad si es necesario.
**Consecuencia**: Dos backends, pero flexibilidad de calidad vs costo.

### 3. Almacenamiento: Supabase Storage

**Opción**: Bucket `sdc-assets` con estructura /clients/{id}/
**Razón**: Supabase ya está configurado. Los MCP tools existentes suben a Supabase.
**Consecuencia**: Assets expiran a 30 días. Cliente recibe URLs públicas.

### 4. Sistema de créditos: SQLite local

**Opción**: SQLite en `data/clone_service.db` para trackear packs y créditos
**Razón**: Simple, no requiere infraestructura nueva. Suficiente para <1000 clientes.
**Consecuencia**: Migrar a PostgreSQL si escala >1000 clientes.

### 5. Canal de comunicación: WhatsApp/Telegram vía OpenClaw

**Opción**: OpenClaw gateway (puerto 18789) para recibir fotos/audio
**Razón**: OpenClaw ya está configurado con WhatsApp y Telegram. No requiere nuevo gateway.
**Consecuencia**: El agente conversacional debe detectar "terminé" y trackear progreso.

### 6. Pricing: 3 packs (Basic $49, Pro $99, Enterprise $199)

**Opción**: Packs con créditos predefinidos, no cobro por asset individual
**Razón**: Modelo simple para el cliente, revenue predecible.
**Consecuencia**: Clientes grandes pueden necesitar packs personalizados.

---

## Opciones consideradas

| Opción | Pros | Contras | Decisión |
|--------|------|---------|----------|
| GPU propia (RunPod) | Control total, sin dependencia | Configuración extra, mínimo $30/mes | ❌ |
| FAL.ai solo | Simple, ya tenemos API key | Dependencia externa | ✅ |
| FaceFusion local | All-in-one, calidad excelente | Requiere GPU, licencia comercial | ❌ |
| PostgreSQL para créditos | Escalable, robusto | Overkill para MVP | ❌ |
| Stripe para cobro por asset | Tracking granular | Complejidad extra | ❌ |

---

## Consecuencias

- Costo operativo ~$5-6/cliente + ~$0.01-0.15/asset
- Margen >90% con pack de $99
- Dependencia de FAL.ai (riesgo mitigado con OmniVoice local para TTS)
- Sin GPU local → todo el procesamiento pesado va a la nube
- Escala horizontal: agregar más clientes = más requests a FAL, sin cambios de infraestructura
