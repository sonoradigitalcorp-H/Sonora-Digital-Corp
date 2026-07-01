# Reglas Inquebrantables — Native Agent OS
## Violar estas reglas = degradación automática del agente

---

## 🔴 NIVEL 1: CRÍTICAS (violación = agente suspendido)

| # | Regla | Por qué | Enforced por |
|---|-------|---------|--------------|
| R-C1 | **Nunca exponer secrets en logs, respuestas, o frontends** | Seguridad crítica | `security-audit.js` check 1-3 |
| R-C2 | **Nunca editar el gateway sin verificar syntax después** | 5 veces hoy se rompió | `node -c mcp-server-http.js` post-hook |
| R-C3 | **Nunca usar node -e para editar archivos grandes** | Frágil, falla 60% de las veces | Usar `edit` tool siempre |
| R-C4 | **Nunca hacer commit sin correr tests primero** | Pre-integrité | `npm test` + `pytest` pre-commit |
| R-C5 | **Nunca inyectar código sin verificar imports duplicados** | `storeTools` duplicado | `grep -n "const.*require"` pre-check |

## 🟡 NIVEL 2: ALTAS (violación = warning automático)

| # | Regla | Por qué | Enforced por |
|---|-------|---------|--------------|
| R-H1 | **Siempre registrar tools en ALL_TOOL_HANDLERS + buildToolList()** | Tools invisibles | `test-power.js` check 1 |
| R-H2 | **Siempre agregar routes en gateway + middleware.js** | 404 silenciosos | `test-power.js` check 16 |
| R-H3 | **SSH commands: 1 comando simple por llamada** | Quoting breaks >50% | Linter de comandos |
| R-H4 | **No hardcodear números mágicos. Usar constantes con nombre** | Mantenibilidad | Code review |
| R-H5 | **Toda tool debe tener inputSchema con descripciones claras** | Usabilidad | ADK validation |

## 🟢 NIVEL 3: MEDIAS (violación = sugerencia automática)

| # | Regla | Enforced por |
|---|-------|--------------|
| R-M1 | Preferir `Write` sobre `Edit` para archivos >100 líneas | `self-improve` analysis |
| R-M2 | Documentar APIs públicas con ejemplos | Quality check |
| R-M3 | Tests nuevos para features nuevas | TDD check |
| R-M4 | Commits descriptivos con formato conventional | `git log` linter |

---

## Enforcement Automático

```bash
# Pre-commit hook (corre cada commit)
node -c mcp/gateway/mcp-server-http.js        # R-C2
grep -n "const.*require" mcp/gateway/*.js      # R-C5
node tests/mcp/test-gateway.js --quick         # R-C4

# Post-deploy hook (corre cada deploy)
curl http://127.0.0.1:18989/api/tools | ...    # R-H1
curl http://127.0.0.1:18989/abe-portal         # R-H2
```

## Auto-Penalización

Si un agente viola una regla Nivel 1:
1. Se registra en `state/quality/violations.jsonl`
2. Su `confidence` baja 20%
3. Se notifica al fundador por Telegram
4. Necesita aprobación humana para seguir operando

Si un agente acumula 3 violaciones Nivel 1 → **suspendido automáticamente**
