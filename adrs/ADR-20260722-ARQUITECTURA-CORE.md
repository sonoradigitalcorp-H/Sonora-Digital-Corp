# ADR-20260722: Arquitectura de Capas para Sonora Digital Corp

## Estado
Aceptado

## Contexto
El monorepo de Sonora Digital Corp creció orgánicamente mezclando:
- **Core** del sistema (constitution, infra, mcp, apps, skills del sistema)
- **Productos** que SDC vende (Mystic Shield, Mystika, ABE Music, Clone Service...)
- **Clientes** externos (AstroTech, Fourgea, El Joyero, Nathy Conta...)
- **Especificaciones** históricas y activas
- **Estado** del sistema (registry, eventos, memoria)

Esta mezcla crea fricción: no está claro qué pertenece al kernel del sistema vs qué es
una ofrenda a un cliente, y la navegación del agente se vuelve ambigua.

## Decisión
Adoptar una **arquitectura de 6 capas concéntricas** organizadas en el monorepo:

```
sonora-digital-corp/
├── kernel/                 ← Capa 0: identidad, reglas, constitution (symlink → constitution/)
├── infra/                  ← Capa 1: infraestructura SSOT (fleet.yml, docker, nginx)
├── apps/ + mcp/ + skills/  ← Capa 2: servicios core del sistema
├── products/               ← Capa 3: lo que SDC vende (cada uno aislado)
├── clients/                ← Capa 4: clientes externos
├── portal/                 ← Capa transversal: visualización del sistema (Grimoire 3D)
├── ops/                    ← Capa transversal: playbooks, runbooks, recovery
├── reference/              ← Capa transversal: especificaciones cerradas, arqueología
└── state/                  ← Capa transversal: estado vivo del sistema
```

### Principios

1. **El core no se mezcla con clientes**: kernel/, infra/, apps/, mcp/ contienen solo
   lo que hace funcionar a Sonora Digital Corp como empresa. Productos y clientes
   importan del core, nunca al revés.

2. **Cada producto es un sistema aislado**: products/<id>/ contiene su propio
   código, tests, skills, y documentación. Puede convertirse en repo separado
   cuando escale.

3. **Cada cliente es una galaxia aparte**: clients/<id>/ contiene branding,
   conocimiento, memoria, skills y flujos específicos de ese cliente. No comparte
   estado con otros clientes ni con el core.

4. **El portal es la interfaz visual del sistema**: portal/ contiene el Grimoire 3D
   (Three.js) que representa en tiempo real el estado de todas las capas.

5. **Los playbooks gobiernan el comportamiento**: ops/playbooks/ contiene recetas
   paso a paso para que los agentes ejecuten procedimientos estandarizados.

### Cambios respecto al estado anterior

| Antes | Ahora |
|-------|-------|
| `constitution/` suelto en raíz | `kernel/` como symlink a `constitution/` |
| todo mezclado en raíz | productos, clientes y core separados |
| sin `portal/` | `portal/` con Grimoire 3D |
| sin `ops/` | `ops/` con playbooks y runbooks |
| `~/sonora-digital-corp` roto | symlink funcional desde home |
| `~/sdc` roto | symlink funcional |
| `~/jarvis` roto | symlink funcional |

## Consecuencias

**Positivas**:
- Navegación clara para agentes humanos y de IA
- Escalamiento: cada producto puede independizarse sin refactor
- Seguridad: clientes no acceden al core ni viceversa
- Visualización: el portal refleja la arquitectura real

**Riesgos**:
- Migración de código existente puede dejar archivos huérfanos
- Scripts que referencian rutas absolutas pueden romperse
- Se requiere disciplina para mantener la separación

**Mitigación**:
- Los playbooks en ops/playbooks/ documentan el procedimiento
- Los scripts heredados se actualizan gradualmente
- Los tests existentes no se mueven hasta que se refactorice su código

## Referencias
- MAPA-SDC.md — blueprint original del que esta ADR es concreción
- AGENTS.md — guía actualizada del repositorio
- portal/data/system.json — datos del sistema que alimenta el Grimoire
