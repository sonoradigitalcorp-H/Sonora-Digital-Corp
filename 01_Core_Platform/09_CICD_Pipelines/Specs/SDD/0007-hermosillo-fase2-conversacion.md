# Spec SDD 0007 — Hermosillo Contabilidad Fase 2: Identidad, Memoria, Paquetes y Visualización

**ID**: 0007-hermosillo-fase2-conversacional
**Version**: 1.0.0
**Date**: 2026-08-16
**Author**: Luis Daniel Guerrero Enciso (MYSTIC / SDC)
**Status**: PLANIFICADO

## Resumen

Elevar la conversación del bot de Nathaly (@HermosilloCont_bot + orbe web) a nivel
**vendedor senior**: recordar al cliente por nombre, vincular memoria por chat_id,
**visualizar su contabilidad con nuestro sistema** (dashboard IA + asistente + horas
recuperadas), mostrar **3 paquetes**, CTAs de acción y refinar la identidad del agente
para transacciones rápidas y confianza. Reutiliza TODO lo de SDD 0006 — no crea
infraestructura nueva. Separa lógica por tenant y por cliente.

## Constitution Check

### Principio I: Orquestación única
- [x] Conv sigue entrando por `webhook_hermosillo` (webhook Telegram + /chat web) → agente nathaly
- [x] UN solo detector de intención (clasificador) + motor determinista
- [x] Hermes gateway (VPS) sigue siendo orquestador; NO se duplica su rol

### Principio II: Determinista vs LLM
Determinista:
- [x] Memoria de nombre: lookup por chat_id (SQLite leads / conversaciones) → INSERT nombre
- [x] Paquetes: tabla OKF estática (3 paquetes con beneficios, sin precios)
- [x] CTAs: reglas por estado (nuevo_lead → ofrece diagnóstico; post-escalar → agradece)
- [x] Script de "tu contabilidad con nosotros": sustitución determinista de variables
LLM:
- [x] Detección de nombre en mensajes libres (schema capture)
- [x] Detección de interés (dashboard/paquete) para preferencia

### Principio III: Local-first + regla de oro
- [x] Datos: SQLite leads + conversaciones (YA existe la tabla)
- [x] Fotos: fal.ai (FAL_KEY activa vía fal_client) — generadas y cacheadas en SFTP
- [x] Voz: edge-tts es-MX-DaliaNeural (local ligero / VPS MP3 endpoint)

### Principio IV: Pruebas
- [x] Tests memoria nombre (retorna nombre conocido, no saluda genérico)
- [x] Tests paquetes (3 paquetes con campos requeridos)
- [x] Tests script visión (sustitución de variables)

### Principio V: Trazabilidad
- [x] Cada turno queda en conversaciones (chat_id, rol, texto, intencion, timestamp)
- [x] El nombre del lead queda ligado a su chat_id en leads

## Spec

### 1. Memoria de nombre (llamar por nombre)
- Fuente: `leads.nombre` (capturado por clasificador) + `conversaciones` (historial)
- Función `get_nombre(chat_id)` → devuelve el nombre conocido O "" si no
- En `handle_update`/`chat_json`: si hay nombre y el saludo es nuevo → "¡Hola {nombre}! …"
- Si el usuario vuelve (mismo chat_id/sid) → lo llama por nombre sin preguntar de nuevo

### 2. Paquetes (3) — LIBERTAD DE TIEMPO
Tabla estática en OKF `sdd.pkgs`:

| Paquete | Incluye | Propuesta de valor |
|---------|---------|---------------------|
| **Básico "Orden"** | Contabilidad mensual + IVA/ISR | Tiempo de vuelta al negocio |
| **Pro "Control"** | + Administración/nómina + Consultoría IA | Dashboard mensual + asistente |
| **Empresa "Crecimiento"** | + Importaciones + Citas SAT + Asistente cliente/personal | Todo el negocio liberado |

Nota: precios → Nathaly (nunca inventar). Se ofrecen beneficios y "cotización exacta por WhatsApp".

### 3. Visualización "Así se vería tu contabilidad"
- Assets IA (fal.ai) ya generados: dashboard financiero, asistente IA, hora-devuelta
- En flujo: cuando el lead muestra interés → enviar imagen + beneficio + pregunta CTA
- Assets en `03_Media_Assets/vision/` (por tenant)

### 4. Identidad del agente nathaly (refinada)
- persona.md v2: superheroe comercial — calcula beneficios en tiempo, concreta, pregunta
- reglas.md: no inventar precios, siempre ofrecer diagnóstico, paquetes si pregunta,
  detectar nombre, llamar por nombre, CTA constante

### 5. Sin sobreingeniería
- Todos los datos en las TABLAS existentes (leads, conversaciones)
- Reutiliza `OnboardingHermosillo`, `classify_intent_hermosillo`, `assets_hermosillo`
- No se toca gateway Hermes físico; solo config de agente y webhook

## Acceptance
- [ ] Enviar mensaje con nombre → respuesta lo llama por su nombre
- [ ] Pedir "paquetes" → 3 paquetes con beneficios (sin precios)
- [ ] Lead calificado → llega imagen "dashboard para tu negocio"
- [ ] El nombre persiste entre turnos (mismo chat/sid)
- [ ] Toda conversación en `conversaciones`