# SPEC — Capability Registry + Decision Engine

| Campo | Valor |
|-------|-------|
| **ID** | `SPEC-20260701-004` |
| **Fecha** | 2026-07-01 |
| **Autor** | Mystic (Strategy OS) |
| **Tier** | 2 |
| **Estado** | activo |
| **Score requerido** | ≥75 |

---

## 1. Objetivo

Pasar de `sync.py` importando `fetch_artist` de Deezer directo (orden fijo, sin fallback real) a un sistema donde el runtime consulta un registry de capacidades, elige el mejor proveedor según disponibilidad, y ejecuta contra cualquier fuente sin cambiar código cliente.

Zero cambios en `sync.py` cuando se agregue el collector #8.

---

## 2. Value Driver

founder-independence, automation, reliability, scalability

---

## 3. Functional Requirements

| FR# | Descripción |
|-----|-------------|
| FR1 | Registry declarativo JSON con capabilities, providers, input/output schemas, cost, weight, health_url |
| FR2 | Decision Engine que selecciona mejor provider según weight, health, cost para una capability dada |
| FR3 | Health checking automático con cache de 5 min TTL y refresh on demand |
| FR4 | Fallback automático: si provider primario falla, engine prueba el siguiente por weight |
| FR5 | Events: CapabilityExecuted, ProviderFailed, ProviderDegraded emitidos a events.jsonl |
| FR6 | Backward compatible: sync.py sigue funcionando durante migración |
| FR7 | Cost tracking: cada ejecución registra latency y costo estimado |
| FR8 | Cada collector expone CAPABILITY_ID y PROVIDER_ID como metadata |

---

## 4. Success Criteria

- [ ] Registry contiene ≥3 capabilities con ≥1 provider cada una
- [ ] Decision Engine selecciona provider correcto para Hector Rubio (Deezer #1 si healthy)
- [ ] Si Deezer falla (mock 403), engine elige Apple Music automáticamente
- [ ] Evento CapabilityExecuted escrito por cada ejecución exitosa
- [ ] sync.py migrado a usar engine — zero cambios en collectors
- [ ] Todos los tests existentes de ABE Service siguen pasando (9/9)
- [ ] Score ≥75

---

## 5. Gherkin Scenarios

Ver `gherkin/SPEC-20260701-004.feature` (25 escenarios)

---

## 6. Edge Cases

- [EC1] Provider no tiene health_url → asumir healthy con weight penalty
- [EC2] Cache de health está stale → refresh automático antes de decisión
- [EC3] Provider falla entre health check y ejecución → fallback al siguiente
- [EC4] Registry JSON inválido → error load con mensaje claro
- [EC5] Capability sin providers → NoProviderAvailableError
- [EC6] Provider con enabled=false → excluido de selección
- [EC7] Cost tracking sin costo definido → asumir 0
- [EC8] Timeout en health check → status degraded

---

## 7. Technical Approach

```
planner/
├── __init__.py              # Re-export: select_provider, get_capability
├── models.py                # Pydantic: Capability, Provider, ProviderHealth, CapabilityResult
├── registry.py              # Loader + validator de config/registry.json
├── health.py                # Health checker con cache TTL 5min
├── decision_engine.py       # Provider selection + execution con fallback
├── events.py                # Event emitter a state/logs/events.jsonl
└── exceptions.py            # NoProviderAvailableError, ProviderExecutionError

scrapers/sync.py             # Migrado a usar decision_engine.execute_capability()
scrapers/collectors/*.py     # Anotados con CAPABILITY_ID, PROVIDER_ID
config/registry.json         # Expandido: capabilities + providers schema v2
```

Pipeline:
```
sync.py → planner.decide(capability="acquire-metadata", input={artist})
            ↓
          registry.lookup(capability)
            ↓
          health.filter(providers)
            ↓
          engine.select(providers, weight, cost)
            ↓
          provider.execute(input)
            ↓
          event: CapabilityExecuted
            ↓
          resultado → merge a data/abe-music.json
```

---

## 8. Dependencies

- `config/registry.json` existente (skills) — se expande, no reemplaza
- `config/providers.json` existente (LLM providers) — se unifica
- `scrapers/collectors/*.py` existentes — se anotan, no modifican lógica
- `scrapers/sync.py` existente — se migra a engine
- `state/logs/events.jsonl` existente — se agregan eventos, no se rompen existentes
- Python 3.10+ con Pydantic v2

---

## 9. Events to Emit

| Evento | Cuándo |
|--------|--------|
| `CapabilityExecuted` | Provider ejecuta exitosamente |
| `ProviderFailed` | Provider falla durante ejecución |
| `ProviderDegraded` | Provider responde pero latencia > threshold |
| `ProviderRecovered` | Provider vuelve a healthy después de degraded/down |
| `NoProviderAvailable` | Engine no encuentra provider healthy |
| `RegistryUpdated` | Registry recargado exitosamente |
| `SyncCycleStarted` | Ciclo de sync inicia |
| `SyncCycleCompleted` | Ciclo de sync termina |

---

## 10. Kill Criteria

Si después de 1 semana:
1. Registry no se consulta en runtime (sigue siendo decorativo), o
2. sync.py no se migró y sigue en orden fijo, o
3. Engine añade más latencia de la que ahorra
→ Abortar, mantener orden fijo actual.

---

## 11. Scale Criteria

Cuando el sistema maneje >10 capacidades o >5 providers por capacidad:
- Agregar cola de mensajes (Redis Streams) para health checks asíncronos
- Rate limiting por provider
- Dashboard de salud de providers
- Provider auto-discovery via MCP
