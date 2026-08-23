# Spec SDD 0013 — Multi-landing por persona (Tu Bandera A.C. + Naty Contabilidad)

**ID**: 0013-multi-landing-personas
**Version**: 1.0.0
**Date**: 2026-08-22
**Author**: MYSTIC / SDC
**Status**: EN IMPLEMENTACIÓN

## Resumen

Multi-landing sobre la base de `index.html` (orbe + glassmorphism + mic) del SDD-0012.
Reutiliza el sistema de personas `P` para servir 3 marcas sin duplicar código:

1. **Sonora Digital Corp** (index `?p=sdc`) — asistente para dueños de negocio.
2. **Nathaly Contabilidad** (index `?p=nathaly`) — SOLO contabilidad, estrategia fiscal,
   contabilidad inteligente. Sin mezclar con otros clientes.
3. **Tu Bandera A.C.** (`/tubandera.html`, `?p=tubandera`) — recuperación de adicciones,
   apoyo al usuario, familia y seguimiento. Marca propia rojo/azul + fotos Gemini.

## Constitution Check

### Principio I: Orquestación Única
- [x] Reutiliza vps_ai_server.py :8643 (sin duplicar backend)
- [x] Una sola instancia de STT/TTS en VPS
- [x] Persona `tubandera` añadida como identidad en el server (SOUL + intent replies)

### Principio II: Separación Determinista vs LLM
- [x] Router determinista (precio/cita/silencio/ubicación) por persona
- [x] SOUL por persona server-side (cero exclamaciones, cero tecnicismos)
- [x] El nombre de marca nunca se mezcla entre personas (memoria aislada por persona)

### Principio III: Cargas pesadas SOLO en VPS
- [x] STT/TTS en VPS :5292/:5293
- [x] Laptop no corre nada (solo editor)

### Principio IV: Testing
- [x] Test integración: 3 personas responden vía LLM/router
- [x] Test voz E2E: TTS→audio→STT→texto
- [x] Test HTTP page: / # /tubandera.html 200 + assets 200
- [x] Gherkin scenarios (abajo)

### Principio V: Trazabilidad
- [x] Cada persona/respuesta logueada con person + latencia
- [x] Assets de marca en `/var/www/sonoradigitalcorp/tubandera_assets/`

## Micro-interacciones requeridas (diferentes al SDD-0012)

### Detección de silencio en mic (auto-stop)
- Cuando el usuario graba y detecta `avg < 12` por **>1200ms**, la grabación se detiene
  sola y se envía a STT. Ya no es solo push-to-talk (SDD-0012 era tocar para enviar).
- Transcribir en cuanto el usuario habla; al detectar silencio, auto-enviar.

## Gherkin Scenarios

```gherkin
Feature: Multi-landing por persona
  As a visitor on sonoradigitalcorp.com
  I want the right brand and assistant per page
  So that each client gets their own tailored experience

  Scenario: Tu Bandera price intent hits deterministic router
    Given I open /tubandera.html
    When I ask "cuanto cuesta"
    Then the assistant replies with free first assessment (no price invented)

  Scenario: Tu Bandera crisis response stays human
    Given I ask the Tu Bandera assistant "quiero dejar las drogas"
    Then it responds with warmth and never diagnoses or gives medical advice

  Scenario: Nathaly page shows only accounting
    Given I open index with p=nathaly
    When I ask about taxes
    Then it talks only about accounting/fiscal, not other services

  Scenario: Mic auto-stops on silence
    Given the user is speaking into the mic
    When 1.2 seconds of silence are detected
    Then recording stops and is sent to STT automatically
```

## Contratos API (reutilizados SDD-0012)

- POST `/api/v1/chat/completions` — body `{person: sdc|nathaly|tubandera, messages[]}`
- POST `/api/stt` — multipart `file`
- POST `/api/tts` — JSON `{text, person}`
- Assets marca — `/tubandera_assets/<archivo>`

## Despliegue
- `index.html` (sdc/nathaly) y `tubandera.html` (tubandera) en `/var/www/sonoradigitalcorp/`

## Criterios de Aceptación

| ID | Criterio | Verificación |
|----|----------|--------------|
| AC-01 | Cada página sirve con título y branding propio (SDC, Nathaly, Tu Bandera) | `curl https://sonoradigitalcorp.com/<page>` → `<title>` distinto por persona |
| AC-02 | La persona `tubandera` responde router determinista de precio sin inventar costo | POST `/api/v1/chat/completions` person=tubandera "cuanto cuesta" → model=router-deterministic-price |
| AC-03 | Tu Bandera nunca diagnostica ni da consejo médico; deriva a humano/911 | POST person=tubandera con frase de crisis → respuesta cálida sin diagnósticos |
| AC-04 | Nathaly habla SOLO de contabilidad/fiscal/impuestos, no de otros servicios | POST person=nathaly → menciona contab/impuestos/SAT |
| AC-05 | El mic se detiene solo al detectar 1.2s de silencio y envía a STT | Analizador web `avg<12` por >1200ms → stopRec() + POST /api/stt |
| AC-06 | deepseek-0731 es el modelo principal con fallback a free | `/health` llm ok; payload usa `max_tokens=800` |
| AC-07 | Las páginas HTML no se cachean (siempre frescas) | `curl -D -` → `cache-control: no-cache` en `/`, `/nathaly.html`, `/tubandera.html` |
| AC-08 | Test de integración pasa 7/7 en VPS | `pytest test_sdd0013_landing.py` → 7 passed |
- Assets en `/var/www/sonoradigitalcorp/tubandera_assets/`
- Server `vps_ai_server.py` con identidad `tubandera`
