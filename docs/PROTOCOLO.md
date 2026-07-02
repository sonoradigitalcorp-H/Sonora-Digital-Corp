# Protocolo de Construcción — No Fallar

**Autor**: Lecciones de SPEC-20260701-004 y SPEC-20260701-005  
**Propósito**: Cada vez que construyas algo nuevo, sigue esta secuencia. No importa lo simple que parezca.

---

## Los 7 Mandamientos

### 1. Piensa en la cadena completa antes de escribir código

No construyas una pieza aislada. Traza el flujo completo:

```
input → [tu código] → transformación → almacenamiento → lectura → visualización
```

Si construyes un health check, piensa:
- ¿Quién lo llama? → ¿Dónde se guarda? → ¿Quién lo lee? → ¿Dónde se ve?

Si construyes un dashboard, piensa:
- ¿De dónde vienen los datos? → ¿Están siendo generados? → ¿El formato es correcto?

**No construyas el 3er paso sin verificar que el 1ero funciona.**

---

### 2. Verifica el output inmediatamente después de construirlo

No asumas. No confíes. Verifica.

| Construiste | Verifica |
|-------------|----------|
| Una función que guarda datos | ¿Los datos realmente están guardados? |
| Un servicio systemd | `systemctl --user status` |
| Una regla de firewall | `curl desde afuera`, no desde localhost |
| Un health check | `get_cache_stats()` — ¿hay algo en cache? |
| Una página web | `curl http://IP_PUBLICA:PUERTO/` |
| Un cron | ¿El archivo de log existe? ¿Tiene contenido? |
| CI pipeline | Espera a que corra. No asumas que va a pasar. |

**La regla**: si no lo verificaste con tus ojos (o con un curl), no existe.

---

### 3. Prueba desde el exterior, no desde el interior

El error más repetido esta semana fue probar algo desde localhost y asumir que funciona desde internet.

```
❌ curl http://localhost:8080/          → assumption
✅ curl http://149.56.46.173:8080/      → reality
```

| Contexto | Prueba local | Prueba real |
|----------|-------------|-------------|
| Puerto | `ss -tlnp \| grep PUERTO` | `curl http://IP_PUBLICA:PUERTO/` |
| Firewall | `ufw status` | `curl desde otra máquina` |
| Binding | `127.0.0.1` vs `0.0.0.0` | `curl $IP_PUBLICA` |
| Servicio | `systemctl status` | `curl $IP_PUBLICA:$PUERTO` |

---

### 4. Una cosa a la vez. Una verificación a la vez.

No construyas 3 cosas en paralelo. El cerebro humano no hace bien paralelismo.

```
❌ Construir health check + dashboard + seed Qdrant al mismo tiempo
   → 3 cosas rotas, no sabes cuál arreglar

✅ Health check → verificar → Dashboard → verificar → Seed → verificar
   → Cada paso está firme antes del siguiente
```

**Si algo falla, sabes exactamente qué lo causó.**

---

### 5. El CI no miente. Obsérbalo.

Cada push a main genera un CI run. No lo ignores. Un CI rojo significa que tu código está roto — aunque funcione en tu máquina.

```
❌ git push y cerrar la terminal
   → 3 días después, 20 commits rojos, nadie sabe cuál rompió qué

✅ git push, esperar 2 minutos, check CI status
   → Si está verde, siguiente tarea. Si está rojo, arreglarlo AHORA.
```

URL del CI: `https://github.com/sonoradigitalcorp-H/Sonora-Digital-Corp/actions`

---

### 6. Documenta mientras construyes, no al final

El momento de escribir el ADR, la LECCION, y el Score es cuando el conocimiento está fresco.

```
❌ Construir todo el día, decir "lo documento mañana"
   → "mañana" nunca llega. Las decisiones se pierden.

✅ Escribir SPEC antes de empezar.
✅ Escribir ADR cuando tomas una decisión.
✅ Escribir LECCION cuando terminas.
✅ Escribir Score ANTES de pasar al siguiente spec.
```

El template está en `process/templates/`. No hay excusa.

---

### 7. Piensa en el olvido

Luis Daniel es olvidadizo. El sistema debe recordar por él.

```
❌ "Ya sé cómo acceder a esto, no hace falta guardarlo"
   → 2 días después: "cómo se abría esto?"

✅ Todo URL, contraseña, comando, y procedimiento está en:
   → config/machines.json (máquinas y personas)
   → AGENTS.md (comandos y estructura)
   → memory/learning/ (sesiones pasadas)
```

**Si no está escrito, no existe. Si no existe, te olvidarás.**

---

## Checklist de construcción

Copia esto en cada tarea nueva. Marca cada paso antes de pasar al siguiente.

```
[ ] SPEC escrita con FRs y criterios de éxito
[ ] Primer paso funcional y VERIFICADO
     - [ ] Código escrito
     - [ ] Output verificado (curl, stat, cache, etc)
     - [ ] Prueba desde exterior (no solo localhost)
[ ] Segundo paso funcional y VERIFICADO
[ ] Tests escritos y pasando (pytest -q)
[ ] Lint limpio (ruff check --quiet)
[ ] CI verde (esperar y verificar)
[ ] ADR escrito (si aplica)
[ ] Commits limpios (uno por concepto)
[ ] Push a main
```

---

## El mantra

> **"Construye una cosa. Verifica que funciona. Pasa a la siguiente. No construyas lo que no has verificado."**
