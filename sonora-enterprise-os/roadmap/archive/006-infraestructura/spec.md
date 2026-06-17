# Feature Specification: Infraestructura y Seguridad

**Feature**: 006-infraestructura
**Status**: Active
**Input**: JARVIS necesita una base sólida: sin credenciales expuestas, tests automatizados, Docker funcional, y documentación clara.

---

## User Stories

### US15 — Sin credenciales expuestas
El proyecto no contiene API keys, tokens ni contraseñas en el código fuente ni en el historial git.

**Prioridad**: P1
**Dependencias**: Ninguna

**Independent Test**: Ejecutar `grep -r "sk-" src/ --include="*.py"` — no debe devolver resultados. Ejecutar `git log -p | grep "sk-"` — no debe devolver resultados. Testeable sin servicios.

**Acceptance Scenarios**:
1. **Given** el repositorio, **When** se busca cualquier string `sk-` o `ghp_` en el código, **Then** no hay coincidencias (excepto placeholders en `.env.example`).
2. **Given** el repositorio, **When** se ejecuta `git log -p`, **Then** no hay credenciales en ningún commit.
3. **Given** las credenciales, **When** se usan, **Then** se cargan desde `.env` (que apunta a `~/sdcorp/.secrets/keys.env` fuera del repo).

### US16 — Tests automatizados
El proyecto tiene tests que validan la funcionalidad core y pueden ejecutarse con un solo comando.

**Prioridad**: P1
**Dependencias**: Ninguna

**Independent Test**: Ejecutar `pytest tests/unit/` — debe pasar sin errores. Testeable sin Docker ni servicios externos (LLM mockeado).

**Acceptance Scenarios**:
1. **Given** el proyecto, **When** se ejecuta `pytest`, **Then** todos los tests pasan (93 tests actualmente).
2. **Given** un cambio en el código, **When** se ejecutan los tests, **Then** los tests relevantes detectan regresiones.
3. **Given** el CI, **When** se hace push, **Then** los tests se ejecutan automáticamente (GitHub Actions).

### US17 — Docker funcional
Los servicios de infraestructura (Neo4j, Qdrant, MCP Server) se levantan con `docker compose up`.

**Prioridad**: P2
**Dependencias**: Ninguna

**Independent Test**: Ejecutar `docker compose config` — debe validar sin errores. Ejecutar `docker compose up -d` y verificar health checks. Testeable con Docker instalado.

**Acceptance Scenarios**:
1. **Given** `docker-compose.yml`, **When** se ejecuta `docker compose up -d`, **Then** los servicios Neo4j, Qdrant y MCP Server arrancan sin errores.
2. **Given** los servicios corriendo, **When** se verifica health check, **Then** todos responden OK.
3. **Given** `docker-compose.yml`, **When** se inspecciona, **Then** no hay servicios que apunten a directorios inexistentes.

---

### Edge Cases

- ¿Qué pasa si el archivo `.env` no existe? El sistema MUST mostrar error claro con instrucciones para crearlo desde `.env.example`.
- ¿Qué pasa si Docker no está instalado? Los tests MUST funcionar sin Docker (servicios mockeados).
- ¿Qué pasa si GitHub Actions falla por un error de infraestructura? El workflow MUST reintentar automáticamente.
- ¿Qué pasa si un health check falla repetidamente? Docker MUST reiniciar el servicio automáticamente.
- ¿Qué pasa si el backup ocupa más espacio del disponible? El script MUST abortar con advertencia de espacio.
- ¿Qué pasa si se ejecuta `pytest` sin instalar dependencias? MUST dar error claro de importación, no fallos silenciosos.

---

## Requirements

### Functional Requirements

**FR-050**: El sistema MUST cargar todas las credenciales desde archivo `.env`, no desde código.
**FR-051**: El archivo `.env` MUST estar en `.gitignore` y `.env.example` MUST contener solo placeholders.
**FR-052**: El proyecto MUST tener tests unitarios para: orquestador, tools, neo4j_store, agents, voice.
**FR-053**: El proyecto MUST tener tests de integración para la API REST.
**FR-054**: `docker-compose.yml` MUST definir servicios solo para Neo4j, Qdrant y MCP Server.
**FR-055**: Cada servicio Docker MUST tener HEALTHCHECK.
**FR-056**: El CI (GitHub Actions) MUST ejecutar lint + tests + docker build en cada push.
**FR-057**: El proyecto MUST tener scripts de automatización: backup, healthcheck, setup systemd.

### Key Entities

- **.env**: Archivo de configuración de credenciales, fuera del repo (symlink a `~/sdcorp/.secrets/keys.env`).
- **Secrets**: API keys, tokens, contraseñas gestionadas fuera del repositorio.
- **CI Pipeline**: GitHub Actions workflow que corre lint, tests, docker build.

---

## Success Criteria

- **SC-050**: `git log -p` no muestra credenciales en ningún commit.
- **SC-051**: `pytest` pasa 93+ tests en < 60s.
- **SC-052**: `docker compose config` valida sin errores.
- **SC-053**: No hay servicios rotos en docker-compose.yml (que apunten a paths inexistentes).
- **SC-054**: Los workflows de GitHub Actions existen y son sintácticamente válidos.

---

## Assumptions

- Las credenciales se rotan periódicamente (no solo al inicio).
- Los tests mockean servicios externos (Neo4j, Qdrant, LLM).
- Docker y docker-compose están instalados en el sistema.
