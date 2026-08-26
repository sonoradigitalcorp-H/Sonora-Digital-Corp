---
name: code-review-adversarial
description: Arnés de code review adversarial por IA con separación de deberes (autor/revisor/refutador/validador), ledger congelado por hash, gates y racionalidad acotada. Usar cuando haya que revisar un cambio, evitar loops infinitos de review, encontrar findings falsos, prevenir autoaprobación, o ahorrar tokens mediante revisión rigorosa. Basado en el video "curso de code review por IA" de Gentleman programming (ID 38Y1JWU-mdE).
---
# Code Review Adversarial (Arnés 4R)

**Problema core**: un agente que es autor + revisor + juez de su propio trabajo se autoaprueba, alucina findings, cae en loops, y "se va de mambo" arreglando de más. La confianza en el modelo necesita un **arnés** (harness) que lo abrace y lo contradiga.

**Consigna**: hacer las cosas bien la primera vez ahorra más tokens que iterar rápido y que explote producción. Fail-closed: lo que no se prueba **se rechaza**.

## Roles (separación de deberes — NUNCA el mismo agente ejerce 2 roles)

| Rol | Qué hace | Prohibido |
|-----|----------|-----------|
| **AUTOR** | implementa el cambio (subagente de aplicación) | revisar su propio trabajo |
| **REVISOR** | lee el código, devuelve findings CON evidencia | tocar código (solo lectura) |
| **REFUTADOR** | trata de replicar/refutar cada finding | aceptar findings sin evidencia |
| **VALIDADOR** | verifica el delta (solo las líneas que tocó el fix) | expandir scope |

## Flujo completo (apply → post-apply → gates)

```
[usuario pide cambio]
   → apply (subagente implementa)
   → post-apply:
       → orquestador CLASIFICA (modelo potente):
           LOW   = docs/comentarios/formato → NO revisión profunda, skip
           MEDIUM= cualquier otro cambio → lens dominante (1 R)
           HIGH  = auth/seguridad/pagos/vulnerabilidad → review completo (4R)
       → run_review_start: fotografía (transacción + evento + revisión previa vacía)
       → barridos: cada lens corre read-only en su subagente (4R)
           → findings con evidencia → FREEZE → ledger congelado → HASH
           (hash = huella digital del estado: "con este código, estos problemas")
       → día del juicio: 2 jueces INDEPENDIENTES (modelos distintos, no se conocen)
           → evalúan el código con criticidad (warning/critical) → iteran máx 2×
           → cada iteración revisa SOLO lo arreglado (scope minimizado)
       → clasificar evidencia: determinista | inferida | insuficiente
           determinista (test que falla) → no refutar, arreglar directo
           inferida (puede pasar) → refutar
           insuficiente (sin pruebas) → warning/suggestion, guardar, no bloquear
       → refutador: corroborado | refutado | inconcluso
           (target inmutable = JSON de problemática + evidencia; busca y replica)
           output incompleto/mal informado = inconcluso → escalar
       → corrección ACOTADA: "arreglá SOLO esto, código mínimo"
       → hash nuevo + evidencia de runtime + (rollback si falla)
       → validador del delta: verifica SOLO líneas tocadas por el fix
           → aprobado O escalar (nunca agrega scope)
       → RECEIPT (recibo): verificación final con estado → se guarda en Engram/JSON
   → gates: pre-commit | pre-push | pre-release | post-apply
       cada gate valida el receipt (hash + evidencia) antes de avanzar
   → fast-path estrecho SOLO en main: hash de origin/main + CI verde
       (si ya pasó todo, se permite release sin re-revisión)
```

## Máquina de estados del review

```
no_revisado → en_revision → jueces_confirman → se_congelan_findings
  → se_clasifica_evidencia → se_requiere_fix → se_esta_arreglando
  → se_valida_fix → revision_final → aprobado | escalar
```

## El gate en detalle (review_validate)

| Situación | Veredicto | Acción |
|-----------|-----------|--------|
| Receipt valida, huella ok | **PASA** | avanzar (commit/PR) |
| Cambió el scope, hay contenido no revisado | **INVALIDADO** | `invalidated` → revisar de nuevo |
| Nueva evidencia (CI dice test no arreglado) | **INVALIDADO** | re-validar |
| Cadena cortada / problema nuevo / se perdió | **ESCALADO** | `missing_escalated` → parar y re-validar |

## Donde vive cada pieza

- **Eventos** → Git (inmutables, traceables desde el origen)
- **Artefactos** → OpenSpec / SDD specs (`01_Core_Platform/09_CICD_Pipelines/Specs/SDD/`)
- **Espejo / lecturas** → Engram (`mem_save`)
- **Recuperación** → cadena encadenada (event sourcing) en Git + Engram

## Conceptos clave (resumen)

1. **Event sourcing**: el estado nunca se sobreescribe; cada evento es inmutable y se reconstruye la cadena desde el origen.
2. **Content-addressed storage**: hash (SHA-256) del contenido = huella digital; cambiar código cambia el hash → requiere re-revisión.
3. **Fail-closed**: todo lo que no se prueba se rechaza (cadena truncada / hash no cuadra / output incompleto → denegar).
4. **Racionalidad acotada**: presupuesto finito; máx. loops evitando el "verify, verify, verify" infinito.
5. **Verificación adversarial**: "dame evidencia". Nada se aprueba sin pruebas replicables.

## Anti-patrones que este arnés mata

- Loops infinitos de review (revisa de nuevo cosas ya revisadas)
- Findings persuasivos pero falsos (alucinación)
- Sycophancy / autoaprobación (el autor aprueba lo suyo)
- Findings que desaparecen tras iterar (una vez congelados, no se borran)
- El fix que toca 10 cosas (scope creep)
- "Ya lo revisé, confiá" (sin prueba → fail-closed)
- Amnesia de contexto (resolver con event sourcing + Engram)
