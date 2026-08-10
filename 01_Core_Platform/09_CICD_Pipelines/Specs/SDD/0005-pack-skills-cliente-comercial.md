# Spec SDD 0005 — Pack de Skills por Cliente + Modelo Comercial

**ID**: 0005-pack-skills-cliente-comercial
**Version**: 1.0.0
**Date**: 2026-08-08
**Author**: Luis Daniel Guerrero Enciso
**Status**: PROPUESTA para aprobación

## Resumen

Empaquetar OpenClaw como producto por cliente: **los mismos cimientos** para todos,
con skills que se adaptan a la necesidad de cada uno. Dos clientes piloto:
- **Iván (RYE)** — industria, GRATIS (regalo hermano), máximo valor.
- **César (Aztrotech)** — venta IA/software, SE LE VENDE con modelo de ingresos.

## Contexto / Servicios Relacionados

| Servicio | Relación |
|----------|----------|
| OpenClaw agentes | cesar, rye (bots Telegram) |
| Skills workspace | packs rye-* y cesar-* (creados) |
| OKF aztrotech.pricing | cotización César |
| rye_engine.py / Qdrant kb_rye | conocimiento industrial Iván |
| Ollama VPS | LLM local $0 |
| edge-tts + faster-whisper | pipeline voz $0 |

## Especificación

### 1. Pack Skills IVÁN (RYE) — GRATIS, regalo hermano
Objetivo: dar a RYE lo que no tiene — conocer la empresa en tiempo real.
9 skills: `rye-shop-floor`, `rye-alarm-live`, `rye-shift-report`, `rye-oee`,
`rye-maintenance`, `rye-escalation`, `rye-process-improvement`,
`rye-visibility-portal`, `rye-digital-twin-ops`.

Costo para IVÁN: **$0/mes** (regalo). Luego se vende "paquete empresarial" a la empresa RYE.

### 2. Pack Skills CÉSAR (Aztrotech) — SE VENDE
8 skills: `cesar-diagnostico`, `cesar-cotizador`, `cesar-voice-recepcionista`,
`cesar-crm-demo`, `cesar-contenido`, `cesar-reporte-ejecutivo`,
`cesar-referidos`, `cesar-multi-agente`.

### 3. Modelo comercial CÉSAR (fee setup + monthly por agentes + tokens + voz)

| Concepto | Precio | Nota |
|----------|--------|------|
| **Setup fee** | **$799 USD** (una vez) | configuración bot + skills + integraciones |
| **Monthly plan 1 (1 agente)** | **$99 USD/mes** | bot ventas + 1M tokens/mes incluidos |
| **Monthly plan 2 (2-3 agentes)** | **$149 USD/mes** | multi-agente + 3M tokens/mes incluidos |
| **Monthly plan 3 (4+ agentes)** | **$249 USD/mes** | suite completa + 6M tokens/mes incluidos |
| **Token fee** | $5 USD por 1M tokens extra | solo si excede la cuota del plan (costo real cubierto) |
| **Voz clonada** | +$200 USD setup + $50/mes | clon de voz del dueño (Enterprise) |
| **Diagnóstico IA** | $0 | siempre gratis (es la puerta de venta) |

- La **mensualidad depende de: nº de agentes activos + tokens controlados**.
- Cada plan incluye su cuota de tokens; lo que exceda → token fee ($5/1M).
- Soporte incluido en todos los planes: mantenimiento, mejoras, hosting.

### 4. Programa de referidos (César embajador)
| Referido que contrata | Descuento mensualidad César |
|----------------------|----------------------------|
| Starter ($999) | -10% |
| Growth ($1999) | -15% |
| Enterprise ($3999) | -20% |

Cada referido calificado → descuento. Aprobación manual (Luis) antes de aplicar.

### 5. Espejo de mejoras (aprender de ambos)
- Lo que funcione para César (venta) → compartir patrón a futuros clientes de venta
- Lo que funcione para Iván (industrial) → paquete empresarial RYE

## Criterios de Éxito
- Bot César vende + capta leads con las skills (diagnóstico→cotiza→agenda→referido)
- Bot Iván da visibilidad en tiempo real + alerta alarmas críticas + reportes OEE
- Aztrotech: ingreso recurrente (setup + monthly) + programa de referidos activo
- RYE: regalo funcionando; luego vender "paquete empresarial" a la empresa

## Decisiones Técnicas
- Skills sin código LLM → marcan la estructura y trigon; el LLM las ejecuta
- Datos en tiempo real vía MCP (shop-floor) — no inventar estados
- Voz: pipeline local $0 (edge-tts + faster-whisper + qwen Ollama)
- Costo tokens minimizado: Ollama VPS para LLM, evitando OpenRouter

## Veredicto spec-judge recomendado
APROBADA CON CAMBIOS si falta: validar naming, pruebas e2e de cada skill, y
confirmar números de precio con Luis antes de aplicar a César.

## Spec-Judge (ejecutado 2026-08-08 · skill spec-judge · QoS $0 con Ollama)
**Veredicto: APROBADA CON CAMBIOS**
- Constitution: O1 ✅ · D2 ✅ · L3 ✅ · T4 ⚠️ (falta testing detallado) · T5 ✅
- Duplicados: ninguno (specs 0002-0004 no cubren pack por cliente)
- Correcciones: (a) agregar sección Testing con cómo probar cada skill;
  (b) confirmar precios (setup $500, monthly $99-150) y descuentos referidos
  con Luis antes de presentar a César.
- La presentación formal a César se autoriza como demo/vista previa,
  sujeto a confirmar números finales.

## Próximos pasos
1. [ ] Confirmar números de precio (Luis)
2. [ ] Probar cada skill con el bot real
3. [ ] Configurar OpenClaw→Ollama ($0) para que las skills corran gratis
4. [ ] Activar voz recepcionista — demo
