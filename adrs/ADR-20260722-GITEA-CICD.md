---
id: ADR-20260722-GITEA-CICD
title: Gitea CI/CD — Self-Hosted Git + Actions Infrastructure
status: accepted
date: 2026-07-22
---

# Gitea CI/CD Infrastructure

## Context

Sonora Digital Corp's CI/CD pipeline had three critical issues:

### 1. Split-brain (Gitea fuera del monorepo)
Gitea y Gitea Runner corrían como contenedores independientes (creados manualmente con `docker run`), sin estar declarados en `infra/docker-compose.yml`. Esto significaba que:
- No había un único source of truth para la infraestructura del sistema
- `docker compose ps` no mostraba Gitea
- No se podía hacer `docker compose up -d` para levantar todo el sistema
- Los volúmenes no estaban gestionados por compose

### 2. Policy P3 violada (0.0.0.0 sin nginx proxy)
Gitea exponía sus puertos en `0.0.0.0:3080` (HTTP) y `0.0.0.0:2223` (SSH), violando la política P3 que establece: *"Ningún servicio puede bindear 0.0.0.0 sin un proxy nginx delante"*.
- El servicio era accesible públicamente sin SSL
- No había virtual host configurado para `git.sonoradigitalcorp.com`
- No había redirección HTTP → HTTPS

### 3. Actions no espejeadas (`DEFAULT_ACTIONS_URL = self`)
Gitea Actions estaba configurado con `DEFAULT_ACTIONS_URL = self`, lo que significa que el runner busca las actions en la instancia local de Gitea (`/actions/checkout.git`, etc.) en lugar de en GitHub.com.
- El script `scripts/mirror-gh-actions.sh` existía pero con un TODO — nunca se ejecutó
- Los logs del runner mostraban `404 Not Found` para `/actions/checkout/info/refs`
- No existían workflows en `.gitea/workflows/`

### 4. Sin documentación
No existía ADR, SPEC ni documentación de la arquitectura de CI/CD en el repositorio.

## Decision

Incorporar Gitea formalmente a la infraestructura gestionada del sistema:

1. **Agregar Gitea + Gitea Runner al `docker-compose.yml`** como servicios con dominio `cicd`, con puertos bindeados a `127.0.0.1` (cumpliendo Policy P3), healthchecks, límites de memoria, y volúmenes nombrados.

2. **Agregar servicios al `docker-compose.vps.yml`** mediante `extends:` para el entorno de producción.

3. **Configurar nginx como proxy reverso** para `git.sonoradigitalcorp.com` con SSL, redirección HTTP→HTTPS y soporte WebSocket.

4. **Reescribir `scripts/mirror-gh-actions.sh`** con lógica real de mirror:
   - Clone mirror desde GitHub
   - Crear repositorio en Gitea vía API (idempotente)
   - Push mirror a Gitea
   - Reportar éxito/fallo por cada acción

5. **Crear `.gitea/workflows/verify.yml`** como workflow de prueba.

6. **Documentar en este ADR** la arquitectura, decisiones y procedimientos.

## Opciones Consideradas

### Opción A: Solo GitHub Actions (rechazada)
- **Pros**: Cero mantenimiento de infraestructura, ecosistema maduro
- **Contras**: Dependencia total de GitHub, límites de minutos gratuitos, sin control sobre runners, vendor lock-in
- **Veredicto**: Rechazada por violar el principio de vendor independence (OMEGA-PROMPT: "Vendors are replaceable")

### Opción B: Solo Gitea (seleccionada, enfoque híbrido)
- **Pros**: Control total, sin límites de ejecución, sin dependencia externa, datos en infraestructura propia
- **Contras**: Requiere mantenimiento del servidor, mirror de actions, actualizaciones periódicas
- **Veredicto**: Aceptada con mirror de GitHub Actions como puente

### Opción C: Híbrido Gitea + GitHub Actions (descartado por ahora)
- **Pros**: Lo mejor de ambos mundos
- **Contras**: Complejidad operativa duplicada, confusión sobre dónde corren los workflows, split-brain de CI/CD
- **Veredicto**: Posible en el futuro si hay casos de uso que requieran GitHub específicamente

## Consequences

### Positivas
- ✅ **Single source of truth**: Gitea ahora está declarado en `docker-compose.yml`
- ✅ **Policy P3 compliance**: Puertos bindeados a `127.0.0.1`, nginx como proxy con SSL
- ✅ **CI/CD self-hosted**: Sin dependencia de GitHub para ejecutar pipelines
- ✅ **Actions locales**: El mirror permite usar `actions/checkout@v4` y otras actions populares
- ✅ **Workflow de prueba**: `.gitea/workflows/verify.yml` permite validar que el runner funciona
- ✅ **Documentación**: ADR creado con contexto, decisión y consecuencias

### Negativas
- ⚠️ **Mantenimiento**: El mirror de actions debe ejecutarse periódicamente para mantenerlas actualizadas
- ⚠️ **Storage**: Cada action espejeada ocupa espacio en disco (~100-500MB cada una)
- ⚠️ **Runner OVH**: El runner registrado (`ovh-runner-1`) está en el mismo VPS — compite por recursos con los demás servicios
- ⚠️ **Token de registro**: El token `VF9KHaiCSScPeL0qOjfudzc4vXZTS9WCZbjaakwh` está hardcodeado en docker-compose — debería ir en una env var

### Recomendaciones
1. Mover `GITEA_RUNNER_REGISTRATION_TOKEN` a una variable de entorno en `fleet.yml` o `.env`
2. Agregar un cron job (o workflow en Gitea) que ejecute `mirror-gh-actions.sh` semanalmente
3. Monitorear el disco: 19 actions × ~200MB = ~4GB de datos espejeados
4. Considerar un segundo runner en otra máquina para alta disponibilidad

## Referencias
- Policy P3: `constitution/TRUTH.md` — "No service binds 0.0.0.0 without nginx proxy"
- OMEGA-PROMPT: Vendor independence, self-healing system
- Split-brain resolution: `AGENTS.md` — systemd vs Docker services
- Gitea Actions docs: https://docs.gitea.com/usage/actions/overview
