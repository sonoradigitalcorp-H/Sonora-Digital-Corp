# page-fix — Reparar páginas web rotas (links, APIs, datos, imágenes)

**Audit ID**: SKILL-PAGE-FIX-001
**Version**: 1.0.0

## Business Objective
Reparar páginas web que tienen links rotos, frontend desconectado del backend, imágenes duplicadas, chats que no funcionan, y datos falsos.

## Pipeline

```
1. Diagnosticar
   - curl -sI $URL → HTTP status?
   - ¿Links funcionan? (grep href, onclick)
   - ¿API conecta? (fetch a backend)
   - ¿Datos reales o hardcodeados?
   - ¿Chat/OpenClaw presente?

2. Reparar
   - Links rotos → corregir o eliminar
   - APIs desconectadas → agregar proxy nginx
   - Datos falsos → conectar a API real o agregar fallback
   - Chat/OpenClaw ausente → agregar chat-widget.js
   - Frontend estático → servir con nginx (no Next.js si no conecta)

3. Verificar
   - curl -sL $URL → HTTP 200
   - Click en cada link → no 404
   - API devuelve datos reales
   - Chat responde
```

## Inputs

```gherkin
Given a page URL with broken functionality
When page-fix pipeline runs
Then all links work
And API returns real data
And chat widget responds
```

## Outputs

```gherkin
Then page loads with HTTP 200
And all interactive elements connect to real backend
And OpenClaw chat is available
```

## Tools
- bash (curl, grep, nginx)
- python3 (API testing)
- openclaw (chat integration)

## Uso
```
/sdd-page https://abe.sonoradigitalcorp.com
```
