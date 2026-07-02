# SPEC — MCP Tools Activos + Bloqueos Producción

| Campo | Valor |
|-------|-------|
| **ID** | `SPEC-20260701-011` |
| **Fecha** | 2026-07-01 |
| **Autor** | OpenClaw |
| **Tier** | 2 |
| **Estado** | activo |
| **Score requerido** | ≥60 |

---

## 1. Objetivo

Conectar Git MCP y Memory MCP a los agentes activos para que recuerden decisiones y commiteen cambios. Resolver los 3 bloqueos de producción: Instagram, Wikipedia y TikTok handles.

---

## 2. Functional Requirements

| FR# | Descripción |
|-----|-------------|
| FR1 | Git MCP agregado como tool disponible para agentes |
| FR2 | Memory MCP conectado para que agentes recuerden decisiones |
| FR3 | Instagram: remover del sync o fix con cookies |
| FR4 | Wikipedia: probar API alternativa o marcar como degraded permanente |
| FR5 | TikTok handles: validar datos CEO vs handles reales |
| FR6 | Tests para los cambios |

---

## 3. Success Criteria

- [ ] Git MCP tool accesible desde HermesClient
- [ ] Memory MCP tool accesible desde HermesClient
- [ ] Instagram no causa errores en sync (graceful degradation)
- [ ] Wikipedia no causa errores en sync
- [ ] TikTok handles corregidos o documentados
- [ ] CI verde

---

## 4. Technical Approach

```
Git MCP: agregar tool mcp_server_git a HermesClient
Memory MCP: conectar via Hermes para que agentes guarden/recuperen contexto
Instagram: agregar detection + skip en sync si no hay cookies
Wikipedia: documentar 403 como expected, skip graceful
TikTok: verificar handles reales vs CEO data
```
