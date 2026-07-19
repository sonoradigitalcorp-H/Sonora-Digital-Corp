# ADR — Python SDK para Sonora OS

| Campo | Valor |
|-------|-------|
| **ID** | `ADR-20260719-SDK-PYTHON` |
| **Fecha** | 2026-07-19 |
| **Spec** | SPEC-20260719-UNIFICACION (FR-05) |
| **Estado** | activo |

## Contexto
El sistema tiene un SDK en Node.js (`mcp/sdk/sonora-client.js`) con JWT auth, health checks, tool calls, capability registry, y skill marketplace. Sin embargo, el ~90% del código del sistema está en Python. Cada script Python que necesita llamar al gateway reinventa la rueda con `httpx` o `subprocess`. No hay una librería unificada.

## Decisión
Crear `mcp/sdk/sonora_client.py` como mirror del SDK Node.js con:
- Misma API de alto nivel (`health()`, `tool()`, `tools()`, `capabilities()`, `skills()`)
- Mismo sistema de auth JWT con auto-refresh
- Async (asyncio) para compatibilidad con el resto del ecosistema
- Type hints para IDE support
- Logging a `state/logs/sdk/`

## Opciones Consideradas
| Opción | Pros | Contras |
|--------|------|---------|
| **SDK Python mirror (elegido)** | API familiar para usuarios del SDK Node.js | Doble mantenimiento |
| SDK Python con API diferente | Optimizado para Python | Curva de aprendizaje para usuarios del SDK Node |
| No crear SDK Python | Sin trabajo | Cada script reinventa comunicación con gateway |

## Consecuencias
- Positivas: Todos los scripts Python pueden importar `SonoraSDK` y llamar tools
- Positivas: Auth JWT centralizado, no más tokens hardcodeados
- Positivas: Logging automático de todas las llamadas
- Carga: Mantener ambos SDKs sincronizados

## Lecciones
- mockear `httpx.AsyncClient` permite tests sin gateway real (patrón de `test_hermes_client.py`)
- El gateway escucha en :18989 y expone `/auth/token`, `/health`, `/execute`, `/tools`
