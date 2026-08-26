# ADR 0016: Code Review Adversarial — Arnés 4R con Separación de Deberes

**Fecha**: 2026-08-26
**Estado**: ADOPTADO (propuesto como proceso canónico)
**Autor**: MYSTIC / SDC
**Fuente**: Video "curso de code review por IA" (Gentleman Programming, ID `38Y1JWU-mdE`). Transcript canónico: `01_Core_Platform/05_SelfImprovement/learning/youtube/38Y1JWU-mdE_code_review_adversarial_transcript.txt`

## Contexto

El sistema COSUDE (Hermes + OpenCode) opera con agentes que generan, revisan y aprueban su propio trabajo. Esta autoaprobación genera duplicaciones, findings falsos, loops de revisión y "fix de mambo" que tocan más de lo pedido. El usuario reporta **situaciones duplicadas** y pide remediarlas volviendo el proceso de revisión más eficiente y eficaz.

## Problema

Un agente que es a la vez autor, revisor y juez de su trabajo:
1. **Se autoaprueba** (`sycophancy`) — confirma que está bien bajo su propio contexto, pero falla con el big picture.
2. **Alucina findings** — crítico persuasivo pero falso (no existe; hay que replicarlo).
3. **Cae en loops infinitos** — re-verifica cosas ya verificadas (ruido, gasto de tokens).
4. **Se va de mambo** — arregla 10 cosas cuando solo se pidió 1 (scope creep).
5. **Dice "ya lo revisé" sin prueba** — confianza ciega en el modelo.

## Decisión

Adoptar un **arnés de code review adversarial** con **separación de deberes** en 4 roles (autor, revisor, refutador, validador) + **ledger de findings congelado por hash** + **gates**. Implementación como skill reutilizable: `.opencode/skills/mystic/code-review-adversarial/SKILL.md`.

### Elementos canónicos obligatorios
- **Separación de deberes**: autor ≠ revisor ≠ refutador ≠ validador. Ningún agente ejerce 2 roles.
- **Content-addressed storage**: SHA-256 del contenido = huella digital. Cambiar código → cambia el hash → requiere re-revisión.
- **Event sourcing**: estado inmutable; reconstruir cadena desde el origen (evita amnesia de contexto).
- **Fail-closed**: lo no probado se rechaza (cadena truncada, hash que no cuadra, output incompleto = denegar).
- **Ledger congelado**: findings congelados + hash nunca se borran/cambian → no desaparecen tras iterar.
- **Racionalidad acotada**: presupuesto finito, máx. 2 iteraciones de jueces, scope minimizado por iteración.
- **Gates**: pre-commit, pre-push, pre-release, post-apply — validan el receipt antes de avanzar.
- **Fast-path estrecho** SOLO en main: hash de origin/main + CI verde → release sin re-revisión.

### Fases del flujo
```
apply (subagente implementa)
 → post-apply
   → orquestador clasifica LOW/MEDIUM/HIGH
   → run_review_start (transacción + evento + revisión previa)
   → barridos por lens read-only (4R) → findings con evidencia → FREEZE → hash
   → día del juicio: 2 jueces independientes (modelos distintos) → criticidad
   → clasificar evidencia: determinista | inferida | insuficiente
   → refutador: corroborado | refutado | inconcluso
   → corrección acotada ("arreglá solo esto") → hash nuevo + evidencia runtime
   → validador del delta (solo líneas tocadas) → aprobado | escalar
   → RECEIPT → gates → fast-path en main
```

## Alternativas consideradas

| Opción | Veredicto |
|--------|-----------|
| Dejar autoaprobación tal cual | ❌ Rechazada — duplica trabajo, findings falsos, loops |
| Solo `verification-planning` (evidencia) | ⚠️ Parcial — falta separación de roles y gates |
| Solo `sdlc-review` (review de handoffs Kanban) | ⚠️ Parcial — revisa entrega, no arnés adversarial completo |
| Arnés 4R completo (este ADR) | ✅ Adoptado — ataca la raíz (autoaprobación) |

## Consecuencias

### Positivas
- Menos duplicación y loops → ahorro de tokens (hacer bien > iterar rápido).
- Findings congelados = trazabilidad garantizada (no desaparecen).
- Fail-closed evita el "ya lo revisé, confiá".
- Separación de deberes reduce riesgo de autoaprobación.

### Negativas / costo
- Más pasos y más LLM calls por cambio (los gates y jueces usan modelo). Mitigado por: clasificación LOW (skip review), fast-path en main, y racionalidad acotada (máx 2 iteraciones).
- Requiere orquestador potente para clasificar (LOW/MEDIUM/HIGH) correctamente.

## Implementación
- **Skill**: `.opencode/skills/mystic/code-review-adversarial/SKILL.md` (arnés completo + máquina de estados + gates).
- **Transcript**: `01_Core_Platform/05_SelfImprovement/learning/youtube/38Y1JWU-mdE_code_review_adversarial_transcript.txt`.

## Estado
**PROPUESTO para adoptar como proceso canónico.** Pendiente validar en un caso real (ej. un fix concreto con findings falsos) antes de marcarlo IMPLEMENTADO.
